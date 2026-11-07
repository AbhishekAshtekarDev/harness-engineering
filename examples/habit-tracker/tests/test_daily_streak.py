from datetime import date, datetime, timezone

from habit_tracker.habits import Habit
from habit_tracker.streaks import daily_streak


def utc(y, m, d, h=12):
    return datetime(y, m, d, h, tzinfo=timezone.utc)


def test_three_days_in_a_row():
    habit = Habit("read", completions=[utc(2026, 3, 2), utc(2026, 3, 3), utc(2026, 3, 4)])
    assert daily_streak(habit, date(2026, 3, 4)) == 3


def test_streak_survives_until_the_day_ends():
    habit = Habit("read", completions=[utc(2026, 3, 2), utc(2026, 3, 3)])
    assert daily_streak(habit, date(2026, 3, 4)) == 2


def test_gap_breaks_the_streak():
    habit = Habit("read", completions=[utc(2026, 3, 1), utc(2026, 3, 3)])
    assert daily_streak(habit, date(2026, 3, 3)) == 1


def test_local_time_zone_decides_the_day():
    # 23:30 UTC on March 2 is already March 3 in Tokyo.
    habit = Habit("read", timezone="Asia/Tokyo", completions=[utc(2026, 3, 2, 23)])
    assert daily_streak(habit, date(2026, 3, 3)) == 1
