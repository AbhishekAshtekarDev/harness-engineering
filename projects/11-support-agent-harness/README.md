# A Harness for a Support Agent That Moves Money

Project 11 of 11 · Goes with [Harnesses Beyond Coding](../../course/17-harnesses-beyond-coding.md) · about 75 minutes

## What you build

In `exercise/guardrails.py`, four layers for a refund-capable support agent:

- `input_guardrail`: route messages aimed at the AI, or floods of text, to a person
- `scan_untrusted`: withhold instructions hidden in order notes before they reach the context
- `refund_guard`: business rules on every refund call (known order, same customer, confirmed with the customer, within the total, under the auto-approval limit)
- `output_guardrail`: no other customer's email, no promises, no claimed refund that did not happen

`support_agent.py` wires them into `harnesslab` and plays four conversations, including one where the scripted model is fooled by a planted note and tries to refund someone else's $900 order.

## Steps

1. Implement the four functions; `python -m pytest -q`.
2. `cd exercise && python support_agent.py` and read each scenario's outcome.

## Done when

All six tests pass. In the injection scenario no money moves, even though the model asked for it.

## Stretch goals

- Run the scenarios with a real model and see which layer stops it.
- Add an approval queue that a person clears, and resume the escalated refund after approval.
