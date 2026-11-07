# Harness Checklist

A design review for any agent harness. Not every task needs every item; for each unchecked box, write down why the task does not need it.

## Minimum safe harness

The smallest set worth running unattended on real work.

- [ ] Success criteria the harness can check without asking the agent
- [ ] The agent's "done" triggers verification; only a passing verdict counts as success
- [ ] Writes limited to the task's folders, enforced in code or by an OS sandbox
- [ ] Network closed, or limited to an allow-list
- [ ] No secrets readable by the agent; credentials live in tools or a proxy
- [ ] Iteration, token and time limits enforced by the harness
- [ ] A trace of every model call and tool call, with the task ID
- [ ] A person approves anything irreversible (merge, deploy, payment, customer message)

## Guidance

- [ ] Instruction file under about 100 lines, written by hand, each rule traceable to a failure
- [ ] Heavy terms defined; examples cover edge cases
- [ ] Stale and contradicting documents removed from what the agent can find
- [ ] Deeper docs linked, not pasted (progressive disclosure)
- [ ] Stable prompt prefix (system prompt, instructions, tools) identical and first on every call

## Capability

- [ ] The fewest tools that cover the task; no overlapping tools
- [ ] Each description says what the tool does, what it returns and when to use it
- [ ] Inputs have unambiguous names and enums where values are fixed
- [ ] Outputs shaped: filtered, sorted, capped, with meaningful identifiers
- [ ] Errors say what went wrong and what to do next
- [ ] Each tool rated low, medium or high risk; high-risk tools gated or absent
- [ ] Every MCP server and skill reviewed before use

## Environment and boundaries

- [ ] A fresh, disposable workspace per task (container, VM or OS sandbox)
- [ ] Path guard resolves symlinks and `../`; protected files listed
- [ ] Command allow / ask / deny rules, with the sandbox as the real boundary
- [ ] Child-process environment built from an allow-list
- [ ] No agent holds production credentials; no single agent has the lethal trifecta
- [ ] Worst realistic outcome written down and acceptable

## Continuity

- [ ] Task state persisted outside the process, written atomically
- [ ] Progress file or task record updated before any session ends
- [ ] Structured feature list; status changes only after verification
- [ ] Checkpoint after each verified step, before risky actions and before approvals
- [ ] Resume routine: read records, run checks, then continue
- [ ] Side-effecting tools are idempotent
- [ ] Memory writes carry their source and are reviewed before they become permanent

## Checking

- [ ] Fast checks after every edit (lint, types, related tests)
- [ ] Acceptance tests written from requirements before work starts
- [ ] Held-out tests the agent never sees; existing tests protected
- [ ] Input, tool and output guardrails where the domain needs them
- [ ] Eval suite of 20 to 50 real tasks with code, model and human graders
- [ ] pass^k tracked where the agent must work every time
- [ ] LLM judges calibrated against human labels
- [ ] A separate evaluator for work the builder should not grade

## Visibility

- [ ] Context sent, model output, tokens and stop reason recorded per call
- [ ] Tool name, arguments, result and the harness's decision recorded per call
- [ ] Versions of model, prompts, tools, hooks and permissions in every trace
- [ ] Metrics: success, cost and duration per task, tool error rates, escalations
- [ ] Alerts with owners, kept few and meaningful
- [ ] Trace access restricted; sensitive fields redacted; retention set

## Correction and control flow

- [ ] Failure signals computed from traces (repeated edits, flat progress, rising tokens)
- [ ] Transient failures retried with backoff; substantive ones change the approach
- [ ] Rollback after repeated failure on one problem
- [ ] Escalation packages the task, attempts, stopping point and decision needed
- [ ] Event triggers ignore the agent's own activity
- [ ] Graph cycles carry attempt counters; graphs cap total steps
- [ ] Multiple agents only where each solves a named problem
- [ ] A regular review that adds controls for recurring failures and removes ones that never fire

## Production

- [ ] Model pinned to a snapshot; upgrades go through regression evals and gradual rollout
- [ ] Every behavior-shaping component versioned and reviewed like code
- [ ] Deploys do not switch agents mid-task (rainbow or equivalent)
- [ ] Queues and concurrency limits for provider rate limits
- [ ] Cost tracked per successful task; budgets per task, loop and team
- [ ] Adversarial tasks (injection attempts) in the eval suite
- [ ] Named owner for each agent and for the harness
- [ ] Audit records answer who did what, when, with what authority
- [ ] Each model upgrade: remove scaffolding one piece at a time and measure
