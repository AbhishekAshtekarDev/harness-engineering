import sys
import os
from pathlib import Path

import pytest

from harnesslab.checks import Verdict
from harnesslab.evals import pass_at_k, pass_pow_k, judge_grader
from harnesslab.loop import AgentLoop, Budget
from harnesslab.models import ScriptedModel, ToolCall
from harnesslab.permissions import PathError, PathGuard, PermissionPolicy, Rule
from harnesslab.schema import validate
from harnesslab.state import FeatureList, FeatureListError, TaskState
from harnesslab.tools import Tool, summarize_pytest
from harnesslab.trace import Tracer, waterfall


def call(name, **args):
    return ToolCall("c1", name, args)


def test_deny_beats_allow_regardless_of_order():
    policy = PermissionPolicy(rules=[Rule("allow", "run_command"), Rule("deny", "run_command", "*rm -rf*")])
    assert policy.decide(call("run_command", command="rm -rf /")).effect == "deny"
    assert policy.decide(call("run_command", command="ls")).effect == "allow"
    assert policy.decide(call("other")).effect == "ask"  # default


@pytest.mark.skipif(sys.platform == "win32", reason="symlinks need admin rights on Windows")
def test_path_guard_blocks_traversal_symlinks_and_protected(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "config").mkdir()
    outside = tmp_path.parent / "outside-secret.txt"
    outside.write_text("secret", encoding="utf-8")
    (tmp_path / "src" / "link.txt").symlink_to(outside)
    guard = PathGuard(tmp_path, writable=("src/*",), protected=("src/keep.py",))
    assert guard.check_write("src/new.py") == (tmp_path / "src" / "new.py").resolve()
    for bad in ("../outside-secret.txt", "src/link.txt", "src/../../outside-secret.txt"):
        with pytest.raises(PathError):
            guard.check_write(bad)
    with pytest.raises(PathError):
        guard.check_write("config/app.toml")
    with pytest.raises(PathError):
        guard.check_write("src/keep.py")


def test_schema_validation_reports_useful_errors():
    schema = {"type": "object", "properties": {"n": {"type": "integer"}, "mode": {"enum": ["a", "b"]}},
              "required": ["n"], "additionalProperties": False}
    assert validate({"n": 1, "mode": "a"}, schema) == []
    errors = validate({"n": "1", "mode": "c", "x": 0}, schema)
    assert any("should be integer" in e for e in errors)
    assert any("must be one of" in e for e in errors)
    assert any("not an allowed field" in e for e in errors)
    assert validate({}, schema) == ["input.n is required"]
    assert validate({"n": True}, schema)  # booleans are not integers


def test_pass_at_k_and_pass_pow_k():
    assert pass_at_k(10, 10, 3) == 1.0
    assert pass_pow_k(10, 0, 3) == 0.0
    # 3 of 4 trials passed: one-shot success 0.75, all-of-3 success 0.25
    assert pass_pow_k(4, 3, 1) == pytest.approx(0.75)
    assert pass_pow_k(4, 3, 3) == pytest.approx(0.25)
    assert pass_at_k(4, 3, 2) == pytest.approx(1.0)
    assert pass_at_k(5, 1, 2) == pytest.approx(0.4)


def test_judge_grader_handles_unknown_and_garbage():
    grade = judge_grader("clarity", "is clear", lambda p: '{"verdict": "UNKNOWN", "reason": "no info"}', str)
    assert grade({}).passed is False and "UNKNOWN" in grade({}).note
    bad = judge_grader("clarity", "is clear", lambda p: "I think it is fine", str)
    assert bad({}).passed is False


def test_feature_list_only_status_may_change(tmp_path):
    fl = FeatureList(tmp_path / "features.json")
    fl.create(["user sets a weekly target", "streak resets after a missed week"])
    with pytest.raises(FeatureListError):
        fl.mark("F001", True, verified=False)
    fl.mark("F001", True, verified=True)
    assert fl.next_unfinished()["id"] == "F002"
    import json
    edited = fl.items()
    edited[1]["description"] = "streaks never reset"
    with pytest.raises(FeatureListError):
        fl.guard_rewrite(json.dumps(edited))


def test_task_state_round_trip(tmp_path):
    TaskState("T1", status="running", iterations=3).save(tmp_path)
    assert TaskState.load(tmp_path, "T1").iterations == 3
    assert TaskState.load(tmp_path, "missing").status == "pending"


def test_summarize_pytest_keeps_failures_only():
    raw = ("....F.\n" + "_" * 10 + " test_week " + "_" * 10 + "\n\n    def test_week():\n>       assert 1 == 2\n"
           "E       assert 1 == 2\n\ntests/test_x.py:3: AssertionError\n"
           "FAILED tests/test_x.py::test_week - assert 1 == 2\n1 failed, 5 passed in 0.10s\n")
    out = summarize_pytest(raw)
    assert "1 failed, 5 passed" in out and "E       assert 1 == 2" in out and "...." not in out
    assert summarize_pytest("10 passed in 0.1s").startswith("All tests passed")


def echo_tool():
    return Tool("echo", "echo text", {"type": "object", "properties": {"text": {"type": "string"}},
                                      "required": ["text"]}, lambda text: text)


def test_loop_stops_at_iteration_limit():
    model = ScriptedModel([{"calls": [("echo", {"text": str(i)})]} for i in range(100)])
    result = AgentLoop(model, [echo_tool()], "sys", budget=Budget(max_iterations=5)).run("go")
    assert result.status == "stopped" and "iteration limit" in result.reason and result.iterations == 5


def test_loop_refuses_identical_failed_call_and_unknown_tools():
    model = ScriptedModel([{"calls": [("echo", {})]}, {"calls": [("echo", {})]}, {"calls": [("nope", {})]}])
    result = AgentLoop(model, [echo_tool()], "sys").run("go")
    tool_msgs = [m["content"] for m in result.messages if m["role"] == "tool"]
    assert "Invalid arguments" in tool_msgs[0]
    assert "already failed" in tool_msgs[1]
    assert "Unknown tool" in tool_msgs[2]


class FakeWs:
    root = Path(".")


def test_claimed_done_is_verified_and_escalates_after_repeated_failure():
    verdicts = iter([Verdict(False, "[FAIL] tests: 2 failing", 1), Verdict(False, "[FAIL] tests", 1),
                     Verdict(False, "[FAIL] tests", 1)])
    model = ScriptedModel([{"say": "done"}, {"say": "done"}, {"say": "done"}])
    loop = AgentLoop(model, [], "sys", workspace=FakeWs(), verifier=lambda ws: next(verdicts),
                     budget=Budget(max_verification_failures=3))
    result = loop.run("go")
    assert result.status == "escalated"
    assert any("not done yet" in m["content"] for m in result.messages if m["role"] == "user")


def test_no_progress_detector():
    model = ScriptedModel([{"say": "done"}] * 10)
    loop = AgentLoop(model, [], "sys", workspace=FakeWs(), verifier=lambda ws: Verdict(False, "x", 3),
                     budget=Budget(max_verification_failures=10, no_progress_window=2))
    assert "no progress" in loop.run("go").reason


def test_trace_spans_nest_and_render(tmp_path):
    tracer = Tracer(tmp_path / "t.jsonl")
    with tracer.span("root"):
        with tracer.span("child", **{"gen_ai.tool.name": "read_file"}):
            pass
    assert tracer.spans[1].parent_id == tracer.spans[0].span_id
    assert "read_file" in waterfall(tracer.spans)
    assert len((tmp_path / "t.jsonl").read_text(encoding="utf-8").splitlines()) == 2


def test_demo_run_succeeds():
    from harnesslab.demo import main
    assert main() == 0
