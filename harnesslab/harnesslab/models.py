"""Model adapters.

The harness talks to every model through one small interface:

    turn = model.complete(system, messages, tools)

`messages` is a provider-neutral transcript made of plain dicts:

    {"role": "user", "content": "..."}
    {"role": "assistant", "content": "...", "tool_calls": [{"id", "name", "args"}]}
    {"role": "tool", "tool_call_id": "...", "name": "...", "content": "...", "is_error": bool}

Three adapters ship with harnesslab:

    ScriptedModel   replays a script. No API key, fully deterministic. The course
                    uses it so you can watch the harness react to known behavior.
    AnthropicModel  Claude through the Anthropic Messages API.
    OpenAIModel     any Chat Completions compatible model.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, Union


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass
class ModelTurn:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = ""


class Model(Protocol):
    name: str

    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> ModelTurn: ...


def estimate_tokens(text: str) -> int:
    """Rough token estimate (about four characters per token in English)."""
    return max(1, len(text) // 4)


# --------------------------------------------------------------------------- #
# Scripted model
# --------------------------------------------------------------------------- #

Step = Union[ModelTurn, dict, Callable[[list[dict]], Union[ModelTurn, dict]]]


class ScriptedModel:
    """A fake model that plays back a list of steps.

    Each step is one of:
      - a dict: {"say": "text", "calls": [("tool_name", {...args})]}
      - a ModelTurn
      - a function(messages) -> dict | ModelTurn, for steps that react to
        what the harness returned (for example, the last test output)

    When the script runs out, the model answers "Done." with no tool calls,
    which is how a real model signals that it thinks it has finished.
    """

    name = "scripted"

    def __init__(self, steps: list[Step]):
        self.steps = list(steps)
        self.cursor = 0
        self._ids = 0

    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> ModelTurn:
        prompt_text = system + json.dumps(messages) + json.dumps(tools)
        if self.cursor >= len(self.steps):
            return ModelTurn(text="Done.", input_tokens=estimate_tokens(prompt_text), output_tokens=2,
                             stop_reason="end_turn")
        step = self.steps[self.cursor]
        self.cursor += 1
        if callable(step):
            step = step(messages)
        if isinstance(step, dict):
            calls = []
            for name, args in step.get("calls", []):
                self._ids += 1
                calls.append(ToolCall(id=f"call_{self._ids}", name=name, args=args))
            step = ModelTurn(text=step.get("say", ""), tool_calls=calls)
        step.input_tokens = step.input_tokens or estimate_tokens(prompt_text)
        step.output_tokens = step.output_tokens or estimate_tokens(step.text + json.dumps(
            [c.args for c in step.tool_calls]))
        step.stop_reason = step.stop_reason or ("tool_use" if step.tool_calls else "end_turn")
        return step


# --------------------------------------------------------------------------- #
# Anthropic
# --------------------------------------------------------------------------- #

class AnthropicModel:
    """Claude via the Anthropic Messages API (`pip install anthropic`).

    Set ANTHROPIC_API_KEY. Choose the model with HARNESSLAB_MODEL or the
    `model` argument; check Anthropic's model list for current names.
    """

    def __init__(self, model: str | None = None, max_tokens: int = 4096):
        import anthropic  # imported lazily so the course runs without it

        self.client = anthropic.Anthropic()
        self.name = model or os.environ.get("HARNESSLAB_MODEL", "claude-sonnet-5-5")
        self.max_tokens = max_tokens

    @staticmethod
    def _to_api(messages: list[dict]) -> list[dict]:
        out: list[dict] = []
        for m in messages:
            if m["role"] == "user":
                out.append({"role": "user", "content": m["content"]})
            elif m["role"] == "assistant":
                blocks: list[dict] = []
                if m.get("content"):
                    blocks.append({"type": "text", "text": m["content"]})
                for c in m.get("tool_calls", []):
                    blocks.append({"type": "tool_use", "id": c["id"], "name": c["name"], "input": c["args"]})
                out.append({"role": "assistant", "content": blocks or [{"type": "text", "text": "(no text)"}]})
            elif m["role"] == "tool":
                block = {"type": "tool_result", "tool_use_id": m["tool_call_id"],
                         "content": m["content"], "is_error": bool(m.get("is_error"))}
                # Consecutive tool results share one user message.
                if out and out[-1]["role"] == "user" and isinstance(out[-1]["content"], list) \
                        and out[-1]["content"] and out[-1]["content"][0].get("type") == "tool_result":
                    out[-1]["content"].append(block)
                else:
                    out.append({"role": "user", "content": [block]})
        return out

    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> ModelTurn:
        resp = self.client.messages.create(
            model=self.name,
            max_tokens=self.max_tokens,
            system=system,
            tools=[{"name": t["name"], "description": t["description"], "input_schema": t["input_schema"]}
                   for t in tools],
            messages=self._to_api(messages),
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        calls = [ToolCall(id=b.id, name=b.name, args=dict(b.input)) for b in resp.content if b.type == "tool_use"]
        return ModelTurn(text=text, tool_calls=calls, input_tokens=resp.usage.input_tokens,
                         output_tokens=resp.usage.output_tokens, stop_reason=resp.stop_reason or "")


# --------------------------------------------------------------------------- #
# OpenAI (Chat Completions)
# --------------------------------------------------------------------------- #

class OpenAIModel:
    """Any model behind an OpenAI-compatible Chat Completions endpoint.

    Set OPENAI_API_KEY and HARNESSLAB_MODEL (for example a current GPT model).
    OPENAI_BASE_URL lets you point it at a compatible server, such as a local one.
    """

    def __init__(self, model: str | None = None):
        import openai

        self.client = openai.OpenAI()
        self.name = model or os.environ["HARNESSLAB_MODEL"]

    @staticmethod
    def _to_api(system: str, messages: list[dict]) -> list[dict]:
        out: list[dict] = [{"role": "system", "content": system}]
        for m in messages:
            if m["role"] == "user":
                out.append({"role": "user", "content": m["content"]})
            elif m["role"] == "assistant":
                msg: dict = {"role": "assistant", "content": m.get("content") or None}
                if m.get("tool_calls"):
                    msg["tool_calls"] = [{"id": c["id"], "type": "function",
                                          "function": {"name": c["name"], "arguments": json.dumps(c["args"])}}
                                         for c in m["tool_calls"]]
                out.append(msg)
            elif m["role"] == "tool":
                out.append({"role": "tool", "tool_call_id": m["tool_call_id"], "content": m["content"]})
        return out

    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> ModelTurn:
        resp = self.client.chat.completions.create(
            model=self.name,
            messages=self._to_api(system, messages),
            tools=[{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                                     "parameters": t["input_schema"]}} for t in tools],
        )
        choice = resp.choices[0]
        calls = []
        for c in choice.message.tool_calls or []:
            try:
                args = json.loads(c.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {"_unparseable_arguments": c.function.arguments}
            calls.append(ToolCall(id=c.id, name=c.function.name, args=args))
        usage = resp.usage
        return ModelTurn(text=choice.message.content or "", tool_calls=calls,
                         input_tokens=getattr(usage, "prompt_tokens", 0),
                         output_tokens=getattr(usage, "completion_tokens", 0),
                         stop_reason=choice.finish_reason or "")


def load_model(provider: str, model: str | None = None) -> Model:
    if provider == "anthropic":
        return AnthropicModel(model)
    if provider == "openai":
        return OpenAIModel(model)
    raise ValueError(f"unknown provider {provider!r} (use 'anthropic' or 'openai')")
