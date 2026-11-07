"""Project 05: the controls that end a loop for a stated reason.

A loop whose only exit is the model saying "done" runs forever on a task the
model can neither finish nor give up on. These functions are the exits the
harness owns: budgets, progress detection, repeat detection, failure
classification with backoff, and a circuit breaker for a failing dependency.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Budget:
    max_iterations: int = 40
    max_tokens: int = 500_000
    max_seconds: float = 2700
    max_cost_usd: float = 5.0
    no_progress_window: int = 5   # stop after this many iterations without a better score
    max_repeats: int = 3          # identical consecutive actions allowed


@dataclass
class LoopState:
    iterations: int = 0
    tokens: int = 0
    seconds: float = 0.0
    cost_usd: float = 0.0
    actions: list[str] = field(default_factory=list)   # e.g. 'edit_file streaks.py'
    scores: list[float] = field(default_factory=list)  # e.g. passing test count after each iteration


def stop_reason(s: LoopState, b: Budget) -> str | None:
    """Return why the loop must stop now, or None to continue.

    Check in this order and return the first match:
      iterations, tokens, seconds, cost   ("<name> budget exhausted")
      no progress: the best score of the last `no_progress_window` iterations
                   is not higher than the best score before them ("no progress")
      repeats: the last `max_repeats` actions are identical ("repeating the same action")
      oscillation: the last four actions are A, B, A, B with A != B ("oscillating")
    """
    # TODO: implement the checks above in order.
    # BEGIN SOLUTION
    for name, used, limit in (("iterations", s.iterations, b.max_iterations), ("tokens", s.tokens, b.max_tokens),
                              ("seconds", s.seconds, b.max_seconds), ("cost", s.cost_usd, b.max_cost_usd)):
        if used >= limit:
            return f"{name} budget exhausted"
    w = b.no_progress_window
    if w and len(s.scores) > w and max(s.scores[-w:]) <= max(s.scores[:-w]):
        return "no progress"
    if len(s.actions) >= b.max_repeats and len(set(s.actions[-b.max_repeats:])) == 1:
        return "repeating the same action"
    if len(s.actions) >= 4:
        a, bb, c, d = s.actions[-4:]
        if a == c and bb == d and a != bb:
            return "oscillating"
    return None
    # END SOLUTION


TRANSIENT = re.compile(r"\b(429|500|502|503|504)\b|rate limit|timed? ?out|timeout|connection (reset|refused)|"
                       r"temporar(y|ily)|overloaded|try again", re.I)


def classify_failure(error: str) -> str:
    """'transient' (retry the same thing after a pause) or 'substantive' (change the approach)."""
    # TODO: return "transient" if TRANSIENT matches the error text, else "substantive".
    # BEGIN SOLUTION
    return "transient" if TRANSIENT.search(error) else "substantive"
    # END SOLUTION


def backoff_delays(attempts: int, base: float = 1.0, factor: float = 2.0, cap: float = 60.0) -> list[float]:
    """Exponential backoff: base, base*factor, base*factor^2 ... each capped at `cap`.

    (Production code adds random jitter so many clients do not retry in lockstep.)
    """
    # TODO: return the list of `attempts` delays.
    # BEGIN SOLUTION
    return [min(cap, base * factor ** i) for i in range(attempts)]
    # END SOLUTION


class CircuitBreaker:
    """Stop calling a dependency that keeps failing, then test it again after a cool-down.

    closed     calls go through; `threshold` consecutive failures -> open
    open       calls are refused until `cooldown` seconds have passed -> half_open
    half_open  one trial call: success -> closed, failure -> open again
    """

    def __init__(self, threshold: int = 3, cooldown: float = 30.0):
        self.threshold, self.cooldown = threshold, cooldown
        self.state, self.failures, self.opened_at = "closed", 0, 0.0

    def allow(self, now: float) -> bool:
        # TODO: in "open", move to "half_open" once the cool-down has passed; refuse calls while open.
        # BEGIN SOLUTION
        if self.state == "open":
            if now - self.opened_at >= self.cooldown:
                self.state = "half_open"
                return True
            return False
        return True
        # END SOLUTION

    def record(self, ok: bool, now: float) -> None:
        # TODO: success -> closed with 0 failures; failure -> count it and open when the
        #       threshold is reached, or immediately if the failing call was the half_open trial.
        # BEGIN SOLUTION
        if ok:
            self.state, self.failures = "closed", 0
            return
        self.failures += 1
        if self.state == "half_open" or self.failures >= self.threshold:
            self.state, self.opened_at = "open", now
        # END SOLUTION


def should_trigger(event: dict, agent_id: str) -> bool:
    """Event-driven loops must ignore events their own agent caused, or they retrigger forever."""
    # TODO: return False when event["actor"] == agent_id, else True.
    # BEGIN SOLUTION
    return event.get("actor") != agent_id
    # END SOLUTION
