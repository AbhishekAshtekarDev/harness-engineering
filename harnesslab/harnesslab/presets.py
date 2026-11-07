"""The habit-tracker harness the course builds, assembled in one place.

Read this file top to bottom: it is the course's capstone harness in about a
hundred lines. Every block maps to a module of the course.
"""
from __future__ import annotations

import re
from pathlib import Path

from .checks import AllOf, ChangedFilesCheck, PytestCheck
from .hooks import Hooks, after_edit, block_commands, inject_on_read
from .loop import AgentLoop, Budget
from .models import Model
from .permissions import Approver, PathGuard, PermissionPolicy, Rule, deny_all_approver
from .tools import coding_tools
from .trace import Tracer
from .workspace import Workspace

REPO_ROOT = Path(__file__).resolve().parents[2]
HABIT_TRACKER = REPO_ROOT / "examples" / "habit-tracker"

WRITABLE = ("habit_tracker/*", "tests/*")
PROTECTED = ("tests/test_daily_streak.py", "tests/test_habits.py", "tests/test_timeutils.py",
             "tests/conftest.py", "config/*")

SYSTEM_PROMPT = """You are a careful software engineer working in a Python repository.
Use the tools to explore, edit and test. Follow AGENTS.md in the project root.
Work in small steps: change one thing, run the tests, read the result.
When you believe the task is complete, reply with a short report and no tool calls:
files changed, tests run, assumptions made. The harness will verify your work."""

DATE_GUIDANCE = ("Date rule for this project: completions are aware UTC datetimes. Turn them into the "
                 "user's calendar day with timeutils.local_date(c, habit.timezone) and into a week with "
                 "timeutils.week_start(day). Weeks run Monday to Sunday in the user's local time zone.")


def date_lint(ws: Workspace):
    """A custom lint rule whose message tells the agent how to fix the problem."""
    def run(path: str) -> str | None:
        if not path.startswith("habit_tracker/") or not path.endswith(".py") or path.endswith("timeutils.py"):
            return None
        problems = []
        for n, line in enumerate((ws.root / path).read_text().splitlines(), 1):
            if re.search(r"\.date\(\)", line) and not line.lstrip().startswith("#"):
                problems.append(
                    f"[lint] {path}:{n} calls .date() on a datetime. That is the UTC day, which is wrong for "
                    "users in other time zones. Fix: use timeutils.local_date(c, habit.timezone), and "
                    "timeutils.week_start(day) for weeks.")
        return "\n".join(problems) or None
    return run


def build_habit_tracker_harness(model: Model, project: Path = HABIT_TRACKER, approver: Approver = deny_all_approver,
                                trace_path: str | Path | None = None, budget: Budget | None = None,
                                on_step=None) -> tuple[AgentLoop, Workspace]:
    # Environment: a private copy of the project; .harness/ stays outside it.
    ws = Workspace(project)
    guard = PathGuard(ws.root, writable=WRITABLE, protected=PROTECTED)

    # Capability: a small, well-described toolset.
    tools = coding_tools(ws, guard)

    # Permissions: deny first, then ask, then allow.
    policy = PermissionPolicy(default="ask", rules=[
        Rule("deny", "run_command", "*rm -rf*", "destructive deletes are not allowed"),
        Rule("deny", "run_command", "*git push*", "agents never push; the harness opens the pull request"),
        Rule("deny", "run_command", "*curl*", "no network access from this sandbox"),
        Rule("ask", "run_command", "*pip install*", "new dependencies need a person's approval"),
        Rule("allow", "run_command", "python -m pytest*"),
        Rule("allow", "list_files"), Rule("allow", "search_code"), Rule("allow", "read_file"),
        Rule("allow", "edit_file"), Rule("allow", "write_file"), Rule("allow", "run_tests"),
    ])

    # Guides and sensors: guidance at the moment it matters, fast feedback after every edit.
    hooks = Hooks(
        pre=[block_commands("*sudo*", why="sudo is never available to the agent.")],
        post=[inject_on_read("habit_tracker/timeutils.py", DATE_GUIDANCE),
              inject_on_read("habit_tracker/streaks.py", DATE_GUIDANCE),
              after_edit(date_lint(ws))],
    )

    # Verification: the definition of done, checked by the harness, cheapest check first.
    hidden = project / ".harness"
    verifier = AllOf([
        ChangedFilesCheck(allowed=WRITABLE, protected=PROTECTED),
        PytestCheck(name="unit tests"),
        PytestCheck(name="acceptance + held-out tests",
                    extra_tests=sorted((hidden / "acceptance").glob("test_*.py")) +
                    sorted((hidden / "heldout").glob("test_*.py"))),
    ])

    loop = AgentLoop(model=model, tools=tools, system_prompt=SYSTEM_PROMPT, workspace=ws, policy=policy,
                     approver=approver, hooks=hooks, verifier=verifier,
                     budget=budget or Budget(max_iterations=40, max_tokens=600_000, max_seconds=45 * 60),
                     tracer=Tracer(trace_path), on_step=on_step)
    return loop, ws


def ticket(project: Path = HABIT_TRACKER) -> str:
    return (project / "TICKET-HT-142.md").read_text() + \
        "\nRead AGENTS.md first. Implement the ticket with unit tests."
