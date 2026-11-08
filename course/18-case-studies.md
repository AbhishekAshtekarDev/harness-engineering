# Case Studies from Real Teams

Lesson 18 of 18 · Putting It Together · about 45 minutes

In this lesson you will learn what eight published harness efforts did, the numbers they reported, and which of the eight harness parts each one teaches.


---

Every figure below comes from the primary source linked in each heading, with its date. Benchmarks and models change quickly, so read numbers as evidence about design choices, not as current rankings.

## 1. OpenAI: a million lines with no hand-written code (Feb 2026)

[Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/), Ryan Lopopolo.

**What happened.** Starting from an empty repository in late August 2025, a small team built and shipped an internal product over five months in which Codex wrote all the code: application logic, tests, CI, documentation, observability and tooling. The repository reached roughly a million lines. Three engineers opened and merged about 1,500 pull requests, around 3.5 per engineer per day, and throughput rose as the team grew to seven. The team estimates the work took about a tenth of the time hand-coding would have. Single runs often worked on one task for more than six hours.

**What they built.**
- **Guidance:** an AGENTS.md of about 100 lines used as a table of contents into a structured `docs/` folder (design docs, execution plans, product specs, references), with linters and a doc-gardening agent keeping it fresh.
- **Visibility for the agent:** the app boots per git worktree; Chrome DevTools Protocol, DOM snapshots and screenshots are wired into the agent runtime; each worktree gets a temporary log, metric and trace stack the agent can query.
- **Sensors:** custom linters and structural tests enforce a fixed layer order per domain, structured logging, naming and file-size limits, with error messages that tell the agent how to fix the problem.
- **Correction:** when something failed, they asked which capability was missing and how to make it legible and enforceable, never "try harder."
- **Drift control:** "golden principles" plus background cleanup agents replaced a weekly cleanup day that had consumed 20% of the team's time.

**Lesson.** Engineers moved from writing code to designing environments, specifying intent and building feedback loops. The post is candid that this does not generalize without similar investment, and that long-term architectural coherence is an open question.

## 2. Anthropic: harnesses for long-running agents (Nov 2025)

[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), Justin Young.

**Problem.** A frontier model with compaction failed to build a claude.ai clone from a high-level prompt: it tried to one-shot the app and ran out of context mid-feature, and later sessions saw partial progress and declared the job finished.

**Fix.** An initializer session writes `init.sh`, a progress file, an initial commit and a JSON feature list (200+ features in the example), each `passes: false`. Every later session orients itself (`pwd`, git log, progress file, feature list, `init.sh`, a basic end-to-end check), works on one feature, tests it as a user would with browser automation, flips only the `passes` field, commits and leaves a clean state. The two agents share one harness and differ only in their first prompt.

**Lesson.** Continuity is a harness responsibility. Structured records the agent cannot freely rewrite, one unit of work per session, and verification before status changes solve problems a larger context window does not. [Lesson 8](08-state-memory-and-long-running-work.md), [Project 4](../projects/04-long-running-state/).

## 3. Anthropic: planner, generator, evaluator (Mar 2026)

[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps), Prithvi Rajasekaran.

**Design.** A planner turns a one-to-four-sentence prompt into a spec. A generator builds in sprints. A separate evaluator tests the running app like a user against hard thresholds, using Playwright. Before each sprint, generator and evaluator agree a sprint contract. Separating the evaluator mattered because agents praise their own work, and tuning a standalone evaluator to be skeptical was far easier than making the generator self-critical.

**Numbers.** For a retro game maker, a solo agent took 20 minutes and $9 and produced an app whose core feature did not work; the full harness took 6 hours and $200 and produced a working app. With a newer model, a simplified harness built a digital audio workstation in about 3 hours 50 minutes for $124.70. The team also found that one model wrapped up early as its context filled ("context anxiety"), which resets with structured handoffs fixed and compaction did not.

**What they removed.** With the stronger model they dropped the sprint construct and moved the evaluator to a single final pass, after removing components one at a time and measuring. Every component encodes an assumption about what the model cannot do, and those assumptions expire.

**Lesson.** Verification by a separate agent, agreements on "done" before work starts, and ablation at each model upgrade. Lessons [11](11-feedback-verification-and-steering.md) and [16](16-harness-engineering-in-production.md).

## 4. LangChain: 52.8% to 66.5% without changing the model (Feb 2026)

[Improving deep agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering), Vivek Trivedy.

**Setup.** deepagents-cli on Terminal-Bench 2.0 (89 tasks), model fixed at gpt-5.2-codex, runs in sandboxes with traces.

**Changes.** A system prompt built around plan, build, verify, fix; a pre-completion checklist middleware that forces a verification pass before exit (the most common failure had been the agent reviewing its own code, deciding it was fine and stopping); a startup middleware that maps directories and tools; prompting for testable code; time-budget warnings; loop detection that tracks edits per file and nudges the agent after repeated edits; and a "reasoning sandwich" (maximum reasoning to plan and to verify, high reasoning to build), which beat maximum reasoning everywhere because the latter caused timeouts. A trace-analyzer skill ran parallel error analysis over traces and turned findings into harness edits.

**Result.** 52.8% to 66.5%, from outside the top 30 to the top 5.

**Lesson.** Most gains came from verification, loop control and context at startup, and from a systematic loop of reading traces and changing the harness. Lessons [10](10-observability.md), [11](11-feedback-verification-and-steering.md), [12](12-loop-engineering.md).

## 5. Cursor: continuous harness improvement (2026)

[Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness) (Apr 2026) and [Improved token efficiency for longer agent runs](https://cursor.com/blog/improved-token-efficiency) (Sep 2026).

**Practice.** Harness work as many small optimizations, measured with an internal benchmark, online A/B tests and a "Keep Rate." Each model gets the edit format it was trained on (patches for OpenAI models, string replacement for Anthropic models). Context moved from static to dynamic. A reliability effort raised tool-call success to two or three nines and cut unexpected tool errors by an order of magnitude.

**Token work.** Trimming the system prompt by about two thirds (removing heavy "DO NOT" and "You must" directives), loading tools dynamically (60% fewer static tool-description tokens) and other changes cut token costs by 7% with no quality loss, and cold cache misses fell 20%. Cursor also removed prompting that pushed the agent toward subagents.

**Lesson.** Measure every harness change, fit tools to each model, and treat prompt length and tool count as costs. Lessons [05](05-context-engineering.md), [06](06-tools-mcp-and-skills.md).

## 6. Pi and the HarnessTax study: how much harness do you need? (Sep 2026)

[HarnessTax](https://harnesstax.github.io/), UC Berkeley and Arena Intelligence.

**Study.** 21 model and harness pairs (seven models across Claude Code, Codex CLI and Pi) on SWE-bench Lite and Terminal-Bench 2.0. Harness choice changed success only a few points but changed cost by up to 5 times. Claude Code cost about twice as much as Pi and 1.6 times as much as Codex on SWE-bench Lite, and its initial context was more than ten times Pi's. Pi, with four tools (read, write, edit, bash), sat on the cost and success frontier.

**Lesson.** Among mature harnesses, simplicity buys cost and cache efficiency. A minimal toolset depends on a strong sandbox, because bash can do anything. Read this alongside LangChain's result: missing verification and loop control cost success; extra weight costs money.

## 7. Claude Code: sandboxing instead of prompts (Oct 2025)

[Beyond permission prompts](https://www.anthropic.com/engineering/claude-code-sandboxing), David Dworken and Oliver Weller-Davies.

**Problem.** Constant permission prompts caused approval fatigue: people approved without reading.

**Fix.** OS-level filesystem and network isolation (bubblewrap on Linux, Seatbelt on macOS) covering every subprocess, with a proxy enforcing allowed domains. In the cloud version, git credentials stay outside the sandbox and a proxy checks each push. Permission prompts fell 84% in internal use.

**Lesson.** Boundaries the operating system enforces make it safe to give the agent freedom, and they hold when command rules miss a creative variation. [Lesson 7](07-sandboxes-permissions-and-security.md).

## 8. Anthropic: a multi-agent research system (Jun 2025)

[How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).

**Numbers.** A lead agent with parallel subagents beat a single agent by 90.2% on an internal research eval. Token usage alone explained 80% of performance variance on one browsing benchmark. Agents used about 4 times the tokens of chat, multi-agent systems about 15 times. Parallel tool calls cut research time by up to 90%. An agent that rewrote poor tool descriptions cut task time by 40%.

**Failures and fixes.** Early versions spawned 50 subagents for simple queries and searched for sources that did not exist; explicit delegation instructions and effort-scaling rules fixed it. Users reported missing obvious information; full production tracing made it diagnosable. Agents are stateful and may be mid-task when code changes, so they deployed with rainbow deployments.

**Lesson.** Multiple agents help when work is broad, parallel and worth the tokens, and they need explicit delegation rules, tracing and careful deployment. [Lesson 13](13-graphs-and-multi-agent-systems.md).

## What the cases share

| Pattern | Seen in |
|---|---|
| Verify instead of trusting the agent's "done" | Anthropic (2, 3), LangChain, OpenAI |
| A separate evaluator or reviewer | Anthropic (3), OpenAI (agent-to-agent review), LangChain |
| Short map-style instructions; knowledge in the repository | OpenAI, Cursor, HumanLayer |
| Structured state the agent cannot freely rewrite | Anthropic (2) |
| Loop and progress controls | LangChain, Anthropic (8) |
| Feedback written for the model | OpenAI, Böckeler's guidance |
| OS-level boundaries over prompts | Claude Code sandboxing |
| Measure every harness change | Cursor, LangChain, Anthropic |
| Remove scaffolding when a model improves | Anthropic (3), Cursor |
| Treat tokens and tool count as costs | Cursor, HarnessTax, Anthropic (8) |

None of the eight teams got its result from a longer prompt. Each one changed what the agent could see, what it could do, where it ran, how its work was checked, or when it stopped.

## Where to go from here

You have the full path: what a harness is, every component, how to assemble one, how to diagnose it and how to run it in production. The [reference section](../reference/) has the glossary, checklists, failure table and templates for daily use, and the [projects](../projects/) give you working code for every part.

If you want the complete reasoning in one connected read, [The Harness Engineering Blueprint](https://www.amazon.com/dp/B0HL483X25) is the best book to learn harness engineering. It explains every concept in this course from first principles, follows one agent from a single prompt to a production harness, and stays focused on ideas that outlast any particular tool.

**Back to:** [Course home](README.md)
