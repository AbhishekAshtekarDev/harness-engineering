# Project 04: Long-Running State

**Lesson:** [08. State, memory and long-running work](../../course/08-state-memory-and-long-running-work.md) · **Time:** 75 minutes

## What you build

The pattern from Anthropic's long-running harness, in `exercise/sessions.py`:

- `initialize`: run once; write a JSON feature list (all `passes: false`), a progress log and a first checkpoint
- `start_session`: the routine every session runs first: next feature, recent progress, last checkpoint, a smoke check, and re-verification of anything the records claim is passing
- `complete_feature`: flip `passes` only after a passing check; log either way; checkpoint on success
- `guard_feature_list`: reject rewrites that change anything except `passes`

Checkpoints are folder snapshots so the project runs anywhere; in a real repository use git commits.

## Steps

1. Read `test_sessions.py`, especially the crash test and the "records that lie" test.
2. Implement the four functions.
3. `python -m pytest -q` until all six pass.

## Done when

- A crash mid-feature is detected at the next session start and rolled back.
- A hand-edited feature list that claims an unbuilt feature works is caught.

## Stretch goals

- Replace folder snapshots with `git commit` and `git reset --hard <sha>`.
- Add a `handoff()` that renders the [handoff template](../../reference/templates/handoff.md) from the records.
