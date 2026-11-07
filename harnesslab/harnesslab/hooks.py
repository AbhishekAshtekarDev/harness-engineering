"""Hooks: harness code that runs at fixed points around every tool call.

A hook gives you deterministic control. The model may forget an instruction;
it cannot skip a hook. Two kinds:

    pre-tool hooks   run before the call. Return a string to block the call and
                     tell the agent why, or None to let it through.
    post-tool hooks  run after the call. Return a string to append feedback to
                     the tool result (for example lint errors after an edit),
                     or None to add nothing.

The helpers below are the hooks the course uses. Each is small on purpose.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Callable

from .models import ToolCall

PreHook = Callable[[ToolCall], "str | None"]
PostHook = Callable[[ToolCall, str, bool], "str | None"]


@dataclass
class Hooks:
    pre: list[PreHook] = field(default_factory=list)
    post: list[PostHook] = field(default_factory=list)

    def run_pre(self, call: ToolCall) -> str | None:
        for hook in self.pre:
            verdict = hook(call)
            if verdict:
                return verdict
        return None

    def run_post(self, call: ToolCall, result: str, is_error: bool) -> str:
        notes = [n for hook in self.post if (n := hook(call, result, is_error))]
        return "\n\n".join(notes)


def block_commands(*patterns: str, why: str = "This command is not allowed in this harness.") -> PreHook:
    """Block run_command calls whose command matches any glob pattern."""
    def hook(call: ToolCall) -> str | None:
        if call.name == "run_command":
            cmd = str(call.args.get("command", ""))
            if any(fnmatch.fnmatchcase(cmd, p) for p in patterns):
                return why
        return None
    return hook


def inject_on_read(path_glob: str, guidance: str) -> PostHook:
    """Feedforward at the right moment: add guidance when the agent opens matching files."""
    def hook(call: ToolCall, result: str, is_error: bool) -> str | None:
        if call.name == "read_file" and not is_error and fnmatch.fnmatchcase(str(call.args.get("path", "")), path_glob):
            return f"[harness guidance] {guidance}"
        return None
    return hook


def after_edit(run: Callable[[str], str | None]) -> PostHook:
    """Run a fast check (lint, related tests) after every successful edit or new file."""
    def hook(call: ToolCall, result: str, is_error: bool) -> str | None:
        if call.name in ("edit_file", "write_file") and not is_error:
            return run(str(call.args.get("path", "")))
        return None
    return hook
