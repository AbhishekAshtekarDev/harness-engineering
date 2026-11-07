# Project 01: Build an Agent Loop from Scratch

**Lesson:** [02. How an AI agent works](../../course/02-how-an-agent-works.md) · **Time:** 45 minutes · **Needs:** Python 3.10+, pytest

## What you build

The whole agent loop in about 30 lines: send the model the task and tool specs, record its turn, run the tools it asks for, send the results back, stop when it stops asking. Then you point the same loop at a real model.

## Why it matters

Every harness wraps this loop. Once you have written it, every later component has an obvious place to plug in: permissions before a tool runs, verification when the model stops, budgets around the loop, a trace around each step.

## Steps

1. Read `test_agent_loop.py`. The tests define the transcript format exactly.
2. In `exercise/mini_agent.py`, write `execute_tool`: unknown tool names return an error listing real tools; exceptions become `Error: <Type>: <message>`; nothing raises.
3. Write `run_agent`: the loop with a `max_turns` limit.
4. Run `python -m pytest -q` until all five tests pass.
5. Optional, with an API key: `pip install anthropic` (or `openai`), set the key, then `cd exercise && python run_real.py anthropic`. Read the transcript it prints.

## Done when

- All five tests pass.
- You can explain why the loop, not the model, owns `max_turns`.

## What to notice in the real run

- How many turns did the model take? Did it run the file before claiming success?
- `run_python` executes code on your machine. Which project makes that safe?

## Stretch goals

- Run tool calls from one turn in parallel when they are all read-only.
- Add a `verify` callback: when the model stops calling tools, run it and send failures back instead of returning.
