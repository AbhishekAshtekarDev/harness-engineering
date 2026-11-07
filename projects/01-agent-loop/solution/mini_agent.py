"""Project 01: an agent loop from scratch.

An agent is a model that calls tools in a loop. This file is the whole loop.
The transcript format matches harnesslab, so the same loop runs with the
scripted model in the tests and with a real model in run_real.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass
class Turn:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class Model(Protocol):
    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> Turn: ...


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    fn: Callable[..., str]

    def spec(self) -> dict:
        return {"name": self.name, "description": self.description, "input_schema": self.input_schema}


@dataclass
class Result:
    status: str          # "finished" or "max_turns"
    turns: int
    final_text: str
    messages: list[dict]


def execute_tool(tools: dict[str, Tool], call: ToolCall) -> tuple[str, bool]:
    """Run one tool call. Return (result_text, is_error). Never raise.

    A model learns from errors only if it can read them, so every failure
    becomes text: an unknown tool name lists the tools that exist, and an
    exception inside a tool comes back as its type and message.
    """
    # TODO: look up the tool; on a missing name return an error listing available tools.
    # TODO: call tool.fn(**call.args); on any exception return "Error: <Type>: <message>".
    # BEGIN SOLUTION
    tool = tools.get(call.name)
    if tool is None:
        return f"Error: unknown tool '{call.name}'. Available tools: {', '.join(sorted(tools))}.", True
    try:
        return str(tool.fn(**call.args)), False
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}", True
    # END SOLUTION


def run_agent(model: Model, tools: list[Tool], task: str,
              system: str = "You are a helpful agent. Use tools when they help. "
                            "When the task is complete, answer without calling tools.",
              max_turns: int = 10) -> Result:
    """The agent loop.

    1. Send the model the system prompt, the transcript and the tool specs.
    2. Record its turn in the transcript.
    3. No tool calls means the model thinks it is done: return "finished".
    4. Otherwise run every tool call and append one tool message per call.
    5. Stop with "max_turns" if the model never finishes. This limit is the
       harness's job, not the model's.
    """
    by_name = {t.name: t for t in tools}
    specs = [t.spec() for t in tools]
    messages: list[dict] = [{"role": "user", "content": task}]
    # TODO: write the loop described in the docstring.
    # Assistant message: {"role": "assistant", "content": text, "tool_calls": [{"id", "name", "args"}]}
    # Tool message:      {"role": "tool", "tool_call_id": id, "name": name, "content": text, "is_error": bool}
    # BEGIN SOLUTION
    for turn_number in range(1, max_turns + 1):
        turn = model.complete(system, messages, specs)
        messages.append({"role": "assistant", "content": turn.text,
                         "tool_calls": [{"id": c.id, "name": c.name, "args": c.args} for c in turn.tool_calls]})
        if not turn.tool_calls:
            return Result("finished", turn_number, turn.text, messages)
        for call in turn.tool_calls:
            content, is_error = execute_tool(by_name, call)
            messages.append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                             "content": content, "is_error": is_error})
    return Result("max_turns", max_turns, "", messages)
    # END SOLUTION
