"""Search metadata for the website: titles, descriptions and schema.org JSON-LD.

build_site.py calls `decorate(dst, text)` for every page it writes. Each page gets
YAML front matter (seo_title, description) that overrides/main.html renders into
<title>, meta description, Open Graph and Twitter tags, plus a JSON-LD block that
tells search engines and AI assistants what the page is: the course, a lesson, a
project, the FAQ or the videos.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SITE = "https://abhishekashtekardev.github.io/harness-engineering/"
GH = "https://github.com/AbhishekAshtekarDev/harness-engineering"
COURSE_ID = SITE + "#course"
PERSON_ID = SITE + "#author"
PUBLISHED = "2026-11-08"
BOOK_URL = "https://www.amazon.com/dp/B0HL483X25"
COURSE_NAME = "Harness Engineering: The Free, Complete Course"
COURSE_DESC = ("A free, open-source harness engineering course on GitHub: 18 lessons, 11 tested Python projects, "
               "12 short videos and a runnable agent harness. Learn to design the instructions, context, tools, "
               "sandboxes, permissions, memory, evals, observability and loops that make AI agents reliable.")

PERSON = {"@type": "Person", "@id": PERSON_ID, "name": "Abhishek Ashtekar", "url": "https://zerotoaimastery.com",
          "sameAs": ["https://github.com/AbhishekAshtekarDev", "https://zerotoaimastery.com"]}

TITLES = {
    "projects/index.md": "Harness Engineering Projects: 11 Hands-On Python Projects with Tests",
    "reference/index.md": "Harness Engineering Reference: Checklist, Glossary, Templates",
    "reference/glossary.md": "Harness Engineering Glossary: About 90 Terms Defined",
    "reference/reading-list.md": "Harness Engineering Reading List: The Primary Sources",
    "reference/harness-checklist.md": "Agent Harness Checklist: A Design Review to Production",
    "reference/failure-diagnosis.md": "AI Agent Failure Diagnosis Table: Symptom to Fix",
    "reference/frameworks-map.md": "Harness Engineering Frameworks Map: How the Models Line Up",
    "reference/templates/index.md": "Harness Engineering Templates: AGENTS.md, Hooks, Threat Model",
    "harnesslab/index.md": "harnesslab: A Readable Agent Harness in Python",
    "skills/index.md": "harness-review: An Agent Skill That Reviews Your Harness",
    "examples/habit-tracker/index.md": "Habit Tracker: The Course's Running Example App",
}

TEACHES = ["Harness engineering", "AI agent design", "Agent loop", "AGENTS.md and instruction files",
           "Context engineering", "Tool design and MCP", "Agent Skills", "Sandboxing and permissions",
           "Prompt injection defense", "Agent memory and long-running work", "Guardrails", "Agent evals",
           "Observability and tracing", "Loop engineering", "Multi-agent systems", "Production AI agents"]


def plain(md: str) -> str:
    """Markdown to one line of plain text."""
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[*_`]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def clip(s: str, n: int = 158) -> str:
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "..."


def url_for(rel: Path) -> str:
    parts = rel.with_suffix("").as_posix()
    if parts == "index":
        return SITE
    if parts.endswith("/index"):
        return SITE + parts[: -len("index")]
    return SITE + parts + "/"


def first_paragraph(body: str) -> str:
    for block in re.split(r"\n\s*\n", body):
        b = block.strip()
        if not b or b.startswith(("#", "<", "|", "```", "---", "[![", "!", ">")):
            continue
        if re.match(r"^(Lesson|Project) \d+ of", b):
            continue
        return plain(b)
    return ""


def h1(body: str) -> str:
    m = re.search(r"^# (.+)$", body, re.M)
    return plain(m.group(1)) if m else ""


def crumbs(items: list[tuple[str, str]]) -> dict:
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def minutes(body: str) -> str | None:
    m = re.search(r"about (\d+) minutes", body)
    return f"PT{m.group(1)}M" if m else None


def faq_pairs(body: str) -> list[tuple[str, str]]:
    pairs = []
    for m in re.finditer(r"^\*\*(.+?\?)\*\*\n(.+?)(?=\n\n|\Z)", body, re.M | re.S):
        pairs.append((plain(m.group(1)), plain(m.group(2))))
    return pairs


def video_lengths(root: Path) -> dict[str, str]:
    """slug -> ISO 8601 duration, read from the table in videos/README.md."""
    out = {}
    for m in re.finditer(r"\]\(([\w-]+)\.mp4\) \| (\d+):(\d\d) \|", (root / "videos" / "README.md").read_text(encoding="utf-8")):
        out[m.group(1)] = f"PT{int(m.group(2))}M{int(m.group(3))}S"
    return out


def graph(*nodes: dict) -> str:
    data = json.dumps({"@context": "https://schema.org", "@graph": list(nodes)}, ensure_ascii=False, indent=1)
    return '\n\n<script type="application/ld+json">\n' + data.replace("</", "<\\/") + "\n</script>\n"


def front(title: str, desc: str) -> str:
    return "---\n" + f"seo_title: {json.dumps(title, ensure_ascii=False)}\n" + \
        f"description: {json.dumps(desc, ensure_ascii=False)}\n" + "---\n\n"


def decorate(rel: Path, body: str, lessons: list[tuple[str, str]], root: Path, videos: list[dict] | None = None) -> str:
    """Return the page with front matter and JSON-LD added. `rel` is the path inside docs/."""
    url = url_for(rel)
    title = h1(body)
    s = rel.as_posix()
    home = ("Harness Engineering Course", SITE)

    if s == "index.md":
        seo_title = "Harness Engineering Course: Free Lessons, Projects and Code on GitHub"
        desc = clip(COURSE_DESC)
        course = {
            "@type": "Course", "@id": COURSE_ID, "name": COURSE_NAME, "description": COURSE_DESC, "url": SITE,
            "sameAs": GH, "provider": {"@id": PERSON_ID}, "author": {"@id": PERSON_ID}, "creator": {"@id": PERSON_ID},
            "isAccessibleForFree": True, "inLanguage": "en", "educationalLevel": "Beginner to advanced",
            "teaches": TEACHES, "timeRequired": "PT14H", "datePublished": PUBLISHED,
            "license": "https://creativecommons.org/licenses/by/4.0/", "image": SITE + "assets/social-preview.png",
            "keywords": "harness engineering, agent harness, AI agents, harness engineering course, "
                        "harness engineering github, AGENTS.md, context engineering, MCP, agent evals",
            "offers": {"@type": "Offer", "category": "Free", "price": 0, "priceCurrency": "USD"},
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Online", "courseWorkload": "PT14H",
                                  "instructor": {"@id": PERSON_ID}},
            "hasPart": [{"@type": "LearningResource", "name": n, "url": u} for n, u in lessons],
        }
        site = {"@type": "WebSite", "@id": SITE + "#website", "url": SITE, "name": "Harness Engineering Course",
                "description": COURSE_DESC, "inLanguage": "en", "publisher": {"@id": PERSON_ID}}
        code = {"@type": "SoftwareSourceCode", "name": "harness-engineering", "codeRepository": GH,
                "description": "Course source, the harnesslab teaching harness and 11 tested projects.",
                "programmingLanguage": "Python", "license": "https://opensource.org/licenses/MIT",
                "author": {"@id": PERSON_ID}, "isPartOf": {"@id": COURSE_ID}}
        book = {"@type": "Book", "name": "The Harness Engineering Blueprint", "author": {"@id": PERSON_ID},
                "url": BOOK_URL, "bookFormat": "https://schema.org/EBook", "inLanguage": "en",
                "workExample": [{"@type": "Book", "bookFormat": "https://schema.org/Paperback", "isbn": "9798177042343"},
                                {"@type": "Book", "bookFormat": "https://schema.org/Hardcover", "isbn": "9798177119168"}]}
        ld = graph(site, course, code, PERSON, book)

    elif re.match(r"course/\d\d-", s):
        n = int(s.split("/")[1][:2])
        lead = re.search(r"In this lesson you will learn (.+?)\n", body)
        learn = ("Learn " + plain(lead.group(1))) if lead else first_paragraph(body)
        tail = f" Lesson {n} of a free harness engineering course."
        desc = learn + tail if len(learn + tail) <= 160 else clip(learn)
        seo_title = f"{title}: Harness Engineering Lesson {n}"
        node = {"@type": ["LearningResource", "Article"], "@id": url + "#lesson", "name": title, "headline": title,
                "description": desc, "url": url, "learningResourceType": "Lesson", "position": n,
                "isPartOf": {"@id": COURSE_ID}, "isAccessibleForFree": True, "inLanguage": "en",
                "author": {"@id": PERSON_ID}, "datePublished": PUBLISHED, "image": SITE + "assets/social-preview.png",
                "license": "https://creativecommons.org/licenses/by/4.0/"}
        if minutes(body):
            node["timeRequired"] = minutes(body)
        ld = graph(node, crumbs([home, ("Course", SITE + "course/"), (title, url)]), PERSON)

    elif re.match(r"projects/\d\d-", s):
        n = int(s.split("/")[1][:2])
        table = (root / "projects" / "README.md").read_text(encoding="utf-8")
        m = re.search(rf"^\| {n} \| [^|]+\| ([^|]+?) \|", table, re.M)
        what = plain(m.group(1)) if m else first_paragraph(body)
        desc = clip(f"Build {what[0].lower() + what[1:]}. Free harness engineering project {n} in Python, with tests and a solution.")
        seo_title = f"{title}: Harness Engineering Project {n}"
        node = {"@type": "LearningResource", "@id": url + "#project", "name": title, "description": desc, "url": url,
                "learningResourceType": "Project", "position": n, "isPartOf": {"@id": COURSE_ID},
                "isAccessibleForFree": True, "inLanguage": "en", "author": {"@id": PERSON_ID},
                "programmingLanguage": "Python", "datePublished": PUBLISHED}
        if minutes(body):
            node["timeRequired"] = minutes(body)
        ld = graph(node, crumbs([home, ("Projects", SITE + "projects/"), (title, url)]), PERSON)

    elif s == "reference/faq.md":
        pairs = faq_pairs(body)
        seo_title = "Harness Engineering FAQ: Answers to Common Questions"
        desc = clip("What is harness engineering, how it differs from prompt and context engineering, "
                    "whether AGENTS.md works, how to sandbox and evaluate agents, and where to learn it.")
        node = {"@type": "FAQPage", "@id": url + "#faq", "url": url, "name": title, "isPartOf": {"@id": COURSE_ID},
                "mainEntity": [{"@type": "Question", "name": q,
                                "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}
        ld = graph(node, crumbs([home, ("Reference", SITE + "reference/"), ("FAQ", url)]))

    elif s == "videos/index.md":
        lengths = video_lengths(root)
        seo_title = "Harness Engineering Videos: 12 Short Explainers"
        desc = clip("Twelve narrated videos under a minute each: the agent loop, context rot, MCP, the lethal "
                    "trifecta, long-running agents, guides and sensors, pass^k, loops and failure diagnosis.")
        nodes = []
        for v in videos or []:
            node = {"@type": "VideoObject", "@id": f"{url}#{v['slug']}", "name": v["title"],
                    "description": plain(v["scenes"][-1]["idea"]),
                    "thumbnailUrl": f"{SITE}videos/posters/{v['id']}.jpg", "uploadDate": PUBLISHED + "T00:00:00+00:00",
                    "contentUrl": f"{SITE}videos/{v['slug']}.mp4", "embedUrl": f"{url}#{v['slug']}",
                    "inLanguage": "en", "isPartOf": {"@id": COURSE_ID}, "isAccessibleForFree": True}
            if v["slug"] in lengths:
                node["duration"] = lengths[v["slug"]]
            nodes.append(node)
        ld = graph(*nodes, crumbs([home, ("Videos", url)]))

    else:
        desc = clip(first_paragraph(body) or COURSE_DESC)
        if s == "course/index.md":
            seo_title = "Harness Engineering Course Outline: 18 Lessons in 9 Parts"
            node = {"@type": "ItemList", "name": "Harness engineering lessons", "url": url,
                    "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "url": u}
                                        for i, (n, u) in enumerate(lessons)]}
            ld = graph(node, crumbs([home, ("Course", url)]))
        else:
            seo_title = TITLES.get(s) or (f"{title} | Harness Engineering Course" if title else "Harness Engineering Course")
            ld = graph({"@type": "WebPage", "name": title, "url": url, "description": desc,
                        "isPartOf": {"@id": SITE + "#website"}}, crumbs([home, (title or "Page", url)]))

    return front(seo_title, desc) + body.rstrip() + "\n" + ld


def lesson_index(root: Path) -> list[tuple[str, str]]:
    out = []
    for p in sorted((root / "course").glob("[0-9][0-9]-*.md")):
        out.append((h1(p.read_text(encoding="utf-8")), SITE + "course/" + p.stem + "/"))
    return out


def llms_full(root: Path) -> str:
    """Every lesson, the FAQ and the glossary in one Markdown file for AI assistants."""
    parts = ["# Harness Engineering: The Free, Complete Course (full text)", "",
             f"Source: {GH} · Website: {SITE} · Author: Abhishek Ashtekar · License: CC BY 4.0", ""]
    files = sorted((root / "course").glob("[0-9][0-9]-*.md")) + [root / "reference" / "faq.md", root / "reference" / "glossary.md"]
    for p in files:
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"<details><summary>(.+?)</summary>", r"**\1**", text)
        text = text.replace("</details>", "")
        rel = p.relative_to(root).as_posix()
        parts += ["", "---", "", f"<!-- {GH}/blob/main/{rel} -->", "", text.strip(), ""]
    return "\n".join(parts)
