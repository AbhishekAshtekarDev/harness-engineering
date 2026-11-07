# Failure Diagnosis Table

Keep this open the next time an agent goes wrong. Full method in [Lesson 15](../course/15-diagnosing-agent-failures.md).

## The five questions

Ask them at the **first** point the run went wrong:

1. What did the agent **see**? (context)
2. What could it **do**? (tools)
3. What was it **allowed** to do? (environment, permissions)
4. What **feedback** did it get, and was it accurate and useful? (checks)
5. What told it to **continue or stop**? (loop, success criteria)

Then: one event or a pattern? Could the check or the task be wrong? Does a stronger model succeed in the same harness?

## Symptom to fix

| Symptom | Pattern | Look at | First fixes to try |
|---|---|---|---|
| Rewrites a helper that exists; follows an old convention; misquotes a policy | Lacks information | Context sent at the decision point | Point to it from AGENTS.md; improve search; delete the stale doc; inject guidance when the file opens |
| Describes what to do instead of doing it; long shell workarounds | Cannot act | Tool calls and their errors | Add or consolidate a tool; rewrite the description; enums; actionable errors; a skill |
| Calls a tool with wrong arguments again and again | Cannot act | Schema and error messages | Clearer parameter names; examples in the description; errors that list valid values |
| Edits files outside scope; destructive commands; reads secrets | Unsafe action | Blocked and allowed calls, permissions | Narrow write paths; OS sandbox; remove the credential; approval gate |
| Follows instructions found in an issue, page or email | Unsafe action (injection) | Which untrusted text entered context | Break a trifecta leg; scan untrusted text; guard the dangerous tool in code |
| Same command repeated; edits flip back and forth | Repeats itself | Edits per file, action history | Progress detector; per-problem attempt cap with rollback; failed-approaches log; refuse repeated failed calls |
| Runs never end; costs spike | Repeats itself | Iterations, tokens, retries | Harness-owned budgets; self-event filter; circuit breaker |
| Redoes finished work after a crash or reset | Forgets progress | State vs what the context showed | Persist state; progress update before session end; feature list; commit per verified step |
| Opens a duplicate PR or sends a message twice | Forgets progress | Retries around side effects | Idempotent tools; check before create |
| Says "done" with parts missing | Finishes too early | Exit condition, success criteria | Checkable criteria; verification as the only success exit; acceptance tests first |
| Tests pass, users find the bug | Looks right, does not work | Test levels, who wrote the tests | End-to-end checks; held-out tests; acceptance tests; calibrated rubric grader |
| A fix sticks for one task and the mistake returns next week | Same mistake everywhere | Feedback timing and persistence | Lint rule with fix instructions after every edit; guidance before the action; regression eval |
| Nobody can say why it failed | Unexplainable | The trace itself | Record context sent, tool args and results, task IDs, versions |
| The judge passes work people reject | Wrong check | Judge vs human labels | Tighter rubric; one criterion per call; different model; UNKNOWN option; calibrate |
| Every agent fails the same vague ticket | Wrong task | The input | Ticket template with acceptance criteria; intake rejects tickets without them |

## Prefer fixes in this order

1. Remove the cause from the environment (fix the repo, the doc, the flaky test, the tool).
2. Enforce instead of request (deterministic check, permission, guardrail).
3. Targeted guidance at the moment it matters (hook, skill).
4. An inferential check (evaluator, rubric grader).
5. A short line in the general prompt.

Change one thing at a time, confirm with evals, and add the failure to the regression set.
