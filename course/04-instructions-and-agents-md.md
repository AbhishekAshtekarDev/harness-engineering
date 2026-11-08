# Instructions and AGENTS.md

Lesson 4 of 18 · Guidance · about 40 minutes

In this lesson you will learn the five elements of a good task instruction, how to write a short instruction file that works across agents, what the 2026 evidence says about AGENTS.md, and where prompting stops and enforcement must begin.

**Template:** [AGENTS.md template](../reference/templates/AGENTS.md) · **Example:** [habit-tracker AGENTS.md](../examples/habit-tracker/AGENTS.md)


---

## The new-employee test

Anthropic suggests treating the model like a brilliant new employee who knows nothing about your norms. A capable new hire handed a one-line request fills the gaps with reasonable assumptions, and some of those assumptions are wrong. Anthropic pairs the analogy with a practical test: show the prompt to a colleague with little context on the task. If they would be confused, the model will be too.

## Five elements of a task instruction

| Element | Weak | Strong |
|---|---|---|
| **Goal and reason** | "Add a weekly streak." | "Show how many consecutive weeks the user met their weekly target, so people are rewarded for habits they do a few times a week." |
| **Instructions** | "Write good code." | "Add `weekly_streak(habit, today)` to `streaks.py`, show it on the habit page, add unit tests." |
| **Constraints** | (none) | "No schema changes. No new packages. Keep `daily_streak` behavior identical." |
| **Examples** | (none) | Three cases: four good weeks gives 4; a missed finished week gives 0; an unfinished current week does not break the streak. |
| **Output requirements** | "Tell me when done." | "Finish with: files changed, tests run and their results, assumptions made." |

The reason behind a goal matters more than it looks. A model that knows *why* the feature exists can make sensible choices about edge cases you forgot to mention. Examples settle ambiguity faster than paragraphs of description, with one risk: the model copies surface features. If every example uses a target of 3, vary the targets.

Watch the words that carry weight. "Weekly streak" hides at least four decisions: which day starts a week, whose time zone, whether a week means a calendar week or any seven days, and whether a missed target or zero activity breaks the streak. A model will not stop to ask unless you tell it to. It will pick the most common interpretation in its training data and implement it with confidence. Define the heavy terms, ask the agent to list its assumptions, and for costly ambiguity tell it to stop and ask.

Recent models also follow instructions more exactly as written than older ones. Anthropic's guidance notes that "can you suggest some changes" may produce suggestions instead of changes. If you want action, say so.

## Structure: stable instructions and task instructions

Most model APIs separate developer-level instructions from user messages, and OpenAI states that the model prioritizes developer messages. Put stable material at the developer level and in the instruction file: the agent's role, how to approach work, the commands that run tests, how to report. Put the specific request in the task. Within a long prompt, separate kinds of content with Markdown headings or XML tags, and put long documents before the question.

## The instruction file: AGENTS.md

Most coding agents read a project instruction file at the start of every session. [AGENTS.md](https://agents.md/) is the open format: plain Markdown, no required fields, stewarded by the Agentic AI Foundation under the Linux Foundation, and used by more than 60,000 open-source projects according to its site. Codex, Cursor, Gemini CLI, GitHub Copilot's coding agent, Jules, Factory, Aider, goose, opencode, Zed, Warp, Devin, Amp and many others read it. Nested AGENTS.md files are allowed; the one closest to the edited file wins, and the user's chat prompt overrides everything.

Claude Code reads `CLAUDE.md`. To keep one source of truth, create a `CLAUDE.md` that imports the shared file with the line `@AGENTS.md`, or keep both in sync with a symlink.

### What the evidence says

The 2026 research on instruction files is mixed, and the mix tells you how to write one.

- An ETH Zurich study, [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988), found that repository context files did not generally improve task success and raised inference cost by more than 20%.
- A study of [2,853 GitHub repositories](https://arxiv.org/abs/2602.14690) found that context files are the most common harness mechanism teams use, and often the only one.
- OpenAI's team tried one large AGENTS.md and [abandoned it](https://openai.com/index/harness-engineering/) for four reasons: context is scarce, too much guidance becomes no guidance, the file rots, and nobody can verify it. Their replacement was about 100 lines that act as a table of contents into a structured `docs/` folder.
- Mitchell Hashimoto writes each line of his project's AGENTS.md in response to a specific bad agent behavior.
- Cursor trimmed its own system prompt by about two thirds in 2026, removing heavy "DO NOT" and "You must" directives, and [token costs fell](https://cursor.com/blog/improved-token-efficiency) with no loss in quality.

The consensus across these sources: keep the file short (roughly 60 to 100 lines), write it by hand, add a line only when you have seen the failure it prevents, and point to deeper documents instead of pasting them. A generated, encyclopedic file costs tokens on every call and dilutes the rules that matter.

### A file that works

```markdown
# AGENTS.md: habit-tracker

A Python library that tracks habits, completions and streaks.

## Layout
- `habit_tracker/` source. `timeutils.py` owns all day and week logic.
- `tests/` pytest suite. `docs/product-spec.md` defines streak behavior.
- `config/` shared settings: read-only for agents.

## Commands
- All tests: `python -m pytest -q`
- One file:  `python -m pytest -q tests/test_daily_streak.py`

## Rules
- Use `timeutils.local_date` and `timeutils.week_start` for every day or week
  calculation. Never call `.date()` on a completion directly.
- Do not edit or delete existing tests. Add new tests next to them.
- Do not add dependencies.

## Done means
All tests pass, new logic has tests, and your final message lists files
changed, tests run and assumptions made.
```

Notice what it leaves out: no architecture essay, no history, no motivational paragraph, no list of every module. It answers the five questions a fresh session needs: what is this, how is it organized, how do I run it, how do I verify my work, and what are the few rules that bite.

### Progressive disclosure

Progressive disclosure means revealing information in layers as it becomes relevant. The instruction file is the first layer. It points to the second: design docs, specs, execution plans and runbooks in the repository. The agent opens those only when a task needs them. OpenAI's repository used exactly this structure, with linters and a recurring "doc-gardening" agent to keep the docs fresh and cross-linked. [Skills](06-tools-mcp-and-skills.md) push the same idea further, loading packaged know-how only when a task matches.

### Rule hygiene

Rules accumulate. Keep each one honest:

Note the failure that created each rule, as a PR number or a single sentence, so a reviewer can tell later whether the rule still earns its place. Put rules that apply to one folder in a nested AGENTS.md inside that folder instead of the root file. Review rules that have not mattered in weeks: a rule about a library you removed costs tokens on every call and confuses the agent, so delete it.

## Where prompting stops

An instruction is a request. The model usually follows it and occasionally does not, especially late in a long task when the instruction sits far from the recent context. When a rule must hold every time, the harness has to enforce it.

| Rule | Prompt can say it | Harness enforces it with |
|---|---|---|
| Never edit `config/` | Yes | Path guard or OS sandbox (Lesson 7) |
| Run the tests before finishing | Yes | Verification on every "done" claim (Lesson 11) |
| Use the time-zone helper | Yes | A lint rule that explains the fix (Lesson 11) |
| Never push to main | Yes | Deny rule plus a credential that cannot push (Lesson 7) |
| Keep weekly targets between 1 and 7 | Yes | Business-rule check in code and a test (Lesson 9) |

The pattern repeats through the course: the prompt communicates the expectation, and the harness guarantees it. When an agent fails, the instinct is to add another line to the prompt. After a few months that instinct produces a long, contradictory rulebook in which every line patches one past mistake. OpenAI describes the same trap and the same escape: move knowledge to where it belongs, and turn rules into checks.

## Prompts are everywhere in a harness

Prompt engineering does not disappear inside a harness. It spreads into every place the system tells the model something: tool descriptions, the instruction file, skill descriptions, handoff messages between agents, the feedback a loop sends after a failed test, and the rubric an evaluator applies. Write all of them with the same care.

## Check yourself

<details><summary>1. Your AGENTS.md is 600 lines and the agent still ignores the time-zone rule. What do you try first?</summary>

Shorten the file to the rules that bite, move detail into linked docs, and turn the time-zone rule into a lint check whose message explains the fix. A long file dilutes attention; an enforced rule does not depend on attention.
</details>

<details><summary>2. Why do studies find instruction files often fail to improve success, while practitioners swear by them?</summary>

The studies include many generated or generic files that add cost without adding information. Short, human-written files built from observed failures carry specific information the agent cannot infer. Both findings point to the same practice: small and failure-driven.
</details>

<details><summary>3. Which two of the five instruction elements prevent the "weekly streak means one check-in per week" misreading?</summary>

The goal with its reason (reward consistency against a weekly target) and examples (three concrete cases with expected streak values).
</details>

## Try it

Open [examples/habit-tracker/AGENTS.md](../examples/habit-tracker/AGENTS.md). Delete the "Rules" section and run `python -m harnesslab run --provider anthropic` (or `openai`) from `harnesslab/`. Put the section back and run it again. Read both traces with `python -m harnesslab trace runs/HT-142.jsonl`. Note how many iterations and tokens each run used and where the first run went wrong.

## Go deeper

- Anthropic's [prompt engineering documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) and OpenAI's [prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering) cover structure, examples and model-specific behavior.
- HumanLayer's [Skill Issue](https://humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) explains why they keep CLAUDE.md under 60 lines.

**Next lesson:** [Context Engineering for Harnesses](05-context-engineering.md)
