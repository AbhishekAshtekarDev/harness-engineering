"""python -m pytest -q   (or SOLUTION=1 python -m pytest -q)"""
from sensors import lint_source, on_read_hook, post_edit_hook

BUGGY = '''from collections import Counter
from datetime import date, datetime, timedelta


def weekly_streak(habit, today):
    # .date() in a comment must not count
    counts = Counter(c.date() for c in habit.completions)
    now = datetime.now()
    later = datetime.utcnow()
    also = date.today()
    fine = datetime.now(tz)
    return counts, "use .date() carefully"
'''


def test_finds_each_problem_once_with_line_numbers():
    found = [(f.rule, f.line) for f in lint_source("habit_tracker/streaks.py", BUGGY)]
    assert found == [("HT001", 7), ("HT002", 8), ("HT002", 9), ("HT002", 10)]


def test_messages_tell_the_agent_how_to_fix_it():
    msg = lint_source("habit_tracker/streaks.py", BUGGY)[0].for_agent()
    assert msg.startswith("habit_tracker/streaks.py:7 [HT001]")
    assert "Why:" in msg and "Fix:" in msg and "local_date" in msg


def test_rule_scope():
    assert lint_source("habit_tracker/timeutils.py", BUGGY) == []
    assert lint_source("tests/test_x.py", BUGGY) == []


def test_hook_is_silent_on_success_and_specific_on_failure():
    clean = "def f(x):\n    return x\n"
    assert post_edit_hook("habit_tracker/streaks.py", clean, lambda p: (True, "3 passed")) is None
    out = post_edit_hook("habit_tracker/streaks.py", clean, lambda p: (False, "1 failed: test_week"))
    assert "test_week" in out
    out = post_edit_hook("habit_tracker/streaks.py", BUGGY, lambda p: (True, "3 passed"))
    assert out.count("[HT00") == 4


def test_guidance_arrives_when_the_file_is_opened():
    assert "week_start" in on_read_hook("habit_tracker/timeutils.py")
    assert on_read_hook("habit_tracker/habits.py") is None
