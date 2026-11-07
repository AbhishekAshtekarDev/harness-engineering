"""Tracing: a record of every step, detailed enough to explain any decision.

A trace is a tree of spans. Each span has a name, start and end times,
attributes and a parent. One run of the agent is one trace: a root span for the
task, a span per loop iteration, and inside it spans for the model call, each
tool call, each check.

Attribute names follow the OpenTelemetry GenAI semantic conventions where one
exists (gen_ai.request.model, gen_ai.usage.input_tokens, gen_ai.tool.name...).
Those conventions are still marked as in development, so names can change.
The tracer writes JSON Lines, one span per line, so you can grep it, load it
in a notebook, or convert it for a tracing backend.
"""
from __future__ import annotations

import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator


@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_id: str | None
    start: float
    end: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"

    def set(self, **attrs: Any) -> None:
        self.attributes.update(attrs)

    def to_dict(self) -> dict:
        return {"name": self.name, "trace_id": self.trace_id, "span_id": self.span_id,
                "parent_id": self.parent_id, "start": self.start, "end": self.end,
                "duration_ms": round(((self.end or self.start) - self.start) * 1000, 2),
                "status": self.status, "attributes": self.attributes}


class Tracer:
    def __init__(self, path: str | Path | None = None):
        self.trace_id = uuid.uuid4().hex[:16]
        self.spans: list[Span] = []
        self._stack: list[Span] = []
        self.path = Path(path) if path else None

    @contextmanager
    def span(self, name: str, **attrs: Any) -> Iterator[Span]:
        parent = self._stack[-1].span_id if self._stack else None
        s = Span(name, self.trace_id, uuid.uuid4().hex[:8], parent, time.time(), attributes=dict(attrs))
        self.spans.append(s)
        self._stack.append(s)
        try:
            yield s
        except Exception as exc:
            s.status = "error"
            s.set(error=f"{type(exc).__name__}: {exc}")
            raise
        finally:
            s.end = time.time()
            self._stack.pop()
            if self.path:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a") as f:
                    f.write(json.dumps(s.to_dict(), default=str) + "\n")

    def event(self, name: str, **attrs: Any) -> None:
        """A zero-length span, for things like a blocked call or a budget warning."""
        with self.span(name, **attrs):
            pass


def load(path: str | Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def waterfall(spans: list[dict] | list[Span], width: int = 40, max_label: int = 58) -> str:
    """Render spans as a text waterfall: indentation shows nesting, bars show timing."""
    rows = [s.to_dict() if isinstance(s, Span) else s for s in spans]
    if not rows:
        return "(empty trace)"
    t0 = min(r["start"] for r in rows)
    t1 = max((r["end"] or r["start"]) for r in rows)
    total = max(t1 - t0, 1e-6)
    by_parent: dict[str | None, list[dict]] = {}
    for r in sorted(rows, key=lambda r: r["start"]):
        by_parent.setdefault(r["parent_id"], []).append(r)
    ids = {r["span_id"] for r in rows}
    roots = [r for r in rows if r["parent_id"] not in ids]
    lines: list[str] = []

    def label(r: dict) -> str:
        a = r["attributes"]
        extra = a.get("gen_ai.tool.name") or a.get("summary") or ""
        mark = " !" if r["status"] != "ok" or a.get("blocked") or a.get("is_error") else ""
        return f"{r['name']}{(' ' + str(extra)) if extra else ''}{mark}"

    def walk(r: dict, depth: int) -> None:
        start = int((r["start"] - t0) / total * width)
        length = max(1, int(((r["end"] or r["start"]) - r["start"]) / total * width))
        bar = " " * start + "#" * min(length, width - start)
        text = ("  " * depth + label(r))[:max_label]
        lines.append(f"{text:<{max_label}} |{bar:<{width}}| {r['duration_ms']:>8.1f} ms")
        for child in by_parent.get(r["span_id"], []):
            walk(child, depth + 1)

    for root in sorted(roots, key=lambda r: r["start"]):
        walk(root, 0)
    return "\n".join(lines)
