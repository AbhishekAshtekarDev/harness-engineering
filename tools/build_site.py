"""Assemble the website's docs/ folder from the repository, then `mkdocs build`.

    python tools/build_site.py && mkdocs build

Markdown pages are copied as they are. Links to files that are not pages on the
site (Python code, folders without a README, JSON) are rewritten to GitHub URLs,
so every link works in both places.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GH = "https://github.com/AbhishekAshtekarDev/harness-engineering"
sys.path.insert(0, str(ROOT / "videos" / "build"))
from specs import VIDEOS  # noqa: E402

PAGES = ["README.md", "course/*.md", "reference/*.md", "reference/templates/README.md", "projects/README.md",
         "projects/*/README.md", "harnesslab/README.md", "examples/habit-tracker/README.md", "CONTRIBUTING.md",
         "skills/README.md"]
LINK = re.compile(r"(\]\()([^)\s]+)(\))|(src=\")([^\"]+)(\")|(href=\")([^\"]+)(\")")


def page_path(src: Path) -> Path:
    rel = src.relative_to(ROOT)
    if rel == Path("README.md"):
        return DOCS / "index.md"
    if rel.name == "README.md":
        return DOCS / rel.parent / "index.md"
    return DOCS / rel


def main() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    sources = sorted({p for pat in PAGES for p in ROOT.glob(pat)})
    pages = {s.resolve(): page_path(s) for s in sources}
    targets = dict(pages)
    targets[(ROOT / "videos" / "README.md").resolve()] = DOCS / "videos" / "index.md"  # generated below
    for src, dst in pages.items():
        dst.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text()

        def fix(m: re.Match) -> str:
            pre, target, post = [g for g in m.groups() if g is not None]
            if re.match(r"^(https?:|mailto:|#)", target):
                return pre + target + post
            path, _, frag = target.partition("#")
            resolved = (src.parent / path).resolve()
            frag = ("#" + frag) if frag else ""
            if resolved in targets:
                rel = Path(targets[resolved]).relative_to(DOCS)
                here = dst.parent.relative_to(DOCS)
                new = Path(__import__("os").path.relpath(rel, here))
                return pre + new.as_posix() + frag + post
            if resolved.is_dir() and (resolved / "README.md").resolve() in pages:
                rel = pages[(resolved / "README.md").resolve()].relative_to(DOCS)
                new = Path(__import__("os").path.relpath(rel, dst.parent.relative_to(DOCS)))
                return pre + new.as_posix() + frag + post
            if str(resolved).startswith(str(ROOT / "assets")) or str(resolved).startswith(str(ROOT / "videos")):
                rel = resolved.relative_to(ROOT)
                new = Path(__import__("os").path.relpath(rel, dst.parent.relative_to(DOCS)))
                return pre + new.as_posix() + frag + post
            try:
                rel = resolved.relative_to(ROOT).as_posix()
            except ValueError:
                return pre + target + post
            kind = "tree" if resolved.is_dir() else "blob"
            return pre + f"{GH}/{kind}/main/{rel}{frag}" + post

        dst.write_text(LINK.sub(fix, text))

    shutil.copytree(ROOT / "assets", DOCS / "assets")
    vids = DOCS / "videos"
    vids.mkdir(parents=True, exist_ok=True)
    (vids / "posters").mkdir(exist_ok=True)
    out = ["# Videos", "", "Twelve short narrated explainers, one per core idea. "
           f"Download the MP4 files from the [repository]({GH}/tree/main/videos).", ""]
    for v in VIDEOS:
        mp4 = ROOT / "videos" / f"{v['slug']}.mp4"
        poster = ROOT / "videos" / "posters" / f"{v['id']}.jpg"
        if mp4.exists():
            shutil.copy(mp4, vids / mp4.name)
        if poster.exists():
            shutil.copy(poster, vids / "posters" / poster.name)
        idea = v["scenes"][-1]["idea"]
        out += [f"## {v['id']}. {v['title']} {{#{v['slug']}}}", "",
                f'<video controls preload="none" playsinline poster="posters/{v["id"]}.jpg" '
                f'style="width:100%;border-radius:12px" src="{v["slug"]}.mp4"></video>', "",
                f"**The idea:** {idea}", ""]
    (vids / "index.md").write_text("\n".join(out))
    print(f"docs/ assembled: {len(pages)} pages")


if __name__ == "__main__":
    main()
