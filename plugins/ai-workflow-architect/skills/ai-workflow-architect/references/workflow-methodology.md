# Workflow methodology

The core passes, what each must produce, and how the modes use them. Read this for any Standard or Full design.

## Contents
1. Business context
2. Requirements (WR)
3. Drivers (WD)
4. Triggers
5. Steps and step types
6. Decisions (DEC)
7. Data flow and state
8. Orchestration and platform choice
9. Alternatives and trade-offs
10. Modes

## 1. Business context

Establish these before drawing anything. Mark each with its evidence tag; unknown ones become `Q-` entries only if they change the design.

- Business problem and objective (`BO-`), expected outcome, how success is measured
- Users, stakeholders, process owner, and who is accountable when it goes wrong
- Current process (what people/systems do today, where it hurts) and desired process
- Operational, compliance, geographic, budget and timeline constraints

Why this comes first: the same "send an email when a lead arrives" request is a three-step automation or a regulated approval flow depending on answers that live here.

## 2. Requirements (WR)

Categories: functional, automation, AI, integration, data, security, reliability, performance, human approval, monitoring, cost. Only create categories you have content for — an "AI requirements" section with no AI need is padding.

Each requirement: ID, description, source (evidence tag), priority, rationale, acceptance criteria, dependencies. A requirement is testable or it is marked "target not defined." Details in `output-schema.md`.

## 3. Drivers (WD)

Drivers are the forces that shape the architecture — the few requirements that make some options wrong. Examples: low latency, low cost, high reliability, mandatory human approval, large volume, sensitive data, complex reasoning, many integrations, asynchronous processing, auditability, real-time execution. A design with ten drivers has none; pick the three to five that actually eliminate options, and say which options each eliminates.

## 4. Triggers

Types: HTTP webhook, API event, database event, queue message, scheduler/cron, user action, file upload, email, form submission, application/CRM/payment/SaaS event, manual run, AI-generated trigger.

For every trigger define: source, event, payload shape, authentication (how you know it's genuine), validation, frequency, expected volume, failure behavior. Also decide what a **duplicate or replayed** trigger does — most real systems deliver at-least-once.

## 5. Steps

Every significant step defines: Step ID, name, purpose, type, input, processing, output, dependencies, failure behavior, retry strategy, timeout, security requirements, observability.

Types: trigger, action, transformation, condition, router, loop, aggregator, API call, database operation, AI call, agent, tool call, human approval, queue, delay, validation, notification, storage, search, retrieval, function/code.

Keep steps at a level where each one has a single purpose and a single failure story. A step that "fetches, enriches, decides and sends" has four failure modes hiding in one box.

## 6. Decisions (DEC)

Each decision point: input, method (rule / AI / human / hybrid), possible outputs, fallback. If the method involves AI, also specify model class, prompt purpose, output schema, confidence handling, validation, fallback and human escalation (see `ai-workflow-architecture.md`). Prefer a rule when one can be written; use AI where the input is unstructured or the judgment is fuzzy; use a human where the cost of being wrong is high.

## 7. Data flow and state

Trace: source → input → transformation → validation → processing → storage → output. Classify data as structured/unstructured, files/documents, metadata, embeddings, secrets, PII, business-sensitive, temporary vs persistent. Anything sensitive gets its handling stated here (see `workflow-security.md`).

Decide whether the workflow is stateless, stateful, session-based, task-based or event-sourced, and where state lives (database, workflow engine, queue, object storage, cache). Hidden state — something later steps depend on that no step declares — is the commonest cause of un-debuggable workflows. Don't recommend state infrastructure (a cache, a queue, an event store) without a requirement behind it.

## 8. Orchestration and platform choice

Options: application code, workflow-automation platform, queue, event bus, scheduler, serverless functions, custom orchestrator, agent runtime. Compare on complexity, reliability, observability, cost, vendor dependency, developer experience and scale.

Rules of thumb:
- Few steps, low volume, business-owned, tolerant of occasional manual re-run → a visual automation platform or plain code is usually enough.
- Long-running, must resume after failure, needs timers, human waits, or strict exactly-once-ish semantics → look at durable-execution/orchestration engines or a queue plus persisted state.
- Heavy custom logic or strict testing needs → application code with a thin scheduler.

Never assume a particular platform is the answer; state the requirement that points to it and the alternative you rejected. Verify any platform capability you rely on (`REQUIRES VALIDATION` if you can't).

## 9. Alternatives and trade-offs

For important workflows produce at least two real options (e.g. A deterministic, B AI-assisted, C agentic). For each: architecture, complexity, cost, reliability, scalability, maintainability, security, operational burden, advantages, disadvantages, when it fits. Then select one for this case, recording the decision as a `WADR-` (see `adr-template.md`).

## 10. Modes

| Mode | Start from | Produce |
|---|---|---|
| Greenfield | Goal/idea | Full pass 1→14 at the right depth |
| Existing-workflow analysis | Export, screenshots, description | Reconstruct steps, triggers, data, hidden state; mark `[OBSERVED]` vs `[INFERRED]` |
| Review | A design | Findings by severity against quality attributes and anti-patterns; what's solid vs missing |
| Optimization | Running workflow | Unnecessary steps, bottlenecks, latency, cost, reliability fixes, ranked by value |
| Modernization | Legacy automation | Target architecture, migration steps, what to keep, parity/rollback plan |
| AI transformation | Manual/traditional flow | Where AI adds value (rung 2), where it doesn't, evaluation plan |
| Agentic transformation | Workflow or goal | Verdict on whether an agent is justified, with the deciding requirement; else lower-rung design |
| Comparison | Two+ options | Side-by-side on shared criteria, no universal winner, selection for the stated context |
| Debugging | Failure symptoms/logs | Hypotheses ranked by evidence, how to confirm each, fix and prevention; do not guess root cause as fact |
| Scaling | Growth target | Bottleneck analysis (see `workflow-cost.md`), changes in order of necessity |
| Security review | Design or system | Threats by category (see `workflow-security.md`), required fixes |
| Cost optimization | Usage data | Cost drivers, labeled estimates, levers with trade-offs |
| Workflow-to-implementation | Approved architecture | `TASK-` list with dependencies, acceptance criteria and tests |
