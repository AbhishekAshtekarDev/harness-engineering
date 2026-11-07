"""Ablation study: remove one harness component at a time and see what changes.

    python ablation.py                       # scripted agent, offline, seconds
    python ablation.py --provider anthropic  # a real model (costs money; run a few times)

For every variant we record three different answers to "did it work?":
  agent says    what the agent claimed in its last message
  harness says  the loop's status (succeeded / stopped / escalated)
  truth         an independent audit after the run: hidden tests pass AND
                no protected file changed

The interesting rows are where those three disagree.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harnesslab"))

from harnesslab.checks import AllOf, ChangedFilesCheck, PytestCheck  # noqa: E402
from harnesslab.demo import demo_model  # noqa: E402
from harnesslab.hooks import Hooks  # noqa: E402
from harnesslab.models import load_model  # noqa: E402
from harnesslab.permissions import PathGuard, PermissionPolicy  # noqa: E402
from harnesslab.presets import HABIT_TRACKER, PROTECTED, WRITABLE, build_habit_tracker_harness, ticket  # noqa: E402
from harnesslab.tools import coding_tools  # noqa: E402

HIDDEN = sorted((HABIT_TRACKER / ".harness").glob("*/test_*.py"))


def audit(ws) -> bool:
    return ChangedFilesCheck(WRITABLE, PROTECTED)(ws).passed and PytestCheck(extra_tests=HIDDEN)(ws).passed


def remove(component: str, loop, ws) -> None:
    if component == "verifier":
        loop.verifier = None
    elif component == "hooks":
        loop.hooks = Hooks()
    elif component == "permissions":
        loop.policy = PermissionPolicy(default="allow")
        loop.tools = {t.name: t for t in coding_tools(ws, PathGuard(ws.root, writable=("*",)))}
    elif component == "hidden tests":
        loop.verifier = AllOf([ChangedFilesCheck(WRITABLE, PROTECTED), PytestCheck(name="unit tests")])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["anthropic", "openai"])
    args = ap.parse_args()
    rows = []
    for component in ("nothing", "verifier", "hidden tests", "hooks", "permissions"):
        model = load_model(args.provider) if args.provider else demo_model()
        loop, ws = build_habit_tracker_harness(model)
        try:
            remove(component, loop, ws)
            result = loop.run(ticket(), task_id=f"ablate-{component}")
            claim = "done" if "done" in result.final_text.lower() else (result.final_text[:20] or "-")
            rows.append((component, claim, f"{result.status}", "PASS" if audit(ws) else "FAIL",
                         result.iterations, ", ".join(ws.changed_files())))
        finally:
            ws.destroy()
    print(f"{'removed':<14}{'agent says':<12}{'harness says':<14}{'truth':<7}{'iters':>6}  changed files")
    for r in rows:
        print(f"{r[0]:<14}{r[1]:<12}{r[2]:<14}{r[3]:<7}{r[4]:>6}  {r[5]}")


if __name__ == "__main__":
    main()
