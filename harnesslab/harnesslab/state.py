"""State that outlives a session: task records, a progress log, a feature list.

The model is stateless between calls. Anything the next session needs must be
written somewhere durable. Three records cover most long-running work:

    TaskState    the harness's own bookkeeping (status, attempts, usage, why it stopped)
    ProgressLog  a plain-text log each session appends to before it ends
    FeatureList  a JSON list of required behaviors; sessions may change only `passes`

The FeatureList guard follows Anthropic's long-running harness: the list is
JSON (models rewrite JSON less freely than Markdown) and an update may flip a
feature's `passes` flag but may not add, delete or reword features.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class TaskState:
    task_id: str
    status: str = "pending"          # pending | running | succeeded | stopped | escalated
    iterations: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = ""
    plan: list[str] = field(default_factory=list)
    updated_at: float = field(default_factory=time.time)

    def save(self, folder: str | Path) -> Path:
        path = Path(folder) / f"{self.task_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = time.time()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(self), indent=2))
        tmp.replace(path)  # atomic on the same filesystem: no half-written state after a crash
        return path

    @classmethod
    def load(cls, folder: str | Path, task_id: str) -> "TaskState":
        path = Path(folder) / f"{task_id}.json"
        return cls(**json.loads(path.read_text())) if path.exists() else cls(task_id)


class ProgressLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, session: str, done: str, next_step: str, notes: str = "") -> None:
        entry = f"\n## {session} ({time.strftime('%Y-%m-%d %H:%M')})\n- Done: {done}\n- Next: {next_step}\n"
        if notes:
            entry += f"- Notes: {notes}\n"
        with self.path.open("a") as f:
            f.write(entry)

    def read(self) -> str:
        return self.path.read_text() if self.path.exists() else "(no progress recorded yet)"


class FeatureListError(ValueError):
    pass


class FeatureList:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def create(self, descriptions: list[str]) -> None:
        if self.path.exists():
            raise FeatureListError("feature list already exists; the initializer runs once")
        items = [{"id": f"F{i + 1:03d}", "description": d, "passes": False} for i, d in enumerate(descriptions)]
        self.path.write_text(json.dumps(items, indent=2))

    def items(self) -> list[dict]:
        return json.loads(self.path.read_text())

    def next_unfinished(self) -> dict | None:
        return next((f for f in self.items() if not f["passes"]), None)

    def mark(self, feature_id: str, passes: bool, verified: bool) -> None:
        """Flip one feature's status. Refuses to mark passing without verification."""
        if passes and not verified:
            raise FeatureListError(f"{feature_id} cannot be marked passing before a check confirms it")
        items = self.items()
        for f in items:
            if f["id"] == feature_id:
                f["passes"] = passes
                self.path.write_text(json.dumps(items, indent=2))
                return
        raise FeatureListError(f"unknown feature {feature_id}")

    def guard_rewrite(self, proposed_json: str) -> None:
        """Reject an agent-written replacement that changes anything except `passes`."""
        old, new = self.items(), json.loads(proposed_json)
        strip = lambda xs: [{k: v for k, v in x.items() if k != "passes"} for x in xs]
        if strip(old) != strip(new):
            raise FeatureListError("only the 'passes' field may change; features cannot be added, removed or edited")
