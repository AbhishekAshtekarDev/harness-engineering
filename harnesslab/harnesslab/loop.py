"""The agent loop, with the controls a real harness needs.

The core is the familiar cycle: call the model, run the tools it asks for,
send back the results, repeat until it stops asking for tools. Everything
else in this file is harness:

    - every tool call is schema-checked, permission-checked and hooked
    - an identical call that already failed is refused instead of repeated
    - "I'm done" is a claim; the verifier decides whether the run succeeded
    - budgets on iterations, tokens and wall-clock time end runaway runs
    - a progress detector stops runs that keep going without improving
    - every step lands in the trace, and the run ends with a stated reason
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Callable

from .checks import Verdict
from .hooks import Hooks
from .models import Model, ModelTurn, ToolCall
from .permissions import Approver, PermissionPolicy, deny_all_approver
from .tools import Tool, execute
from .trace import Tracer
from .workspace import Workspace


@dataclass
class Budget:
    max_iterations: int = 40
    max_tokens: int = 500_000           # input + output, summed across calls
    max_seconds: float = 45 * 60
    max_verification_failures: int = 3  # rejected "done" claims before escalating
    no_progress_window: int = 0         # stop if the progress score has not risen in N verifications (0 = off)


@dataclass
class RunResult:
    status: str          # succeeded | stopped | escalated
    reason: str
    iterations: int
    input_tokens: int
    output_tokens: int
    seconds: float
    final_text: str = ""
    verdict: Verdict | None = None
    messages: list[dict] = field(default_factory=list)


class AgentLoop:
    def __init__(
        self,
        model: Model,
        tools: list[Tool],
        system_prompt: str,
        workspace: Workspace | None = None,
        policy: PermissionPolicy | None = None,
        approver: Approver = deny_all_approver,
        hooks: Hooks | None = None,
        verifier: Callable[[Workspace], Verdict] | None = None,
        budget: Budget | None = None,
        tracer: Tracer | None = None,
        on_step: Callable[[str], None] | None = None,
    ):
        self.model, self.system = model, system_prompt
        self.tools = {t.name: t for t in tools}
        self.ws = workspace
        self.policy = policy or PermissionPolicy(default="allow")
        self.approver = approver
        self.hooks = hooks or Hooks()
        self.verifier = verifier
        self.budget = budget or Budget()
        self.tracer = tracer or Tracer()
        self.say = on_step or (lambda line: None)

    # ------------------------------------------------------------------ #
    def run(self, task: str, task_id: str = "task") -> RunResult:
        messages: list[dict] = [{"role": "user", "content": task}]
        failed_calls: set[str] = set()
        in_tok = out_tok = 0
        rejected_claims = 0
        best_score, stale = float("-inf"), 0
        start = time.monotonic()
        turn = ModelTurn()

        with self.tracer.span("invoke_agent", **{"gen_ai.operation.name": "invoke_agent", "task_id": task_id,
                                                 "gen_ai.request.model": self.model.name}) as root:
            def finish(status: str, reason: str, verdict: Verdict | None = None) -> RunResult:
                root.set(status=status, stop_reason=reason, iterations=i,
                         **{"gen_ai.usage.input_tokens": in_tok, "gen_ai.usage.output_tokens": out_tok})
                self.say(f"[{status}] {reason}")
                return RunResult(status, reason, i, in_tok, out_tok, time.monotonic() - start,
                                 turn.text, verdict, messages)

            i = 0
            while True:
                # ---- budgets: checked by the harness, independent of the model ----
                if i >= self.budget.max_iterations:
                    return finish("stopped", f"iteration limit ({self.budget.max_iterations}) reached")
                if in_tok + out_tok >= self.budget.max_tokens:
                    return finish("stopped", f"token budget ({self.budget.max_tokens}) used up")
                if time.monotonic() - start >= self.budget.max_seconds:
                    return finish("stopped", f"time limit ({self.budget.max_seconds:.0f}s) reached")
                i += 1

                with self.tracer.span("iteration", n=i):
                    with self.tracer.span("chat", **{"gen_ai.operation.name": "chat",
                                                     "gen_ai.request.model": self.model.name}) as s:
                        turn = self.model.complete(self.system, messages, [t.spec() for t in self.tools.values()])
                        in_tok += turn.input_tokens
                        out_tok += turn.output_tokens
                        s.set(**{"gen_ai.usage.input_tokens": turn.input_tokens,
                                 "gen_ai.usage.output_tokens": turn.output_tokens,
                                 "gen_ai.response.finish_reasons": [turn.stop_reason],
                                 "summary": (turn.text[:60] or f"{len(turn.tool_calls)} tool call(s)")})
                    messages.append({"role": "assistant", "content": turn.text,
                                     "tool_calls": [{"id": c.id, "name": c.name, "args": c.args}
                                                    for c in turn.tool_calls]})
                    if turn.text:
                        self.say(f"agent: {turn.text}")

                    # ---- the agent says it is done: verify instead of trusting ----
                    if not turn.tool_calls:
                        if not self.verifier or not self.ws:
                            return finish("succeeded", "agent finished (no verifier configured)")
                        with self.tracer.span("verify", summary="harness verification") as v:
                            verdict = self.verifier(self.ws)
                            v.set(passed=verdict.passed, score=verdict.score, result_preview=verdict.summary[:300])
                        failing = [l for l in verdict.summary.splitlines() if l.startswith("[FAIL]")]
                        self.say(f"verify: {'PASS' if verdict.passed else 'FAIL ' + (failing[0][7:110] if failing else '')}")
                        if verdict.passed:
                            return finish("succeeded", "verification passed", verdict)
                        rejected_claims += 1
                        if self.budget.no_progress_window:
                            if verdict.score > best_score:
                                best_score, stale = verdict.score, 0
                            else:
                                stale += 1
                            if stale >= self.budget.no_progress_window:
                                return finish("stopped", f"no progress in {stale} verification rounds", verdict)
                        if rejected_claims >= self.budget.max_verification_failures:
                            return finish("escalated", f"verification failed {rejected_claims} times; "
                                                       "needs a person", verdict)
                        messages.append({"role": "user", "content":
                                         "The harness ran verification and the work is not done yet:\n"
                                         f"{verdict.summary}\nFix the problems, then finish again."})
                        continue

                    # ---- run each tool call through the harness ----
                    for call in turn.tool_calls:
                        result, is_error = self._handle(call, failed_calls)
                        messages.append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                         "content": result, "is_error": is_error})

    # ------------------------------------------------------------------ #
    def _handle(self, call: ToolCall, failed_calls: set[str]) -> tuple[str, bool]:
        key = call.name + json.dumps(call.args, sort_keys=True)
        attrs = {"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": call.name,
                 "gen_ai.tool.call.id": call.id, "args": call.args}
        with self.tracer.span("execute_tool", **attrs) as s:
            tool = self.tools.get(call.name)
            if tool is None:
                return self._blocked(s, f"Unknown tool '{call.name}'. Available: {', '.join(self.tools)}.", "unknown")
            if key in failed_calls:
                return self._blocked(s, "This exact call already failed. Repeating it will fail again; "
                                        "change the arguments or try a different approach.", "repeat")
            decision = self.policy.decide(call)
            if decision.effect == "deny":
                return self._blocked(s, f"Blocked by policy: {decision.reason}", "deny")
            if decision.effect == "ask":
                approved = self.approver(call, decision.reason)
                s.set(approval="granted" if approved else "refused")
                if not approved:
                    return self._blocked(s, f"A person did not approve this action ({decision.reason}).", "refused")
            veto = self.hooks.run_pre(call)
            if veto:
                return self._blocked(s, veto, "hook")
            result, is_error = execute(tool, call.args)
            extra = self.hooks.run_post(call, result, is_error)
            if extra:
                result = f"{result}\n\n{extra}"
            if is_error:
                failed_calls.add(key)
            s.set(is_error=is_error, result_preview=result[:200])
            self.say(f"tool {call.name} {'ERROR' if is_error else 'ok'}: {result.splitlines()[0][:100] if result else ''}")
            return result, is_error

    def _blocked(self, span, message: str, why: str) -> tuple[str, bool]:
        span.set(blocked=why, is_error=True, result_preview=message[:200])
        self.say(f"blocked ({why}): {message[:100]}")
        return message, True
