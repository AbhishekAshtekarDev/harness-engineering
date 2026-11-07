"""The Habit model and its business rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


class HabitError(ValueError):
    """Raised when a habit would break a business rule."""


@dataclass
class Habit:
    name: str
    timezone: str = "UTC"
    weekly_target: int = 1
    completions: list[datetime] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Business rule: a weekly target is between 1 and 7 completions.
        if not 1 <= self.weekly_target <= 7:
            raise HabitError("weekly_target must be between 1 and 7")

    def complete(self, at: datetime) -> None:
        if at.tzinfo is None:
            raise HabitError("completion time must be timezone-aware")
        self.completions.append(at)
