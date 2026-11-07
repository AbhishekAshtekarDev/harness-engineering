# Project 08: Evals

**Lesson:** [09. Guardrails, tests and evals](../../course/09-guardrails-tests-and-evals.md) · **Time:** 75 minutes

## What you build

In `exercise/evalkit.py`: `pass_at_k`, `pass_pow_k`, a Wilson confidence interval, `compare` (which says "inconclusive" when the evidence is thin), `pairwise_judge` (asks in both orders to cancel position bias) and `cohen_kappa` (judge vs human agreement).

`run_suite.py` then evaluates two scripted agents on the habit-tracker ticket, grading outcomes with hidden tests:

```text
agent              passed          95% CI   pass@3   pass^3
careful (0.9)       9/10        0.60-0.98     1.00     0.70
hasty (0.5)         6/10        0.31-0.83     0.97     0.17
```

## Steps

1. Implement the six functions; `python -m pytest -q`.
2. `cd exercise && python run_suite.py --trials 10`, then `--trials 40`. Watch the intervals narrow.
3. Write three eval tasks for an agent you use with the [eval task template](../../reference/templates/eval-task.md).

## Done when

All five tests pass, and you can explain why both agents look alike on pass@3 and very different on pass^3.

## Stretch goals

- Add a model-based grader with `harnesslab.evals.judge_grader` and calibrate it against ten labels you write by hand.
- Run the suite with a real model in place of the scripted agents.
