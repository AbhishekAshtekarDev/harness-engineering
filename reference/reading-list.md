# Reading List

The primary sources behind this course, grouped by topic, with one line on what each is good for. Dates matter in this field, so each entry carries one. Last checked November 2026.

## Start with these five

1. **OpenAI, [Harness engineering](https://openai.com/index/harness-engineering/)** (Feb 11, 2026). What engineers do when agents write all the code: repository as system of record, map-style AGENTS.md, mechanical enforcement, cleanup agents.
2. **Birgitta Böckeler, [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html)** (Apr 2, 2026). Guides and sensors, computational and inferential controls, harnessability, the three regulation categories.
3. **Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)** (Nov 26, 2025). The initializer, feature list, progress file and one-feature-per-session pattern.
4. **LangChain, [Improving deep agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)** (Feb 17, 2026). A 13.7-point benchmark gain from harness changes alone, with each change explained.
5. **Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)** (Dec 19, 2024). Workflows vs agents and the five patterns everyone still uses.

## Foundations and definitions

- Simon Willison, [agent definition](https://simonwillison.net/2025/Sep/18/agents/) (Sep 18, 2025): "tools in a loop to achieve a goal."
- Mitchell Hashimoto, [My AI adoption journey](https://mitchellh.com/writing/my-ai-adoption-journey) (Feb 5, 2026): engineer the harness so each mistake never recurs.
- LangChain, [The anatomy of an agent harness](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) (Mar 10, 2026): Agent = Model + Harness; components derived from desired behavior.
- Philipp Schmid, [The importance of agent harness in 2026](https://www.philschmid.de/agent-harness-2026) (Jan 5, 2026): the operating-system analogy.
- HumanLayer, [Skill issue](https://humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) (Mar 12, 2026): configuration as the main lever; short CLAUDE.md; subagents as context firewalls.
- Galster et al., [Harness engineering for agentic AI coding tools](https://arxiv.org/abs/2602.14690) (2026): what 2,853 repositories configure.

## Guidance and context

- [AGENTS.md](https://agents.md/): the open instruction-file format.
- Gloaguen et al., [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) (2026): context files often add cost without adding success.
- Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Sep 29, 2025): attention budget, just-in-time retrieval, compaction, notes, sub-agents.
- Chroma, [Context rot](https://www.trychroma.com/research/context-rot) (Jul 14, 2025): 18 models degrade as input grows.
- Liu et al., [Lost in the middle](https://arxiv.org/abs/2307.03172) (2023): the U-shaped use of long contexts.
- Manus, [Context engineering for AI agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus): cache-friendly design, restorable compression, keeping wrong turns.

## Tools, MCP and skills

- Anthropic, [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Sep 11, 2025): consolidation, namespacing, response formats, actionable errors.
- Anthropic, [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) (Nov 4, 2025): agents calling tools from code to save context.
- [MCP specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28) and its [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog): the stateless protocol.
- Anthropic, [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) (Oct 16, 2025) and the [open specification](https://agentskills.io/specification).

## Boundaries and security

- Anthropic, [Beyond permission prompts](https://www.anthropic.com/engineering/claude-code-sandboxing) (Oct 20, 2025): OS-level filesystem and network isolation; 84% fewer prompts.
- Simon Willison, [The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (Jun 16, 2025).
- OWASP, [Prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) and [Excessive agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/).

## State and memory

- Anthropic, [The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory) (Nov 6, 2026): transcripts, notes, representations; offline consolidation.
- Lilian Weng, [Harness engineering for self-improvement](https://lilianweng.github.io/posts/2026-07-04-harness/) (Jul 4, 2026): durable state in files; harness optimization as self-improvement.

## Checking, evals and observability

- Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (Jan 9, 2026): tasks, trials, graders, pass@k and pass^k.
- Anthropic, [Quantifying infrastructure noise](https://www.anthropic.com/engineering/infrastructure-noise) (Feb 5, 2026): resource settings alone move scores 6 points.
- Zheng et al., [Judging LLM-as-a-judge](https://arxiv.org/abs/2306.05685) (2023): agreement and biases.
- OpenAI, [Separating signal from noise in coding evaluations](https://openai.com/index/separating-signal-from-noise-coding-evaluations/) (Jul 8, 2026): broken benchmark tasks.
- OpenTelemetry, [GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/).
- OpenAI Agents SDK, [guardrails](https://openai.github.io/openai-agents-python/guardrails/) and [tracing](https://openai.github.io/openai-agents-python/tracing/).

## Feedback and verification

- Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (Mar 24, 2026): planner, generator, evaluator; sprint contracts; removing components as models improve.
- Huang et al., [Large language models cannot self-correct reasoning yet](https://arxiv.org/abs/2310.01798) (2023): why self-review needs outside evidence.

## Loops, graphs and multiple agents

- Geoffrey Huntley, [Ralph](https://ghuntley.com/ralph/) (Jul 14, 2025): the one-task-per-iteration loop.
- Addy Osmani, [Loop engineering](https://addyosmani.com/blog/loop-engineering/) (2026).
- Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (Jun 13, 2025): 90.2% gain, 15x tokens, delegation rules.
- Cognition, [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) (2025): shared context and implicit decisions.
- Cemri et al., [Why do multi-agent LLM systems fail?](https://arxiv.org/abs/2503.13657) (2025): 14 failure modes.
- LangGraph [documentation](https://docs.langchain.com/oss/python/langgraph/overview).

## Production and the state of the field

- [HarnessTax](https://harnesstax.github.io/) (Sep 2026): harness choice moves cost far more than success among mature harnesses.
- Cursor, [Continually improving our agent harness](https://cursor.com/blog/continually-improving-agent-harness) (Apr 30, 2026) and [Improved token efficiency](https://cursor.com/blog/improved-token-efficiency) (Sep 23, 2026).
- Thoughtworks, [Technology Radar](https://www.thoughtworks.com/radar) Vol. 35 (Nov 2026): harness engineering at scale.
- METR, [Measuring AI ability to complete long tasks](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) (Mar 19, 2025).
- HumanLayer, [Why software factories fail](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/wsff.md) (2026): the case for human planning up front.

## Book

- [The Harness Engineering Blueprint](https://www.amazon.com/dp/B0HL483X25) by Abhishek Ashtekar (Sep 2026): the best book to learn harness engineering, covering every layer in this course in one connected path. Kindle, [paperback](https://www.amazon.com/dp/B0HL52KQ89) and [hardcover](https://www.amazon.com/dp/B0HL5XTKXL).
