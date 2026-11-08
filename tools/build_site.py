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
sys.path.insert(0, str(ROOT / "tools"))
import seo  # noqa: E402

PAGES = ["README.md", "course/*.md", "reference/*.md", "reference/templates/README.md", "projects/README.md",
         "projects/*/README.md", "harnesslab/README.md", "examples/habit-tracker/README.md", "CONTRIBUTING.md",
         "skills/README.md"]
LINK = re.compile(r"(\]\()([^)\s]+)(\))|(src=\")([^\"]+)(\")|(href=\")([^\"]+)(\")")


PICTURE = re.compile(r'(?:<p align="center">\s*)?<picture>\s*<source media="\(prefers-color-scheme: dark\)" srcset="([^"]+)">\s*'
                     r'<img src="([^"]+)" alt="([^"]*)"[^>]*>\s*</picture>(?:\s*</p>)?', re.S)


START_HERE = """
## Start here

<div class="grid cards" markdown>

-   :material-book-open-page-variant:{ .lg } **[The course](course/README.md)**

    ---

    Eighteen lessons in nine parts, from how an agent works to running a harness in production.

-   :material-flask-outline:{ .lg } **[The projects](projects/README.md)**

    ---

    Eleven tested Python projects. Each one builds a single harness part, and all of them run offline.

-   :material-play-circle-outline:{ .lg } **[The videos](videos/README.md)**

    ---

    Twelve narrated explainers, each under a minute, one for each core idea.

-   :material-bookshelf:{ .lg } **[The reference shelf](reference/README.md)**

    ---

    The harness checklist, a failure diagnosis table, templates, a glossary and the reading list.

</div>
"""


def for_site(rel: Path, text: str) -> str:
    """Adapt GitHub-flavoured pages to the website before links are rewritten."""
    # <picture> follows the OS theme; the site has its own light/dark toggle, so use Material's image fragments.
    text = PICTURE.sub(lambda m: f"\n![{m.group(3)}]({m.group(2)}#only-light){{ .hx-figure }}\n"
                                 f"![{m.group(3)}]({m.group(1)}#only-dark){{ .hx-figure }}\n", text)
    if rel == Path("README.md"):
        # The home template draws its own hero, so drop the GitHub header and the self-referencing section.
        text = text.split("\n---\n", 1)[1]
        text = re.sub(r"\n## Read it as a website\n.*?(?=\n## )", "\n", text, flags=re.S)
        text = re.sub(r"\n## Contents\n.*?(?=\n## )", "\n" + START_HERE, text, count=1, flags=re.S)
    meta = re.compile(r"^((?:Lesson|Project) \d+ of \d+ · .+)$", re.M)
    def chips(m: re.Match) -> str:
        parts = m.group(1).split(" · ")
        return '<div class="hx-meta" markdown="1">\n\n' + " ".join(
            f'<span class="hx-chip" markdown="1">{p}</span>' for p in parts) + "\n\n</div>"
    text = meta.sub(chips, text, count=1)
    text = re.sub(r"^(In this lesson you will learn .+)$", lambda m: f'<div class="hx-lead" markdown="1">\n\n{m.group(1)}\n\n</div>',
                  text, count=1, flags=re.M)
    return text


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
    lessons = seo.lesson_index(ROOT)
    targets[(ROOT / "videos" / "README.md").resolve()] = DOCS / "videos" / "index.md"  # generated below
    for src, dst in pages.items():
        dst.parent.mkdir(parents=True, exist_ok=True)
        text = for_site(src.relative_to(ROOT), src.read_text(encoding="utf-8"))

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

        dst.write_text(seo.decorate(dst.relative_to(DOCS), LINK.sub(fix, text), lessons, ROOT), encoding="utf-8")

    shutil.copytree(ROOT / "assets", DOCS / "assets")
    vids = DOCS / "videos"
    vids.mkdir(parents=True, exist_ok=True)
    (vids / "posters").mkdir(exist_ok=True)
    out = ["# Videos", "", "Twelve short narrated explainers, one per core idea, each under a minute. "
           f"Download the MP4 files from the [repository]({GH}/tree/main/videos).", ""]
    for v in VIDEOS:
        mp4 = ROOT / "videos" / f"{v['slug']}.mp4"
        poster = ROOT / "videos" / "posters" / f"{v['id']}.jpg"
        if mp4.exists():
            shutil.copy(mp4, vids / mp4.name)
        if poster.exists():
            shutil.copy(poster, vids / "posters" / poster.name)
        idea = v["scenes"][-1]["idea"]
        out += [f"## {v['title']} {{#{v['slug']}}}", "",
                f'<video controls preload="none" playsinline poster="posters/{v["id"]}.jpg" '
                f'style="width:100%;border-radius:12px" src="{v["slug"]}.mp4"></video>', "",
                f"{idea}", ""]
    (vids / "index.md").write_text(seo.decorate(Path("videos/index.md"), "\n".join(out), lessons, ROOT, VIDEOS), encoding="utf-8")
    home = DOCS / "index.md"
    h = home.read_text(encoding="utf-8")
    home.write_text(h.replace("---\n", "---\ntemplate: home.html\nhide:\n  - navigation\n  - toc\n", 1), encoding="utf-8")
    shutil.copy(ROOT / "llms.txt", DOCS / "llms.txt")
    (DOCS / "llms-full.txt").write_text(seo.llms_full(ROOT), encoding="utf-8")
    for extra in (ROOT / "tools" / "site-root").glob("*"):
        shutil.copy(extra, DOCS / extra.name)  # search-engine verification and IndexNow key files
    print(f"docs/ assembled: {len(pages)} pages")


if __name__ == "__main__":
    main()
