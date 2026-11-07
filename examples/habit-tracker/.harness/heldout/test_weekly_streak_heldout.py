"""Held-out edge cases. The agent never sees these."""
from datetime import date, datetime, timezone

from habit_tracker.habits import Habit
from habit_tracker.streaks import weekly_streak


def test_local_week_not_utc_week():
    # Sunday 20:00 UTC is already Monday 05:00 in Tokyo, so it belongs to the new local week.
    h = Habit("read", timezone="Asia/Tokyo", weekly_target=1, completions=[
        datetime(2026, 3, 16, 3, tzinfo=timezone.utc),   # Mon 16 Mar, Tokyo
        datetime(2026, 3, 22, 20, tzinfo=timezone.utc),  # Mon 23 Mar 05:00, Tokyo
    ])
    assert weekly_streak(h, date(2026, 3, 23)) == 2


def test_no_completions_means_no_streak():
    assert weekly_streak(Habit("read", weekly_target=2), date(2026, 3, 25)) == 0
