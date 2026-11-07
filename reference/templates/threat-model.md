# Threat model: <agent name>

## 1. What the agent can reach

| Capability | Yes / No | Details |
|---|---|---|
| Reads private data (code with secrets, customer records, email, internal docs) | | |
| Sees untrusted content (web pages, public issues, inbound email, third-party files, MCP results) | | |
| Communicates externally (network, comments, email, messages, URLs it can open) | | |

If all three are Yes, you have the **lethal trifecta**. Remove at least one leg before shipping:
split the agent, close the network, or keep secrets out of reach.

## 2. Tools and permissions

| Tool | Reads or writes | Reversible? | Credential behind it | Risk (L/M/H) | Control |
|---|---|---|---|---|---|
| | | | | | |

## 3. Worst realistic outcomes

For each high-risk tool or permission: what happens if the agent misuses it, by its own mistake or under an attacker's instructions?

| Scenario | Worst outcome | Acceptable? | Change that shrinks it |
|---|---|---|---|
| | | | |

## 4. Boundaries

- Filesystem: writable paths `...`; protected paths `...`; enforced by `...`
- Network: allowed hosts `...`; enforced by `...`
- Secrets: where they live `...`; how the agent uses them without reading them `...`
- Approvals: actions that need a person `...`; who approves `...`; timeout behavior `...`

## 5. Detection

- Which guardrails trip on this agent's abuse cases?
- Which adversarial tasks are in the eval suite?
- Who gets alerted, and on what threshold?
