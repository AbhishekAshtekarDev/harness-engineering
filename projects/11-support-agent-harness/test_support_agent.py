"""python -m pytest -q   (or SOLUTION=1 python -m pytest -q)"""
from guardrails import Session, input_guardrail, output_guardrail, refund_guard, scan_untrusted
from support_agent import ORDERS, SCENARIOS, run


def scenario(name):
    sc = SCENARIOS[name]
    session = Session(sc["email"])
    return run(sc["message"], session, sc["wants"], sc["script"]), session


def test_normal_refund_goes_through():
    out, session = scenario("normal refund")
    assert session.refunds == [("A1001", 89.0)] and out["status"] == "succeeded"


def test_planted_instructions_are_withheld_and_the_refund_is_blocked():
    out, session = scenario("injection in order data")
    assert session.refunds == [], "no money moves, even though the scripted model was fooled"
    joined = "\n".join(out["tool_results"])
    assert "withheld" in joined and "VIP" not in joined
    assert "different customer" in joined


def test_large_refund_needs_a_person():
    out, session = scenario("over the auto limit")
    assert session.refunds == [] and len(session.escalations) == 1
    assert out["status"] == "succeeded"


def test_direct_injection_never_reaches_the_agent():
    out, session = scenario("direct injection")
    assert out["status"] == "routed to a person" and session.refunds == []


def test_guard_rules_in_order():
    s = Session("maya@example.com")
    assert "search_orders" in refund_guard(None, 10, s)
    assert "different customer" in refund_guard(ORDERS["B2009"], 10, s)
    assert "confirm_order" in refund_guard(ORDERS["A1001"], 10, s)
    s.confirmed_orders.add("A1001")
    assert "89.00" in refund_guard(ORDERS["A1001"], 500, s)
    assert refund_guard(ORDERS["A1001"], 89, s) is None
    s.confirmed_orders.add("A1002")
    assert "escalate_to_human" in refund_guard(ORDERS["A1002"], 150, s)


def test_input_and_output_guardrails():
    assert input_guardrail("Where is my order?") is None
    assert input_guardrail("x" * 5000)
    assert scan_untrusted("Leave at the back door") == "Leave at the back door"
    s = Session("maya@example.com")
    assert output_guardrail("Your order A1001 is on its way.", s) == []
    assert len(output_guardrail("I guarantee lee@example.com was refunded.", s)) == 3
