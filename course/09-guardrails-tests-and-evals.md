# 09. Guardrails, Tests and Evals

> A test checks the code. An eval checks the agent. A guardrail stops the run. Know which question you are asking.

**You will learn** the four families of checks and where each belongs, how agents game tests and how to stop it, how to design evals with tasks, trials and graders, why pass@k and pass^k tell different stories, and how to use an LLM judge without fooling yourself.
**Time:** 60 minutes · **Video:** [pass@k vs pass^k (1:00)](../videos/README.md#09-pass-at-k-vs-pass-pow-k) · **Project:** [08. Evals](../projects/08-evals/) · **Template:** [Eval task and rubric](../reference/templates/eval-task.md)

---

## Four families of checks

| Check | Question | When it runs | Example |
|---|---|---|---|
| Guardrail | Should this be allowed to happen or pass through? | During the run, and it can stop it | Block an edit outside `habit_tracker/`; stop a $900 refund |
| Validation | Does this data follow fixed rules? | Whenever data crosses a boundary | The agent's final report matches its JSON schema |
| Test | Does this code behave correctly? | After changes | `weekly_streak` returns 4 for four good weeks |
| Eval | How well does the agent perform across many tasks? | Before releases and changes, and on samples of production | Time-zone tickets succeed in 9 of 10 trials |

A single harness usually uses all four. The time-zone concern shows them working together: a unit test confirms a Tokyo user's streak, schema validation confirms the report is well formed, an output guardrail confirms no forbidden file changed, and an eval measures how often the agent handles time-zone tickets across many trials. The first three protect one run. The eval tells you whether the system is getting better or worse.

## Guardrails

A **guardrail** inspects what flows through the system and stops, modifies or redirects work that crosses a line. Permissions decide what the agent can do at all; guardrails look at the content of each specific input, output or action. OpenAI's [guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) treats guardrails as layered defense, since no single one is enough.

| Where | Checks | Habit-tracker | Support agent |
|---|---|---|---|
| Input | The request before the agent spends effort | Ticket labelled by a maintainer; no text aimed at AI agents; length limit | Reject "ignore previous instructions" messages |
| Tool | Each call's arguments and results | Edits only in allowed folders; block destructive commands | Refunds over $100 go to a person |
| Output | What leaves the harness | No secrets in the diff; report claims match recorded test results | No other customer's email in the reply |

The [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/guardrails/) runs input guardrails either in parallel with the agent (lower latency, but the agent may already have acted) or blocking (the input never reaches the agent if rejected), and it runs tool guardrails on each guarded call, which matters when agents hand work to one another. Guardrails can be deterministic code or a small model classifying content. Both stop the run.

## Validation: schemas and business rules

**Schema validation** checks structured data against its shape: required fields, types, allowed values. If the agent's final report lacks the `tests_passed` boolean, the harness rejects it and asks again instead of passing malformed data on.

**Business rules** encode domain policy: a weekly target between 1 and 7, a streak that is never negative, no reminders before 8 a.m. local time. A prompt can state them. Code enforces them, either as a guardrail during the run or as a test that tries to save a target of 0 and expects an error.

These are **deterministic checks**: same input, same answer, fast and cheap, with failures that explain themselves. Anthropic's eval guidance lists the strengths: fast, cheap, objective, reproducible and easy to debug. Whenever a property can be checked by a fixed rule, check it that way.

## Tests, and how agents game them

| Level | Checks | Speed | Habit-tracker example |
|---|---|---|---|
| Unit | One function in isolation | Milliseconds | Four good weeks give 4; a missed week gives 0 |
| Integration | Pieces working together | Seconds | Save completions through the data layer, read the streak back |
| End-to-end | The app as a user sees it | Seconds to minutes | Open the habit page, complete three times, advance the clock, see a badge of 1 |

Anthropic's long-running agents marked features complete after unit tests while the feature did not work for a user; results improved substantially once the agent tested through a browser. Use all three levels: unit tests for fast feedback while working, integration for the seams, end-to-end for the final confirmation.

An agent rewarded for passing tests can pass them without doing the work: delete a failing test, weaken an assertion, or special-case the exact inputs a test uses. Anthropic's prompt told its agent that editing or removing tests was unacceptable. Back that request with enforcement:

- make existing test files read-only for tasks that should not change them (the habit-tracker `PathGuard` protects them);
- flag any change to test files for review;
- run tests yourself in a clean environment, never trusting the agent's report of results;
- keep **acceptance tests** written from the requirements before work starts, so the agent's own tests cannot confirm its own misunderstanding;
- keep **held-out tests** the agent never sees ([`examples/habit-tracker/.harness/`](../examples/habit-tracker/.harness/) does this).

**Linters and type checkers** are the fastest deterministic checks, cheap enough to run after every edit. Custom lint rules can encode your architecture and conventions, and their messages can tell the agent how to fix the problem. [Lesson 11](11-feedback-verification-and-steering.md) builds one.

## Evals

An **eval** measures an agent system across a set of tasks. Anthropic's [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) gives the vocabulary:

| Term | Meaning |
|---|---|
| Task | One test case with inputs and success criteria |
| Trial | One attempt at a task; run several, because agents vary |
| Grader | Logic that scores one aspect of a trial |
| Transcript | The full record of a trial: outputs, tool calls, intermediate results |
| Outcome | The final state of the environment when the trial ends |
| Evaluation harness | The infrastructure that runs tasks, records them, grades and aggregates |

Transcript and outcome differ in an important way. A flight-booking agent may *say* the flight is booked; the outcome is whether a reservation exists in the database. Grade outcomes.

Evaluating an agent always evaluates the model and the harness together. The runtime environment counts too: Anthropic measured [infrastructure noise](https://www.anthropic.com/engineering/infrastructure-noise) moving Terminal-Bench 2.0 scores by 6 percentage points from resource configuration alone, and advises treating leaderboard gaps under 3 points as unreliable unless configurations match.

### Success criteria first

Write criteria that are specific and measurable, usually several per task. Anthropic's test for a well-defined task: two domain experts looking at the same result would independently reach the same verdict. If they would disagree, the ambiguity becomes noise in every score.

### Three kinds of grader

| Grader | Good at | Weak at |
|---|---|---|
| Code-based (tests, state checks, string match) | Fast, cheap, consistent | Qualities fixed rules cannot express |
| Model-based (LLM-as-judge with a rubric) | Open-ended quality: clarity, intent, convention | Varies between runs, costs more, needs calibration |
| Human | Most trustworthy; the reference for the others | Slow, expensive |

Grade the outcome, not the path. Agents find valid approaches you did not anticipate, and a grader that demands one sequence of steps punishes correct work.

### Using a model as judge

The 2023 paper by Zheng and colleagues that popularized [LLM-as-judge](https://arxiv.org/abs/2306.05685) found strong judges agreeing with human preferences more than 80% of the time, about as often as humans agree with each other. It also documented the biases you must design around:

| Bias | Design response |
|---|---|
| Position bias (favors the first answer) | Compare in both orders; treat disagreement as a tie |
| Verbosity bias (favors longer answers) | Rubric criteria that reward correctness, not length |
| Self-enhancement (favors its own model family's writing) | Use a different model from the one that did the work |
| Weak on reasoning-heavy questions | Prefer code graders where a fixed check exists |

Give the judge a specific rubric, judge one criterion per call, require structured output, and give it an **UNKNOWN** option so it does not invent a verdict. Then check it against human labels on a sample and keep checking. [Project 08](../projects/08-evals/) implements the two-order comparison and Cohen's kappa for judge-human agreement.

### pass@k and pass^k

Agents vary from trial to trial, so you read rates, not single results. Two numbers answer two different questions:

- **pass@k**: the probability that at least one of k attempts succeeds. Right when a person can retry and one success is enough.
- **pass^k**: the probability that all k attempts succeed. Right when the agent must work every time, such as a customer-facing or unattended agent.

With 75% success per trial, pass^3 is about 0.75³, roughly 42%, while pass@3 is about 98%. The two numbers diverge fast as k grows. The eval suite in [Project 08](../projects/08-evals/) shows it with two scripted agents:

```text
agent              passed          95% CI   pass@3   pass^3
careful (0.9)       9/10        0.60-0.98     1.00     0.70
hasty (0.5)         6/10        0.31-0.83     0.97     0.17
```

On pass@3 the two agents look nearly identical. On pass^3 one is four times as dependable. The confidence intervals overlap, which is the other lesson: ten trials rarely prove that one version beats another.

### Capability evals and regression evals

**Capability evals** target what the agent cannot yet do well; they start with low pass rates and give you a hill to climb. **Regression evals** cover what it already does; they should pass nearly every time, and a drop means a change broke something. Tasks graduate from capability to regression once the agent passes them reliably. Run the regression set on every change to a prompt, tool, hook, permission or model.

Start small. Anthropic suggests 20 to 50 tasks drawn from real failures; LangChain suggests starting with 10 to 20 examples from real traces. Early changes have large effects, so a small suite catches them. And read the transcripts behind the scores: a failed task may be an agent mistake or a grader that rejected a valid solution, and only the transcript tells you which.

## Human review

The last check is a person. Human review catches what automation misses, such as a feature that meets every written criterion and solves the wrong problem. Review capacity is limited, and people who review too much stop reviewing carefully. Automated checks are what make human review sustainable: by the time a pull request reaches a reviewer, guardrails, linters, type checks, three levels of tests and a rubric grader have already passed it, so the reviewer can spend attention on intent and design.

## Check yourself

<details><summary>1. The agent says "all tests pass." What does the harness do with that sentence?</summary>

Nothing, except log it. The harness runs the tests itself in a clean environment, including acceptance and held-out tests, and records the outcome.
</details>

<details><summary>2. Your support agent succeeds 90% of the time per conversation. A customer contacts support four times this month. What is the chance every contact goes right?</summary>

About 0.9⁴ ≈ 66%. That is the pass^k view, and it is the number your customer experiences.
</details>

<details><summary>3. Version B of your harness scores 9/10, version A scored 7/10. Ship B?</summary>

Not on that evidence alone. The 95% intervals overlap widely. Run more tasks and trials, and read the failing transcripts to see whether B fixed a real cause.
</details>

<details><summary>4. Your LLM judge passes 95% of pull requests; human reviewers pass 60%. What do you check?</summary>

Calibration. Compare judge and human labels case by case, compute agreement (for example Cohen's kappa), and tighten the rubric, split criteria into separate calls, use a different model, and add an UNKNOWN option.
</details>

## Try it

Do [Project 08: Evals](../projects/08-evals/). You implement pass@k, pass^k, Wilson confidence intervals, a comparison that refuses to overclaim, a two-order pairwise judge, and Cohen's kappa, then run `run_suite.py` against two scripted agents on the habit-tracker ticket.

## Go deeper

- Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) and [Quantifying infrastructure noise](https://www.anthropic.com/engineering/infrastructure-noise).
- OpenAI, [Separating signal from noise in coding evaluations](https://openai.com/index/separating-signal-from-noise-coding-evaluations/): why roughly 30% of SWE-Bench Pro tasks turned out to be broken, and what that means for your own task sets.
- LangChain, [The most common questions about agent evals](https://www.langchain.com/blog/common-questions-about-agent-evals).

**Next:** [10. Logs, Traces and Observability](10-observability.md)
