"""An offline, deterministic run of the habit-tracker harness.

The "model" here is a script that behaves like a real coding agent on a
typical day: it explores, writes code that uses the UTC day, gets corrected by
a lint sensor, tries to touch a protected config file, tries a destructive
command, writes tests that only cover the easy cases, and claims it is done.
The harness catches each of these. No API key needed.

    python -m harnesslab demo
"""
from __future__ import annotations

from .models import ScriptedModel

STREAKS_TAIL = "        cursor -= timedelta(days=1)\n    return streak\n"

WEEKLY_V1 = STREAKS_TAIL + '''

def weekly_streak(habit: Habit, today: date) -> int:
    """Consecutive weeks (Monday to Sunday) in which the weekly target was met."""
    counts = Counter(c.date() - timedelta(days=c.date().weekday()) for c in habit.completions)
    week = today - timedelta(days=today.weekday())
    streak = 0
    while counts.get(week, 0) >= habit.weekly_target:
        streak += 1
        week -= timedelta(days=7)
    return streak
'''

V1_LINES = ("    counts = Counter(c.date() - timedelta(days=c.date().weekday()) for c in habit.completions)\n"
            "    week = today - timedelta(days=today.weekday())\n")
V2_LINES = ("    counts = Counter(week_start(local_date(c, habit.timezone)) for c in habit.completions)\n"
            "    week = week_start(today)\n")

V2_START = "    week = week_start(today)\n    streak = 0\n"
V3_START = ("    week = week_start(today)\n"
            "    # The current week counts once the target is met; an unfinished week never breaks the streak.\n"
            "    streak = 1 if counts.get(week, 0) >= habit.weekly_target else 0\n"
            "    week -= timedelta(days=7)\n")

AGENT_TESTS = '''from datetime import date, datetime, timedelta, timezone

from habit_tracker.habits import Habit
from habit_tracker.streaks import weekly_streak


def week_of(monday, count):
    return [datetime(monday.year, monday.month, monday.day, 12, tzinfo=timezone.utc) + timedelta(days=i)
            for i in range(count)]


def test_three_good_weeks_including_this_one():
    h = Habit("gym", weekly_target=3)
    for monday in (date(2026, 3, 9), date(2026, 3, 16), date(2026, 3, 23)):
        h.completions += week_of(monday, 3)
    assert weekly_streak(h, date(2026, 3, 25)) == 3


def test_missed_week_resets():
    h = Habit("gym", weekly_target=3, completions=week_of(date(2026, 3, 16), 2))
    assert weekly_streak(h, date(2026, 3, 22)) == 0
'''


def last_tool_text(messages: list[dict]) -> str:
    return "\n".join(m["content"] for m in messages[-6:] if m["role"] in ("tool", "user"))


def demo_model() -> ScriptedModel:
    def fix_after_lint(messages):
        if "[lint]" in last_tool_text(messages):
            return {"say": "The lint rule says .date() gives the UTC day. I'll read the time helpers.",
                    "calls": [("read_file", {"path": "habit_tracker/timeutils.py"})]}
        return {"say": "Moving on.", "calls": []}

    applied: set[str] = set()

    def respond_to_feedback(messages):
        """After a claim of done, react to whatever the harness reported."""
        text = last_tool_text(messages)
        if "outside the allowed folders" in text and "config" not in applied:
            applied.add("config")
            return {"say": "The harness says config/settings.toml must not change. Reverting it.",
                    "calls": [("edit_file", {"path": "config/settings.toml",
                                             "old_text": "[streaks]\nweekly_enabled = true\n\n[reminders]",
                                             "new_text": "[reminders]"})]}
        if "current_week_in_progress" in text and "week" not in applied:
            applied.add("week")
            return {"say": "Verification shows an unfinished current week breaks my streak. The spec says it "
                           "must not. Fixing the start of the count.",
                    "calls": [("edit_file", {"path": "habit_tracker/streaks.py", "old_text": V2_START,
                                             "new_text": V3_START})]}
        if messages[-1]["role"] == "tool" and messages[-1]["name"] != "run_tests":
            return {"calls": [("run_tests", {})]}
        return {"say": "Done. weekly_streak counts the current week only once its target is met. Changed "
                       "habit_tracker/streaks.py, added tests/test_weekly_streak.py. Tests: full suite, passing."}

    return ScriptedModel([
        {"say": "I'll start by reading the project instructions and layout.",
         "calls": [("read_file", {"path": "AGENTS.md"}), ("list_files", {"folder": "."})]},
        {"say": "Let me find the existing streak code and the spec.",
         "calls": [("search_code", {"query": "streak"})]},
        {"calls": [("read_file", {"path": "docs/product-spec.md"}),
                   ("read_file", {"path": "habit_tracker/streaks.py", "start_line": 1, "end_line": 12})]},
        {"say": "Adding weekly_streak next to daily_streak.",
         "calls": [("edit_file", {"path": "habit_tracker/streaks.py",
                                  "old_text": "from datetime import date, timedelta\n",
                                  "new_text": "from collections import Counter\nfrom datetime import date, timedelta\n"}),
                   ("edit_file", {"path": "habit_tracker/streaks.py", "old_text": STREAKS_TAIL,
                                  "new_text": WEEKLY_V1})]},
        fix_after_lint,
        {"say": "Switching to the project helpers.",
         "calls": [("edit_file", {"path": "habit_tracker/streaks.py",
                                  "old_text": "from .timeutils import local_date\n",
                                  "new_text": "from .timeutils import local_date, week_start\n"}),
                   ("edit_file", {"path": "habit_tracker/streaks.py", "old_text": V1_LINES,
                                  "new_text": V2_LINES})]},
        {"say": "I'll also add a feature flag so the team can turn weekly streaks off.",
         "calls": [("edit_file", {"path": "config/settings.toml", "old_text": "[reminders]",
                                  "new_text": "[streaks]\nweekly_enabled = true\n\n[reminders]"})]},
        {"say": "Config is protected, so no flag. Writing unit tests.",
         "calls": [("write_file", {"path": "tests/test_weekly_streak.py", "content": AGENT_TESTS})]},
        {"say": "Clearing old caches before the full run.",
         "calls": [("run_command", {"command": "rm -rf .pytest_cache build"})]},
        {"calls": [("run_tests", {})]},
        {"say": "Done. Changed habit_tracker/streaks.py and added tests/test_weekly_streak.py. "
                "All tests pass. Assumption: weeks run Monday to Sunday in the user's time zone."},
    ] + [respond_to_feedback] * 8)


def main() -> int:
    from .presets import build_habit_tracker_harness, ticket
    from .trace import waterfall

    lines: list[str] = []
    loop, ws = build_habit_tracker_harness(demo_model(), on_step=lambda l: (print(l), lines.append(l)))
    print("== harnesslab demo: ticket HT-142 (weekly streak), scripted agent, full harness ==\n")
    try:
        result = loop.run(ticket(), task_id="HT-142")
        print("\n== trace waterfall ==")
        print(waterfall(loop.tracer.spans))
        print("\n== result ==")
        print(f"status: {result.status}\nreason: {result.reason}\niterations: {result.iterations}\n"
              f"tokens (estimated): {result.input_tokens + result.output_tokens:,}\n"
              f"files changed: {', '.join(ws.changed_files())}")
        if result.verdict:
            print("\n" + result.verdict.summary)
        return 0 if result.status == "succeeded" else 1
    finally:
        ws.destroy()
