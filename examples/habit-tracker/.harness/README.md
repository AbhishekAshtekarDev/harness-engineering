# Harness-owned files

The harness copies the project into a fresh workspace for every task and
leaves this folder out, so the agent never sees these files.

- `acceptance/` tests a developer wrote from the ticket *before* the agent
  started. They define "done" independently of the agent's own tests.
- `heldout/` extra edge cases the agent is never told about. Passing them
  takes correct code, not code tuned to known examples.

During verification the harness copies these tests into the workspace, runs
them, and deletes them again.
