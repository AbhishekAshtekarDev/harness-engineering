"""The plan -> build -> test -> review -> approve workflow from the course, on minigraph.

Deterministic nodes (create branch, run tests, open PR) are plain code.
Agentic nodes (plan, build, review) are where a model would be called; here
they are stubs you can replace with harnesslab loops. The cycle build -> test
is bounded by an attempt counter in state, routed to escalation at the limit.
"""
from __future__ import annotations

from typing import Callable

from minigraph import END, START, Graph, Interrupt, append

MAX_ATTEMPTS = 3


def build_workflow(build: Callable[[dict], bool], review_ok: Callable[[dict], bool]) -> Graph:
    """build(state) -> True if the tests pass after this attempt. review_ok(state) -> reviewer verdict."""
    g = Graph(reducers={"log": append}, max_steps=40)

    g.add_node("plan", lambda s: {"plan": ["calc", "badge", "tests"], "attempts": 0, "log": ["planned"]})
    g.add_node("branch", lambda s: {"branch": f"agent/{s['ticket']}", "log": ["branch created"]})

    def build_node(s):
        return {"attempts": s["attempts"] + 1, "tests_pass": build(s), "log": [f"build #{s['attempts'] + 1}"]}

    def test_node(s):  # deterministic: no route around it
        return {"log": ["tests " + ("passed" if s["tests_pass"] else "failed")]}

    def review_node(s):
        ok = review_ok(s)
        return {"review_ok": ok, "log": ["review " + ("approved" if ok else "requested changes")],
                "tests_pass": s["tests_pass"] and ok}

    def approval_node(s):
        if "human" not in s:
            raise Interrupt({"ask": "Merge this change?", "branch": s["branch"], "log": s["log"]})
        return {"approved": s["human"] == "approve", "log": [f"human said {s['human']}"]}

    g.add_node("build", build_node)
    g.add_node("test", test_node)
    g.add_node("review", review_node)
    g.add_node("approve", approval_node)
    g.add_node("open_pr", lambda s: {"pr": f"PR for {s['branch']}", "log": ["pull request opened"]})
    g.add_node("escalate", lambda s: {"escalated": True, "log": [f"escalated after {s['attempts']} attempts"]})

    g.add_edge(START, "plan")
    g.add_edge("plan", "branch")
    g.add_edge("branch", "build")
    g.add_edge("build", "test")
    # TODO: route after "test": pass -> "review"; fail and attempts < MAX_ATTEMPTS -> "build"; else "escalate"
    # TODO: route after "review": approved -> "approve"; changes requested -> same rule as a test failure
    # TODO: route after "approve": approved -> "open_pr", rejected -> END
    # BEGIN SOLUTION
    def retry_or_escalate(s):
        return "build" if s["attempts"] < MAX_ATTEMPTS else "escalate"

    g.add_router("test", lambda s: "review" if s["tests_pass"] else retry_or_escalate(s))
    g.add_router("review", lambda s: "approve" if s["review_ok"] else retry_or_escalate(s))
    g.add_router("approve", lambda s: "open_pr" if s["approved"] else END)
    # END SOLUTION
    g.add_edge("open_pr", END)
    g.add_edge("escalate", END)
    return g
