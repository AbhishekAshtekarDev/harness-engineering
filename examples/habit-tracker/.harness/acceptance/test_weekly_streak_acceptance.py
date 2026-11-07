"""Acceptance tests for HT-142, written from docs/product-spec.md before work began."""
from datetime import date, datetime, timedelta, timezone

from habit_tracker.habits import Habit
from habit_tracker.streaks import weekly_streak

TODAY = date(2026, 3, 25)  # a Wednesday; the current week started Monday 2026-03-23


def completions_in_week(monday: date, count: int) -> list[datetime]:
    return [datetime(monday.year, monday.month, monday.day, 12, tzinfo=timezone.utc) + timedelta(days=i)
            for i in range(count)]


def habit(target: int, weeks: dict[date, int], tz: str = "UTC") -> Habit:
    h = Habit("gym", timezone=tz, weekly_target=target)
    for monday, count in weeks.items():
        h.completions.extend(completions_in_week(monday, count))
    return h


def test_four_finished_weeks_and_current_week_in_progress():
    h = habit(3, {date(2026, 2, 23): 3, date(2026, 3, 2): 3, date(2026, 3, 9): 4,
                  date(2026, 3, 16): 3, date(2026, 3, 23): 1})
    assert weekly_streak(h, TODAY) == 4


def test_missed_most_recent_finished_week_resets_to_zero():
    h = habit(3, {date(2026, 2, 23): 3, date(2026, 3, 2): 3, date(2026, 3, 9): 3, date(2026, 3, 16): 2})
    assert weekly_streak(h, TODAY) == 0


def test_current_week_counts_once_target_is_met():
    h = habit(3, {date(2026, 3, 9): 3, date(2026, 3, 16): 3, date(2026, 3, 23): 3})
    assert weekly_streak(h, TODAY) == 3
