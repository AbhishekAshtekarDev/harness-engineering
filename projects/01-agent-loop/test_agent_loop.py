"""Run with:  python -m pytest -q            (tests your exercise/ code)
         or:  SOLUTION=1 python -m pytest -q (tests the reference solution)"""
from mini_agent import Tool, ToolCall, Turn, execute_tool, run_agent


class ScriptedModel:
    def __init__(self, turns):
        self.turns, self.seen = list(turns), []

    def complete(self, system, messages, tools):
        self.seen.append([dict(m) for m in messages])
        return self.turns.pop(0) if self.turns else Turn("done")


def add_tool():
    return Tool("add", "Add two integers.", {"type": "object", "properties": {
        "a": {"type": "integer"}, "b": {"type": "integer"}}, "required": ["a", "b"]}, lambda a, b: str(a + b))


def test_finishes_when_model_stops_calling_tools():
    model = ScriptedModel([Turn("4")])
    result = run_agent(model, [add_tool()], "What is 2 + 2?")
    assert result.status == "finished" and result.turns == 1 and result.final_text == "4"


def test_tool_results_go_back_to_the_model():
    model = ScriptedModel([Turn("", [ToolCall("c1", "add", {"a": 2, "b": 3})]), Turn("The answer is 5.")])
    result = run_agent(model, [add_tool()], "Add 2 and 3")
    tool_msg = result.messages[2]
    assert tool_msg == {"role": "tool", "tool_call_id": "c1", "name": "add", "content": "5", "is_error": False}
    assert model.seen[1][-1]["content"] == "5", "the second model call must see the tool result"
    assert result.status == "finished" and result.turns == 2


def test_several_calls_in_one_turn_each_get_a_result():
    model = ScriptedModel([Turn("", [ToolCall("a", "add", {"a": 1, "b": 1}), ToolCall("b", "add", {"a": 2, "b": 2})])])
    result = run_agent(model, [add_tool()], "two sums")
    assert [m["content"] for m in result.messages if m["role"] == "tool"] == ["2", "4"]


def test_max_turns_stops_a_model_that_never_finishes():
    model = ScriptedModel([Turn("", [ToolCall(str(i), "add", {"a": 1, "b": 1})]) for i in range(50)])
    result = run_agent(model, [add_tool()], "loop forever", max_turns=3)
    assert result.status == "max_turns" and result.turns == 3


def test_unknown_tool_and_crashing_tool_become_readable_errors():
    def boom():
        raise ValueError("disk full")
    tools = {"add": add_tool(), "boom": Tool("boom", "fails", {"type": "object"}, boom)}
    text, err = execute_tool(tools, ToolCall("x", "nope", {}))
    assert err and "unknown tool" in text and "add" in text and "boom" in text
    text, err = execute_tool(tools, ToolCall("y", "boom", {}))
    assert err and "ValueError" in text and "disk full" in text
    text, err = execute_tool(tools, ToolCall("z", "add", {"a": 1}))
    assert err and "TypeError" in text  # a missing argument is reported, not raised
