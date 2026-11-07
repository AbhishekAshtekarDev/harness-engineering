"""python -m pytest -q   (or SOLUTION=1 python -m pytest -q)"""
from pathlib import Path

from trace_analysis import edits_per_file, files_read, first_problem, load, summary

T = Path(__file__).parent / "traces"


def test_summary_of_a_stuck_run():
    s = summary(load(T / "run-b.jsonl"))
    assert s["status"] == "stopped" and "iteration limit" in s["stop_reason"]
    assert s["iterations"] == 12 and s["tool_calls"]["run_tests"] >= 4
    assert s["input_tokens"] > 0


def test_stuck_run_edits_one_file_over_and_over():
    assert edits_per_file(load(T / "run-b.jsonl"))["habit_tracker/streaks.py"] >= 5


def test_blocked_actions_in_the_injection_run():
    s = summary(load(T / "run-d.jsonl"))
    tools = [tool for tool, _ in s["blocked"]]
    assert "run_command" in tools
    assert s["tool_errors"]["edit_file"] >= 1  # the protected config edit


def test_first_problem_points_at_the_root_cause():
    p = first_problem(load(T / "run-d.jsonl"))
    assert p["tool"] == "run_command"
    p = first_problem(load(T / "run-c.jsonl"))
    assert p["name"] == "post_run_audit"


def test_what_the_agent_read():
    assert "docs/old-design-note.md" in files_read(load(T / "run-a.jsonl"))
    assert summary(load(T / "run-a.jsonl"))["verifications"] == [False, False]
