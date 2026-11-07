# Contributing

Thank you for helping improve the course.

## What helps most

- **Corrections.** A wrong fact, a broken link, a test that fails on your platform.
- **Newer primary sources.** The field moves monthly. If a claim has a newer or better primary source, open an issue with the link.
- **Clearer explanations.** If a paragraph confused you, say which one and why.
- **Translations.** Open an issue first so work is not duplicated.

## Rules for content

- Every factual claim links to its primary source (the company's engineering post, the paper, the spec), with a date where it matters.
- Do not invent numbers. If a figure appears only in secondary coverage, leave it out.
- Keep the writing style: no em dashes, no contractions, no exclamation marks, active voice, specific nouns. Run `python tools/style_check.py` before opening a pull request.
- Describe emerging terms (loop engineering, graph engineering) as developing ideas, not settled standards.

## Rules for code

- Keep harnesslab dependency-free and readable. Clarity beats cleverness here.
- Projects: edit the file in `solution/`, mark the learner's part with `# BEGIN SOLUTION` / `# END SOLUTION` under a `# TODO` comment, then run `python tools/make_exercises.py`.
- Run the checks:

```bash
python -m pytest -q harnesslab/tests
for d in projects/*/; do (cd "$d" && SOLUTION=1 python -m pytest -q) ; done
python tools/style_check.py
```
