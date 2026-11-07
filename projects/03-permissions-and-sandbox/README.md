# Project 03: Permissions and a Sandbox

**Lesson:** [07. Sandboxes, permissions and security](../../course/07-sandboxes-permissions-and-security.md) · **Time:** 75 minutes · **Optional:** Docker

## What you build

In `exercise/guard.py`:

- `decide`: allow / ask / deny rules where any matching deny wins, regardless of rule order
- `check_write`: a path guard that refuses `../` escapes, absolute paths, symlinks out of the workspace, protected files and non-writable folders, and tells the agent where it may write
- `scrub_env`: the child environment built from an allow-list, never a deny-list
- `trifecta_report`: flags the lethal trifecta

In `sandbox/`: a Dockerfile and `run-in-sandbox.sh`, which runs one command with the network off, one mounted workspace, a non-root user, all capabilities dropped and resource limits.

## Why it matters

Rules steer normal behavior. Boundaries hold when rules miss. One test, `test_rules_are_tripwires_not_walls`, passes precisely because a deny rule on `git push*` does not catch `git -C . push`. Read it twice.

## Steps

1. Implement the four functions; `python -m pytest -q` until all pass.
2. With Docker: `docker build -t harness-sandbox:latest sandbox/`, then `sandbox/run-in-sandbox.sh ../../examples/habit-tracker "python -m pytest -q"`.
3. Prove the boundaries: run `curl https://example.com` and `touch /etc/x` through the script and confirm both fail.
4. Fill in the [threat model](../../reference/templates/threat-model.md) for an agent you use.

## Done when

- All five tests pass.
- You can name which boundary stops each of: a secret leaking over the network, a write to `~/.ssh`, a fork bomb.

## Stretch goals

- Add an egress allow-list with a proxy container instead of `--network none`.
- Wire `check_write` into Project 01's file tool.
