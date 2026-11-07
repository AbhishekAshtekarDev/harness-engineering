"""Project 11: guardrails for a customer-support agent that can issue refunds.

Harness engineering is not only for coding agents. This agent reads order
data (including free-text notes anyone can write), talks to customers and
moves money. Four layers, each catching what the others miss:

  input guardrail    screens the customer's message before the agent runs
  tool-output scan   withholds instructions hidden in untrusted data (order notes)
  refund guard       a pre-tool hook enforcing business rules on every refund call
  output guardrail   checks the final reply before the customer sees it

None of these makes prompt injection impossible. The refund guard is the one
that matters most, because it holds even when the model has been fooled.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

INJECTION = re.compile(
    r"ignore (all |any |the )?(previous|prior|above) (instructions|rules)|disregard (your|the) (rules|instructions)|"
    r"you are now|system prompt|(note|message) to (the )?(ai|assistant|agent)|\bai (assistant|agent)s?:",
    re.I)
AUTO_REFUND_LIMIT = 100.0


@dataclass
class Session:
    customer_email: str
    confirmed_orders: set[str] = field(default_factory=set)
    refunds: list[tuple[str, float]] = field(default_factory=list)
    escalations: list[str] = field(default_factory=list)


def input_guardrail(message: str) -> str | None:
    """Return a reason to stop before the agent runs, or None.

    Reject messages that look like attempts to instruct the AI, and messages
    over 4,000 characters (an attempt to flood the context).
    """
    # TODO
    raise NotImplementedError("Your code here: see the TODO above")


def scan_untrusted(text: str) -> str:
    """Use on free text from untrusted sources before it enters the context.

    If the text matches INJECTION, return "[note withheld by harness: it contained
    instructions]"; otherwise return the text unchanged.
    """
    # TODO
    raise NotImplementedError("Your code here: see the TODO above")


def refund_guard(order: dict | None, amount: float, session: Session) -> str | None:
    """Business rules for every refund call. Return a refusal message, or None to allow.

    In this order:
      unknown order                        -> refuse, tell the agent to use search_orders
      order belongs to another customer    -> refuse
      order not confirmed in this session  -> refuse, tell the agent to call confirm_order first
      amount <= 0 or above the order total -> refuse, state the maximum
      amount above AUTO_REFUND_LIMIT       -> refuse, tell the agent to call escalate_to_human
    """
    # TODO
    raise NotImplementedError("Your code here: see the TODO above")


def output_guardrail(reply: str, session: Session) -> list[str]:
    """Problems with the final reply (empty list = OK to send).

    - mentions any email address other than the session customer's
    - promises or guarantees anything ("guarantee", "promise")
    - claims a refund ("refunded") when no refund happened this session
    """
    # TODO
    raise NotImplementedError("Your code here: see the TODO above")
