# Harness Engineering in Production

Lesson 16 of 18 · Putting It Together · about 60 minutes

In this lesson you will learn what changes when a harness moves from prototype to production: reliability targets, security against attackers, cost and caching, latency, model selection and upgrades, versioning and deployment, scale, governance, harnessability, drift, and how to simplify a harness as models improve.

**Checklist:** [Production readiness](../reference/harness-checklist.md#production)


---

Anthropic's engineers, describing the move from research prototype to production, wrote that for agents the last mile often becomes most of the journey ([multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)). In production the agent handles work people depend on, at a volume nobody reviews item by item, for months, while the model, the codebase, the tools and the team all change, and some inputs come from people trying to misuse it.

## Reliability

Turn the definition (acceptable results across real inputs; visible, safe failure otherwise) into measured targets: task success rate, consistency across trials (pass^k), escalation rate, reviewer acceptance rate. Measure results, not uptime: a service that always responds can still be wrong a third of the time.

Plan for failures outside the agent. Providers have outages, APIs change, sandboxes fail to start. Degrade gracefully: queue tasks until the provider recovers, fall back to another model where acceptable, route urgent work to people, and record what happened instead of failing silently.

## Security

OWASP lists prompt injection first among risks for LLM applications, and any agent that reads outside content will meet injection attempts. The defenses are the layers from [Lesson 7](07-sandboxes-permissions-and-security.md): OS-level sandboxes, least privilege for every tool and credential, designs that keep the lethal trifecta out of any one agent, guardrails on inputs, tool calls and outputs, and audit trails. Production adds two practices:

- **Review every new tool, MCP server and skill** before an agent can use it, as you would a third-party library.
- **Keep adversarial tasks in the eval suite**, such as tickets containing injection attempts, so you know the defenses hold and notice when a change weakens them.

## Cost

Tokens are the largest cost for most agents, and input tokens dominate, because each loop iteration resends everything before it. Anthropic measured agents using about 4 times the tokens of chat and multi-agent systems about 15 times.

Harness design changes the bill more than many teams expect. The [HarnessTax study](https://harnesstax.github.io/) found that mature coding harnesses differed by up to 5 times in cost on the same tasks with similar success; one popular harness's initial context was more than ten times larger than a minimal one's. Practical controls:

| Control | What it does |
|---|---|
| Budgets per task, per loop per day, per team | Caps what any run can spend (Lesson 12) |
| Shaped tool output, cleared old results | Fewer tokens per call (Lessons 5, 6) |
| Fewer, dynamically loaded tools | Cursor cut static tool-description tokens by 60% this way |
| Shorter system prompt | Cursor trimmed its prompt by about two thirds; token costs fell 7% with no quality loss |
| **Prompt caching** | Reuses processing of an unchanged prompt prefix; Anthropic prices cache reads at roughly a tenth of normal input on most models, and caching also cuts latency |
| Smaller models for simple steps | Classification and routing rarely need the largest model |

Caching rewards a harness that keeps system instructions, the instruction file and tool definitions identical and first on every call. Track **cost per successful task**, not cost per run: a cheap harness that fails half the time can cost more than an expensive one that succeeds.

## Latency

Latency comes from model generation, the number of sequential steps, tool runtime and verification. Factory reported that in its long-running work most elapsed time goes to validation that operates the live application. Anthropic reported that parallel tool calls and starting several subagents at once cut research time by up to 90%. Run fast deterministic checks before slow ones, so a problem a linter catches never waits on an end-to-end test. For interactive products, showing progress and letting people redirect the agent matters as much as raw speed.

## Model selection and upgrades

Choose models on **your** evals inside **your** harness, weighing cost, latency, context size, tool-use reliability and data terms. Public leaderboards describe a model inside someone else's harness, and models are partly trained on their own vendor's harness, so swapping harnesses can regress results. Cursor gives each model the edit format it was trained on. Different steps can use different models: a strong lead with smaller subagents, as in Anthropic's research system.

Upgrades are a common source of production surprises: a better model overall can behave differently on your prompts, call tools differently or follow instructions more exactly as written. A disciplined upgrade:

1. Pin production to a specific model snapshot.
2. Run regression and capability evals with the new model and the current harness.
3. Compare success, consistency, cost and latency; read a sample of traces.
4. Roll out gradually, starting with a small share of tasks, with a fast path back.
5. Use the upgrade to look for scaffolding the new model no longer needs (see the end of this lesson).

## Regression testing and versioning

Treat the harness as software. Run the regression suite on every change to anything that shapes behavior: prompts, instruction files, tool definitions, skills, hooks, permissions, graph structure, model, framework version. Every diagnosed production failure adds a task, so the suite becomes a record of everything the system has learned.

Version every behavior-shaping component and record the versions in every trace. Deploy carefully, because agents may be mid-task when a new version lands. Anthropic's answer for its research system was **rainbow deployments**: old and new versions run side by side while traffic shifts gradually, so running agents finish on the version they started with.

## Scale

Providers cap request rates, so the harness needs queues and concurrency limits. Each task needs its own isolated environment, created on demand and removed after. Shared resources cause contention: parallel tasks sharing one test database interfere, and parallel pull requests conflict at merge.

Parallel work moves the bottleneck to people. OpenAI's team found that as agents produced more code, human capacity to check it became the limit, and Thoughtworks' Radar Vol. 35 describes review as the bottleneck when teams run many agent sessions. Scale review by strengthening automated checks, not by lowering the bar for approval.

## Production permissions, governance and audit

- Separate production from development. Agents reach production only through the reviewed deploy path people use. Agents that must touch production start read-only, use narrow tools, and need approval for any change.
- Keep secrets in a **secrets manager** that issues scoped, short-lived credentials. Secrets never appear in context or traces.
- Review permissions periodically. They tend to grow, one reasonable request at a time.

**Governance** decides which tasks agents may do, who owns each agent, which actions need approval, how new tools and permissions are reviewed, what data agents may touch and how incidents are handled. Frameworks such as the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) (govern, map, measure, manage) help structure it. For the harness engineer it becomes concrete: a named owner per agent, reviewed harness changes, documented approvals for high-risk actions, an incident process, and audit records that exist. Auditability means you can answer, months later, why a refund was issued, who approved a merge, which harness version was running, and what the agent saw. Build it in from the start; adding it after an auditor asks is much harder.

People stay responsible for goals, standards and the decisions that shape what agents do. Böckeler puts the aim well: a good harness should not aim to eliminate human input entirely, but direct it to where it matters most.

## Harnessability

**Harnessability** is how easy a system is for an agent to understand and operate in. Böckeler notes that strongly typed languages give type checking as a free sensor, clear module boundaries make architectural rules enforceable, and opinionated frameworks reduce what the agent must get right. Legacy systems need a harness most and are hardest to harness. OpenAI's team pursued harnessability directly by making the repository the system of record for knowledge that would otherwise live in chat threads and people's heads. A codebase an agent can find its way around is usually one a new developer can too.

## Three kinds of harness

Böckeler groups controls by what they regulate:

| Harness | Regulates | Maturity | Examples |
|---|---|---|---|
| Maintainability | Internal code quality | Most mature: plenty of tooling | Duplication, complexity, coverage and style sensors; model review for semantic duplication |
| Architecture fitness | Performance, dependency structure, observability | Growing | Fitness functions; OpenAI's fixed layers (Types, Config, Repo, Service, Runtime, UI) enforced by custom linters and structural tests |
| Behavior | Does the app do what users need? | Least solved | Specs as guides plus tests as sensors; AI-written tests are not yet trustworthy enough alone |

Behavior is where human judgment matters most. Acceptance tests written before the work, evaluators that operate the app, held-out tests and production monitoring all help; none removes the need for people to confirm the software does what users need.

## Drift and garbage collection

At agent speed, inconsistencies, dead code, stale docs and copied patterns accumulate in code that passes every test. OpenAI's team used to spend every Friday, 20% of the week, cleaning up. It replaced that with encoded "golden principles" and recurring background agents that open small refactoring PRs, plus a doc-gardening agent that fixes documentation that no longer matches the code. Böckeler recommends continuous sensors outside any single change: dead-code detection, coverage quality, dependency scanners.

The harness drifts too: instructions go stale, rules contradict each other, tool descriptions fall out of step with their APIs, and eval tasks stop resembling current work. Give the harness an owner and a review schedule. Ask which checks never fire (are they unnecessary, or blind?), whether eval tasks still match real work, whether tool descriptions match tool behavior, and whether instructions describe the product as it is. Remove as readily as you add.

## Simplify as models improve

Anthropic stated the principle directly in its [harness design work](https://www.anthropic.com/engineering/harness-design-long-running-apps): every component in a harness encodes an assumption about what the model cannot do alone, and those assumptions deserve testing because they can be wrong and they go stale. Their own first attempt to simplify cut too much at once, lost performance and made it hard to see which parts mattered. They switched to removing one component at a time and measuring. When a stronger model arrived, they dropped the sprint structure, because the model could break the work down itself, and reduced the evaluator to one final pass, which still added value at the edge of the model's ability. The space of useful harnesses shifts as models improve, instead of shrinking.

Some components exist for reasons unrelated to model skill and stay:

| Removable as models improve | Stays regardless |
|---|---|
| Step-by-step planning scaffolds | Permissions and sandboxes |
| Self-check prompts and intermediate evaluators | Verification that provides evidence |
| Heavy context curation for weaker models | Audit trails and versioned records |
| Many narrow tools | Human approval for irreversible, high-stakes actions |

The routine: at each model upgrade, run the evals with each piece of scaffolding removed in turn; keep what still improves results; remove the rest.

## Where this is heading

Teams are starting to automate the steering loop itself. Lilian Weng argues that near-term self-improvement is more likely to come through [harness optimization than through changing weights](https://lilianweng.github.io/posts/2026-07-04-harness/). Google Research's [Harness²](https://github.com/google-research/harness2) proposes, probes and composes harness edits with model weights frozen. LangChain's trace-analyzer skill turns error analysis into targeted harness changes. All of them need hard-to-game evaluators and permissions kept outside the loop being optimized. Thoughtworks predicts that an "enterprise harness" may become a product category, much as platform engineering did.

## Check yourself

<details><summary>1. A new model scores higher on public benchmarks. What do you do before switching?</summary>

Run your regression and capability evals with the new model inside your harness, compare success, consistency, cost and latency, read traces, then roll out gradually with a fast path back. Pin snapshots so the model does not change underneath you.
</details>

<details><summary>2. Your cost per run fell 30% after a change, and success fell from 80% to 55%. Better or worse?</summary>

Compute cost per successful task: 0.7 / 0.55 is about 1.27 times the old cost per success. Worse, before counting the cost of the extra failures.
</details>

<details><summary>3. Name two components you would keep even if the model never made a mistake.</summary>

Any two of: permissions and sandboxes (limit damage from attacks), verification (evidence for people who rely on the work), audit trails (accountability), human approval for irreversible actions (responsibility).
</details>

## Go deeper

- Böckeler, [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html): harnessability, regulation categories, harness templates.
- OpenAI, [Harness engineering](https://openai.com/index/harness-engineering/): entropy, garbage collection and merge philosophy at high throughput.
- HarnessTax, [harnesstax.github.io](https://harnesstax.github.io/): cost and success across 21 model and harness pairs.

**Next lesson:** [Harnesses Beyond Coding](17-harnesses-beyond-coding.md)
