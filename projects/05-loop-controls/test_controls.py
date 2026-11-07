"""python -m pytest -q   (or SOLUTION=1 python -m pytest -q)"""
from controls import Budget, CircuitBreaker, LoopState, backoff_delays, classify_failure, should_trigger, stop_reason


def test_budgets():
    b = Budget(max_iterations=10, max_tokens=1000, max_seconds=60, max_cost_usd=1)
    assert stop_reason(LoopState(iterations=10), b) == "iterations budget exhausted"
    assert stop_reason(LoopState(tokens=1000), b) == "tokens budget exhausted"
    assert stop_reason(LoopState(seconds=61), b) == "seconds budget exhausted"
    assert stop_reason(LoopState(cost_usd=1.2), b) == "cost budget exhausted"
    assert stop_reason(LoopState(iterations=3), b) is None


def test_no_progress():
    b = Budget(no_progress_window=3)
    assert stop_reason(LoopState(scores=[1, 2, 5, 5, 4, 5]), b) == "no progress"
    assert stop_reason(LoopState(scores=[1, 2, 5, 5, 4, 6]), b) is None
    assert stop_reason(LoopState(scores=[1, 1]), b) is None  # too early to tell


def test_repeats_and_oscillation():
    b = Budget(max_repeats=3, no_progress_window=0)
    assert stop_reason(LoopState(actions=["run_tests", "run_tests", "run_tests"]), b) == "repeating the same action"
    assert stop_reason(LoopState(actions=["edit a", "run_tests", "edit a", "run_tests"]), b) == "oscillating"
    assert stop_reason(LoopState(actions=["edit a", "run_tests", "edit b", "run_tests"]), b) is None


def test_failure_classes():
    for e in ["HTTP 429 Too Many Requests", "503 Service Unavailable", "Read timed out", "connection reset by peer",
              "Overloaded, try again"]:
        assert classify_failure(e) == "transient", e
    for e in ["AssertionError: expected 4, got 0", "NameError: name 'week_start' is not defined", "FAILED test_x"]:
        assert classify_failure(e) == "substantive", e


def test_backoff():
    assert backoff_delays(5) == [1, 2, 4, 8, 16]
    assert backoff_delays(8, cap=10)[-1] == 10


def test_circuit_breaker():
    cb = CircuitBreaker(threshold=2, cooldown=10)
    assert cb.allow(0)
    cb.record(False, 0)
    cb.record(False, 1)
    assert cb.state == "open" and not cb.allow(5)
    assert cb.allow(12) and cb.state == "half_open"
    cb.record(False, 12)
    assert cb.state == "open" and not cb.allow(13)
    assert cb.allow(23)
    cb.record(True, 23)
    assert cb.state == "closed" and cb.failures == 0


def test_loops_ignore_their_own_events():
    assert should_trigger({"type": "issue_comment", "actor": "maintainer"}, "agent-7")
    assert not should_trigger({"type": "issue_comment", "actor": "agent-7"}, "agent-7")
