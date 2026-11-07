"""Tools: the actions an agent can take.

A tool has four parts. The model sees three of them (name, description,
input schema). The fourth, the implementation, stays in the harness.

`coding_tools(workspace, guard)` builds the small toolset the course uses for
the habit-tracker agent. Notice the design choices, each of which is a lesson:

- `search_code` returns matching lines with file and line number, not files.
- `read_file` reads a line range, so the agent need not load a whole file.
- `edit_file` replaces one exact snippet. It cannot silently drop the rest of
  a file, and it fails loudly if the snippet is missing or ambiguous.
- `run_tests` returns failures only, not thousands of passing lines.
- Errors say what went wrong *and* what to do next.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .permissions import PathError, PathGuard
from .schema import validate
from .workspace import Workspace, run_command


class ToolError(Exception):
    """Raise inside a tool to return a helpful error to the model."""


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    fn: Callable[..., str]
    risk: str = "low"   # low | medium | high, used by permission rules and approvals

    def spec(self) -> dict:
        return {"name": self.name, "description": self.description, "input_schema": self.input_schema}

    def validate(self, args: dict) -> list[str]:
        return validate(args, self.input_schema)

    def __call__(self, **kwargs: Any) -> str:
        return self.fn(**kwargs)


def _obj(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


def summarize_pytest(output: str) -> str:
    """Shape raw pytest output into what an agent needs: failures and their errors."""
    tail = [l for l in output.splitlines() if re.search(r"\d+ (passed|failed|error)", l)]
    summary = tail[-1].strip("= ") if tail else "no summary line found"
    failures = re.findall(r"^(?:FAILED|ERROR) (.+)$", output, flags=re.M)
    if not failures and "passed" in summary and "failed" not in summary and "error" not in summary:
        return f"All tests passed ({summary})."
    blocks = re.split(r"\n_{5,} (.+?) _{5,}\n", output)
    details = []
    for i in range(1, len(blocks) - 1, 2):
        name, body = blocks[i], blocks[i + 1]
        lines = [l for l in body.splitlines() if l.startswith("E ") or re.match(r"^\S+\.py:\d+", l)]
        details.append(f"- {name}\n    " + "\n    ".join(lines[-6:]))
    text = f"Test run: {summary}\nFailing: {', '.join(failures) if failures else 'see output'}"
    if details:
        text += "\n" + "\n".join(details)
    elif not failures:
        text += "\n" + output[-2000:]
    return text


def coding_tools(ws: Workspace, guard: PathGuard, test_command: str = "python -m pytest -q -p no:cacheprovider") -> list[Tool]:
    root = ws.root

    def list_files(folder: str = ".") -> str:
        base = guard.resolve(folder)
        if not base.is_dir():
            raise ToolError(f"'{folder}' is not a folder. Use list_files with '.' to see the top level.")
        items = sorted(p.relative_to(root).as_posix() + ("/" if p.is_dir() else "")
                       for p in base.iterdir() if not p.name.startswith(".") and p.name != "__pycache__")
        return "\n".join(items) or "(empty folder)"

    def search_code(query: str, folder: str = ".") -> str:
        base = guard.resolve(folder)
        hits = []
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix in {".py", ".md", ".toml", ".txt", ".json"} and "__pycache__" not in p.parts:
                for n, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                    if query.lower() in line.lower():
                        hits.append(f"{p.relative_to(root).as_posix()}:{n}: {line.strip()[:160]}")
        if not hits:
            return f"No matches for '{query}'. Try a shorter or different word."
        more = f"\n... {len(hits) - 30} more matches; narrow the query or the folder." if len(hits) > 30 else ""
        return "\n".join(hits[:30]) + more

    def read_file(path: str, start_line: int = 1, end_line: int = 400) -> str:
        target = guard.resolve(path)
        if not target.is_file():
            near = sorted(p.name for p in target.parent.glob("*")) if target.parent.is_dir() else []
            hint = f" Files in that folder: {', '.join(near)}." if near else ""
            raise ToolError(f"No file at '{path}'.{hint}")
        lines = target.read_text(errors="replace").splitlines()
        chunk = lines[start_line - 1:end_line]
        numbered = "\n".join(f"{i:>4} {l}" for i, l in enumerate(chunk, start_line))
        more = f"\n[{len(lines) - end_line} more lines; read with start_line={end_line + 1}]" if len(lines) > end_line else ""
        return numbered + more

    def edit_file(path: str, old_text: str, new_text: str) -> str:
        target = guard.check_write(path)
        if not target.is_file():
            raise ToolError(f"No file at '{path}'. To create a new file use write_file.")
        text = target.read_text()
        count = text.count(old_text)
        if count == 0:
            raise ToolError("old_text was not found. Read the file again and copy the exact lines, including indentation.")
        if count > 1:
            raise ToolError(f"old_text appears {count} times. Include more surrounding lines so it is unique.")
        target.write_text(text.replace(old_text, new_text, 1))
        return f"Edited {path}: replaced {old_text.count(chr(10)) + 1} line(s) with {new_text.count(chr(10)) + 1}."

    def write_file(path: str, content: str) -> str:
        target = guard.check_write(path)
        if target.exists():
            raise ToolError(f"'{path}' already exists. Use edit_file to change it.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"Created {path} ({content.count(chr(10)) + 1} lines)."

    def run_tests(path: str = "") -> str:
        if path:
            guard.resolve(path)
        result = run_command(f"{test_command} {path}".strip(), cwd=root, timeout=300, max_chars=60_000)
        if result.timed_out:
            return "The test run timed out after 300s. Run a single test file to find the slow test."
        return summarize_pytest(result.output)

    def run_command_tool(command: str) -> str:
        result = run_command(command, cwd=root, timeout=120)
        return f"exit code {result.exit_code}\n{result.output}".strip()

    str_ = {"type": "string"}
    return [
        Tool("list_files", "List files and folders inside a project folder (relative path, default '.').",
             _obj({"folder": str_}, []), list_files),
        Tool("search_code",
             "Case-insensitive text search across the project. Returns 'path:line: text' for each match. "
             "Use it to find where something is defined before reading files.",
             _obj({"query": str_, "folder": str_}, ["query"]), search_code),
        Tool("read_file",
             "Read a text file with line numbers. Optionally pass start_line and end_line to read part of a long file.",
             _obj({"path": str_, "start_line": {"type": "integer"}, "end_line": {"type": "integer"}}, ["path"]),
             read_file),
        Tool("edit_file",
             "Replace one exact, unique snippet of an existing file. old_text must match the file exactly, "
             "including indentation. Use for all changes to existing files.",
             _obj({"path": str_, "old_text": str_, "new_text": str_}, ["path", "old_text", "new_text"]),
             edit_file, risk="medium"),
        Tool("write_file", "Create a new file. Fails if the file already exists.",
             _obj({"path": str_, "content": str_}, ["path", "content"]), write_file, risk="medium"),
        Tool("run_tests",
             "Run the test suite (or one test file or folder via path) and return only failures and their "
             "error lines. Run it after every change and before you say you are done.",
             _obj({"path": str_}, []), run_tests),
        Tool("run_command", "Run a shell command in the project folder. Subject to permission rules.",
             _obj({"command": str_}, ["command"]), run_command_tool, risk="high"),
    ]


def execute(tool: Tool, args: dict) -> tuple[str, bool]:
    """Run a tool and turn every failure into a message the model can act on."""
    errors = tool.validate(args)
    if errors:
        return ("Invalid arguments: " + "; ".join(errors) +
                f". Expected schema: {tool.input_schema}"), True
    try:
        return tool(**args), False
    except (ToolError, PathError) as exc:
        return str(exc), True
    except Exception as exc:  # a bug in the tool, not a mistake by the model
        return f"Internal tool error ({type(exc).__name__}: {exc}). This is a harness bug, not your fault.", True
