# Loop Controls That Stop for a Reason

Project 5 of 11 · Goes with [Loop Engineering](../../course/12-loop-engineering.md) · about 60 minutes

## What you build

The exits a harness owns, in `exercise/controls.py`:

- `stop_reason`: iteration, token, time and cost budgets; no-progress detection; repeated actions; A-B-A-B oscillation
- `classify_failure`: transient (retry) or substantive (adjust)
- `backoff_delays`: exponential backoff with a cap
- `CircuitBreaker`: closed, open, half-open
- `should_trigger`: event loops ignore events their own agent caused

## Steps

1. Implement each function; run `python -m pytest -q` after each one.
2. Compare with `harnesslab/harnesslab/loop.py`, which uses budgets, repeat refusal and a no-progress window.

## Done when

All seven tests pass, and for each control you can name the runaway-loop cause it prevents.

## Stretch goals

- Add jitter to `backoff_delays` and a test that two clients do not retry in lockstep.
- Add `stop_reason` to Project 1's loop.
