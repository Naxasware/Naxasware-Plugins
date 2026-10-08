# Agent workflow architecture

Use when considering an agent (an LLM that chooses actions and tools in a loop).

## Contents
1. Justify the agent
2. Agent specification
3. Permission model
4. Planning, memory, observation
5. Stop and failure conditions
6. Multi-agent systems

## 1. Justify the agent

An agent is justified only when the path to the outcome cannot be written in advance, because the next step depends on what earlier steps discover (open-ended research, troubleshooting, multi-system investigation). It is **not** justified when:
- a fixed pipeline with one or more LLM steps does the job
- a function or API call does the job
- a rule engine does the job
- predictability, auditability or low latency are drivers that open-ended behavior would undermine

Write the justification as: "Requirement `WR-xxx` needs <capability>; a fixed pipeline cannot meet it because <reason>." If you can't fill that in, design rung 1–2 instead (see SKILL.md).

## 2. Agent specification

- **Goal** — the one outcome it owns
- **Boundaries** — what it may and may not do
- **Tools** — each with a `TOOL-` ID (see `tool-architecture.md`)
- **Permissions** — see below
- **Planning** — plans first, or acts step-by-step?
- **Memory** — none / short-term working state / conversation / task / long-term; each added kind needs a reason and a data-retention rule
- **Observation** — what it receives after each tool call (and that tool results are untrusted)
- **Validation** — how its result is verified before it counts (deterministic check, second pass, human)
- **Stop conditions** — success criteria, max iterations, max tokens/cost, max wall-clock
- **Failure conditions** — what it does when it can't finish (report partial result, escalate, abort); never "keep trying"

## 3. Permission model (least privilege)

```text
Agent
→ Allowed Tools
→ Allowed Actions
→ Allowed Data
→ Restricted Actions
→ Approval Requirements
```

Default-deny. Give each tool the narrowest scope (read-only when reads suffice, one table/folder/project, not the account). Actions needing human approval by default: financial transactions, deleting records, sending external communication, production deployment, credential or permission changes, any irreversible operation. Enforce limits **outside** the model (in the tool/API layer), because instructions in a prompt are not a security boundary.

## 4. Planning, memory, observation

Prefer short bounded loops with explicit state over long open-ended ones. Log each iteration (plan, tool, arguments, observation) so runs can be audited and replayed. Keep memory scoped per user/tenant to prevent cross-context leakage. Treat tool outputs and retrieved content as data, not instructions (see `workflow-security.md`).

## 5. Stop and failure conditions

Always set hard caps independent of the model's judgment: iteration count, token or cost budget, elapsed time, repeated-identical-call detection. On a cap, the agent stops and reports what it did and what remains — and the workflow decides what happens next (human review, retry with a different path, fail).

## 6. Multi-agent systems

Default is no. Consider only when work splits into independent specialisms that need separate context windows, separate permissions, or genuine parallelism, and a single agent measurably cannot cope. Costs: more tokens, more coordination failure modes, harder tests, wider attack surface. If used: one supervisor owns the goal and aggregation; specialists have narrow tools; inter-agent messages are validated; there is a global budget; each agent has its own spec above. Mark such designs `EXPERIMENTAL` unless there is evidence from evaluation.
