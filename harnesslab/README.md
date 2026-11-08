# harnesslab

A small, readable agent harness for learning harness engineering. About 1,000 lines of Python with no required dependencies. Every part of the harness is its own module, small enough to read in one sitting.

```bash
python -m pip install -e .            # from this folder
python -m harnesslab demo             # offline, scripted agent, no API key
python -m pytest -q tests             # 14 tests
```

## Modules

| Module | Harness part | What to read for |
|---|---|---|
| [`models.py`](harnesslab/models.py) | The model boundary | One neutral transcript format; a scripted model for deterministic runs; Anthropic and OpenAI-compatible adapters |
| [`tools.py`](harnesslab/tools.py) | Capability | Tool anatomy, schema validation, shaped outputs, errors that say what to do next |
| [`schema.py`](harnesslab/schema.py) | Validation | The JSON Schema subset tool inputs need |
| [`permissions.py`](harnesslab/permissions.py) | Boundaries | Deny-first rules; a path guard that resolves symlinks and `../` |
| [`workspace.py`](harnesslab/workspace.py) | Environment | A private copy per task; commands with timeouts, capped output and an allow-listed environment |
| [`hooks.py`](harnesslab/hooks.py) | Guides and sensors | Pre-tool vetoes, guidance on file open, checks after every edit |
| [`checks.py`](harnesslab/checks.py) | Verification | Tests (with acceptance and held-out tests copied in only for the check), changed-file checks, composition |
| [`state.py`](harnesslab/state.py) | Continuity | Task state written atomically, progress log, a feature list where only `passes` may change |
| [`trace.py`](harnesslab/trace.py) | Visibility | Spans with OpenTelemetry GenAI attribute names, JSONL output, a text waterfall |
| [`loop.py`](harnesslab/loop.py) | Control flow | The loop: verified exits, budgets, repeat refusal, no-progress detection, escalation |
| [`evals.py`](harnesslab/evals.py) | Evals | Trials, graders, pass@k, pass^k, an LLM-judge grader with an UNKNOWN option |
| [`presets.py`](harnesslab/presets.py) | All of it | The course's complete habit-tracker harness in about 100 lines |
| [`demo.py`](harnesslab/demo.py) | | A scripted agent that makes the mistakes real agents make |

## Real models

```bash
pip install anthropic          # or: pip install openai
export ANTHROPIC_API_KEY=...   # or OPENAI_API_KEY
export HARNESSLAB_MODEL=claude-sonnet-5-5    # any current model name for your provider
python -m harnesslab run --provider anthropic --trace runs/HT-142.jsonl
python -m harnesslab trace runs/HT-142.jsonl
```

`--interactive` asks you to approve "ask" actions in the terminal; without it, nobody is there to approve, so they are refused. `--keep` keeps the workspace so you can inspect the agent's changes. `OPENAI_BASE_URL` points the OpenAI adapter at any compatible server, including local models.

## Limits, on purpose

- The workspace is a copied folder and commands run as your user. That organizes the work; it does not isolate it. For real isolation, run the harness inside the container from [Project 3](../projects/03-permissions-and-sandbox/), or use an OS sandbox.
- Command rules match text. They steer behavior and are easy to bypass on purpose. Lesson 7 explains why the sandbox, not the rules, is the boundary.
- The token counts in the demo are estimates (four characters per token).

harnesslab is a teaching harness. For production work, use a maintained framework or product and apply the same design decisions.
