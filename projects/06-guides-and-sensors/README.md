# Guides and Sensors

Project 6 of 11 · Goes with [Feedback, Verification and the Steering Loop](../../course/11-feedback-verification-and-steering.md) · about 60 minutes

## What you build

- `lint_source`: two habit-tracker rules using Python's `ast`, so comments and strings never match. HT001 flags `.date()` on a datetime; HT002 flags reading the clock without a time zone. Each finding renders as WHAT, WHY and FIX.
- `post_edit_hook`: runs lint and related tests after each edit. Silent on success, specific on failure.
- `on_read_hook`: delivers guidance when the agent opens a relevant file.

## Why it matters

The same check can say `HT001 violation` or tell the agent exactly what to change. The second gets the problem fixed on the next step. This is the sensor half of the ratchet; the on-read hook is the guide half.

## Steps

1. Implement the three functions; `python -m pytest -q`.
2. Open `harnesslab/harnesslab/presets.py` and compare its `date_lint` (regex) with yours (AST). Which false positives does the AST avoid?

## Done when

All five tests pass.

## Stretch goals

- Add HT003: week arithmetic with `weekday()` outside `timeutils.py`.
- Register your lint as a Claude Code PostToolUse hook using the [settings template](../../reference/templates/claude-settings.json).
