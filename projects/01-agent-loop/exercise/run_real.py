"""Run your loop with a real model on a tiny task in a temporary folder.

    pip install anthropic            # or: pip install openai
    export ANTHROPIC_API_KEY=...     # or OPENAI_API_KEY and HARNESSLAB_MODEL
    python run_real.py anthropic     # or: python run_real.py openai

The tools are deliberately unsafe in one way: run_python executes code on
your machine. Project 03 fixes that. Keep the task small and read the output.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "harnesslab"))
from harnesslab.models import load_model  # noqa: E402

from mini_agent import Tool, Turn, ToolCall, run_agent  # noqa: E402


class Adapter:
    """Wrap a harnesslab model so it returns this project's Turn type."""

    def __init__(self, inner):
        self.inner = inner

    def complete(self, system, messages, tools):
        t = self.inner.complete(system, messages, tools)
        return Turn(t.text, [ToolCall(c.id, c.name, c.args) for c in t.tool_calls])


def main() -> None:
    provider = sys.argv[1] if len(sys.argv) > 1 else "anthropic"
    work = Path(tempfile.mkdtemp(prefix="p01-"))
    s = {"type": "string"}

    def write_file(path: str, content: str) -> str:
        (work / path).write_text(content, encoding="utf-8")
        return f"wrote {path}"

    def read_file(path: str) -> str:
        return (work / path).read_text(encoding="utf-8")

    def run_python(path: str) -> str:
        r = subprocess.run([sys.executable, path], cwd=work, capture_output=True, text=True, timeout=20)
        return f"exit {r.returncode}\n{r.stdout}{r.stderr}"[-3000:]

    tools = [
        Tool("write_file", "Create or overwrite a file in the work folder.",
             {"type": "object", "properties": {"path": s, "content": s}, "required": ["path", "content"]}, write_file),
        Tool("read_file", "Read a file from the work folder.",
             {"type": "object", "properties": {"path": s}, "required": ["path"]}, read_file),
        Tool("run_python", "Run a Python file from the work folder and return its output.",
             {"type": "object", "properties": {"path": s}, "required": ["path"]}, run_python),
    ]
    task = ("Write fizzbuzz.py that prints FizzBuzz for 1..15, run it, check the output is right, "
            "fix it if not, then report what you did.")
    result = run_agent(Adapter(load_model(provider)), tools, task, max_turns=8)
    for m in result.messages:
        if m["role"] == "assistant":
            print("assistant:", m["content"][:200], [c["name"] for c in m["tool_calls"]])
        elif m["role"] == "tool":
            print("   tool:", m["content"][:120].replace("\n", " | "))
    print(f"\nstatus={result.status} turns={result.turns} folder={work}")


if __name__ == "__main__":
    main()
