"""Streak calculations."""
from __future__ import annotations

from datetime import date, timedelta

from .habits import Habit
from .timeutils import local_date


def daily_streak(habit: Habit, today: date) -> int:
    """Count consecutive local days with at least one completion.

    The streak may end today or yesterday: a habit you have not done yet today
    still shows yesterday's streak until the day is over.
    """
    days = {local_date(c, habit.timezone) for c in habit.completions}
    cursor = today if today in days else today - timedelta(days=1)
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak
