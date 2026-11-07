"""The tools a team shipped first. Each one is a real anti-pattern. Do not edit."""
from __future__ import annotations

import json

from shop_data import ORDERS

BAD_TOOL_SPECS = [
    {"name": "get_orders", "description": "Gets orders.",
     "input_schema": {"type": "object", "properties": {"user": {"type": "string"}}}},
    {"name": "refund", "description": "Refund.",
     "input_schema": {"type": "object", "properties": {"id": {"type": "string"}, "amt": {"type": "number"}}}},
]


def get_orders(user: str = "") -> str:
    # Anti-patterns: returns every order of every customer, as raw JSON, with internal
    # UUIDs, in database order. "user" is ignored and its meaning is unclear anyway.
    return json.dumps(ORDERS)


def refund(id: str, amt: float) -> str:
    # Anti-patterns: wants the internal UUID the agent should never need, and fails cryptically.
    if not any(o["id"] == id for o in ORDERS):
        return "Error 400"
    return "OK"
