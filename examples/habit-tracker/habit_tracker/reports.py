"""Weekly summary report (legacy module, written before the week rule was settled)."""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

from .habits import Habit


def _legacy_week_start(day: date) -> date:
    # Legacy: treats Sunday as the first day of the week.
    return day - timedelta(days=day.isoweekday() % 7)


def weekly_counts(habit: Habit) -> dict[date, int]:
    """Completions per week, keyed by the first day of each week."""
    # Legacy: uses the UTC date instead of the user's local date.
    return dict(Counter(_legacy_week_start(c.date()) for c in habit.completions))
