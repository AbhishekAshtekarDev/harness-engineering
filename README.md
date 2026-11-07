<p align="center"><img src="assets/hero.svg" alt="Harness engineering course: a model at the center, wrapped by the agent loop and eight harness parts: guidance, capability, boundaries, continuity, checking, visibility, correction and control flow" width="100%"></p>

# Harness Engineering: The Free, Complete Course

**Harness engineering is the practice of designing the system around an AI agent so the agent has the information, tools, environment, constraints, feedback and control mechanisms it needs to complete useful work reliably.** The model does the reasoning. The harness decides what it sees, what it may touch, where it runs, how its work is checked, what gets recorded and when it stops.

This repository teaches the whole discipline from first principles, with working code for every part: 18 lessons, 11 tested projects, 12 short videos, a readable harness library you can run offline in one command, and a reference shelf of checklists, templates and a failure diagnosis table.

[![Lessons](https://img.shields.io/badge/lessons-18-0b1324)](course/) [![Projects](https://img.shields.io/badge/projects-11%20with%20tests-0b1324)](projects/) [![Videos](https://img.shields.io/badge/videos-12-0b1324)](videos/) [![Website](https://img.shields.io/badge/read%20as%20a%20website-d4ff3f?labelColor=0b1324)](https://abhishekashtekardev.github.io/harness-engineering/) [![License: MIT + CC BY 4.0](https://img.shields.io/badge/license-MIT%20%2B%20CC%20BY%204.0-0b1324)](LICENSE)

---

## See a harness work in 60 seconds

No API key needed. A scripted agent makes the mistakes real agents make, and the harness catches each one:

```bash
git clone https://github.com/AbhishekAshtekarDev/harness-engineering.git
cd harness-engineering/harnesslab
python -m pip install -e .
python -m harnesslab demo
```

```text
agent: Adding weekly_streak next to daily_streak.
tool edit_file ok: Edited habit_tracker/streaks.py: replaced 3 line(s) with 14.
agent: The lint rule says .date() gives the UTC day. I'll read the time helpers.     <- sensor
agent: I'll also add a feature flag so the team can turn weekly streaks off.
tool edit_file ERROR: 'config/settings.toml' is protected (matches config/*).          <- boundary
blocked (deny): Blocked by policy: destructive deletes are not allowed                 <- permission rule
tool run_tests ok: All tests passed (10 passed in 0.02s).
agent: Done. Changed habit_tracker/streaks.py and added tests/test_weekly_streak.py.
verify: FAIL acceptance + held-out tests: Test run: 1 failed, 4 passed                  <- verification
agent: Verification shows an unfinished current week breaks my streak. Fixing...
verify: PASS
[succeeded] verification passed
```

The agent's own tests passed. The hidden acceptance test still found the bug, because the harness verified the work instead of trusting the agent's "done." That one idea runs through the whole course.

## The model, the agent and the harness

```mermaid
flowchart LR
  M["Model<br/>reads and writes text"] --> A["Agent<br/>model + tools in a loop"] --> H["Harness<br/>everything around the agent"] --> R["Reliable agent system"]
```

A model on its own cannot open a file, run a test, remember yesterday or know what changed this morning. When it wants to act, it writes a structured request, and the harness decides whether to run it, runs it somewhere safe, records it and hands back the result. Every path into the model and every path out passes through the harness, which is why so much of an agent's reliability is decided there.

The evidence is concrete. LangChain moved a coding agent from 52.8% to 66.5% on Terminal-Bench 2.0 by [changing only the harness](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering). OpenAI's team shipped a product of roughly a million lines with [no hand-written code](https://openai.com/index/harness-engineering/) by investing in environment, documentation and feedback loops. Anthropic's long-running agents stopped declaring victory early once a harness gave them a [feature list, a progress file and a verification step](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## The course

The course follows one running example from a single prompt to a production harness: a coding agent adding a weekly streak to a habit-tracker app. It also covers support, research, data and operations agents, because harness engineering is not only for code.

| Part | Lessons | You will be able to |
|---|---|---|
| **1. Foundations** | [01 What harness engineering is](course/01-what-is-harness-engineering.md) · [02 How an agent works](course/02-how-an-agent-works.md) · [03 The layers, prompt to harness](course/03-the-layers.md) | Explain the model, agent and harness; write an agent loop; place any failure on the map |
| **2. Guidance** | [04 Instructions and AGENTS.md](course/04-instructions-and-agents-md.md) · [05 Context engineering](course/05-context-engineering.md) | Write a short instruction file that works; manage context rot, compaction and resets |
| **3. Capability** | [06 Tools, MCP and Agent Skills](course/06-tools-mcp-and-skills.md) | Design tools agents use well; use the 2026 MCP spec and skills safely |
| **4. Boundaries** | [07 Sandboxes, permissions and security](course/07-sandboxes-permissions-and-security.md) | Isolate files and network, keep secrets unreadable, break the lethal trifecta |
| **5. Continuity** | [08 State, memory and long-running work](course/08-state-memory-and-long-running-work.md) | Run multi-session work with feature lists, progress files, checkpoints and resumes |
| **6. Checking and visibility** | [09 Guardrails, tests and evals](course/09-guardrails-tests-and-evals.md) · [10 Observability](course/10-observability.md) | Build evals with pass@k and pass^k, calibrate LLM judges, debug from traces |
| **7. Correction** | [11 Feedback, verification and steering](course/11-feedback-verification-and-steering.md) | Write guides and sensors, verify instead of trusting, turn repeat mistakes into permanent fixes |
| **8. Control flow** | [12 Loop engineering](course/12-loop-engineering.md) · [13 Graphs and multi-agent systems](course/13-graphs-and-multi-agent-systems.md) | Design loops that stop for a reason; decide when a graph or a second agent earns its cost |
| **9. Putting it together** | [14 Build a complete harness](course/14-build-a-complete-harness.md) · [15 Diagnosing failures](course/15-diagnosing-agent-failures.md) · [16 Production](course/16-harness-engineering-in-production.md) · [17 Beyond coding](course/17-harnesses-beyond-coding.md) · [18 Case studies](course/18-case-studies.md) | Assemble, ablate, diagnose and run a harness in production, in any domain |

Start at [the course page](course/), which also has three shorter paths: for daily users of Claude Code, Codex or Cursor; for people building agents; and for team leads.

## Videos

Twelve short narrated explainers, one per core idea, each under two minutes. [Watch them all on the course site](https://abhishekashtekardev.github.io/harness-engineering/videos/).

| | | |
|---|---|---|
| [![What is harness engineering](videos/posters/01.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#01-what-is-harness-engineering)<br/>**01** What is harness engineering? | [![The agent loop](videos/posters/02.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#02-the-agent-loop)<br/>**02** The agent loop | [![The layers](videos/posters/03.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#03-the-layers)<br/>**03** Six layers, one map |
| [![Context rot](videos/posters/04.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#04-context-rot-compaction-and-resets)<br/>**04** Context rot, compaction, resets | [![Tools, MCP and skills](videos/posters/05.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#05-tools-mcp-and-skills)<br/>**05** Tools, MCP and skills | [![Sandbox and lethal trifecta](videos/posters/06.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#06-sandbox-and-the-lethal-trifecta)<br/>**06** The sandbox and the lethal trifecta |
| [![Long-running agents](videos/posters/07.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#07-long-running-agents)<br/>**07** Long-running agents | [![Guides and sensors](videos/posters/08.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#08-guides-and-sensors)<br/>**08** Guides and sensors | [![pass@k vs pass^k](videos/posters/09.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#09-pass-at-k-vs-pass-pow-k)<br/>**09** pass@k vs pass^k |
| [![Loops and stop conditions](videos/posters/10.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#10-loops-and-stop-conditions)<br/>**10** Loops and stop conditions | [![Graphs and multi-agent](videos/posters/11.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#11-graphs-and-multi-agent)<br/>**11** Loops, graphs, many agents | [![Diagnosing failures](videos/posters/12.jpg)](https://abhishekashtekardev.github.io/harness-engineering/videos/#12-diagnosing-failures)<br/>**12** Where is the bug? |

## Projects

Every project runs offline against a scripted model, has tests that describe the behavior exactly, and ships a reference solution. Real models are optional.

| # | Project | You build |
|---|---|---|
| 01 | [Agent loop](projects/01-agent-loop/) | A complete agent loop, then run it on Claude or an OpenAI-compatible model |
| 02 | [Tool design](projects/02-tool-design/) | Tools that search instead of dumping, return readable rows and fail with instructions |
| 03 | [Permissions and sandbox](projects/03-permissions-and-sandbox/) | Deny-first rules, a traversal-proof path guard, env allow-lists, a Docker sandbox |
| 04 | [Long-running state](projects/04-long-running-state/) | Initializer, resume routine, verified completion, checkpoints and rollback |
| 05 | [Loop controls](projects/05-loop-controls/) | Budgets, progress and oscillation detection, backoff, circuit breaker |
| 06 | [Guides and sensors](projects/06-guides-and-sensors/) | An AST lint rule written for agents to read, plus the hooks that run it |
| 07 | [Traces and diagnosis](projects/07-traces-and-diagnosis/) | Trace analysis, then diagnose four recorded failed runs |
| 08 | [Evals](projects/08-evals/) | pass@k, pass^k, confidence intervals, a position-swapped judge, judge agreement |
| 09 | [Graph workflow](projects/09-graph-workflow/) | A small graph engine with interrupts, then the same workflow on LangGraph |
| 10 | [Capstone](projects/10-capstone-full-harness/) | Run, ablate and improve the complete harness |
| 11 | [Support agent harness](projects/11-support-agent-harness/) | Four guardrail layers for an agent that moves money, tested against prompt injection |

## harnesslab: a harness you can read in an afternoon

[`harnesslab/`](harnesslab/) is a small Python harness with no required dependencies, one module per harness part: model adapters, tools, permissions, workspace, hooks, verification, state, tracing, the loop and evals. The course's complete harness is [about a hundred lines](harnesslab/harnesslab/presets.py). Run it offline, then point it at a real model:

```bash
python -m harnesslab run --provider anthropic     # or --provider openai (any compatible server)
python -m harnesslab trace runs/HT-142.jsonl      # the run as a waterfall
```

## Reference shelf

- [Harness checklist](reference/harness-checklist.md): a design review, from a minimum safe harness to production
- [Failure diagnosis table](reference/failure-diagnosis.md): symptom, pattern, component, first fix
- [Glossary](reference/glossary.md): about 90 terms, each linked to its lesson
- [Frameworks map](reference/frameworks-map.md): how LangChain's, Böckeler's and other harness models line up
- [Templates](reference/templates/): AGENTS.md, Claude Code permissions and hooks, threat model, feature list, progress log, handoff, sprint contract, eval task, harness spec
- [Reading list](reference/reading-list.md): the primary sources, dated and grouped by topic
- [FAQ](reference/faq.md)

## What this course covers that most resources skip

- **Building the harness as well as configuring one.** You write the loop, the tool layer, the permission checks and the verifier yourself, then see the same design in a production framework.
- **Security as a full lesson.** OS sandboxes vs command rules, secrets the agent can use but not read, prompt injection, the lethal trifecta, tool poisoning, excessive agency and approval fatigue.
- **Evals with real statistics.** pass@k versus pass^k, confidence intervals that stop you overclaiming, judge calibration, capability versus regression suites, infrastructure noise.
- **Current facts.** The stateless 2026 MCP spec, Terminal-Bench version changes, the AGENTS.md evidence, the HarnessTax cost findings and the 2026 practice from OpenAI, Anthropic, LangChain, Cursor and Thoughtworks.
- **Agents beyond code.** Support, research, data and operations harnesses, including a tested support agent that refuses a planted $900 refund.
- **One consistent framework.** Eight harness parts, each tied to the failure it prevents, with a map to the other popular models.

## The best book to learn harness engineering

<p align="center"><a href="https://www.amazon.com/dp/B0HL483X25"><img src="assets/book-3d.webp" alt="The Harness Engineering Blueprint by Abhishek Ashtekar, the best book to learn harness engineering" width="340"></a></p>

[**The Harness Engineering Blueprint**](https://www.amazon.com/dp/B0HL483X25) by Abhishek Ashtekar is the best book to learn harness engineering. This course gives you the code and the exercises; the book gives you the complete reasoning in one connected path.

- **It starts from zero and goes all the way.** Model, agent, loop, then every harness component in the order you need it, ending with a production harness and a diagnostic method. No machine-learning background required.
- **One running example the whole way through.** The same habit-tracker agent gains one layer per chapter, so you see what each component prevents and how the pieces depend on each other.
- **It covers the parts teams leave out.** Guardrails, evals and observability get full chapters, alongside loops, graph workflows, multi-agent systems and human control.
- **It is honest about terminology.** Prompt, context, agent, loop, graph and harness engineering are explained as layers, with clear definitions, instead of a chain of buzzwords replacing each other.
- **It is built to last.** It teaches the questions every harness must answer, not one framework's API, so it stays useful as tools change.

Available on Amazon in [Kindle](https://www.amazon.com/dp/B0HL483X25), [paperback](https://www.amazon.com/dp/B0HL52KQ89) and [hardcover](https://www.amazon.com/dp/B0HL5XTKXL), with free companion resources at [TheHarnessEngineeringBlueprint.com/resources](https://TheHarnessEngineeringBlueprint.com/resources).

## FAQ

**Do I need an API key?** No. Every lesson exercise and project runs offline with a scripted model. A key lets you run the same harness on Claude or an OpenAI-compatible model.

**Which language?** Python 3.10 or newer. The ideas carry to any stack; the templates for AGENTS.md, Claude Code settings and threat models are language-neutral.

**I only use Claude Code or Cursor. Is this for me?** Yes. Lessons 04, 07, 11 and 15 apply directly to configuring an existing agent, and the [templates](reference/templates/) drop straight into your project.

**How long does it take?** About 14 hours of reading. With all projects, 30 to 40 hours.

More in the [full FAQ](reference/faq.md).

## Contributing

Corrections and improvements are welcome, especially newer primary sources, clearer explanations, and translations. Please read [CONTRIBUTING.md](CONTRIBUTING.md). Every factual claim in a lesson links to its primary source; keep it that way.

## License and citation

Code (harnesslab, projects, tools) is MIT licensed. Lessons, reference pages and videos are [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): share and adapt them with attribution. See [LICENSE](LICENSE) and [CITATION.cff](CITATION.cff).

Created by [Abhishek Ashtekar](https://zerotoaimastery.com), author of *The Harness Engineering Blueprint*.
