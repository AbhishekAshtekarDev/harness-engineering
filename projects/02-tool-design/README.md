# Project 02: Tool Design

**Lesson:** [06. Tools, MCP and Agent Skills](../../course/06-tools-mcp-and-skills.md) · **Time:** 60 minutes

## What you build

A support agent for a small shop shipped with two bad tools (`bad_tools.py`): `get_orders` dumps every order of every customer as raw JSON with UUIDs, and `refund` wants an internal UUID and answers `Error 400`. You replace them with `search_orders` and `refund_order` in `good_tools.py`.

## Why it matters

The model decides how to use a tool from its description, and decides what to do next from its output. Tool design changes accuracy, cost and safety more than most prompt edits. Anthropic reports that refining tool descriptions alone moved a model to state of the art on SWE-bench Verified.

## Steps

1. Run `python -c "import sys; sys.path.insert(0,'exercise'); from bad_tools import get_orders; print(len(get_orders())//4, 'tokens')"` to see the cost of the bad tool.
2. Implement `search_orders`: validate inputs with errors that show an example; filter by customer and date; sort newest first; cap at `limit` and say how to see more; return readable rows with order numbers, dates and product names.
3. Implement `refund_order`: find orders by the customer-facing number; refuse unknown numbers (pointing to `search_orders`), amounts above the total (stating the maximum) and already refunded orders.
4. Read the two `*_SPEC` dicts. Each property has a description; `response_format` uses an enum.
5. `python -m pytest -q` until all eight tests pass.

## Done when

- Output is at least 20 times smaller than the bad tool's and contains no UUIDs.
- Every error tells the agent what to do next.

## Stretch goals

- Plug both tools into `harnesslab` and run a scripted conversation through `AgentLoop`.
- Add a `response_format="detailed"` test that checks token count stays under a budget.
