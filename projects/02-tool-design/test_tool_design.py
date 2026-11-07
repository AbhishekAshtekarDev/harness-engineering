"""python -m pytest -q   (or SOLUTION=1 python -m pytest -q)"""
import re

import pytest

from bad_tools import get_orders
from good_tools import REFUND_ORDER_SPEC, SEARCH_ORDERS_SPEC, ToolError, refund_order, search_orders

UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-")


def tokens(text):
    return len(text) // 4


def test_search_is_small_readable_and_sorted():
    out = search_orders("maya@example.com", since_days=400, limit=5)
    rows = [l for l in out.splitlines() if l.startswith("A")]
    assert 1 <= len(rows) <= 5
    dates = [r.split(" | ")[1] for r in rows]
    assert dates == sorted(dates, reverse=True), "newest first"
    assert not UUID.search(out), "no internal UUIDs in what the agent sees"
    assert any(p in out for p in ["shoes", "socks", "jacket", "bottle", "Headlamp", "mat", "bag"])
    assert tokens(out) < tokens(get_orders()) / 20, "at least 20x smaller than the bad tool"


def test_search_says_how_to_get_more():
    out = search_orders("maya@example.com", since_days=400, limit=2)
    assert "Showing 2 of" in out


def test_search_empty_result_suggests_next_step():
    out = search_orders("sam@example.com", since_days=0)
    assert "since_days" in out


def test_search_detailed_format_adds_shipping():
    assert "ship to" in search_orders("li.wei@example.com", since_days=400, response_format="detailed")
    with pytest.raises(ToolError):
        search_orders("li.wei@example.com", response_format="verbose")


def test_bad_email_error_shows_an_example():
    with pytest.raises(ToolError, match="example.com"):
        search_orders("maya")


def test_refund_errors_are_actionable():
    with pytest.raises(ToolError, match="search_orders"):
        refund_order("12345", 10, "damaged")
    with pytest.raises(ToolError, match="maximum refund"):
        refund_order("A1001", 99999, "damaged")
    with pytest.raises(ToolError):
        refund_order("A1001", 0, "damaged")


def test_refund_accepts_customer_facing_numbers():
    from shop_data import ORDERS
    order = next(o for o in ORDERS if o["status"] != "refunded")
    assert order["number"] in refund_order(order["number"].lower(), 1.0, "late delivery")
    done = next(o for o in ORDERS if o["status"] == "refunded")
    with pytest.raises(ToolError, match="already refunded"):
        refund_order(done["number"], 1.0, "again")


def test_specs_are_precise():
    props = SEARCH_ORDERS_SPEC["input_schema"]["properties"]
    assert props["response_format"]["enum"] == ["concise", "detailed"]
    assert "customer_email" in SEARCH_ORDERS_SPEC["input_schema"]["required"]
    assert all("description" in p for p in props.values())
    assert "search_orders" in REFUND_ORDER_SPEC["description"]
