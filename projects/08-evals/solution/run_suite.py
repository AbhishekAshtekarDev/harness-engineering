"""Run a small eval of two scripted "agents" on ticket HT-142 and print pass@k and pass^k.

    python run_suite.py --trials 10

Each trial runs the agent inside harnesslab WITHOUT the verifier (we are
measuring the agent, not letting the harness rescue it), then grades the
outcome with the hidden acceptance tests, a code grader, not the agent's word.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "harnesslab"))

from harnesslab.checks import ChangedFilesCheck, PytestCheck  # noqa: E402
from harnesslab.loop import AgentLoop, Budget  # noqa: E402
from harnesslab.models import ScriptedModel  # noqa: E402
from harnesslab.permissions import PathGuard  # noqa: E402
from harnesslab.presets import HABIT_TRACKER, PROTECTED, SYSTEM_PROMPT, WRITABLE  # noqa: E402
from harnesslab.tools import coding_tools  # noqa: E402
from harnesslab.workspace import Workspace  # noqa: E402

from evalkit import pass_at_k, pass_pow_k, wilson_interval  # noqa: E402

TAIL = "        cursor -= timedelta(days=1)\n    return streak\n"
BODY = '''

def weekly_streak(habit, today):
    from .timeutils import week_start
    counts = {}
    for c in habit.completions:
        w = week_start(local_date(c, habit.timezone))
        counts[w] = counts.get(w, 0) + 1
    week = week_start(today)
    streak = {start}
    week -= timedelta(days=7)
    while counts.get(week, 0) >= habit.weekly_target:
        streak += 1
        week -= timedelta(days=7)
    return streak
'''
CORRECT = TAIL + BODY.replace("{start}", "1 if counts.get(week, 0) >= habit.weekly_target else 0")
HASTY = TAIL + BODY.replace("{start}", "0")  # forgets the current week


def agent(skill: float, rng: random.Random) -> ScriptedModel:
    code = CORRECT if rng.random() < skill else HASTY
    return ScriptedModel([
        {"calls": [("read_file", {"path": "docs/product-spec.md"})]},
        {"calls": [("edit_file", {"path": "habit_tracker/streaks.py", "old_text": TAIL, "new_text": code})]},
        {"say": "Done."},
    ])


def trial(skill: float, seed: int) -> bool:
    ws = Workspace(HABIT_TRACKER)
    try:
        loop = AgentLoop(agent(skill, random.Random(seed)), coding_tools(ws, PathGuard(ws.root, WRITABLE, PROTECTED)),
                         SYSTEM_PROMPT, workspace=ws, budget=Budget(max_iterations=6))
        loop.run("Implement HT-142.")
        hidden = sorted((HABIT_TRACKER / ".harness").glob("*/test_*.py"))
        return ChangedFilesCheck(WRITABLE, PROTECTED)(ws).passed and PytestCheck(extra_tests=hidden)(ws).passed
    finally:
        ws.destroy()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--k", type=int, default=3)
    args = ap.parse_args()
    print(f"{'agent':<16}{'passed':>9}{'95% CI':>16}{'pass@' + str(args.k):>9}{'pass^' + str(args.k):>9}")
    for name, skill in (("careful (0.9)", 0.9), ("hasty (0.5)", 0.5)):
        results = [trial(skill, seed) for seed in range(args.trials)]
        n, c = len(results), sum(results)
        lo, hi = wilson_interval(c, n)
        print(f"{name:<16}{c:>5}/{n:<3}{f'{lo:.2f}-{hi:.2f}':>16}{pass_at_k(n, c, args.k):>9.2f}"
              f"{pass_pow_k(n, c, args.k):>9.2f}")


if __name__ == "__main__":
    main()
