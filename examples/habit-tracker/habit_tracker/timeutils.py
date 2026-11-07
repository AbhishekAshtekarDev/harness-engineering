"""Date and time-zone helpers.

Project rule: every calculation that depends on a calendar day or a calendar
week goes through this module. Weeks run Monday to Sunday in the user's local
time zone (see docs/product-spec.md).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

WEEK_STARTS_ON = 0  # Monday, using datetime.weekday() numbering


def local_date(moment: datetime, tz: str) -> date:
    """Return the calendar date of `moment` in the time zone `tz`.

    Completions are stored as timezone-aware UTC datetimes. A naive datetime
    is a bug, so it raises instead of guessing.
    """
    if moment.tzinfo is None:
        raise ValueError("naive datetime: store completions as aware UTC datetimes")
    return moment.astimezone(ZoneInfo(tz)).date()


def week_start(day: date) -> date:
    """Return the Monday that starts the week containing `day`."""
    return day - timedelta(days=(day.weekday() - WEEK_STARTS_ON) % 7)
