# Project 07: Traces and Diagnosis

**Lessons:** [10. Observability](../../course/10-observability.md), [15. Diagnosing agent failures](../../course/15-diagnosing-agent-failures.md) · **Time:** 75 minutes

## What you build

`traces/` holds four real runs of the habit-tracker harness, recorded by `make_traces.py`. Each harness was missing something, so each trace contains one failure pattern. In `exercise/trace_analysis.py` you write:

- `summary`: status, stop reason, iterations, tool calls and errors, blocked calls, verification results, tokens
- `edits_per_file`: the stuck-loop signal
- `first_problem`: where diagnosis starts
- `files_read`: what the agent saw

Then you diagnose each run.

## Steps

1. Look at a trace: `python -m harnesslab trace ../projects/07-traces-and-diagnosis/traces/run-b.jsonl` from the `harnesslab/` folder, or open the JSONL directly.
2. Implement the four functions; `python -m pytest -q`.
3. Fill in `DIAGNOSIS.md` for runs A to D using the [five questions](../../reference/failure-diagnosis.md).
4. Compare with `solution/ANSWERS.md`.

## Done when

All five tests pass and you have named, for each run, the pattern, the component and the cheapest fix.

## Stretch goals

- Add a `cost_by_iteration` function and plot it.
- Export a trace to an OpenTelemetry backend (Jaeger, Phoenix) and compare the waterfall.
