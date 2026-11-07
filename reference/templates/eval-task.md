# Eval task: <id>

- **Source:** <real failure, ticket, or production trace link>
- **Type:** capability | regression
- **Input:** <the exact prompt or ticket>
- **Environment setup:** <repo commit, fixtures, seed data>
- **Trials:** <e.g. 3>; report pass@k and pass^k

## Success criteria
Two experts reading the outcome should independently agree on pass or fail.

| Criterion | Grader | Pass condition |
|---|---|---|
| Hidden tests pass | code | exit code 0 |
| No files outside allowed paths changed | code | changed-files check passes |
| Report states changes and assumptions accurately | model (rubric below) | PASS |

## Rubric (one model call per criterion; UNKNOWN allowed)
- **Report accuracy.** PASS if every file the report lists changed and every changed file is listed; FAIL otherwise; UNKNOWN if the diff is unavailable.

## Notes
- Grade the outcome (final state), not the path.
- Read the transcripts of failing trials before changing anything.
