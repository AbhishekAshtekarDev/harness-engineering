"""Build the course videos as HyperFrames projects.

    ~/.cache/hyperframes/py/bin/python make.py [video ids...]

For each video: Kokoro narration line by line (the voice is the clock), then a
single-composition index.html whose reveals land on the line that names them.
Render each project with `npx hyperframes render`.
"""
from __future__ import annotations

import html
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

from specs import REPO, VIDEOS

HERE = Path(__file__).resolve().parent
OUT = HERE / "projects"
PROMO = Path(os.environ.get("PROMO_ASSETS", HERE.parents[3] / "Videos/harness-blueprint-promo/assets"))
SAY = {"evals": "ee-vals", "JSON": "jason", "know how": "know-how"}
LEAD, TAIL, GAP, SPEED, VOICE = 0.55, 0.65, 0.34, 1.02, "af_heart"
W, H = 1920, 1080


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------- voice
def make_voice(video: dict, assets: Path) -> dict:
    from kokoro_onnx import EspeakConfig, Kokoro
    import espeakng_loader
    c = os.path.expanduser("~/.cache/hyperframes/tts")
    k = Kokoro(f"{c}/models/kokoro-v1.0.onnx", f"{c}/voices/voices-v1.0.bin",
               espeak_config=EspeakConfig(lib_path=espeakng_loader.get_library_path(), data_path=f"{c}/espeak-ng-data"))

    def trim(x, sr):
        idx = np.where(np.abs(x) > 0.012)[0]
        if len(idx) == 0:
            return x
        a, b = max(0, idx[0] - int(0.02 * sr)), min(len(x), idx[-1] + int(0.06 * sr))
        y = x[a:b].copy()
        f = int(0.008 * sr)
        y[:f] *= np.linspace(0, 1, f)
        y[-f:] *= np.linspace(1, 0, f)
        return y

    t, sr, clips, scenes = 0.0, 24000, [], []
    for n, sc in enumerate(video["scenes"]):
        start = t
        t += LEAD if n else 0.8
        cues = []
        for i, line in enumerate(sc["lines"]):
            spoken = line
            for a, b in SAY.items():
                spoken = spoken.replace(a, b)
            x, sr = k.create(spoken, voice=VOICE, speed=SPEED, lang="en-us")
            x = trim(np.asarray(x, dtype=np.float32), sr)
            cues.append({"t": round(t, 3), "d": round(len(x) / sr, 3)})
            clips.append((t, x))
            t += len(x) / sr + (GAP if i < len(sc["lines"]) - 1 else 0)
        t += TAIL if n < len(video["scenes"]) - 1 else 1.6
        scenes.append({"start": round(start, 3), "dur": round(t - start, 3), "cues": cues})
    total = round(t, 3)
    out = np.zeros(int(np.ceil(total * sr)) + sr, dtype=np.float32)
    for st, x in clips:
        i = int(round(st * sr))
        out[i:i + len(x)] += x
    peak = float(np.max(np.abs(out))) or 1.0
    out = out / peak * 0.89  # about -1 dBFS peak
    (assets / "vo").mkdir(parents=True, exist_ok=True)
    sf.write(assets / "vo" / "voice.wav", out[: int(np.ceil(total * sr))], sr)
    return {"total": total, "scenes": scenes}


# --------------------------------------------------------------------------- html
CSS = """
@font-face{font-family:"Inter";src:url("assets/fonts/Inter.woff2") format("woff2");font-weight:100 900;font-display:block}
@font-face{font-family:"JetBrains Mono";src:url("assets/fonts/JetBrainsMono.woff2") format("woff2");font-weight:100 800;font-display:block}
:root{--bg:#0b1324;--card:#111c32;--line:#26375a;--ink:#f2f5fb;--muted:#9fb0cc;--lime:#d4ff3f;--coral:#ff6b5b}
*{box-sizing:border-box;margin:0;padding:0}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Inter",sans-serif;-webkit-font-smoothing:antialiased}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:var(--bg)}
#bgfill{position:absolute;inset:0;background-color:var(--bg);background-image:linear-gradient(#1a2640 1px,transparent 1px),linear-gradient(90deg,#1a2640 1px,transparent 1px);background-size:48px 48px}
#glow{position:absolute;left:960px;top:540px;width:1400px;height:1400px;margin:-700px 0 0 -700px;border-radius:50%;background:radial-gradient(circle,rgba(212,255,63,.10) 0%,rgba(212,255,63,0) 60%)}
.scene{position:absolute;inset:0}
.in{position:absolute;inset:0}
.eb{position:absolute;left:120px;top:96px;font-family:"JetBrains Mono",monospace;font-weight:700;font-size:22px;letter-spacing:.18em;text-transform:uppercase;color:var(--lime)}
.ebt{position:absolute;left:120px;top:136px;font-size:54px;font-weight:800;letter-spacing:-.01em}
.mark{position:absolute;left:120px;bottom:64px;font-family:"JetBrains Mono",monospace;font-size:20px;color:#6f80a0;letter-spacing:.06em}
.term{position:absolute;left:220px;top:260px;width:1480px;background:#0a101e;border:2px solid var(--line);border-radius:18px;overflow:hidden}
.tbar{height:58px;background:#121c31;border-bottom:2px solid var(--line);display:flex;align-items:center;padding:0 24px;gap:12px}
.dot{width:16px;height:16px;border-radius:50%;background:#2c3c5e}
.tname{margin-left:14px;font-family:"JetBrains Mono",monospace;font-size:22px;color:var(--muted)}
.tbody{padding:30px 40px 36px}
.tl{font-family:"JetBrains Mono",monospace;font-size:34px;line-height:1.75;white-space:pre;font-variant-ligatures:none}
.cmd{color:var(--ink)} .ok{color:var(--lime)} .err{color:var(--coral)} .dim{color:var(--muted)}
.node{position:absolute;top:470px;height:190px;border:2px solid var(--line);background:var(--card);border-radius:22px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:0 18px}
.node.hl{border-color:var(--lime);box-shadow:0 0 60px rgba(212,255,63,.18)}
.nl{font-size:40px;font-weight:800}
.node.hl .nl{color:var(--lime)}
.ns{margin-top:12px;font-size:23px;color:var(--muted)}
.arrow{position:absolute;top:565px;height:4px;background:var(--line);transform-origin:left center}
.big{position:absolute;left:160px;right:160px;top:360px;font-size:84px;font-weight:800;line-height:1.12;letter-spacing:-.015em}
.stat{position:absolute;text-align:center}
.sv{font-size:150px;font-weight:900;letter-spacing:-.03em;color:var(--lime);line-height:1}
.stat.bad .sv{color:var(--coral)}
.sl{margin-top:26px;font-size:36px;font-weight:600}
.ss{margin-top:14px;font-family:"JetBrains Mono",monospace;font-size:22px;color:var(--muted)}
.col{position:absolute;top:300px;width:760px;min-height:360px;border:2px solid var(--line);background:var(--card);border-radius:24px;padding:46px 50px}
.ch{font-family:"JetBrains Mono",monospace;font-size:34px;font-weight:700;color:var(--ink);margin-bottom:34px}
.ci{font-size:34px;line-height:1.3;margin:0 0 30px 0;display:flex;gap:20px;align-items:flex-start}
.ci b{font-family:"JetBrains Mono",monospace;color:var(--lime);font-weight:700}
.ci.bad b{color:var(--coral)}
.step{position:absolute;left:300px;height:96px;display:flex;align-items:center;gap:36px}
.sn{width:72px;height:72px;border-radius:50%;background:var(--lime);color:var(--bg);font-weight:900;font-size:34px;display:flex;align-items:center;justify-content:center;flex:none}
.st{font-size:44px;font-weight:700;white-space:pre}
.ring{position:absolute;border-radius:50%;border:3px solid var(--line)}
.ring.hl{border-color:var(--lime)}
.rl{position:absolute;font-family:"JetBrains Mono",monospace;font-weight:700;font-size:26px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);transform:translateX(-50%)}
.rl.hl{color:var(--lime)}
.core{position:absolute;border-radius:50%;background:var(--lime);color:var(--bg);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:34px}
.orb{position:absolute;padding:14px 26px;border-radius:40px;border:2px solid var(--line);background:var(--card);font-size:30px;font-weight:700;transform:translate(-50%,-50%);white-space:nowrap}
.myth{position:absolute;left:220px;font-size:64px;font-weight:800;color:var(--ink)}
.strike{position:absolute;left:-10px;right:-10px;top:52%;height:8px;background:var(--coral);transform-origin:left center}
.blk{position:absolute;left:760px;width:520px;height:110px;border-radius:14px;border:2px solid var(--line);background:var(--card);display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:700}
.blk.hl{border-color:var(--coral);color:var(--coral)}
.win{position:absolute;left:740px;top:250px;width:560px;height:720px;border:3px dashed #3a4f7a;border-radius:20px}
.winl{position:absolute;left:1330px;top:250px;font-family:"JetBrains Mono",monospace;font-size:24px;color:var(--muted);width:420px;line-height:1.5}
.tri{position:absolute;padding:20px 30px;border-radius:18px;border:2px solid var(--line);background:var(--card);font-size:34px;font-weight:800;transform:translate(-50%,-50%);white-space:nowrap}
.tric{position:absolute;left:960px;top:640px;transform:translate(-50%,-50%);font-family:"JetBrains Mono",monospace;font-weight:800;font-size:34px;letter-spacing:.12em;color:var(--coral)}
.idea{position:absolute;left:160px;right:160px;top:330px;font-size:76px;font-weight:800;line-height:1.14;letter-spacing:-.015em}
.rule{position:absolute;left:160px;top:640px;width:220px;height:8px;background:var(--lime)}
.repo{position:absolute;left:160px;top:700px;font-family:"JetBrains Mono",monospace;font-size:30px;color:var(--muted)}
.repo b{color:var(--ink)}
"""


class Builder:
    def __init__(self, video: dict, tl: dict):
        self.v, self.tl = video, tl
        self.html: list[str] = []
        self.js: list[str] = []
        self.sfx: list[tuple[float, str, float]] = []
        self.n = 0

    def uid(self, p: str) -> str:
        self.n += 1
        return f"{p}{self.n}"

    def at(self, si: int, el: dict, default: float = 0.0) -> float:
        cues = self.tl["scenes"][si]["cues"]
        i = min(el.get("at", 0), len(cues) - 1)
        return round(cues[i]["t"] + el.get("d", default), 3)

    def reveal(self, eid: str, t: float, kind: str = "up", sound: str | None = "pop") -> None:
        frm = {"up": "{opacity:0,y:34}", "left": "{opacity:0,x:-40}", "scale": "{opacity:0,scale:.82}",
               "fade": "{opacity:0}"}[kind]
        to = {"up": "{opacity:1,y:0", "left": "{opacity:1,x:0", "scale": "{opacity:1,scale:1",
              "fade": "{opacity:1"}[kind]
        self.js.append(f'tl.fromTo("#{eid}",{frm},{to},duration:.5,ease:"power3.out"}},{t});')
        if sound:
            self.sfx.append((t + 0.03, sound, 0.0))

    def wipe(self, eid: str, t: float, dur: float = 0.55) -> None:
        self.js.append(f'tl.fromTo("#{eid}",{{opacity:0,clipPath:"inset(0% 100% 0% 0%)"}},'
                       f'{{opacity:1,clipPath:"inset(0% 0% 0% 0%)",duration:{dur},ease:"none"}},{t});')

    # ----------------------------------------------------------------- scenes
    def scene(self, si: int, sc: dict) -> None:
        info = self.tl["scenes"][si]
        sid = f"s{si}"
        start, dur = info["start"], info["dur"]
        body: list[str] = []
        if sc.get("h"):
            body.append(f'<div class="eb">Lesson {int(self.v["lesson"])} · {esc(self.v["title"])}</div>')
            body.append(f'<div class="ebt" id="{sid}h">{esc(sc["h"])}</div>')
            self.js.append(f'tl.fromTo("#{sid}h",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.5,ease:"power3.out"}},{start + 0.15});')
        getattr(self, "k_" + sc["kind"])(si, sc, body)
        last = si == len(self.v["scenes"]) - 1
        self.html.append(f'<div id="{sid}" class="clip scene" data-start="{start}" data-duration="{dur}" '
                         f'data-track-index="1"><div class="in" id="{sid}in">' + "".join(body) + "</div></div>")
        self.js.append(f'tl.fromTo("#{sid}in",{{opacity:0}},{{opacity:1,duration:.35}},{start});')
        if not last:
            self.js.append(f'tl.to("#{sid}in",{{opacity:0,duration:.3}},{round(start + dur - 0.34, 3)});')
        if si > 0:
            self.sfx.append((start + 0.02, "slide", 0.0))

    def k_terminal(self, si, sc, body):
        rows = []
        for el in sc["items"]:
            eid = self.uid("tl")
            rows.append(f'<div class="tl {el.get("c", "cmd")}" id="{eid}" style="opacity:0">{esc(el["t"])}</div>')
            t = self.at(si, el)
            self.wipe(eid, t, 0.45)
            self.sfx.append((t + 0.02, "err" if el.get("c") == "err" else "key", 0.0))
        tid = self.uid("term")
        body.append(f'<div class="term" id="{tid}"><div class="tbar"><span class="dot"></span><span class="dot"></span>'
                    f'<span class="dot"></span><span class="tname">{esc(sc.get("win", ""))}</span></div>'
                    f'<div class="tbody">{"".join(rows)}</div></div>')
        self.reveal(tid, self.tl["scenes"][si]["start"] + 0.25, "scale", None)

    def k_chain(self, si, sc, body):
        nodes = sc["nodes"]
        n = len(nodes)
        gap = 70
        width = min(330, (1680 - gap * (n - 1)) // n)
        x0 = (W - (n * width + (n - 1) * gap)) // 2
        xs = [x0 + i * (width + gap) for i in range(n)]
        for i, el in enumerate(nodes):
            eid = self.uid("nd")
            sub = f'<div class="ns">{esc(el["s"])}</div>' if el.get("s") else ""
            hl = " hl" if el.get("hl") else ""
            body.append(f'<div class="node{hl}" id="{eid}" style="left:{xs[i]}px;width:{width}px;opacity:0">'
                        f'<div class="nl">{esc(el["l"])}</div>{sub}</div>')
            t = self.at(si, el)
            self.reveal(eid, t, "up")
            if i > 0:
                aid = self.uid("ar")
                body.append(f'<div class="arrow" id="{aid}" style="left:{xs[i - 1] + width + 8}px;width:{gap - 16}px"></div>')
                self.js.append(f'tl.fromTo("#{aid}",{{scaleX:0}},{{scaleX:1,duration:.3,ease:"power2.out"}},{t - 0.2});')
        if sc.get("loop"):
            a, b = sc["loop"]
            x1, x2 = xs[a] + width // 2, xs[b] + width // 2
            lid = self.uid("lp")
            body.append(f'<svg id="{lid}" style="position:absolute;left:0;top:0;width:1920px;height:1080px;opacity:0" '
                        f'viewBox="0 0 1920 1080"><path d="M{x1} 668 C{x1} 840 {x2} 840 {x2} 676" fill="none" '
                        f'stroke="#d4ff3f" stroke-width="5" stroke-dasharray="14 12"/><path d="M{x2 - 14} 694 L{x2} 668 '
                        f'L{x2 + 14} 694" fill="none" stroke="#d4ff3f" stroke-width="5"/></svg>')
            t = max(self.at(si, nodes[a]), self.at(si, nodes[b])) + 0.5
            self.reveal(lid, t, "fade", "pop")

    def k_orbit(self, si, sc, body):
        cx, cy, r = 1060, 600, 300
        cid = self.uid("core")
        body.append(f'<div class="ring" style="left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px"></div>')
        body.append(f'<div class="core" id="{cid}" style="left:{cx - 95}px;top:{cy - 95}px;width:190px;height:190px;opacity:0">'
                    f'{esc(sc["center"])}</div>')
        self.reveal(cid, self.tl["scenes"][si]["start"] + 0.35, "scale", None)
        import math
        for i, el in enumerate(sc["nodes"]):
            ang = -math.pi / 2 + i * 2 * math.pi / len(sc["nodes"])
            x, y = cx + r * math.cos(ang) * 1.32, cy + r * math.sin(ang) * 1.05
            eid = self.uid("ob")
            body.append(f'<div class="orb" id="{eid}" style="left:{x:.0f}px;top:{y:.0f}px;opacity:0">{esc(el["l"])}</div>')
            self.reveal(eid, self.at(si, el), "fade")

    def k_nest(self, si, sc, body):
        cx, cy = 960, 610
        rings = sc["rings"]
        for i, el in enumerate(rings):
            r = 80 + i * 72
            rid, lid = self.uid("rg"), self.uid("rl")
            hl = " hl" if el.get("hl") else ""
            body.append(f'<div class="ring{hl}" id="{rid}" style="left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;'
                        f'height:{2 * r}px;opacity:0"></div>')
            body.append(f'<div class="rl{hl}" id="{lid}" style="left:{cx}px;top:{cy - r - 40 + (0 if i else r + 22)}px;'
                        f'opacity:0">{esc(el["l"])}</div>')
            t = self.at(si, el)
            self.reveal(rid, t, "scale")
            self.reveal(lid, t + 0.1, "fade", None)

    def k_line(self, si, sc, body):
        eid = self.uid("ln")
        body.append(f'<div class="big" id="{eid}" style="opacity:0">{esc(sc["text"])}</div>')
        self.reveal(eid, self.tl["scenes"][si]["cues"][0]["t"] + 0.2, "up", None)

    def k_stat(self, si, sc, body):
        stats = sc["stats"]
        centers = [960] if len(stats) == 1 else [540, 1380]
        half = 760 if len(stats) == 1 else 380
        for c, el in zip(centers, stats):
            eid = self.uid("st")
            bad = " bad" if el.get("bad") else ""
            src = f'<div class="ss">{esc(el["src"])}</div>' if el.get("src") else ""
            body.append(f'<div class="stat{bad}" id="{eid}" style="left:{c - half}px;width:{2 * half}px;top:390px;opacity:0">'
                        f'<div class="sv" style="font-size:{120 if len(el["v"]) > 8 else 150}px">{esc(el["v"])}</div><div class="sl">{esc(el["l"])}</div>{src}</div>')
            self.reveal(eid, self.at(si, el), "scale")

    def k_compare(self, si, sc, body):
        for side, x in (("left", 160), ("right", 1000)):
            col = sc[side]
            items = []
            for el in col["items"]:
                eid = self.uid("ci")
                bad = " bad" if el.get("bad") else ""
                mark = "✗" if el.get("bad") else "✓"
                items.append(f'<div class="ci{bad}" id="{eid}" style="opacity:0"><b>{mark}</b><span>{esc(el["t"])}</span></div>')
                self.reveal(eid, self.at(si, el), "left")
            cid = self.uid("col")
            body.append(f'<div class="col" id="{cid}" style="left:{x}px;opacity:0"><div class="ch">{esc(col["head"])}</div>'
                        + "".join(items) + "</div>")
            first = min(self.at(si, e) for e in col["items"])
            self.reveal(cid, first - 0.45, "up", None)

    def k_steps(self, si, sc, body):
        n = len(sc["items"])
        top = 300 if n <= 4 else 270
        step = 140 if n <= 4 else 124
        for i, el in enumerate(sc["items"]):
            eid = self.uid("sp")
            body.append(f'<div class="step" id="{eid}" style="top:{top + i * step}px;opacity:0"><div class="sn">{i + 1}</div>'
                        f'<div class="st">{esc(el["l"])}</div></div>')
            self.reveal(eid, self.at(si, el), "left")

    def k_myth(self, si, sc, body):
        for i, el in enumerate(sc["items"]):
            eid, sid = self.uid("my"), self.uid("sk")
            body.append(f'<div class="myth" id="{eid}" style="top:{330 + i * 150}px;opacity:0">{esc(el["t"])}'
                        f'<div class="strike" id="{sid}"></div></div>')
            t = self.at(si, el)
            self.reveal(eid, t, "up")
            self.js.append(f'tl.fromTo("#{sid}",{{scaleX:0}},{{scaleX:1,duration:.35,ease:"power2.in"}},'
                           f'{self.tl["scenes"][si]["cues"][-1]["t"] + 0.15 * i});')
            self.sfx.append((self.tl["scenes"][si]["cues"][-1]["t"] + 0.15 * i + 0.3, "err", 0.0))

    def k_stack(self, si, sc, body):
        body.append('<div class="win"></div><div class="winl">context window<br/>(finite)</div>')
        for i, el in enumerate(sc["blocks"]):
            eid = self.uid("bk")
            hl = " hl" if el.get("hl") else ""
            h = 110 if not el.get("hl") else 200
            y = 850 - i * 130 - (h - 110)
            body.append(f'<div class="blk{hl}" id="{eid}" style="top:{y}px;height:{h}px;opacity:0">{esc(el["l"])}</div>')
            self.reveal(eid, self.at(si, el), "up")

    def k_triangle(self, si, sc, body):
        pts = [(960, 320), (560, 860), (1360, 860)]
        lid = self.uid("tg")
        body.append(f'<svg id="{lid}" style="position:absolute;left:0;top:0;width:1920px;height:1080px;opacity:0" viewBox="0 0 1920 1080">'
                    f'<path d="M960 320 L560 860 L1360 860 Z" fill="rgba(255,107,91,.06)" stroke="#3a4f7a" stroke-width="4"/></svg>')
        for (x, y), el in zip(pts, sc["nodes"]):
            eid = self.uid("tn")
            body.append(f'<div class="tri" id="{eid}" style="left:{x}px;top:{y}px;opacity:0">{esc(el["l"])}</div>')
            self.reveal(eid, self.at(si, el), "fade")
        self.reveal(lid, self.at(si, sc["nodes"][0]) - 0.2, "fade", None)
        cid = self.uid("tc")
        body.append(f'<div class="tric" id="{cid}" style="opacity:0">{esc(sc["center"])}</div>')
        self.reveal(cid, self.at(si, {"at": sc["center_at"], "d": 0.6}), "fade", "impact")

    def k_outro(self, si, sc, body):
        i1, r1, p1 = self.uid("id"), self.uid("ru"), self.uid("rp")
        body.append(f'<div class="idea" id="{i1}" style="opacity:0">{esc(sc["idea"])}</div>')
        body.append(f'<div class="rule" id="{r1}"></div>')
        body.append(f'<div class="repo" id="{p1}" style="opacity:0">Lesson {int(self.v["lesson"])} · <b>{REPO}</b></div>')
        t0 = self.tl["scenes"][si]["cues"][0]["t"]
        self.reveal(i1, t0 - 0.1, "up", None)
        self.js.append(f'tl.fromTo("#{r1}",{{scaleX:0,transformOrigin:"left center"}},{{scaleX:1,duration:.6,ease:"power3.out"}},{t0 + 0.4});')
        self.reveal(p1, t0 + 0.9, "fade", None)

    # ----------------------------------------------------------------- page
    def page(self) -> str:
        for si, sc in enumerate(self.v["scenes"]):
            self.scene(si, sc)
        total = self.tl["total"]
        names = {"pop": ["interface-drop_001.ogg", "interface-drop_002.ogg", "interface-drop_003.ogg"],
                 "key": ["keyboard-keypress-004.wav", "keyboard-keypress-011.wav", "keyboard-keypress-016.wav"],
                 "err": ["interface-error_005.ogg"], "slide": ["casino-card-slide-2.ogg"],
                 "impact": ["impact-impactSoft_heavy_000.ogg"]}
        vol = {"pop": 0.32, "key": 0.30, "err": 0.22, "slide": 0.28, "impact": 0.4}
        audio = [f'<audio id="vo" src="assets/vo/voice.wav" data-start="0" data-duration="{total}" '
                 f'data-track-index="20" data-volume="1"></audio>']
        counters: dict[str, int] = {}
        for j, (t, kind, _) in enumerate(sorted(self.sfx)):
            if t >= total - 0.2:
                continue
            k = counters.get(kind, 0)
            counters[kind] = k + 1
            f = names[kind][k % len(names[kind])]
            audio.append(f'<audio id="fx{j}" src="assets/sfx/{f}" data-start="{t:.3f}" data-duration="{0.25 if kind == "key" else 0.6}" '
                         f'data-track-index="{21 + j % 3}" data-volume="{vol[kind]}"></audio>')
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>{esc(self.v["title"])}</title>
<script src="assets/js/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{total}">
  <div id="bg" class="clip" data-start="0" data-duration="{total}" data-track-index="0" style="position:absolute;inset:0"><div id="bgfill"></div><div id="glow"></div><div class="mark">harness engineering · free course</div></div>
  {"".join(self.html)}
  {"".join(audio)}
</div>
<script>
(function () {{
  var tl = gsap.timeline({{ paused: true }});
  {chr(10).join(self.js)}
  tl.fromTo("#glow", {{ scale: 0.92 }}, {{ scale: 1.08, duration: {total}, ease: "sine.inOut" }}, 0);
  window.__timelines["main"] = tl;
}})();
</script>
</body>
</html>
"""


def main(ids: list[str]) -> None:
    for v in VIDEOS:
        if ids and v["id"] not in ids:
            continue
        proj = OUT / v["slug"]
        assets = proj / "assets"
        for sub in ("fonts", "js", "sfx"):
            (assets / sub).mkdir(parents=True, exist_ok=True)
        for f in ("Inter.woff2", "JetBrainsMono.woff2"):
            shutil.copy(PROMO / "fonts" / f, assets / "fonts" / f)
        shutil.copy(PROMO / "js" / "gsap.min.js", assets / "js" / "gsap.min.js")
        for f in (PROMO / "sfx").iterdir():
            shutil.copy(f, assets / "sfx" / f.name)
        if (proj / "timeline.json").exists() and (assets / "vo" / "voice.wav").exists() and not os.environ.get("REVOICE"):
            tl = json.loads((proj / "timeline.json").read_text(encoding="utf-8"))
        else:
            tl = make_voice(v, assets)
        (proj / "timeline.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
        (proj / "index.html").write_text(Builder(v, tl).page(), encoding="utf-8")
        (proj / "hyperframes.json").write_text(json.dumps({"paths": {"assets": "assets"}}, indent=2), encoding="utf-8")
        print(f"{v['slug']}: {tl['total']:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1:])
