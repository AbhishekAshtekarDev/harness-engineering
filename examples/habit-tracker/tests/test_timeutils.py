from datetime import date, datetime

import pytest

from habit_tracker.timeutils import local_date, week_start


def test_week_starts_on_monday():
    assert week_start(date(2026, 3, 8)) == date(2026, 3, 2)  # Sunday -> Monday before
    assert week_start(date(2026, 3, 2)) == date(2026, 3, 2)  # Monday -> itself


def test_naive_datetime_is_rejected():
    with pytest.raises(ValueError):
        local_date(datetime(2026, 3, 2, 9), "UTC")
