"""Project 04: make work survive across sessions, crashes and context resets.

The pattern follows Anthropic's harness for long-running agents:
  - an initializer session writes a feature list (JSON), a progress log and
    a first checkpoint, once
  - every later session starts with the same routine: read the progress log,
    find the next unfinished feature, run a smoke check, and refuse to start
    new work on top of a broken state
  - a feature becomes "passing" only after a verification check confirms it
  - every verified step is a checkpoint you can roll back to

Checkpoints here are folder snapshots so the project runs anywhere. In a real
repository, use git commits: same idea, better tooling.
"""
from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

STATE = ".agent"            # harness records live here, next to the code
FEATURES = "feature_list.json"
PROGRESS = "progress.md"


def _features(project: Path) -> list[dict]:
    return json.loads((project / STATE / FEATURES).read_text())


def _save_features(project: Path, items: list[dict]) -> None:
    tmp = project / STATE / (FEATURES + ".tmp")
    tmp.write_text(json.dumps(items, indent=2))
    tmp.replace(project / STATE / FEATURES)  # atomic: a crash never leaves half a file


def checkpoint(project: Path, message: str) -> int:
    """Snapshot every file outside .agent/ into .agent/checkpoints/NNN and log the message."""
    cps = project / STATE / "checkpoints"
    cps.mkdir(parents=True, exist_ok=True)
    n = len([p for p in cps.iterdir() if p.is_dir()]) + 1
    dest = cps / f"{n:03d}"
    shutil.copytree(project, dest, ignore=shutil.ignore_patterns(STATE, "__pycache__"))
    with (project / STATE / "checkpoints.log").open("a") as f:
        f.write(f"{n:03d} {message}\n")
    return n


def rollback(project: Path, n: int) -> None:
    """Restore the project files to checkpoint n (harness records are kept)."""
    src = project / STATE / "checkpoints" / f"{n:03d}"
    for p in project.iterdir():
        if p.name != STATE:
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    shutil.copytree(src, project, dirs_exist_ok=True)


def initialize(project: Path, features: list[str]) -> None:
    """The initializer session. Runs once; refuses to run twice."""
    # TODO: refuse if .agent/feature_list.json already exists (raise RuntimeError).
    # TODO: create .agent/, write the feature list with ids F001, F002... and "passes": false,
    #       start progress.md with a header, and take checkpoint "initial state".
    raise NotImplementedError("Your code here: see the TODO above")


@dataclass
class Briefing:
    """What a fresh session needs before it touches anything."""
    next_feature: dict | None
    done: int
    total: int
    recent_progress: str
    last_checkpoint: str
    smoke_ok: bool
    warnings: list[str] = field(default_factory=list)

    def as_prompt(self) -> str:
        nxt = f"{self.next_feature['id']}: {self.next_feature['description']}" if self.next_feature else "none"
        lines = [f"Features passing: {self.done}/{self.total}. Next feature: {nxt}.",
                 f"Last checkpoint: {self.last_checkpoint}", "Recent progress:", self.recent_progress]
        lines += [f"WARNING: {w}" for w in self.warnings]
        return "\n".join(lines)


def start_session(project: Path, smoke_check: Callable[[], bool],
                  verify: Callable[[str], bool] | None = None) -> Briefing:
    """The routine every session runs first.

    smoke_check() says whether the project basically works right now.
    verify(feature_id), if given, re-checks features the log claims are passing,
    because records can drift from reality.
    """
    # TODO: load the features; count passing ones; pick the first non-passing one.
    # TODO: read the last 12 lines of progress.md and the last line of checkpoints.log.
    # TODO: run smoke_check(); if it fails add a warning that says to fix or roll back first.
    # TODO: if verify is given, re-check every "passing" feature and warn about any that fail.
    raise NotImplementedError("Your code here: see the TODO above")


def complete_feature(project: Path, feature_id: str, verify: Callable[[str], bool], note: str) -> bool:
    """Mark a feature passing only if verify(feature_id) is True. Log either way.

    On success: flip `passes`, append a progress entry, take a checkpoint, return True.
    On failure: append a progress entry that says it is still failing, return False.
    """
    # TODO: implement the rule above. Never flip `passes` without a passing check.
    raise NotImplementedError("Your code here: see the TODO above")


def guard_feature_list(old: list[dict], proposed: list[dict]) -> None:
    """Reject an agent-written feature list that changes anything except `passes`."""
    # TODO: compare the lists with the "passes" key removed; raise ValueError if they differ.
    raise NotImplementedError("Your code here: see the TODO above")
