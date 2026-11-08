"""Draw the README diagrams as SVG, one light and one dark version of each.

    python tools/readme_art.py

Writes assets/readme/<name>-light.svg and <name>-dark.svg. The README picks the
right one with <picture> and prefers-color-scheme, so the diagrams match GitHub's
theme. Every diagram also has a plain-text version in the README.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "assets" / "readme"
FONT = "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "Menlo, Consolas, 'Liberation Mono', 'Courier New', monospace"

THEMES = {
    "light": dict(bg="#f6f8fa", card="#ffffff", border="#d0d7de", ink="#1f2328", muted="#59636e", faint="#8c959f",
                  grid="#e6eaef", accent="#d4ff3f", accent_ink="#0b1324", accent_text="#4d7c0f", line="#8c959f",
                  ring="#c4cdd8", good="#1a7f37", good_bg="#dafbe1", bad="#cf222e", bad_bg="#ffebe9",
                  term_bg="#0b1324", term_ink="#e6ecf7", term_muted="#8fa0bf"),
    "dark": dict(bg="#0b1324", card="#121c33", border="#2a3a5c", ink="#f0f3f8", muted="#a9b6cf", faint="#6f7f9c",
                 grid="#16213a", accent="#d4ff3f", accent_ink="#0b1324", accent_text="#d4ff3f", line="#5c6f94",
                 ring="#2f4470", good="#3fb950", good_bg="#0f2a1c", bad="#ff7b72", bad_bg="#341a1e",
                 term_bg="#050a14", term_ink="#e6ecf7", term_muted="#8fa0bf"),
}


def svg(w: int, h: int, t: dict, body: str, title: str, desc: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-labelledby="t d"><title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{t["line"]}"/></marker>'
            '<marker id="arrow-acc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{t["accent_text"]}"/></marker>'
            '<marker id="arrow-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{t["bad"]}"/></marker>'
            '<marker id="arrow-good" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{t["good"]}"/></marker></defs>'
            f'<rect width="{w}" height="{h}" rx="18" fill="{t["bg"]}"/>'
            f'<g font-family="{FONT}">{body}</g></svg>')


def text(x, y, s, size=16, fill="#000", weight=400, anchor="start", spacing=0, family=None):
    fam = f' font-family="{family}"' if family else ""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{ls}{fam}>{escape(s)}</text>')


def box(x, y, w, h, t, fill=None, stroke=None, r=14, sw=1.5, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill or t["card"]}" '
            f'stroke="{stroke or t["border"]}" stroke-width="{sw}"{d}/>')


def pill(x, y, s, t, size=13, fill=None, ink=None, pad=12, h=26, anchor="start", weight=700, char=0.62):
    w = int(len(s) * size * char) + pad * 2
    if anchor == "end":
        x -= w
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h // 2}" fill="{fill or t["accent"]}"/>'
            + text(x + w / 2, y + h / 2 + size * 0.36, s, size, ink or t["accent_ink"], weight, "middle"))


def arrow(x1, y1, x2, y2, t, kind="", dash=""):
    color = {"": t["line"], "acc": t["accent_text"], "bad": t["bad"], "good": t["good"]}[kind]
    mid = f"arrow-{kind}" if kind else "arrow"
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"{d} '
            f'marker-end="url(#{mid})"/>')


def path(d, t, kind="", dash=""):
    color = {"": t["line"], "acc": t["accent_text"], "bad": t["bad"], "good": t["good"]}[kind]
    mid = f"arrow-{kind}" if kind else "arrow"
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2"{ds} marker-end="url(#{mid})"/>'


def ring(cx, cy, t, scale=1.0, labels=True, dots_on=True):
    r1, r2, r3 = 172 * scale, 112 * scale, 52 * scale
    parts = [("GUIDANCE", 0, -184), ("CAPABILITY", 168, -150), ("BOUNDARIES", 236, 5), ("CONTINUITY", 168, 160),
             ("CHECKING", 0, 198), ("VISIBILITY", -168, 160), ("CORRECTION", -238, 5), ("CONTROL FLOW", -176, -150)]
    dots = [(0, -1), (0.707, -0.707), (1, 0), (0.707, 0.707), (0, 1), (-0.707, 0.707), (-1, 0), (-0.707, -0.707)]
    out = [f'<g transform="translate({cx} {cy})" text-anchor="middle">',
           f'<circle r="{r1 + 18}" fill="{t["accent"]}" opacity="0.07"/>',
           f'<circle r="{r1}" fill="none" stroke="{t["ring"]}" stroke-width="2"/>',
           f'<circle r="{r2}" fill="none" stroke="{t["accent_text"]}" stroke-width="2" stroke-dasharray="6 6"/>',
           f'<circle r="{r3}" fill="{t["accent"]}"/>',
           text(0, 7 * scale, "MODEL", 18 * scale, t["accent_ink"], 800, "middle"),
           text(0, -(r2 + 10), "AGENT LOOP", 13 * scale, t["accent_text"], 700, "middle", 2)]
    if labels:
        out += [text(x * scale, y * scale, s, 13 * scale, t["ink"], 650, "middle", 1) for s, x, y in parts]
    if dots_on:
        out += [f'<circle cx="{dx * r1:.1f}" cy="{dy * r1:.1f}" r="4.5" fill="{t["accent_text"]}"/>' for dx, dy in dots]
    out.append("</g>")
    return "".join(out)


def banner(t: dict) -> str:
    w, h = 1280, 420
    grid = "".join(f'<path d="M{x} 0V{h}" stroke="{t["grid"]}"/>' for x in range(32, w, 32)) + \
        "".join(f'<path d="M0 {y}H{w}" stroke="{t["grid"]}"/>' for y in range(32, h, 32))
    body = [f'<g opacity="0.9">{grid}</g>',
            text(64, 104, "FREE COURSE  ·  OPEN SOURCE  ·  2026 EDITION", 16, t["accent_text"], 750, spacing=3),
            text(60, 182, "Harness", 76, t["ink"], 850),
            text(60, 262, "Engineering", 76, t["ink"], 850),
            text(64, 312, "Build the system around an AI agent so it does", 23, t["muted"]),
            text(64, 342, "real work reliably, safely and visibly.", 23, t["muted"])]
    x = 64
    for s in ["18 lessons", "11 tested projects", "12 videos", "runs offline"]:
        wpx = int(len(s) * 8.6) + 30
        body.append(box(x, 362, wpx, 34, t, t["card"], t["border"], 17))
        body.append(text(x + wpx / 2, 384, s, 15, t["ink"], 600, "middle"))
        x += wpx + 10
    body.append(ring(960, 214, t))
    return svg(w, h, t, "".join(body), "Harness Engineering: the free, complete course",
               "A model at the center, wrapped by the agent loop and eight harness parts: guidance, capability, "
               "boundaries, continuity, checking, visibility, correction and control flow.")


PARTS = [("Guidance", "What the agent is told:", "instructions, AGENTS.md, context", "Lessons 4, 5"),
         ("Capability", "What it can do:", "tools, MCP servers, skills", "Lesson 6"),
         ("Boundaries", "Where it runs, what it may touch:", "sandbox, permissions, secrets", "Lesson 7"),
         ("Continuity", "What survives a session:", "state, memory, progress files", "Lesson 8"),
         ("Checking", "How its work is judged:", "guardrails, tests, evals", "Lesson 9"),
         ("Visibility", "What gets recorded:", "logs, traces, cost, metrics", "Lesson 10"),
         ("Correction", "How a mistake becomes a rule:", "feedback, verification, steering", "Lesson 11"),
         ("Control flow", "When it goes on or stops:", "loops, graphs, human approval", "Lessons 12, 13")]


def harness_map(t: dict) -> str:
    w, h = 1280, 620
    cx, cy = 640, 310
    body = [ring(cx, cy, t, 0.95, labels=False, dots_on=False),
            text(cx, cy + 196, "THE HARNESS", 13, t["muted"], 700, "middle", 2)]
    cw, ch, gap = 372, 122, 26
    y0 = (h - (4 * ch + 3 * gap)) // 2
    for i, (name, l1, l2, lesson) in enumerate(PARTS):
        left = i in (0, 7, 6, 5)
        order = {0: 0, 7: 1, 6: 2, 5: 3, 1: 0, 2: 1, 3: 2, 4: 3}[i]
        x = 36 if left else w - 36 - cw
        y = y0 + order * (ch + gap)
        body.append(box(x, y, cw, ch, t))
        body.append(f'<rect x="{x}" y="{y + 18}" width="5" height="{ch - 36}" rx="2.5" fill="{t["accent_text"]}"/>')
        body.append(text(x + 26, y + 40, name, 22, t["ink"], 750))
        body.append(pill(x + cw - 16, y + 18, lesson, t, 12, t["bg"], t["muted"], 10, 24, "end", 650, 0.6))
        body.append(text(x + 26, y + 72, l1, 16, t["muted"]))
        body.append(text(x + 26, y + 96, l2, 16, t["ink"], 550))
        # connector to the outer ring
        import math
        ang = {0: -112.5, 7: -157.5, 6: 157.5, 5: 112.5, 1: -67.5, 2: -22.5, 3: 22.5, 4: 67.5}[i]
        rx, ry = cx + 164 * math.cos(math.radians(ang)), cy + 164 * math.sin(math.radians(ang))
        ex = x + cw if left else x
        body.append(f'<path d="M{ex} {y + ch / 2} L{rx:.1f} {ry:.1f}" stroke="{t["ring"]}" stroke-width="1.5" '
                    'stroke-dasharray="3 5" fill="none"/>')
        body.append(f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="5" fill="{t["accent_text"]}"/>')
    return svg(w, h, t, "".join(body), "Agent = Model + Harness: the eight parts of a harness",
               "The model sits inside the agent loop. Around it, eight harness parts: guidance, capability, "
               "boundaries, continuity, checking, visibility, correction and control flow, each with its lesson.")


def request_path(t: dict) -> str:
    w, h = 1280, 470
    y, bh = 150, 96
    nodes = [(36, 150, "Task", "a ticket or request"), (226, 190, "Context", "instructions, files, history"),
             (456, 150, "Model", "decides the next step"), (646, 190, "Permission check", "is this call allowed?"),
             (876, 168, "Sandbox", "runs the tool call"), (1084, 160, "Trace", "records what happened")]
    body = [text(36, 52, "EVERY ACTION GOES THROUGH THE HARNESS", 14, t["accent_text"], 750, spacing=2),
            text(36, 84, "The model only proposes. The harness decides, runs, records and checks.", 20, t["ink"], 600)]
    for i, (x, bw, title, sub) in enumerate(nodes):
        is_model = title == "Model"
        body.append(box(x, y, bw, bh, t, t["accent"] if is_model else t["card"],
                        t["accent"] if is_model else t["border"]))
        body.append(text(x + bw / 2, y + 42, title, 19, t["accent_ink"] if is_model else t["ink"], 750, "middle"))
        body.append(text(x + bw / 2, y + 68, sub, 13.5, t["accent_ink"] if is_model else t["muted"], 500, "middle"))
        if i < len(nodes) - 1:
            nx = nodes[i + 1][0]
            body.append(arrow(x + bw + 4, y + bh / 2, nx - 6, y + bh / 2, t))
    # result goes back to the model, over the top
    body.append(path(f"M1164 {y - 4} C1164 110, 531 110, 531 {y - 6}", t, "acc", "6 5"))
    body.append(text(848, 112, "the result goes back into the model's context", 14, t["accent_text"], 650, "middle"))
    # done -> verification
    vy = 330
    body.append(arrow(531, y + bh + 4, 531, vy - 6, t))
    body.append(text(543, 300, "agent says done", 13, t["faint"], 600))
    body.append(box(416, vy, 230, 92, t, t["card"], t["accent_text"], 14, 2))
    body.append(text(531, vy + 40, "Verification", 19, t["ink"], 750, "middle"))
    body.append(text(531, vy + 66, "tests and checks it cannot skip", 13.5, t["muted"], 500, "middle"))
    body.append(arrow(650, vy + 46, 796, vy + 46, t, "good"))
    body.append(text(723, vy + 36, "pass", 13, t["good"], 700, "middle"))
    body.append(box(800, vy + 8, 210, 76, t, t["good_bg"], t["good"], 14, 1.5))
    body.append(text(905, vy + 42, "Work accepted", 18, t["good"], 750, "middle"))
    body.append(text(905, vy + 64, "with evidence attached", 13, t["muted"], 500, "middle"))
    body.append(path(f"M412 {vy + 46} C300 {vy + 46}, 300 {y + bh / 2}, 452 {y + bh / 2 + 22}", t, "bad", "6 5"))
    body.append(text(250, vy + 30, "fail: the exact", 13, t["bad"], 650, "middle"))
    body.append(text(250, vy + 48, "failure goes back", 13, t["bad"], 650, "middle"))
    return svg(w, h, t, "".join(body), "How a request passes through an agent harness",
               "A task becomes context for the model. The model proposes a tool call; the harness checks permissions, "
               "runs it in a sandbox, records it in a trace and returns the result. When the agent says it is done, "
               "verification either accepts the work or sends the failure back.")


WITHOUT = [("Writes the date logic with .date()", "Nothing told it about the time-zone helper"),
           ("Edits config/settings.toml", "Nothing stopped it touching shared config"),
           ("Runs its own tests, and they pass", "It wrote them, so they share its blind spot"),
           ("Reports that the work is done", "You take its word for it"),
           ("A week later", "Users in Tokyo lose their streaks")]
WITH = [("A lint rule flags .date() after the edit", "The message names the helper to use"),
        ("The path guard blocks the config edit", "config/* is protected, so the write fails"),
        ("Hidden acceptance tests run", "One fails: the current week breaks the streak"),
        ("The agent fixes it from the failure report", "Verification passes on the next try"),
        ("Every step is in the trace", "You review a diff, not a mystery")]


def without_with(t: dict) -> str:
    w, h = 1280, 600
    body = [text(640, 52, "SAME MODEL, SAME TASK: ADD A WEEKLY STREAK TO A HABIT TRACKER", 14, t["accent_text"],
                 750, "middle", 2)]
    for col, (title, rows, good, result) in enumerate([
            ("Without a harness", WITHOUT, False, "You clean up after the agent"),
            ("With a harness", WITH, True, "You review work that is already verified")]):
        x = 36 + col * 616
        pw = 592
        color, bg = (t["good"], t["good_bg"]) if good else (t["bad"], t["bad_bg"])
        body.append(box(x, 80, pw, 494, t))
        body.append(f'<rect x="{x}" y="80" width="{pw}" height="58" rx="14" fill="{bg}"/>'
                    f'<rect x="{x}" y="124" width="{pw}" height="14" fill="{bg}"/>')
        body.append(text(x + 28, 117, title, 22, color, 800))
        for i, (a, b) in enumerate(rows):
            yy = 172 + i * 72
            body.append(f'<circle cx="{x + 44}" cy="{yy + 12}" r="15" fill="{bg}" stroke="{color}" stroke-width="1.5"/>')
            mark = (f'<path d="M{x + 37} {yy + 12} l5 5 l9 -10" stroke="{color}" stroke-width="2.5" fill="none" '
                    'stroke-linecap="round" stroke-linejoin="round"/>') if good else \
                (f'<path d="M{x + 38} {yy + 6} l12 12 M{x + 50} {yy + 6} l-12 12" stroke="{color}" '
                 'stroke-width="2.5" stroke-linecap="round"/>')
            body.append(mark)
            body.append(text(x + 76, yy + 10, a, 17, t["ink"], 650))
            body.append(text(x + 76, yy + 34, b, 15, t["muted"]))
            if i < len(rows) - 1:
                body.append(f'<path d="M{x + 44} {yy + 30} V{yy + 56}" stroke="{t["border"]}" stroke-width="2"/>')
        body.append(f'<path d="M{x + 24} 520 H{x + pw - 24}" stroke="{t["border"]}"/>')
        body.append(text(x + 28, 553, "Result: " + result, 17, color, 700))
    return svg(w, h, t, "".join(body), "The same agent with and without a harness",
               "Without a harness the agent uses the UTC date, edits shared config, passes its own tests and ships a "
               "time-zone bug. With a harness a lint rule, a path guard and hidden acceptance tests catch each mistake.")


PATH = [("PART 1", "Foundations", ["1  What harness engineering is", "2  How an AI agent works",
                                   "3  Prompt to harness engineering"], ["Demo", "Project 1"]),
        ("PART 2", "Guidance", ["4  Instructions and AGENTS.md", "5  Context engineering"], ["AGENTS.md template"]),
        ("PART 3", "Capability", ["6  Tools, MCP and Agent Skills"], ["Project 2"]),
        ("PART 4", "Boundaries", ["7  Sandboxes, permissions, security"], ["Project 3"]),
        ("PART 5", "Continuity", ["8  State, memory, long-running work"], ["Project 4"]),
        ("PART 6", "Checking and visibility", ["9  Guardrails, tests and evals", "10  Logs, traces, observability"],
         ["Project 8", "Project 7"]),
        ("PART 7", "Correction", ["11  Feedback and the steering loop"], ["Project 6"]),
        ("PART 8", "Control flow", ["12  Loop engineering", "13  Graphs and multi-agent systems"],
         ["Project 5", "Project 9"]),
        ("PART 9", "Putting it together", ["14  Build a complete harness", "15  Diagnosing agent failures",
                                           "16  Harness engineering in production", "17  Harnesses beyond coding",
                                           "18  Case studies from real teams"], ["Capstone", "Project 11"])]


def learning_path(t: dict) -> str:
    w, h = 1280, 960
    cw, ch = 372, 272
    xs, ys = [36, 454, 872], [36, 344, 652]
    slots = [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (2, 2)]
    body = []
    for i, (label, name, lessons, practice) in enumerate(PATH):
        r, c = slots[i]
        x, y = xs[c], ys[r]
        final = i == 8
        body.append(box(x, y, cw, ch, t, t["card"], t["accent_text"] if final else t["border"], 16, 2 if final else 1.5))
        body.append(text(x + 24, y + 36, label, 13, t["accent_text"], 750, spacing=2))
        body.append(text(x + 24, y + 66, name, 22, t["ink"], 780))
        for j, ls in enumerate(lessons):
            num, title = ls.split("  ", 1)
            body.append(text(x + 24, y + 100 + j * 25, num, 15, t["faint"], 700))
            body.append(text(x + 56, y + 100 + j * 25, title, 15, t["ink"], 500))
        px = x + 24
        for p in practice:
            pw = int(len(p) * 7.4) + 24
            body.append(f'<rect x="{px}" y="{y + ch - 46}" width="{pw}" height="28" rx="14" fill="{t["accent"]}"/>')
            body.append(text(px + pw / 2, y + ch - 27, p, 13, t["accent_ink"], 700, "middle"))
            px += pw + 8
    # arrows: 1>2>3 v 4<5<6 v 7>8>9
    mid = lambda r: ys[r] + ch / 2  # noqa: E731
    body += [arrow(xs[0] + cw + 6, mid(0), xs[1] - 8, mid(0), t, "acc"), arrow(xs[1] + cw + 6, mid(0), xs[2] - 8, mid(0), t, "acc"),
             arrow(xs[2] + cw / 2, ys[0] + ch + 6, xs[2] + cw / 2, ys[1] - 8, t, "acc"),
             arrow(xs[2] - 6, mid(1), xs[1] + cw + 8, mid(1), t, "acc"), arrow(xs[1] - 6, mid(1), xs[0] + cw + 8, mid(1), t, "acc"),
             arrow(xs[0] + cw / 2, ys[1] + ch + 6, xs[0] + cw / 2, ys[2] - 8, t, "acc"),
             arrow(xs[0] + cw + 6, mid(2), xs[1] - 8, mid(2), t, "acc"), arrow(xs[1] + cw + 6, mid(2), xs[2] - 8, mid(2), t, "acc")]
    return svg(w, h, t, "".join(body), "Learning path: 18 lessons in nine parts",
               "Nine parts from foundations to production, each with its lessons and the project that practises them.")


DEMO = [("$ python -m harnesslab demo", "cmd", None),
        ("agent: Adding weekly_streak next to daily_streak.", "", None),
        ("tool edit_file ok: Edited habit_tracker/streaks.py", "", None),
        ("agent: The lint rule says .date() gives the UTC day. I'll read the time helpers.", "", "SENSOR"),
        ("agent: I'll also add a feature flag so the team can turn weekly streaks off.", "", None),
        ("tool edit_file ERROR: 'config/settings.toml' is protected (matches config/*)", "bad", "BOUNDARY"),
        ("blocked (deny): destructive deletes are not allowed", "bad", "PERMISSION"),
        ("tool run_tests ok: All tests passed (10 passed in 0.01s).", "", None),
        ("agent: Done. Changed habit_tracker/streaks.py and added tests. All tests pass.", "", None),
        ("verify: FAIL acceptance + held-out tests: 1 failed, 4 passed", "bad", "VERIFICATION"),
        ("agent: Verification shows an unfinished current week breaks my streak. Fixing...", "", None),
        ("verify: PASS", "good", None),
        ("[succeeded] verification passed", "good", None)]


def demo(t: dict) -> str:
    w, h = 1280, 560
    body = [f'<rect x="24" y="24" width="{w - 48}" height="{h - 48}" rx="14" fill="{t["term_bg"]}" '
            f'stroke="{t["border"]}"/>',
            '<circle cx="54" cy="54" r="7" fill="#ff5f57"/><circle cx="78" cy="54" r="7" fill="#febc2e"/>'
            '<circle cx="102" cy="54" r="7" fill="#28c840"/>',
            text(640, 59, "harnesslab demo: a scripted agent inside the full harness, no API key", 14,
                 t["term_muted"], 600, "middle")]
    colors = {"": "#e6ecf7", "cmd": "#d4ff3f", "bad": "#ff8a80", "good": "#7ee787"}
    for i, (line, kind, tag) in enumerate(DEMO):
        y = 106 + i * 32
        body.append(f'<text x="56" y="{y}" font-size="16" fill="{colors[kind]}" font-family="{MONO}" '
                    f'style="font-variant-ligatures:none" xml:space="preserve">{escape(line)}</text>')
        if tag:
            body.append(pill(1224, y - 19, tag, t, 12, "#d4ff3f", "#0b1324", 10, 26, "end", 800, 0.66))
    return svg(w, h, t, "".join(body), "harnesslab demo output",
               "The scripted agent makes four realistic mistakes. A lint sensor, a protected path, a deny rule and "
               "hidden acceptance tests catch them, and the run ends only when verification passes.")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("banner", banner), ("harness-map", harness_map), ("request-path", request_path),
                     ("without-with", without_with), ("learning-path", learning_path), ("demo", demo)]:
        for theme, t in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(fn(t), encoding="utf-8")
    print("wrote", len(list(OUT.glob("*.svg"))), "files to", OUT)


if __name__ == "__main__":
    main()
