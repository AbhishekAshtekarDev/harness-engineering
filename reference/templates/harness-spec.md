# Harness spec: <agent name>

One page. If a section is empty, write why the task does not need it.

| Part | Decision |
|---|---|
| Goal and boundaries | <what it does; what it never does> |
| Success criteria (task) | <checks the harness runs> |
| Success criteria (harness) | <metrics and targets> |
| Guidance | <instruction file, task template, docs it can reach> |
| Context | <loaded up front vs fetched on demand; compaction policy> |
| Tools | <list with risk level each; deliberate omissions> |
| Environment | <workspace, sandbox, network, test data> |
| Permissions | <writable paths, rules, credentials, approvals> |
| State and memory | <task record, progress file, feature list, memory rules> |
| Tests and guardrails | <unit, integration, e2e, acceptance, held-out; input/tool/output guardrails> |
| Evals | <task count, graders, trials, regression set> |
| Observability | <trace contents, metrics, alerts, retention, access> |
| Loop and stop rules | <triggers, budgets, progress detection, exits> |
| Recovery | <retries, checkpoints, rollback, idempotency, escalation> |
| Human control | <who approves what; escalation queue> |
| Not included, and why | <components left out on purpose> |
