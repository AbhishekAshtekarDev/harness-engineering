"""Evals: measure the agent system across many tasks and many trials.

Vocabulary (from Anthropic's guide to agent evals):
    task        one test case with inputs and success criteria
    trial       one attempt at a task; agents vary, so run several
    grader      logic that scores one aspect of a trial
    transcript  the full record of a trial
    outcome     the final state of the environment (what the grader should check)

Two numbers answer two different questions:
    pass@k  chance that at least one of k attempts succeeds (fine when a person can retry)
    pass^k  chance that all k attempts succeed (what you need when it must work every time)

Both use the unbiased estimators over n recorded trials with c successes.
"""
from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from math import comb
from typing import Callable


def pass_at_k(n: int, c: int, k: int) -> float:
    """P(at least one of k trials passes), estimated from n trials with c passes."""
    if k > n:
        raise ValueError("k cannot exceed the number of trials n")
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_pow_k(n: int, c: int, k: int) -> float:
    """P(all k trials pass), estimated from n trials with c passes."""
    if k > n:
        raise ValueError("k cannot exceed the number of trials n")
    return comb(c, k) / comb(n, k)


@dataclass
class Grade:
    grader: str
    passed: bool
    score: float = 1.0
    note: str = ""


Grader = Callable[[dict], Grade]   # receives the trial record: {"outcome":..., "transcript":..., ...}


@dataclass
class EvalTask:
    id: str
    prompt: str
    graders: list[Grader]
    tags: list[str] = field(default_factory=list)


@dataclass
class TrialResult:
    task_id: str
    trial: int
    passed: bool
    grades: list[Grade]
    tokens: int = 0


def run_eval(tasks: list[EvalTask], run_trial: Callable[[EvalTask, int], dict], trials: int = 3) -> list[TrialResult]:
    """`run_trial(task, n)` runs the agent once and returns a record for the graders."""
    results = []
    for task in tasks:
        for n in range(trials):
            record = run_trial(task, n)
            grades = [g(record) for g in task.graders]
            results.append(TrialResult(task.id, n, all(g.passed for g in grades), grades, record.get("tokens", 0)))
    return results


def report(results: list[TrialResult], k: int = 3) -> str:
    by_task: dict[str, list[TrialResult]] = {}
    for r in results:
        by_task.setdefault(r.task_id, []).append(r)
    lines = [f"{'task':<28}{'pass':>6}{'pass@' + str(k):>9}{'pass^' + str(k):>9}"]
    at, pow_ = [], []
    for tid, rs in by_task.items():
        n, c = len(rs), sum(r.passed for r in rs)
        kk = min(k, n)
        a, p = pass_at_k(n, c, kk), pass_pow_k(n, c, kk)
        at.append(a)
        pow_.append(p)
        lines.append(f"{tid:<28}{c:>3}/{n:<2}{a:>9.2f}{p:>9.2f}")
    lines.append(f"{'mean':<28}{'':>6}{statistics.mean(at):>9.2f}{statistics.mean(pow_):>9.2f}")
    return "\n".join(lines)


# ----------------------------- graders ------------------------------------ #

def code_grader(name: str, check: Callable[[dict], bool], note: str = "") -> Grader:
    def grade(record: dict) -> Grade:
        ok = bool(check(record))
        return Grade(name, ok, 1.0 if ok else 0.0, note if not ok else "")
    return grade


JUDGE_TEMPLATE = """You are grading one dimension of an AI agent's work.

Criterion: {criterion}
Scale: PASS if the work clearly meets the criterion, FAIL if it does not,
UNKNOWN if the material below is not enough to decide.

Material:
<work>
{work}
</work>

Answer with JSON only: {{"verdict": "PASS" | "FAIL" | "UNKNOWN", "reason": "<one sentence>"}}"""


def judge_grader(name: str, criterion: str, ask_model: Callable[[str], str],
                 material: Callable[[dict], str]) -> Grader:
    """LLM-as-judge for one rubric criterion.

    One criterion per call, an explicit UNKNOWN escape hatch, and JSON output.
    Calibrate it against human grades on a sample before trusting its numbers.
    """
    def grade(record: dict) -> Grade:
        raw = ask_model(JUDGE_TEMPLATE.format(criterion=criterion, work=material(record)))
        try:
            data = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
            verdict = str(data.get("verdict", "UNKNOWN")).upper()
            reason = str(data.get("reason", ""))
        except ValueError:
            verdict, reason = "UNKNOWN", f"unparseable judge output: {raw[:80]}"
        return Grade(name, verdict == "PASS", 1.0 if verdict == "PASS" else 0.0, f"{verdict}: {reason}")
    return grade
