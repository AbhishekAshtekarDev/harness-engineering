# Capstone: Run, Ablate and Improve a Full Harness

Project 10 of 11 · Goes with [Build a Complete Harness](../../course/14-build-a-complete-harness.md) · about 2 to 4 hours · optional: an API key

## What you do

You work with the complete habit-tracker harness in [`harnesslab/presets.py`](../../harnesslab/harnesslab/presets.py): workspace, path guard, deny-first policy, hooks (on-read guidance and a lint sensor), verification with acceptance and held-out tests, budgets and tracing.

## Steps

1. **Run it offline.** `cd harnesslab && python -m harnesslab demo`. For every line where the harness intervenes, name the part of the eight-part model responsible.
2. **Ablate it.** `python projects/10-capstone-full-harness/ablation.py` from the repo root. It removes one component at a time and reports what the agent claimed, what the harness concluded and what an independent audit found.
3. **Run a real model.** `python -m harnesslab run --provider anthropic` (or `openai`) at least three times. Save the traces. Run the ablation with `--provider` too.
4. **Diagnose.** Pick the most common failure across your real runs and find its address with the [failure table](../../reference/failure-diagnosis.md).
5. **Improve one thing.** Make the smallest change at that component. Prove it with before-and-after runs.
6. **Write the spec.** Fill in the [harness spec template](../../reference/templates/harness-spec.md) for the harness as it now stands, including what it leaves out and why.

## Done when

- You have a table of at least three real runs before and after your change.
- Your spec fits on one page.

## What to notice

The scripted agent follows a fixed plan, so some ablation rows look identical. Real models do not. Small numbers of runs rarely prove much, so report the sample size with every result.
