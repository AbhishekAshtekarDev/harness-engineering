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
    # BEGIN SOLUTION
    if len(message) > 4000:
        return "message too long: route to a person"
    if INJECTION.search(message):
        return "message contains instructions aimed at the AI: route to a person"
    return None
    # END SOLUTION


def scan_untrusted(text: str) -> str:
    """Use on free text from untrusted sources before it enters the context.

    If the text matches INJECTION, return "[note withheld by harness: it contained
    instructions]"; otherwise return the text unchanged.
    """
    # TODO
    # BEGIN SOLUTION
    return "[note withheld by harness: it contained instructions]" if INJECTION.search(text) else text
    # END SOLUTION


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
    # BEGIN SOLUTION
    if order is None:
        return "Unknown order. Use search_orders to find the customer's order numbers."
    if order["customer"] != session.customer_email:
        return "That order belongs to a different customer. Refunds go only to the customer you are serving."
    if order["number"] not in session.confirmed_orders:
        return f"Confirm the order with the customer first: call confirm_order with {order['number']}."
    if amount <= 0 or amount > order["total"]:
        return f"Amount must be between 0 and the order total (${order['total']:.2f})."
    if amount > AUTO_REFUND_LIMIT:
        return (f"Refunds above ${AUTO_REFUND_LIMIT:.0f} need a person. Call escalate_to_human with the order "
                "number, amount and reason.")
    return None
    # END SOLUTION


def output_guardrail(reply: str, session: Session) -> list[str]:
    """Problems with the final reply (empty list = OK to send).

    - mentions any email address other than the session customer's
    - promises or guarantees anything ("guarantee", "promise")
    - claims a refund ("refunded") when no refund happened this session
    """
    # TODO
    # BEGIN SOLUTION
    problems = []
    for email in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", reply):
        if email.lower() != session.customer_email:
            problems.append(f"reply exposes another customer's email ({email})")
    if re.search(r"\b(guarantee|promise)", reply, re.I):
        problems.append("reply makes a promise the policy does not allow")
    if re.search(r"\brefunded\b", reply, re.I) and not session.refunds:
        problems.append("reply claims a refund that did not happen")
    return problems
    # END SOLUTION
