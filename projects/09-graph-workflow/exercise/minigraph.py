"""Project 09: a tiny graph engine, so you can see what LangGraph-style frameworks do.

  nodes      functions state -> partial update (dict)
  edges      fixed: always go to the same next node
  routers    conditional edges: a function state -> next node name
  reducers   how an update merges into state (replace by default, or append)
  limits     max_steps guards against cycles that never end
  interrupt  a node raises Interrupt to pause for a person; the run is checkpointed
             and resume(thread_id, answer) continues from the same node
"""
from __future__ import annotations

import copy
from typing import Any, Callable

START, END = "__start__", "__end__"


class Interrupt(Exception):
    def __init__(self, payload: Any):
        super().__init__(str(payload))
        self.payload = payload


class GraphError(RuntimeError):
    pass


def append(old: list | None, new: list) -> list:
    return (old or []) + list(new)


class Graph:
    def __init__(self, reducers: dict[str, Callable[[Any, Any], Any]] | None = None, max_steps: int = 50):
        self.nodes: dict[str, Callable[[dict], dict]] = {}
        self.edges: dict[str, str] = {}
        self.routers: dict[str, Callable[[dict], str]] = {}
        self.reducers = reducers or {}
        self.max_steps = max_steps
        self.checkpoints: dict[str, dict] = {}   # thread_id -> {"state", "node", "steps"}

    def add_node(self, name: str, fn: Callable[[dict], dict]) -> None:
        self.nodes[name] = fn

    def add_edge(self, src: str, dst: str) -> None:
        self.edges[src] = dst

    def add_router(self, src: str, route: Callable[[dict], str]) -> None:
        self.routers[src] = route

    def _merge(self, state: dict, update: dict) -> dict:
        # TODO: for each key in update, use the key's reducer if one exists
        #       (reducer(old_value, new_value)), otherwise replace. Return a new dict.
        raise NotImplementedError("Your code here: see the TODO above")

    def _next(self, node: str, state: dict) -> str:
        # TODO: a router wins over a fixed edge; no way out of a node is a GraphError.
        raise NotImplementedError("Your code here: see the TODO above")

    def _run_from(self, node: str, state: dict, steps: int, thread_id: str, resume_value: Any = None) -> dict:
        # TODO: loop until node == END:
        #   - if steps >= max_steps raise GraphError("max_steps ...")
        #   - call the node with a copy of state; if this is the resumed node, put resume_value
        #     in state["human"] first
        #   - on Interrupt: save {"state", "node", "steps"} under thread_id, then return
        #     {"status": "interrupted", "payload": exc.payload, "state": state}
        #   - merge the update, count the step, append the node name to state["path"], move on
        # On END delete the checkpoint and return {"status": "done", "state": state}.
        raise NotImplementedError("Your code here: see the TODO above")

    def run(self, state: dict, thread_id: str = "t1") -> dict:
        return self._run_from(self._next(START, state), dict(state), 0, thread_id)

    def resume(self, thread_id: str, value: Any) -> dict:
        cp = self.checkpoints[thread_id]
        return self._run_from(cp["node"], cp["state"], cp["steps"], thread_id, value)
