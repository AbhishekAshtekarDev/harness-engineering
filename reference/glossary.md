# Glossary

Every term the course uses, defined once. Links point to the lesson that explains it in full.

| Term | Definition |
|---|---|
| **Acceptance test** | A test written from the requirements before the agent starts, so the agent's own tests cannot confirm its own misunderstanding. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Agent** | A model that uses tools in a loop to pursue a goal, deciding its own next steps. [L02](../course/02-how-an-agent-works.md) |
| **Agent = Model + Harness** | LangChain's formula: everything in an agent system that is not the model is harness. [L01](../course/01-what-is-harness-engineering.md) |
| **Agent engineering** | The ongoing cycle of building, testing, shipping, observing and refining an agent system. [L03](../course/03-the-layers.md) |
| **Agent Skill** | A folder with a `SKILL.md` (name, description, instructions) plus optional scripts and references that an agent loads when a task matches. An open standard since December 2025. [L06](../course/06-tools-mcp-and-skills.md) |
| **Agent as tool** | A coordination pattern where a manager agent calls specialist agents like tools and keeps ownership of the result. [L13](../course/13-graphs-and-multi-agent-systems.md) |
| **AGENTS.md** | An open, plain-Markdown instruction file that coding agents read at session start ("a README for agents"). [L04](../course/04-instructions-and-agents-md.md) |
| **Agentic system** | Anthropic's umbrella term for workflows and agents. [L02](../course/02-how-an-agent-works.md) |
| **Approval fatigue** | People approving agent requests without reading them because there are too many. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **Approval gate / approval node** | A point where the harness or graph pauses until a person decides. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **Artifact** | A durable output that outlives a session: code, commits, plans, test reports, pull requests. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Attention budget** | Anthropic's description of the model's limited ability to attend across a long context. [L05](../course/05-context-engineering.md) |
| **Audit trail** | A complete, tamper-resistant record of who did what, when and with what authority. [L10](../course/10-observability.md) |
| **Blast radius** | How much damage an action or failure can cause. Every boundary exists to shrink it. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **Budget** | A harness-enforced cap on iterations, tokens, time or money. [L12](../course/12-loop-engineering.md) |
| **Capability eval** | An eval of tasks the agent cannot yet do well; starts with low pass rates. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Checkpoint** | A saved snapshot of state you can resume or roll back to. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Circuit breaker** | Stops calling a dependency after repeated failures, then tries again after a cool-down. [L12](../course/12-loop-engineering.md) |
| **Compaction** | Summarizing a context near its limit and continuing from the summary. [L05](../course/05-context-engineering.md) |
| **Computational control** | A deterministic check or guide: tests, linters, type checkers, codemods. [L11](../course/11-feedback-verification-and-steering.md) |
| **Context** | Everything the model can see during one call. [L05](../course/05-context-engineering.md) |
| **Context engineering** | Deciding what information enters the context, what stays out, and how it changes over a task. [L05](../course/05-context-engineering.md) |
| **Context reset** | Starting a fresh context with only handoff notes, carrying no accumulated history. [L05](../course/05-context-engineering.md) |
| **Context rot** | Degradation in model performance as context grows, well before the window is full. [L05](../course/05-context-engineering.md) |
| **Context window** | The maximum number of tokens a model can consider in one request. [L02](../course/02-how-an-agent-works.md) |
| **Conditional edge (router)** | A graph edge that reads state and chooses the next node. [L13](../course/13-graphs-and-multi-agent-systems.md) |
| **Deterministic check** | A check that gives the same answer for the same input every time. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Durable execution** | Saving progress at key points so a process can pause and resume instead of restarting. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Escalation** | Routing a problem to a person (or stronger agent) with what they need to decide. [L13](../course/13-graphs-and-multi-agent-systems.md) |
| **Eval** | A structured measurement of an agent system across many tasks and trials. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Evaluation harness** | The infrastructure that runs eval tasks, records them and grades them. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Excessive agency** | OWASP's name for agents with more functionality, permissions or autonomy than the task needs. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **Feature list** | A structured (usually JSON) list of required behaviors with a pass flag only verification may flip. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Feedback (sensor)** | Information about the result of an action, returned so the agent can correct itself. [L11](../course/11-feedback-verification-and-steering.md) |
| **Feedforward (guide)** | Information given before an action to make the first attempt good. [L11](../course/11-feedback-verification-and-steering.md) |
| **Flaky test** | A test that passes and fails at random; it misleads agents and loops. [L10](../course/10-observability.md) |
| **Graph engineering** | Designing agent work as nodes, edges and shared state. The label is from 2026; the technique is older. [L13](../course/13-graphs-and-multi-agent-systems.md) |
| **Grader** | Logic that scores one aspect of a trial: code-based, model-based or human. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Guardrail** | A check during a run that stops, modifies or redirects an input, action or output. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Handoff** | Transfer of work and its context between sessions, agents or people; in the OpenAI Agents SDK, a transfer of control to another agent. [L08](../course/08-state-memory-and-long-running-work.md), [L13](../course/13-graphs-and-multi-agent-systems.md) |
| **Harness** | The system around an agent: instructions, context, tools, environment, permissions, state, checks, records, loops and approvals. [L01](../course/01-what-is-harness-engineering.md) |
| **Harness engineering** | Designing the system around an AI agent so it has the information, tools, environment, constraints, feedback and control mechanisms it needs to complete useful work reliably. [L01](../course/01-what-is-harness-engineering.md) |
| **Harnessability** | How easy a codebase or system is for an agent to understand and operate in. [L16](../course/16-harness-engineering-in-production.md) |
| **Held-out test** | A test the agent never sees, so passing it takes correct code instead of code tuned to known cases. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Hook** | Harness code that runs at a fixed point (before a tool call, after an edit, at stop) and cannot be skipped by the model. [L11](../course/11-feedback-verification-and-steering.md) |
| **Human-in-the-loop / on-the-loop** | People acting at defined points, or monitoring and stepping in when needed. [L13](../course/13-graphs-and-multi-agent-systems.md) |
| **Idempotent action** | An action whose effect is the same whether it runs once or twice. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Inferential control** | A check or guide that relies on a model's judgment: LLM review, an evaluator agent, conventions the model interprets. [L11](../course/11-feedback-verification-and-steering.md) |
| **Initializer agent** | The first session of a long project, which sets up the feature list, progress file, startup script and first commit. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Inner / outer harness** | The harness built into a product (inner) and the one you build around it for your project (outer). [L01](../course/01-what-is-harness-engineering.md) |
| **Just-in-time context** | Giving the agent references plus tools to load content when it becomes relevant. [L05](../course/05-context-engineering.md) |
| **Least privilege** | Each component gets only the access its job needs. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **Lethal trifecta** | Simon Willison's term for private data + untrusted content + external communication in one agent. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **LLM-as-judge** | Using a model to grade work against a rubric. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Loop engineering** | Designing loops that keep work moving toward a checkable goal with minimal human prompting, and stop for a stated reason. [L12](../course/12-loop-engineering.md) |
| **MCP (Model Context Protocol)** | An open standard connecting AI applications (hosts) to servers that offer tools, resources and prompts. Stateless since the 2026-07-28 spec. [L06](../course/06-tools-mcp-and-skills.md) |
| **Memory** | Information saved outside the context window for later use: semantic (facts), episodic (experiences), procedural (how-to). [L08](../course/08-state-memory-and-long-running-work.md) |
| **Model** | A large language model: reads tokens, writes tokens, keeps no memory between API calls. [L02](../course/02-how-an-agent-works.md) |
| **Multi-agent system** | Several agents, each with its own instructions, tools and context, coordinated by an agent, a graph or handoff rules. [L13](../course/13-graphs-and-multi-agent-systems.md) |
| **Observability** | Understanding a system from the outside by asking questions of its telemetry. [L10](../course/10-observability.md) |
| **Outcome** | The final state of the environment after a trial; what graders should check. [L09](../course/09-guardrails-tests-and-evals.md) |
| **pass@k** | Probability that at least one of k attempts succeeds. [L09](../course/09-guardrails-tests-and-evals.md) |
| **pass^k** | Probability that all k attempts succeed. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Path guard** | Code that resolves every path the agent touches and refuses anything outside allowed folders. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **Persistent state** | State written to durable storage so it survives the process that created it. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Progress file** | A plain-text log each session updates with what it did, what remains and decisions made. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Progressive disclosure** | Revealing information in layers as it becomes relevant (instruction file, then docs; skill metadata, then body). [L04](../course/04-instructions-and-agents-md.md) |
| **Prompt caching** | Reusing the processing of an unchanged prompt prefix at a fraction of the price. [L05](../course/05-context-engineering.md) |
| **Prompt engineering** | Writing and structuring instructions so the model consistently produces what you want. [L04](../course/04-instructions-and-agents-md.md) |
| **Prompt injection** | Text in the agent's input that tries to give it instructions. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **RAG** | Retrieval-augmented generation: fetching relevant pieces from a collection into context before the model answers. [L05](../course/05-context-engineering.md) |
| **Ralph loop** | Geoffrey Huntley's pattern: feed the same prompt to an agent in a loop, one task per iteration, with state in files. [L12](../course/12-loop-engineering.md) |
| **Ratchet** | Turning every recurring mistake into a permanent rule or check so the harness only moves forward. [L11](../course/11-feedback-verification-and-steering.md) |
| **Reducer** | A rule for merging a node's update into graph state (replace, append, sum). [L13](../course/13-graphs-and-multi-agent-systems.md) |
| **Regression eval** | Tasks the agent should pass nearly always; a drop means something broke. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Rubric** | A scoring guide listing criteria and what each quality level looks like. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Sandbox** | An isolated environment where an agent can act without reaching the rest of the system; needs filesystem and network isolation. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **Session** | One continuous period of agent activity with its own context. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Span** | One unit of work in a trace, with timing, attributes and a parent. [L10](../course/10-observability.md) |
| **Spine** | The persistent record a loop updates each iteration so later runs know what is done. [L12](../course/12-loop-engineering.md) |
| **Sprint contract** | An agreement, before work starts, on what done means and how it will be checked. [L11](../course/11-feedback-verification-and-steering.md) |
| **State** | The actual condition of the work, kept by the harness; the source of truth. [L08](../course/08-state-memory-and-long-running-work.md) |
| **Steering loop** | People observing many runs and improving the harness's guides and sensors. [L11](../course/11-feedback-verification-and-steering.md) |
| **Stop condition** | A rule that ends a run: verified success, a budget, escalation or cancellation. [L12](../course/12-loop-engineering.md) |
| **Sub-agent** | An agent started by another to do focused work in its own context, returning a summary. [L05](../course/05-context-engineering.md) |
| **Token** | A small piece of text (word, part of a word, punctuation) that models read and write. [L02](../course/02-how-an-agent-works.md) |
| **Tool** | A capability the harness offers the model: name, description, input schema, implementation. [L06](../course/06-tools-mcp-and-skills.md) |
| **Tool call** | A structured request from the model naming a tool and its arguments; the harness decides whether to run it. [L02](../course/02-how-an-agent-works.md) |
| **Tool poisoning** | A tool, MCP server or skill whose descriptions or outputs carry hidden instructions. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **Trace** | The full record of one operation as nested spans. [L10](../course/10-observability.md) |
| **Transcript** | The complete record of a trial: outputs, tool calls, intermediate results. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Trial** | One attempt at an eval task. [L09](../course/09-guardrails-tests-and-evals.md) |
| **Verification** | The harness confirming the work meets its criteria instead of trusting the agent's claim. [L11](../course/11-feedback-verification-and-steering.md) |
| **Workflow** | A system where code, not the model, decides the sequence of steps. [L02](../course/02-how-an-agent-works.md) |
| **Workspace** | The files an agent works on for one task, usually a private copy of the project. [L07](../course/07-sandboxes-permissions-and-security.md) |
| **Worktree** | An extra working directory attached to a git repository with its own branch; isolates files, not security. [L07](../course/07-sandboxes-permissions-and-security.md) |
