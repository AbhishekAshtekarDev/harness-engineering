#!/usr/bin/env bash
# Run one command for the agent inside a throwaway container.
#
#   ./run-in-sandbox.sh /path/to/workspace "python -m pytest -q"
#
# Boundaries, each one closing a specific hole:
#   --network none          no exfiltration, no surprise downloads (breaks a trifecta leg)
#   --read-only + --tmpfs   the image cannot be modified; scratch space lives in RAM
#   -v workspace:/work      the ONLY host folder the agent can see or change
#   --user 1000:1000        not root inside the container
#   --cap-drop ALL          no extra kernel capabilities
#   no-new-privileges       setuid binaries cannot raise privileges
#   --pids/--memory/--cpus  a runaway process cannot take the machine down
#   timeout                 every command has a time limit
#   no -e / --env-file      no host secrets enter the container
set -euo pipefail
WORKSPACE="$(cd "$1" && pwd)"
COMMAND="$2"
IMAGE="${SANDBOX_IMAGE:-harness-sandbox:latest}"

timeout --kill-after=5 "${SANDBOX_TIMEOUT:-300}" docker run --rm \
  --network none \
  --read-only --tmpfs /tmp:rw,size=256m --tmpfs /home/agent:rw,size=64m \
  -v "$WORKSPACE":/work:rw -w /work \
  --user 1000:1000 \
  --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 256 --memory 2g --cpus 2 \
  "$IMAGE" sh -c "$COMMAND"
