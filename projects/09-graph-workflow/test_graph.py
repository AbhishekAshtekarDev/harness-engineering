"""python -m pytest -q   (or SOLUTION=1 python -m pytest -q)"""
import importlib.util

import pytest

from minigraph import END, START, Graph, GraphError, append
from workflow import build_workflow


def outcomes(*values):
    it = iter(values)
    return lambda s: next(it)


def test_reducers_append_or_replace():
    g = Graph(reducers={"log": append})
    g.add_node("a", lambda s: {"log": ["a"], "x": 1})
    g.add_node("b", lambda s: {"log": ["b"], "x": 2})
    g.add_edge(START, "a")
    g.add_edge("a", "b")
    g.add_edge("b", END)
    out = g.run({"log": []})
    assert out["status"] == "done" and out["state"]["log"] == ["a", "b"] and out["state"]["x"] == 2
    assert out["state"]["path"] == ["a", "b"]


def test_happy_path_pauses_for_a_human_then_opens_pr():
    g = build_workflow(build=outcomes(True), review_ok=outcomes(True))
    first = g.run({"ticket": "HT-142", "log": []}, "HT-142")
    assert first["status"] == "interrupted" and first["payload"]["branch"] == "agent/HT-142"
    final = g.resume("HT-142", "approve")
    assert final["status"] == "done" and final["state"]["pr"] == "PR for agent/HT-142"
    assert final["state"]["path"] == ["plan", "branch", "build", "test", "review", "approve", "open_pr"]
    assert "HT-142" not in g.checkpoints


def test_failed_tests_cycle_back_and_then_succeed():
    g = build_workflow(build=outcomes(False, True), review_ok=outcomes(True))
    g.run({"ticket": "T", "log": []}, "T")
    final = g.resume("T", "approve")
    assert final["state"]["log"].count("tests failed") == 1 and final["state"]["attempts"] == 2


def test_attempt_limit_routes_to_escalation():
    g = build_workflow(build=outcomes(False, False, False), review_ok=outcomes(True))
    out = g.run({"ticket": "T", "log": []})
    assert out["status"] == "done" and out["state"]["escalated"] and out["state"]["attempts"] == 3


def test_reviewer_rejection_also_counts_as_an_attempt():
    g = build_workflow(build=outcomes(True, True), review_ok=outcomes(False, True))
    g.run({"ticket": "T", "log": []}, "T")
    final = g.resume("T", "reject")
    assert final["state"]["approved"] is False and "pr" not in final["state"]


def test_max_steps_stops_a_runaway_cycle():
    g = Graph(max_steps=5)
    g.add_node("a", lambda s: {})
    g.add_edge(START, "a")
    g.add_edge("a", "a")
    with pytest.raises(GraphError):
        g.run({})


@pytest.mark.skipif(importlib.util.find_spec("langgraph") is None, reason="langgraph not installed")
def test_langgraph_version_matches():
    from langgraph.types import Command
    from langgraph_version import build_app
    app = build_app(outcomes(False, True))
    cfg = {"configurable": {"thread_id": "x"}}
    first = app.invoke({"ticket": "x", "log": []}, cfg)
    assert "__interrupt__" in first
    final = app.invoke(Command(resume="approve"), cfg)
    assert final["log"][-1] == "pull request opened" and final["attempts"] == 2
