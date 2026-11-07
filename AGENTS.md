# AGENTS.md: harness-engineering course

A free course on harness engineering: lessons (Markdown), projects (Python with
tests), a teaching harness (harnesslab) and reference pages.

## Layout
- `course/` 18 lessons. `reference/` checklist, glossary, templates, FAQ.
- `harnesslab/` the teaching harness (Python, no required dependencies).
- `projects/NN-*/` each has `solution/`, generated `exercise/`, and tests.
- `examples/habit-tracker/` the running example. `.harness/` holds hidden tests.
- `tools/` exercise generator and style checker. `docs/` builds the website.

## Commands
- harnesslab tests: `cd harnesslab && python -m pytest -q tests`
- One project (solution): `cd projects/05-loop-controls && SOLUTION=1 python -m pytest -q`
- Regenerate exercises after editing a solution: `python tools/make_exercises.py`
- Style check for prose: `python tools/style_check.py`

## Rules
- Never edit `projects/*/exercise/` by hand; edit `solution/` and regenerate.
- Every factual claim in a lesson links to a primary source.
- Prose style: no em dashes, contractions or exclamation marks; active voice.
