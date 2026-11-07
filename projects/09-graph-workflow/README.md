# Project 09: Graph Workflow

**Lesson:** [13. Graphs and multi-agent systems](../../course/13-graphs-and-multi-agent-systems.md) · **Time:** 90 minutes · **Optional:** `pip install langgraph`

## What you build

- `exercise/minigraph.py`: a small graph engine: nodes, fixed edges, routers, reducers, a step limit, and interrupt-and-resume with checkpoints.
- `exercise/workflow.py`: plan, branch, build, test, review, approve, open PR, with an attempt counter routing to escalation after three failed cycles, and a human approval interrupt.
- `solution/langgraph_version.py`: the same workflow on LangGraph (tested with 1.2), to compare.

## Steps

1. Implement `_merge`, `_next` and `_run_from`; then the three routers in `workflow.py`.
2. `python -m pytest -q`. The LangGraph test runs if `langgraph` is installed.
3. `cd solution && python langgraph_version.py` to watch a run pause for approval and resume.

## Done when

All tests pass, and you can point to where your engine and LangGraph each store the state needed to resume.

## Stretch goals

- Add fan-out and fan-in: build two parts in parallel and join.
- Replace the stub `build` with a `harnesslab.AgentLoop` on the habit tracker.
