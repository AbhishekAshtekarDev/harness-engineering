"""Permissions: what the agent may do, may do after asking, and may never do.

Two layers, as in real coding agents:

1. Rules on tool calls (allow / ask / deny). Deny rules are checked first,
   then ask, then allow, so one deny always wins. Anything no rule covers
   falls through to the policy default.
2. A path guard that resolves every path the agent touches and refuses
   anything outside the workspace or outside the writable folders, including
   `../` tricks and symlinks that point elsewhere.

Rules shape normal behavior. Boundaries such as the path guard (and, in
production, an OS-level sandbox) are what still hold when a rule misses a
creative variation of a command.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal

from .models import ToolCall

Effect = Literal["allow", "ask", "deny"]


@dataclass
class Rule:
    effect: Effect
    tool: str                     # glob on the tool name, e.g. "run_command" or "*"
    match: str | None = None      # glob on the call's main argument (path or command)
    reason: str = ""

    def applies(self, call: ToolCall) -> bool:
        if not fnmatch.fnmatchcase(call.name, self.tool):
            return False
        if self.match is None:
            return True
        subject = str(call.args.get("path") or call.args.get("command") or "")
        return fnmatch.fnmatchcase(subject, self.match)


@dataclass
class Decision:
    effect: Effect
    reason: str
    rule: Rule | None = None


@dataclass
class PermissionPolicy:
    rules: list[Rule] = field(default_factory=list)
    default: Effect = "ask"

    def decide(self, call: ToolCall) -> Decision:
        for effect in ("deny", "ask", "allow"):
            for rule in self.rules:
                if rule.effect == effect and rule.applies(call):
                    return Decision(effect, rule.reason or f"matched {effect} rule for {rule.tool}", rule)
        return Decision(self.default, "no rule matched; using the default")


Approver = Callable[[ToolCall, str], bool]


def deny_all_approver(call: ToolCall, reason: str) -> bool:
    """Non-interactive default: nobody is there to approve, so the answer is no."""
    return False


def console_approver(call: ToolCall, reason: str) -> bool:
    print(f"\n[approval needed] {call.name} {call.args}\n  why: {reason}")
    return input("  approve? [y/N] ").strip().lower() == "y"


class PathError(PermissionError):
    pass


@dataclass
class PathGuard:
    root: Path
    writable: tuple[str, ...] = ("*",)     # globs relative to root, e.g. ("habit_tracker/*", "tests/*")
    protected: tuple[str, ...] = ()        # globs that are never writable, checked first

    def resolve(self, relative: str) -> Path:
        root = Path(self.root).resolve()
        target = (root / relative).resolve()  # follows symlinks and collapses ../
        if target != root and root not in target.parents:
            raise PathError(f"'{relative}' is outside the workspace. Use paths relative to the project root.")
        return target

    def check_write(self, relative: str) -> Path:
        target = self.resolve(relative)
        rel = target.relative_to(Path(self.root).resolve()).as_posix()
        for pattern in self.protected:
            if fnmatch.fnmatchcase(rel, pattern):
                raise PathError(f"'{rel}' is protected (matches {pattern}). "
                                f"You may write only to: {', '.join(self.writable)}.")
        if not any(fnmatch.fnmatchcase(rel, p) for p in self.writable):
            raise PathError(f"'{rel}' is not in a writable folder. "
                            f"You may write only to: {', '.join(self.writable)}.")
        return target
