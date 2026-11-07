# habit-tracker (course example)

The running example for this course: a tiny Python library with habits,
completions and streaks. The harness projects ask an agent to implement ticket
[HT-142](TICKET-HT-142.md), a weekly streak.

The repository contains a few traps on purpose, so you can watch a harness catch them:

- `docs/old-design-note.md` contradicts the product spec (Sunday vs Monday weeks).
- `habit_tracker/reports.py` uses a legacy Sunday week and UTC dates.
- `config/settings.toml` looks like the obvious place to "fix" the week start, but agents may not edit it.

Run the tests with `python -m pytest -q` (Python 3.10+; on Windows also `pip install tzdata`).
