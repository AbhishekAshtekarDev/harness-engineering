---
name: harness-review
description: Review the agent harness of the current project (instruction files, permission settings, hooks, tests, evals, tracing, stop rules) against the harness engineering checklist and produce a prioritized list of gaps with concrete fixes. Use when asked to audit, review or improve how coding agents are set up in a repository, or after an agent failure to find which part of the harness to change.
license: MIT
---

# Harness review

Review this project's harness with the eight-part model: guidance, capability,
environment and boundaries, continuity, checking, visibility, correction, control flow.

## Steps

1. Inventory what exists. Look for: AGENTS.md / CLAUDE.md (length, whether rules trace to failures),
   `.claude/settings.json` or other agent permission files, hooks, MCP server configs, skills,
   test suites and how to run them, CI checks, linters and type checkers, eval sets, trace or
   log configuration, sandbox or container setup, and any progress or feature-list files.
2. For each item in `references/checklist.md`, mark present, partial or missing, quoting the file
   and line that shows it.
3. Check the lethal trifecta: can one agent read private data, see untrusted content and
   communicate externally? Name each leg you find.
4. If the user describes a recent agent failure, run the five diagnostic questions at the first
   point it went wrong (what it saw, could do, was allowed to do, what feedback it got, what told
   it to stop) and name the component.
5. Report gaps ordered by risk, then by effort. For each gap give the smallest fix and prefer, in
   order: removing the cause, enforcing in code, targeted guidance at the right moment, an
   inferential check, and only last a new line in the instruction file.

## Output format

- A one-paragraph summary.
- A table: part, status, evidence, fix.
- The top three changes to make this week.

Do not change files unless the user asks. Keep the report under 600 words.
