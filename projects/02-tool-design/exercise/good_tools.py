"""Project 02: redesign the tools so an agent can use them well.

Rules of thumb from this project (and Anthropic's "Writing effective tools
for agents"):
  - one tool per job the agent does, not one per API endpoint
  - search and filter instead of "list everything"
  - human-meaningful identifiers (order A1042, product names) instead of UUIDs
  - sort and cap results; say how to get more
  - errors say what went wrong AND what to do next
  - a concise format by default, a detailed one on request
"""
from __future__ import annotations

from datetime import date, timedelta

from shop_data import ORDERS, TODAY


class ToolError(Exception):
    pass


SEARCH_ORDERS_SPEC = {
    "name": "search_orders",
    "description": (
        "Find a customer's orders, newest first. Use this before any refund to identify the exact order "
        "the customer means. Returns one line per order: order number, date, products, total, status."),
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_email": {"type": "string", "description": "The customer's email, e.g. maya@example.com"},
            "since_days": {"type": "integer", "description": "Only orders from the last N days (default 90)."},
            "limit": {"type": "integer", "description": "Maximum orders to return (default 5)."},
            "response_format": {"type": "string", "enum": ["concise", "detailed"],
                                "description": "concise (default) or detailed (adds items and shipping)."},
        },
        "required": ["customer_email"],
        "additionalProperties": False,
    },
}

REFUND_ORDER_SPEC = {
    "name": "refund_order",
    "description": ("Refund part or all of one order. Use the order number from search_orders (like A1042). "
                    "Confirm the order with the customer first."),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_number": {"type": "string", "description": "Order number like A1042."},
            "amount": {"type": "number", "description": "Amount in USD, at most the order total."},
            "reason": {"type": "string", "description": "Short reason, shown to the customer."},
        },
        "required": ["order_number", "amount", "reason"],
        "additionalProperties": False,
    },
}


def _line(o: dict, detailed: bool) -> str:
    products = ", ".join(f"{i['name']} x{i['qty']}" for i in o["items"])
    line = f"{o['number']} | {o['created']} | {products} | ${o['total']:.2f} | {o['status']}"
    if detailed:
        line += f" | ship to: {o['shipping_address']}"
    return line


def search_orders(customer_email: str, since_days: int = 90, limit: int = 5,
                  response_format: str = "concise") -> str:
    # TODO: validate the email (must contain "@") with an error that shows an example.
    # TODO: validate response_format ("concise" or "detailed") and limit (1..50).
    # TODO: keep this customer's orders from the last since_days days, newest first.
    # TODO: if none, say so and suggest a larger since_days.
    # TODO: return at most `limit` lines; if more exist, say "Showing X of Y" and how to see more.
    raise NotImplementedError("Your code here: see the TODO above")


def refund_order(order_number: str, amount: float, reason: str) -> str:
    # TODO: find the order by its customer-facing number (case-insensitive).
    #       Unknown number -> error that explains the format and points to search_orders.
    # TODO: reject amount <= 0, or above the order total (say the maximum), or an already refunded order.
    # TODO: on success return a one-line confirmation with order number and amount.
    raise NotImplementedError("Your code here: see the TODO above")
