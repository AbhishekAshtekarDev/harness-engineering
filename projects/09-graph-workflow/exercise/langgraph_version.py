"""The same workflow on LangGraph (pip install langgraph), to compare with minigraph.

Tested with langgraph 1.2. Framework APIs move; check the docs if this breaks.
"""
from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

MAX_ATTEMPTS = 3


class State(TypedDict, total=False):
    ticket: str
    attempts: int
    tests_pass: bool
    approved: bool
    log: Annotated[list[str], operator.add]   # reducer: append instead of replace


def build_app(build):
    def plan(s: State):
        return {"attempts": 0, "log": ["planned"]}

    def build_node(s: State):
        return {"attempts": s["attempts"] + 1, "tests_pass": build(s), "log": [f"build #{s['attempts'] + 1}"]}

    def approve(s: State):
        answer = interrupt({"ask": "Merge this change?", "ticket": s["ticket"]})  # pauses the run
        return {"approved": answer == "approve", "log": [f"human said {answer}"]}

    g = StateGraph(State)
    g.add_node("plan", plan)
    g.add_node("build", build_node)
    g.add_node("approve", approve)
    g.add_node("open_pr", lambda s: {"log": ["pull request opened"]})
    g.add_node("escalate", lambda s: {"log": ["escalated"]})
    g.add_edge(START, "plan")
    g.add_edge("plan", "build")
    g.add_conditional_edges("build", lambda s: "approve" if s["tests_pass"] else
                            ("build" if s["attempts"] < MAX_ATTEMPTS else "escalate"))
    g.add_conditional_edges("approve", lambda s: "open_pr" if s["approved"] else END)
    g.add_edge("open_pr", END)
    g.add_edge("escalate", END)
    return g.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    tries = iter([False, True])
    app = build_app(lambda s: next(tries))
    cfg = {"configurable": {"thread_id": "HT-142"}}
    first = app.invoke({"ticket": "HT-142", "log": []}, cfg)
    print("paused for:", first["__interrupt__"][0].value)
    final = app.invoke(Command(resume="approve"), cfg)
    print("\n".join(final["log"]))
