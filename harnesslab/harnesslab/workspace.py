"""Per-task workspaces and the command runner.

A workspace is a private copy of the project for one task. The agent edits
files there, runs commands there, and the harness throws it away afterwards.

Important: a copied folder and a subprocess are an *organisational* boundary,
not a security boundary. A command can still read your home directory or use
the network. For real isolation run the harness inside a container or VM with
the network off (see projects/03-permissions-and-sandbox). The runner below
does the parts that belong in the harness either way: a scrubbed environment,
a timeout on every command, and capped output.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

# Folders the agent never receives: harness-owned checks, caches, VCS data.
DEFAULT_EXCLUDES = (".harness", ".git", "__pycache__", ".pytest_cache", ".venv")


class Workspace:
    def __init__(self, source: str | Path, excludes: tuple[str, ...] = DEFAULT_EXCLUDES):
        self.source = Path(source).resolve()
        self.root = Path(tempfile.mkdtemp(prefix="harnesslab-")).resolve()
        shutil.copytree(self.source, self.root, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(*excludes))
        self.baseline = self.snapshot()

    def path(self, relative: str) -> Path:
        return (self.root / relative).resolve()

    def snapshot(self) -> dict[str, str]:
        """Hash of every file, used to compute what the agent changed."""
        out = {}
        for p in sorted(self.root.rglob("*")):
            if p.is_file() and not any(part in DEFAULT_EXCLUDES for part in p.relative_to(self.root).parts):
                out[p.relative_to(self.root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
        return out

    def changed_files(self) -> list[str]:
        now = self.snapshot()
        keys = set(now) | set(self.baseline)
        return sorted(k for k in keys if now.get(k) != self.baseline.get(k))

    def destroy(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


@dataclass
class CommandResult:
    command: str
    exit_code: int
    output: str
    seconds: float
    timed_out: bool = False


SAFE_ENV_KEYS = ("PATH", "LANG", "LC_ALL", "TZ", "SYSTEMROOT", "PYTHONIOENCODING")


def run_command(command: str, cwd: Path, timeout: float = 120, max_chars: int = 12_000) -> CommandResult:
    """Run a shell command with a timeout, a scrubbed environment and capped output.

    Secrets usually live in environment variables, so the child process gets
    only a short allow-list of variables. HOME points into the workspace.
    """
    env = {k: os.environ[k] for k in SAFE_ENV_KEYS if k in os.environ}
    env["HOME"] = str(cwd)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"  # child Python processes print UTF-8 on every OS
    # Make `python` mean the interpreter running the harness.
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    start = time.monotonic()
    try:
        proc = subprocess.run(command, shell=True, cwd=cwd, env=env, capture_output=True, encoding="utf-8", errors="replace",
                              text=True, timeout=timeout)
        output = proc.stdout + proc.stderr
        code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        output += f"\n[harness] command timed out after {timeout:.0f}s and was stopped"
        code, timed_out = 124, True
    if len(output) > max_chars:
        head, tail = output[: max_chars // 2], output[-max_chars // 2:]
        output = f"{head}\n[harness] ... {len(output) - max_chars} characters cut ...\n{tail}"
    return CommandResult(command, code, output, time.monotonic() - start, timed_out)
