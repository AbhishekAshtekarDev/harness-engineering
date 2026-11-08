# Frameworks Map

Different guides describe the harness with different lists. They overlap more than they disagree. This page maps each popular framework onto the eight parts this course uses, so you can read any source without translating in your head.

## The course's eight parts

| # | Part | Question | Lessons |
|---|---|---|---|
| 1 | Guidance | What does the agent know? | 4, 5 |
| 2 | Capability | What can it do? | 6 |
| 3 | Environment and boundaries | Where does it act, and what can it reach? | 7 |
| 4 | Continuity | What survives an interruption? | 8 |
| 5 | Checking | Is the work acceptable? | 9 |
| 6 | Visibility | What happened? | 10 |
| 7 | Correction | How do the agent and the harness improve? | 11 |
| 8 | Control flow | When does work start, branch and stop, and who decides? | 12, 13 |

## Mapping other frameworks

| Framework (source) | Its terms | Maps to |
|---|---|---|
| **LangChain**, [Anatomy of an Agent Harness](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) | System prompts · Tools, skills, MCP · Filesystem, sandbox, browser · Orchestration (subagents, handoffs, routing) · Hooks and middleware | 1 · 2 · 3 and 4 · 8 · 5 and 7 |
| **Böckeler / Thoughtworks**, [martinfowler.com](https://martinfowler.com/articles/harness-engineering.html) | Guides (feedforward) · Sensors (feedback) · Computational vs inferential · Steering loop · Maintainability, architecture fitness, behavior harnesses | 1 and 2 · 5 and 6 · a property of 5 and 7 · 7 · 5 by domain |
| **walkinglabs course**, lecture version | Instructions · Tools · Environment · State · Feedback | 1 · 2 · 3 · 4 · 5, 6 and 7 |
| **walkinglabs course**, README version | Instructions · State · Verification · Scope · Session lifecycle | 1 · 4 · 5 · 3 and 8 · 4 and 8 |
| **Panaversity crash course** | Four parts: agent loop, tool interface, context management, control mechanisms · Five verbs: constrain, inform, verify, correct, escalate | 8 · 2 · 1 · 3, 5, 8 · then 3 · 1 · 5 · 7 · 8 |
| **Aakash Gupta, Product Growth** | Instructions · Context · Skills · Memory · Permissions · Tools · Checks · The loop | 1 · 1 · 2 · 4 · 3 · 2 · 5 · 8 |
| **Anthropic**, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Augmented LLM (retrieval, tools, memory) · Workflows (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) · Agents | 1, 2, 4 · 8 · 8 |
| **Phil Schmid**, [Agent harness 2026](https://www.philschmid.de/agent-harness-2026) | Model = CPU · Context window = RAM · Harness = operating system · Agent = application | Analogy for the whole stack |
| **Google Research**, [Harness²](https://github.com/google-research/harness2) | System prompt · Guardrails · Memory · Tool guidance · Subagents · Skills · Scripts · Plugins | 1 · 5 · 4 · 2 · 8 · 2 · 2 · 2 |
| **LangChain**, [company harness](https://www.langchain.com/blog/components-building-company-harness) | Channel presence · Identity · Memory · Sandboxed execution · Scheduled runs | 8 · 3 · 4 · 3 · 8 |

## Where sources disagree

- **Is context engineering inside harness engineering, or the reverse?** HumanLayer treats harness engineering as a subset of context engineering. LangChain, OpenAI, Böckeler and this course treat context as one part of the harness. The practical work is identical either way.
- **Is the loop part of the harness?** Some sources draw the loop separately ("prompt, context, harness, loop"). This course places the agent loop inside the harness because the harness owns its limits and exits.
- **Who coined the term?** Mitchell Hashimoto's post (Feb 5, 2026) predates OpenAI's (Feb 11, 2026), and LangChain popularized the formula. Nobody has shown who used the phrase first anywhere, and it does not change the engineering.
