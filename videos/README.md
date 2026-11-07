# Videos

Twelve short narrated explainers, one per core idea. Each one ends with the idea in one line. Watch them in your browser on the [course site](https://abhishekashtekardev.github.io/harness-engineering/videos/), or download the MP4 files from this folder.

| # | Video | Lesson |
|---|---|---|
| 01 | [What is harness engineering?](01-what-is-harness-engineering.mp4) | [Lesson 01](../course/01-what-is-harness-engineering.md) |
| 02 | [The agent loop](02-the-agent-loop.mp4) | [Lesson 02](../course/02-how-an-agent-works.md) |
| 03 | [Six layers, one map](03-the-layers.mp4) | [Lesson 03](../course/03-the-layers.md) |
| 04 | [Context rot, compaction and resets](04-context-rot-compaction-and-resets.mp4) | [Lesson 05](../course/05-context-engineering.md) |
| 05 | [Tools, MCP and skills](05-tools-mcp-and-skills.mp4) | [Lesson 06](../course/06-tools-mcp-and-skills.md) |
| 06 | [The sandbox and the lethal trifecta](06-sandbox-and-the-lethal-trifecta.mp4) | [Lesson 07](../course/07-sandboxes-permissions-and-security.md) |
| 07 | [Long-running agents](07-long-running-agents.mp4) | [Lesson 08](../course/08-state-memory-and-long-running-work.md) |
| 08 | [Guides and sensors](08-guides-and-sensors.mp4) | [Lesson 11](../course/11-feedback-verification-and-steering.md) |
| 09 | [pass@k vs pass^k](09-pass-at-k-vs-pass-pow-k.mp4) | [Lesson 09](../course/09-guardrails-tests-and-evals.md) |
| 10 | [Loops and stop conditions](10-loops-and-stop-conditions.mp4) | [Lesson 12](../course/12-loop-engineering.md) |
| 11 | [Loops, graphs and many agents](11-graphs-and-multi-agent.mp4) | [Lesson 13](../course/13-graphs-and-multi-agent-systems.md) |
| 12 | [Where is the bug?](12-diagnosing-failures.mp4) | [Lesson 15](../course/15-diagnosing-agent-failures.md) |


<a id="01-what-is-harness-engineering"></a>

## 01. What is harness engineering?

[![What is harness engineering?](posters/01.jpg)](01-what-is-harness-engineering.mp4)

**The idea:** The model supplies the intelligence. The harness makes it reliable.

Goes with [Lesson 01](../course/01-what-is-harness-engineering.md).

<a id="02-the-agent-loop"></a>

## 02. The agent loop

[![The agent loop](posters/02.jpg)](02-the-agent-loop.mp4)

**The idea:** The loop is easy. The harness around it is the work.

Goes with [Lesson 02](../course/02-how-an-agent-works.md).

<a id="03-the-layers"></a>

## 03. Six layers, one map

[![Six layers, one map](posters/03.jpg)](03-the-layers.mp4)

**The idea:** New layers wrap the old ones. Use the map to find the bug.

Goes with [Lesson 03](../course/03-the-layers.md).

<a id="04-context-rot-compaction-and-resets"></a>

## 04. Context rot, compaction and resets

[![Context rot, compaction and resets](posters/04.jpg)](04-context-rot-compaction-and-resets.mp4)

**The idea:** The context window is a desk. Put on it only what this step needs.

Goes with [Lesson 05](../course/05-context-engineering.md).

<a id="05-tools-mcp-and-skills"></a>

## 05. Tools, MCP and skills

[![Tools, MCP and skills](posters/05.jpg)](05-tools-mcp-and-skills.mp4)

**The idea:** Fewer tools, described well, with errors that say what to do next.

Goes with [Lesson 06](../course/06-tools-mcp-and-skills.md).

<a id="06-sandbox-and-the-lethal-trifecta"></a>

## 06. The sandbox and the lethal trifecta

[![The sandbox and the lethal trifecta](posters/06.jpg)](06-sandbox-and-the-lethal-trifecta.mp4)

**The idea:** Rules are tripwires. The sandbox is the wall.

Goes with [Lesson 07](../course/07-sandboxes-permissions-and-security.md).

<a id="07-long-running-agents"></a>

## 07. Long-running agents

[![Long-running agents](posters/07.jpg)](07-long-running-agents.mp4)

**The idea:** Write down what the next session needs.

Goes with [Lesson 08](../course/08-state-memory-and-long-running-work.md).

<a id="08-guides-and-sensors"></a>

## 08. Guides and sensors

[![Guides and sensors](posters/08.jpg)](08-guides-and-sensors.mp4)

**The idea:** Guides before, sensors after. Never trust "done".

Goes with [Lesson 11](../course/11-feedback-verification-and-steering.md).

<a id="09-pass-at-k-vs-pass-pow-k"></a>

## 09. pass@k vs pass^k

[![pass@k vs pass^k](posters/09.jpg)](09-pass-at-k-vs-pass-pow-k.mp4)

**The idea:** Measure the number your users live with.

Goes with [Lesson 09](../course/09-guardrails-tests-and-evals.md).

<a id="10-loops-and-stop-conditions"></a>

## 10. Loops and stop conditions

[![Loops and stop conditions](posters/10.jpg)](10-loops-and-stop-conditions.mp4)

**The idea:** Every run ends in success, or in a reason you can read.

Goes with [Lesson 12](../course/12-loop-engineering.md).

<a id="11-graphs-and-multi-agent"></a>

## 11. Loops, graphs and many agents

[![Loops, graphs and many agents](posters/11.jpg)](11-graphs-and-multi-agent.mp4)

**The idea:** Add an agent only when it solves a problem a simpler design cannot.

Goes with [Lesson 13](../course/13-graphs-and-multi-agent-systems.md).

<a id="12-diagnosing-failures"></a>

## 12. Where is the bug?

[![Where is the bug?](posters/12.jpg)](12-diagnosing-failures.mp4)

**The idea:** A failure has an address. Find it before you touch the prompt.

Goes with [Lesson 15](../course/15-diagnosing-agent-failures.md).

## How these were made

Each video is an HTML composition rendered frame by frame with [HyperFrames](https://github.com/heygen-com/hyperframes), narrated with the open Kokoro text-to-speech model, with CC0 sound effects from Kenney. The scripts and the generator live in [`build/`](build/): edit `specs.py`, run `make.py`, then render each project with `npx hyperframes render`.
