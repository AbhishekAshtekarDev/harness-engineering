from datetime import datetime, timezone

import pytest

from habit_tracker.habits import Habit, HabitError


def test_weekly_target_must_be_between_one_and_seven():
    with pytest.raises(HabitError):
        Habit("run", weekly_target=0)
    with pytest.raises(HabitError):
        Habit("run", weekly_target=8)


def test_completion_must_be_timezone_aware():
    habit = Habit("run")
    with pytest.raises(HabitError):
        habit.complete(datetime(2026, 3, 2, 9, 0))
    habit.complete(datetime(2026, 3, 2, 9, 0, tzinfo=timezone.utc))
    assert len(habit.completions) == 1
