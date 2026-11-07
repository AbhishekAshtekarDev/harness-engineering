# The Course

Eighteen lessons in nine parts, from how an agent works to running a harness in production. Each lesson opens with a one-line idea to remember, states what you will learn, and ends with self-check questions, a hands-on exercise and the primary sources worth reading next.

## Curriculum

| # | Lesson | One idea to remember | Hands-on | Time |
|---|---|---|---|---|
| **Part 1** | **Foundations** | | | |
| 01 | [What harness engineering is](01-what-is-harness-engineering.md) | The model supplies intelligence; the harness decides what it can see, touch and prove | `harnesslab demo` | 35 min |
| 02 | [How an AI agent works](02-how-an-agent-works.md) | An agent is twenty lines of loop; reliability lives around them | [P01 Agent loop](../projects/01-agent-loop/) | 40 min |
| 03 | [The layers: from prompt to harness](03-the-layers.md) | New layers wrap old ones; use the map to find the bug | | 25 min |
| **Part 2** | **Guidance** | | | |
| 04 | [Instructions and AGENTS.md](04-instructions-and-agents-md.md) | A map, not a manual; every line traces to a mistake | [Template](../reference/templates/AGENTS.md) | 40 min |
| 05 | [Context engineering for harnesses](05-context-engineering.md) | The context window is a desk, not a filing cabinet | | 45 min |
| **Part 3** | **Capability** | | | |
| 06 | [Tools, MCP and Agent Skills](06-tools-mcp-and-skills.md) | A tool is a product whose user is a model | [P02 Tool design](../projects/02-tool-design/) | 50 min |
| **Part 4** | **Boundaries** | | | |
| 07 | [Sandboxes, permissions and security](07-sandboxes-permissions-and-security.md) | Rules are tripwires; the sandbox is the wall | [P03 Permissions and sandbox](../projects/03-permissions-and-sandbox/) | 60 min |
| **Part 5** | **Continuity** | | | |
| 08 | [State, memory and long-running work](08-state-memory-and-long-running-work.md) | Write down what the next session needs | [P04 Long-running state](../projects/04-long-running-state/) | 50 min |
| **Part 6** | **Checking and visibility** | | | |
| 09 | [Guardrails, tests and evals](09-guardrails-tests-and-evals.md) | A test checks code, an eval checks the agent, a guardrail stops the run | [P08 Evals](../projects/08-evals/) | 60 min |
| 10 | [Logs, traces and observability](10-observability.md) | Record what the model saw as well as what it said | [P07 Traces](../projects/07-traces-and-diagnosis/) | 45 min |
| **Part 7** | **Correction** | | | |
| 11 | [Feedback, verification and the steering loop](11-feedback-verification-and-steering.md) | Guides before, sensors after; improve both when a mistake repeats | [P06 Guides and sensors](../projects/06-guides-and-sensors/) | 50 min |
| **Part 8** | **Control flow** | | | |
| 12 | [Loop engineering](12-loop-engineering.md) | Design the system that types the next prompt, and the rule that stops it | [P05 Loop controls](../projects/05-loop-controls/) | 50 min |
| 13 | [Graphs and multi-agent systems](13-graphs-and-multi-agent-systems.md) | Put the process on paper; add an agent only for a reason | [P09 Graph workflow](../projects/09-graph-workflow/) | 60 min |
| **Part 9** | **Putting it together** | | | |
| 14 | [Build a complete harness](14-build-a-complete-harness.md) | Work backward from success the harness can check | [P10 Capstone](../projects/10-capstone-full-harness/) | 75 min |
| 15 | [Diagnosing agent failures](15-diagnosing-agent-failures.md) | A failure has an address; find it before touching the prompt | [P07 Traces](../projects/07-traces-and-diagnosis/) | 50 min |
| 16 | [Harness engineering in production](16-harness-engineering-in-production.md) | Version everything; re-test every assumption when the model changes | [Checklist](../reference/harness-checklist.md) | 60 min |
| 17 | [Harnesses beyond coding](17-harnesses-beyond-coding.md) | Change the domain; the eight parts stay | [P11 Support agent](../projects/11-support-agent-harness/) | 40 min |
| 18 | [Real harnesses: case studies](18-case-studies.md) | Read what teams built, broke and removed | | 45 min |

Reading time is about 14 hours. With all eleven projects, plan on 30 to 40 hours.

## Three ways through

**I use Claude Code, Codex or Cursor every day and want better results this week.** Read 01, 04, 07, 11 and 15. Write a short AGENTS.md from the [template](../reference/templates/AGENTS.md), turn on your agent's sandbox, add one lint rule whose message explains the fix, and use the [failure table](../reference/failure-diagnosis.md) the next time the agent goes wrong.

**I build agents and want to understand every layer.** Go in order. Do every project. By Project 10 you will have built, tested and ablated a complete harness.

**I lead a team adopting agents.** Read 01, 03, 09, 13, 15 and 16, then the [harness checklist](../reference/harness-checklist.md). The ablation in Project 10 is a good team exercise.

## Setup

You need Python 3.10 or newer. Nothing else is required for the lessons, the demo or the projects.

```bash
git clone https://github.com/AbhishekAshtekarDev/harness-engineering.git
cd harness-engineering
python -m pip install -e "harnesslab[dev]"
cd harnesslab && python -m harnesslab demo
```

Every project runs offline with a scripted model, so you can see exact harness behavior without an API key. To use a real model, install `anthropic` or `openai`, set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`, and set `HARNESSLAB_MODEL` to a current model name. `OPENAI_BASE_URL` points the OpenAI adapter at any compatible server, including local ones.

## How each project works

Each project has an `exercise/` folder with the parts you write marked `TODO`, a `solution/` folder, and tests:

```bash
cd projects/03-permissions-and-sandbox
python -m pytest -q              # tests your exercise/ code (fails until you finish)
SOLUTION=1 python -m pytest -q   # tests the reference solution
```

On Windows PowerShell, use `$env:SOLUTION=1; python -m pytest -q`.
