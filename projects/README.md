# Projects

Eleven hands-on projects. Each one builds one part of a harness as small, tested Python, so you can see exactly what the part does. Everything runs offline with a scripted model; real models are optional.

| # | Project | You build | Lesson | Time |
|---|---|---|---|---|
| 1 | [Agent loop](01-agent-loop/) | A complete agent loop, then run it on a real model | 2 | 45 min |
| 2 | [Tool design](02-tool-design/) | Tools that search, shape output and fail helpfully | 6 | 60 min |
| 3 | [Permissions and sandbox](03-permissions-and-sandbox/) | Deny-first rules, a path guard, env scrubbing, trifecta check, a Docker sandbox | 7 | 75 min |
| 4 | [Long-running state](04-long-running-state/) | Initializer, resume routine, verified completion, checkpoints, rollback | 8 | 75 min |
| 5 | [Loop controls](05-loop-controls/) | Budgets, progress and repeat detection, backoff, circuit breaker | 12 | 60 min |
| 6 | [Guides and sensors](06-guides-and-sensors/) | An AST lint rule written for agents, and the hooks that run it | 11 | 60 min |
| 7 | [Traces and diagnosis](07-traces-and-diagnosis/) | Trace analysis code, then diagnose four recorded failed runs | 10, 15 | 75 min |
| 8 | [Evals](08-evals/) | pass@k, pass^k, confidence intervals, a two-order judge, judge agreement | 9 | 75 min |
| 9 | [Graph workflow](09-graph-workflow/) | A small graph engine with interrupts, then the same workflow on LangGraph | 13 | 90 min |
| 10 | [Capstone: full harness](10-capstone-full-harness/) | Run, ablate and improve the complete habit-tracker harness | 14 | 2 to 4 h |
| 11 | [Support agent harness](11-support-agent-harness/) | Four guardrail layers for an agent that moves money | 17 | 75 min |

## How to work on a project

```bash
cd projects/05-loop-controls
python -m pytest -q                 # tests your code in exercise/ (fails until you finish the TODOs)
SOLUTION=1 python -m pytest -q      # the reference solution, for comparison
```

Each `exercise/` file marks what you write with `TODO` comments and `NotImplementedError`. The tests describe the behavior exactly; read them first. Maintainers regenerate the exercise folders from the solutions with `python tools/make_exercises.py`.
