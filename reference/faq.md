# Frequently Asked Questions

## Basics

**What is harness engineering, in simple terms?**
Building everything around an AI model that turns it into an agent you can trust with real work: what it is told, what it can see, which tools it gets, where it runs, what it may touch, how its work is checked, what gets recorded, and when it stops or asks a person. The model does the reasoning; the harness makes the reasoning safe, grounded and checkable. [Lesson 1](../course/01-what-is-harness-engineering.md).

**Why is it called a harness?**
Two older meanings combine. A horse harness connects a strong animal to a cart and lets a driver steer it. A software test harness runs code under controlled conditions and checks results. An agent harness does both: it points the model's capability at a task and checks what comes out.

**What does Agent = Model + Harness mean?**
LangChain's formula: every part of an agent system that is not the model is harness. A raw model cannot keep state, run code, reach current information or set up an environment. The harness supplies all of that.

**Is an AI agent the same as a harness?**
No. The agent is the model using tools in a loop toward a goal. The harness is the system that provides the loop, the tools and everything around them. People often call a product like Claude Code "an agent" when it is a model running inside a substantial harness.

**Is Claude Code (or Codex, or Cursor) a harness?**
Each ships a built-in, or inner, harness: system prompt, tools, loop, compaction, permission handling. Your AGENTS.md or CLAUDE.md, permission rules, hooks, skills and tests form an outer harness around it. If you configure these tools, you already do harness engineering.

**Who invented harness engineering?**
The practices (test harnesses, sandboxes, retries, logs) are decades old. The name spread in early 2026: Mitchell Hashimoto wrote about "engineering the harness" on February 5, OpenAI published "Harness engineering" on February 11, and LangChain popularized Agent = Model + Harness. Nobody has shown who used the phrase first.

**What is an example of harness engineering?**
An agent kept writing date code with the server's UTC date. Instead of adding "be careful with time zones" to the prompt, the team added a lint rule that catches `.date()` on timestamps and tells the agent to use the time-zone helper, a hook that shows the date rule when the agent opens date code, and the failed tickets as regression evals. The mistake stopped recurring. [Lesson 11](../course/11-feedback-verification-and-steering.md).

## Comparisons

**Harness engineering vs prompt engineering?**
Prompt engineering is how you tell the model what you want. Harness engineering designs the whole system, and prompts are one part of it. A prompt can ask the agent never to edit config files; the harness makes it impossible.

**Harness engineering vs context engineering?**
Context engineering decides what the model sees on each call. Most sources treat it as one part of the harness, alongside tools, environment, permissions, state and checks. HumanLayer frames it the other way around. The work is the same either way. [Lesson 3](../course/03-the-layers.md).

**Harness engineering vs loop engineering?**
Loop engineering designs the cycles that keep work moving without a person prompting each step, and the rules that stop them. Loops run inside the harness and depend on its components (success criteria, verification, state, limits). [Lesson 12](../course/12-loop-engineering.md).

**Harness vs framework vs runtime vs SDK?**
A framework or SDK (LangGraph, OpenAI Agents SDK, Claude Agent SDK, Google ADK) is a toolkit for building harnesses. A runtime executes agent work durably. The harness is the specific system you assemble for your task from framework pieces, product features and your own code.

**Does the harness matter more than the model?**
Both matter, in different ways. LangChain raised a coding agent from 52.8% to 66.5% on Terminal-Bench 2.0 by changing only the harness. The HarnessTax study found that among mature harnesses, success differed by a few points while cost differed by up to 5 times. A missing harness costs you success; an overbuilt one costs you money.

## Practice

**Do AGENTS.md files work?**
Short, human-written ones built from observed failures do. An ETH Zurich study found context files in general did not improve success and raised cost over 20%, which matches the warning from OpenAI and others against long, generated files. Aim for about 60 to 100 lines that act as a map into your docs. [Lesson 4](../course/04-instructions-and-agents-md.md).

**What are guides and sensors?**
Birgitta Böckeler's terms. Guides steer the agent before it acts (instructions, skills, templates). Sensors check its work after (tests, linters, evaluators). You need both: without sensors the agent never learns whether rules worked; without guides it repeats mistakes.

**What is the ratchet principle?**
Every recurring mistake becomes a permanent rule or check, so the harness only moves forward. Hashimoto's version: when the agent makes a mistake, engineer a solution so it never makes that mistake again.

**How do I sandbox an agent on my own machine?**
Turn on your agent's built-in sandbox if it has one (Claude Code uses OS-level isolation; Codex defaults to no network). For stronger isolation, run commands in a Docker container with the network off, one mounted workspace, a non-root user and dropped capabilities. [Project 3](../projects/03-permissions-and-sandbox/) includes a ready script.

**How do I keep context across sessions?**
Write it down outside the model: a progress file, a structured feature list, commits after each verified step, and a resume routine that reads them and runs checks first. [Lesson 8](../course/08-state-memory-and-long-running-work.md).

**How many subagents should I use?**
Usually none, until a specific problem calls for them: independent verification, broad parallel research, more material than one context holds, or splitting permissions. Multi-agent systems use around 15 times the tokens of chat. [Lesson 13](../course/13-graphs-and-multi-agent-systems.md).

**How do I measure whether my harness is good?**
An eval suite of 20 to 50 real tasks, several trials each, graded on outcomes. Track success, pass^k for consistency, cost per successful task, escalation rate and reviewer acceptance. Run it on every harness change. [Lesson 9](../course/09-guardrails-tests-and-evals.md).

**Does a simple single-agent workflow need a harness?**
It already has one: whatever gives it tools and a loop. The question is how much to add. Add a component when a real failure calls for it, and keep the simplest harness that gives the task the reliability it needs.

**Why do agents fail in production even with a good harness?**
Production brings inputs you never tested, model upgrades, changed APIs, flaky dependencies, attackers and scale. The answers are evals built from production failures, pinned models with regression testing, monitoring, and a harness owner who keeps improving it. [Lesson 16](../course/16-harness-engineering-in-production.md).

**Which harness should I use with local or open models?**
Tool-call reliability varies most with local models. Prefer harnesses with few, clear tools and strict schema validation, give each model the edit format it handles best, and run your own small eval before committing. harnesslab's OpenAI adapter works with any OpenAI-compatible local server through `OPENAI_BASE_URL`.

## Learning and careers

**How do I learn harness engineering?**
Learn how an agent loop works, then add one harness component at a time and watch what each one prevents. This course does exactly that, with a runnable project for each part. Then apply it to the agent you use every day.

**What does a harness engineer do?**
Designs the environment, instructions, tools, permissions, checks and feedback loops around agents; reads traces to find why agents fail; turns recurring failures into permanent fixes; measures changes with evals; and keeps the harness simple as models improve. OpenAI's team describes the shift as engineers designing environments, specifying intent and building feedback loops instead of writing the code themselves.

**Is there a free harness engineering course?**
This one. Eighteen lessons, eleven projects with tests and solutions, and a small harness library you can read in an afternoon. MIT licensed for code, CC BY 4.0 for text.

**What is the best book to learn harness engineering?**
[The Harness Engineering Blueprint](https://www.amazon.com/dp/B0HL483X25) by Abhishek Ashtekar. It explains every concept from first principles in one connected path, from a single prompt to a production harness, and follows one running example through every layer. It pairs well with this course: the book gives the complete reasoning, the course gives you code to run.
