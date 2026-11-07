"""Generate each project's exercise/ folder from its solution/ folder.

In a solution file, wrap the part learners should write like this:

    def decide(...):
        # TODO: check deny rules first, then ask, then allow
        # BEGIN SOLUTION
        ...
        # END SOLUTION

The exercise copy keeps the TODO comment and replaces the block with
`raise NotImplementedError(...)`. Run from the repo root:

    python tools/make_exercises.py
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCK = re.compile(r"^(?P<indent>[ \t]*)# BEGIN SOLUTION\n.*?^[ \t]*# END SOLUTION\n", re.S | re.M)


def strip(text: str) -> str:
    return BLOCK.sub(lambda m: f'{m["indent"]}raise NotImplementedError("Your code here: see the TODO above")\n', text)


def main() -> None:
    for solution in sorted(ROOT.glob("projects/*/solution")):
        exercise = solution.parent / "exercise"
        if exercise.exists():
            shutil.rmtree(exercise)
        for src in solution.rglob("*"):
            if "__pycache__" in src.parts or src.name == "ANSWERS.md":
                continue
            dst = exercise / src.relative_to(solution)
            if src.is_dir():
                dst.mkdir(parents=True, exist_ok=True)
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.suffix == ".py":
                dst.write_text(strip(src.read_text()))
            else:
                shutil.copy(src, dst)
        print(f"wrote {exercise.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
