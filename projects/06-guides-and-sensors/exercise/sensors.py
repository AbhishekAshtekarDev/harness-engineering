"""Project 06: a sensor written for an agent to read, and the hooks that run it.

A linter that says "HT001 violation" tells the agent something is wrong.
A linter that says what is wrong, why it matters here, and exactly how to
fix it gets the problem fixed on the next step. Böckeler calls sensor messages
written for a model a positive kind of prompt injection.

Rules for the habit-tracker codebase:
  HT001  .date() on a datetime outside timeutils.py (gives the UTC day)
  HT002  datetime.now() / datetime.utcnow() / date.today() without a time zone
"""
from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass
class Finding:
    rule: str
    path: str
    line: int
    what: str
    why: str
    fix: str

    def for_agent(self) -> str:
        return f"{self.path}:{self.line} [{self.rule}] {self.what} Why: {self.why} Fix: {self.fix}"


HT001 = dict(rule="HT001", what="calls .date() on a datetime.",
             why="completions are stored in UTC, so .date() gives the UTC day, which is wrong for users "
                 "in other time zones.",
             fix="use timeutils.local_date(moment, habit.timezone); for weeks use timeutils.week_start(day).")
HT002 = dict(rule="HT002", what="reads the clock without a time zone.",
             why="the server clock is not the user's clock.",
             fix="pass `today` in as a parameter (callers know the user's date), or use "
                 "datetime.now(ZoneInfo(habit.timezone)).")


def lint_source(path: str, source: str) -> list[Finding]:
    """Return findings for one file, using the AST (not regex), so comments and strings never match."""
    if not path.startswith("habit_tracker/") or path.endswith("timeutils.py"):
        return []
    findings: list[Finding] = []
    # TODO: parse with ast.parse and walk every ast.Call node.
    # TODO: HT001: a call whose func is an Attribute named "date" with no arguments.
    # TODO: HT002: datetime.now() with no args, datetime.utcnow(), or date.today()
    #       (func is Attribute; func.value is a Name "datetime" or "date").
    # Use Finding(path=path, line=node.lineno, **HT001) and keep findings sorted by line.
    raise NotImplementedError("Your code here: see the TODO above")
    return findings


def post_edit_hook(path: str, source: str, run_related_tests) -> str | None:
    """Runs after every successful edit. Success is silent; failures are specific.

    run_related_tests(path) -> (passed: bool, summary: str)

    Return None when lint is clean and the related tests pass (say nothing:
    every line of feedback costs context). Otherwise return one message that
    lists every lint finding (for_agent format) and, if tests failed, the
    test summary. Lint runs first because it is cheaper.
    """
    # TODO: implement as described.
    raise NotImplementedError("Your code here: see the TODO above")


GUIDANCE = {
    "habit_tracker/timeutils.py": "Date rule: use local_date() and week_start() from this module for every "
                                  "day or week calculation. Weeks run Monday to Sunday in the user's time zone.",
    "habit_tracker/reports.py": "Legacy module: it still uses Sunday weeks and UTC dates. Do not copy its patterns.",
}


def on_read_hook(path: str) -> str | None:
    """Feedforward at the right moment: guidance appears when the agent opens a relevant file."""
    # TODO: return the guidance for this path, or None.
    raise NotImplementedError("Your code here: see the TODO above")
