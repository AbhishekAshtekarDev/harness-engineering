"""Verification: the harness checks the work instead of trusting the agent's claim.

A verifier looks at the workspace and returns a Verdict. Verifiers compose,
so one task can require the test suite, an acceptance test the agent never
saw, and "no forbidden files changed", all at once.

`score` is a number that should rise as the work gets closer to done (for
example, the count of passing tests). The loop uses it to detect runs that
keep going without making progress.
"""
from __future__ import annotations

import fnmatch
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from .tools import summarize_pytest
from .workspace import Workspace, run_command


@dataclass
class Verdict:
    passed: bool
    summary: str
    score: float = 0.0
    details: dict = field(default_factory=dict)


class Verifier(Protocol):
    name: str

    def __call__(self, ws: Workspace) -> Verdict: ...


def _count(pattern: str, text: str) -> int:
    m = re.search(rf"(\d+) {pattern}", text)
    return int(m.group(1)) if m else 0


@dataclass
class PytestCheck:
    """Run pytest in the workspace. `extra_tests` are copied in only for the check.

    Extra tests are how you keep held-out and acceptance tests away from the
    agent: they live outside the workspace, are copied in, run, and removed.
    """
    name: str = "tests"
    target: str = ""
    extra_tests: list[Path] = field(default_factory=list)
    timeout: float = 300

    def __call__(self, ws: Workspace) -> Verdict:
        copied = []
        for src in self.extra_tests:
            dst = ws.root / "tests" / f"_harness_{Path(src).name}"
            shutil.copy(src, dst)
            copied.append(dst)
        try:
            targets = " ".join([self.target] + [str(c.relative_to(ws.root)) for c in copied]).strip()
            r = run_command(f"python -m pytest -q -p no:cacheprovider {targets}", cwd=ws.root,
                            timeout=self.timeout, max_chars=60_000)
        finally:
            for c in copied:
                c.unlink(missing_ok=True)
        passed_n, failed_n = _count("passed", r.output), _count("failed", r.output) + _count("error", r.output)
        ok = r.exit_code == 0 and failed_n == 0
        return Verdict(ok, summarize_pytest(r.output), score=passed_n, details={"passed": passed_n, "failed": failed_n})


@dataclass
class ChangedFilesCheck:
    """Fail if the agent changed anything outside the allowed globs, or touched protected files."""
    allowed: tuple[str, ...]
    protected: tuple[str, ...] = ()
    name: str = "changed-files"

    def __call__(self, ws: Workspace) -> Verdict:
        changed = ws.changed_files()
        bad = [f for f in changed if any(fnmatch.fnmatchcase(f, p) for p in self.protected)
               or not any(fnmatch.fnmatchcase(f, p) for p in self.allowed)]
        if bad:
            return Verdict(False, "Files changed outside the allowed folders: " + ", ".join(bad), details={"changed": changed})
        return Verdict(True, f"{len(changed)} file(s) changed, all allowed: {', '.join(changed) or 'none'}",
                       details={"changed": changed})


@dataclass
class AllOf:
    """Every check must pass. Cheap checks first, so a failure stops the expensive ones."""
    checks: list[Callable[[Workspace], Verdict]]
    name: str = "verification"

    def __call__(self, ws: Workspace) -> Verdict:
        summaries, score = [], 0.0
        for check in self.checks:
            v = check(ws)
            score += v.score
            summaries.append(f"[{'PASS' if v.passed else 'FAIL'}] {getattr(check, 'name', 'check')}: {v.summary}")
            if not v.passed:
                return Verdict(False, "\n".join(summaries), score=score)
        return Verdict(True, "\n".join(summaries), score=score)
