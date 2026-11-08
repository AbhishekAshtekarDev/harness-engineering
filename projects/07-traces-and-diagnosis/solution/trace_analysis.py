"""Project 07: turn a trace into answers.

A trace file is JSON Lines, one span per line, as written by harnesslab:
  {"name", "span_id", "parent_id", "start", "end", "status", "attributes": {...}}

Useful span names: invoke_agent (root), iteration, chat (model call),
execute_tool, verify, post_run_audit. Useful attributes: gen_ai.tool.name,
args, is_error, blocked, passed, stop_reason, gen_ai.usage.input_tokens.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def load(path: str | Path) -> list[dict]:
    spans = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    return sorted(spans, key=lambda s: s["start"])


def summary(spans: list[dict]) -> dict:
    """Return a dict with:
    status, stop_reason      from the invoke_agent span
    iterations               number of 'iteration' spans
    tool_calls               Counter of tool names over execute_tool spans
    tool_errors              Counter of tool names whose span has is_error true
    blocked                  list of (tool name, blocked reason) for spans with a 'blocked' attribute
    verifications            list of booleans from verify spans ('passed'), in order
    input_tokens, output_tokens   from the invoke_agent span
    """
    # TODO: build the dict described above.
    # BEGIN SOLUTION
    root = next(s for s in spans if s["name"] == "invoke_agent")["attributes"]
    tools = [s for s in spans if s["name"] == "execute_tool"]
    return {
        "status": root.get("status"),
        "stop_reason": root.get("stop_reason"),
        "iterations": sum(s["name"] == "iteration" for s in spans),
        "tool_calls": Counter(s["attributes"]["gen_ai.tool.name"] for s in tools),
        "tool_errors": Counter(s["attributes"]["gen_ai.tool.name"] for s in tools if s["attributes"].get("is_error")),
        "blocked": [(s["attributes"]["gen_ai.tool.name"], s["attributes"]["blocked"]) for s in tools
                    if s["attributes"].get("blocked")],
        "verifications": [bool(s["attributes"].get("passed")) for s in spans if s["name"] == "verify"],
        "input_tokens": root.get("gen_ai.usage.input_tokens", 0),
        "output_tokens": root.get("gen_ai.usage.output_tokens", 0),
    }
    # END SOLUTION


def edits_per_file(spans: list[dict]) -> Counter:
    """Count edit_file/write_file calls per path. A high count on one file is a stuck-loop signal."""
    # TODO
    # BEGIN SOLUTION
    return Counter(s["attributes"]["args"].get("path") for s in spans if s["name"] == "execute_tool"
                   and s["attributes"]["gen_ai.tool.name"] in ("edit_file", "write_file"))
    # END SOLUTION


def first_problem(spans: list[dict]) -> dict | None:
    """The earliest span (by start time) that is an error, a block, a failed verify or a failed audit.

    Diagnosis starts here: later problems often follow from the first one.
    Return {"name", "tool", "detail"} where detail is the result_preview (or blocked reason), or None.
    """
    # TODO
    # BEGIN SOLUTION
    for s in spans:
        a = s["attributes"]
        bad = a.get("is_error") or a.get("blocked") or (s["name"] in ("verify", "post_run_audit") and not a.get("passed"))
        if bad:
            return {"name": s["name"], "tool": a.get("gen_ai.tool.name"), "detail": a.get("result_preview") or a.get("blocked")}
    return None
    # END SOLUTION


def files_read(spans: list[dict]) -> list[str]:
    """Paths passed to read_file, in order. 'What did the agent see?' is the first diagnostic question."""
    # TODO
    # BEGIN SOLUTION
    return [s["attributes"]["args"]["path"] for s in spans if s["name"] == "execute_tool"
            and s["attributes"]["gen_ai.tool.name"] == "read_file"]
    # END SOLUTION
