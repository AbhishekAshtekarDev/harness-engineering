# AGENTS.md: habit-tracker

A Python library that tracks habits, completions and streaks.

## Layout
- `habit_tracker/` source. `timeutils.py` owns all day and week logic.
- `tests/` pytest suite. `docs/product-spec.md` defines streak behavior.
- `config/` shared settings: read-only for agents.

## Commands
- Run all tests: `python -m pytest -q`
- Run one file: `python -m pytest -q tests/test_daily_streak.py`

## Rules
- Use `timeutils.local_date` and `timeutils.week_start` for every day or week
  calculation. Never call `.date()` on a completion directly.
- Weeks run Monday to Sunday in the user's local time zone.
- Do not edit or delete existing tests. Add new tests next to them.
- Do not add dependencies.

## Done means
All tests pass, new logic has tests, and your final message lists the files you
changed, the tests you ran and any assumption you made.
