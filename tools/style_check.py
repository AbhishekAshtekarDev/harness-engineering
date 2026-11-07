"""Check Markdown prose for the patterns this course avoids.

    python tools/style_check.py            # all .md files
    python tools/style_check.py course/    # one folder

Skips fenced code, inline code, link targets and HTML tags. Reports
em dashes, contractions, exclamation marks, filler adverbs and stock phrases.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Technical terms and titles of other people's work that contain flagged words.
ALLOW = ("just-in-time", "Just-in-time", "just in time", "Oh My!", "Don't Build Multi-Agents",
         "What's your current AI agentic setup?")
CHECKS = [
    ("em dash", re.compile(r"—|–| -- ")),
    ("contraction", re.compile(r"\b(?:\w+n't|\w+'re|\w+'ve|\w+'ll|\w+'d|I'm|it's|that's|there's|here's|what's|"
                               r"let's|who's|he's|she's|you're|we're|they're)\b", re.I)),
    ("exclamation", re.compile(r"(?<![\[!<])!(?![\[=(])")),
    ("filler adverb", re.compile(r"\b(really|just|simply|actually|truly|fundamentally|genuinely|honestly|"
                                 r"literally|importantly|crucially|basically|essentially|incredibly|deeply)\b", re.I)),
    ("stock phrase", re.compile(r"let's dive|dive in|deep dive|unpack|at its core|landscape|game[- ]changer|"
                                r"secret sauce|superpower|it turns out|the truth is|the reality is|in today's|"
                                r"here's (what|why|the)|it is important to note|it's worth noting|when it comes to|"
                                r"at the end of the day|in a world where|navigate|leverage|seamless|robust|"
                                r"delve|tapestry|unlock|empower|elevate", re.I)),
]


def prose_lines(text: str):
    in_code = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        clean = re.sub(r"`[^`]*`", "", line)
        clean = re.sub(r"\]\([^)]*\)", "]", clean)
        clean = re.sub(r"<[^>]+>", "", clean)
        clean = re.sub(r"https?://\S+", "", clean)
        for allowed in ALLOW:
            clean = clean.replace(allowed, "")
        yield n, clean


def main() -> int:
    targets = [ROOT / a for a in sys.argv[1:]] or [ROOT]
    files = [f for t in targets for f in ([t] if t.is_file() else t.rglob("*.md"))
             if "node_modules" not in f.parts and "site" not in f.parts]
    problems = 0
    for f in sorted(files):
        for n, line in prose_lines(f.read_text()):
            for name, rx in CHECKS:
                for m in rx.finditer(line):
                    problems += 1
                    print(f"{f.relative_to(ROOT)}:{n}: {name}: '{m.group(0)}'  | {line.strip()[:90]}")
    print(f"\n{problems} issue(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
