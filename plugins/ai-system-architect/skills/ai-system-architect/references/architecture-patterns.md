# Architecture Patterns

Read this before selecting or comparing architecture styles, or defining system/component/module structure.

## Architecture styles

Evaluate from this set based on what the drivers actually call for — not from familiarity or trend:

monolith, modular monolith, microservices, serverless, event-driven, service-oriented, layered architecture, hexagonal architecture, clean architecture, CQRS, event sourcing, distributed systems, edge architecture, hybrid architecture.

A style choice needs the same discipline as any other decision: state which drivers pushed toward it, and which alternative was rejected and why. "We chose microservices because the system has many features" is not a justification — feature count alone rarely demands independent deployability; team topology, independent scaling needs, or genuinely divergent technology requirements per component usually are the real drivers, when there are real drivers at all.

## Architecture Decision Records (ADRs)

For every architecturally significant decision — not every decision, just the ones that would be expensive to reverse or that another engineer would reasonably ask "why this?" about:

```
ADR-001

Title
Status          Proposed / Accepted / Rejected / Deprecated / Superseded
Context         What situation prompted this decision
Problem         What question is being answered
Options Considered
Decision        What was chosen
Rationale       Why, tied to specific drivers/constraints
Trade-offs      What was given up
Consequences    What this decision implies for later work
Related Requirements   AD-/FR-/NFR- IDs this traces to
```

Example:

```
ADR-001
Decision: Use a modular monolith for the MVP.
Context: Small development team, moderate initial scale (AD-003, AD-007).
Alternatives: Microservices, traditional monolith.
Reason: Strong module boundaries are needed for future team growth, but
current scale and team size don't justify distributed-systems complexity.
```

## System boundary

Before defining components, be explicit about what's inside vs. outside the system:

- **System** — the thing being architected
- **External actors** — humans or systems that interact with it from outside
- **External systems** — third-party or adjacent systems it integrates with
- **Internal components** — what's built and owned as part of this system
- **Trust boundaries** — where authentication/authorization must be enforced
- **Data boundaries** — where data ownership changes hands

## Component architecture

For each major component, define (the ID is `COMP-001`, `COMP-002`, … and is defined once; other documents cite it):

```
Component ID
Name
Purpose
Responsibilities
Inputs / Outputs
Dependencies
Owned data
APIs exposed
Failure behavior     what happens to callers when this component is down
Scaling strategy
Security considerations
```

## Module boundaries

Draw modules around meaningful business responsibilities the input actually supports — authentication, user management, orders, payments, inventory, reporting, notifications, AI services, administration are common examples, not a checklist to fill in regardless of relevance. Don't create a module just because a noun appears in the requirements; a module should correspond to a real cohesive responsibility with its own data and rules, not to every entity mentioned in passing.

## Anti-patterns — reach for these only when a driver justifies them

Never default to any of the following just because they're common or impressive-sounding; each is a legitimate tool when a specific requirement calls for it, and overhead with no offsetting benefit otherwise:

- **Microservices** — justified by independent scaling needs, team-topology boundaries, or genuinely divergent tech stacks per service, not by feature count alone
- **Kubernetes** — justified by real orchestration needs at a scale where manual ops breaks down, not by "it's the standard"
- **Kafka** — justified by high-throughput event streaming with replay/ordering needs, not by "we might have events"
- **Redis** — justified by a specific caching/pub-sub/rate-limiting need, not as a default add-on
- **GraphQL** — justified by genuinely heterogeneous client query needs, not as a default over REST
- **Event sourcing** — justified by a real audit/replay/temporal-query requirement, which is a significant complexity commitment
- **CQRS** — justified by read/write models that have genuinely diverged, not applied preemptively
- **Multi-agent AI architectures** — justified when the problem decomposes naturally into cooperating specialized agents, not because "agents" sounds more advanced than a single well-tooled agent
- **Vector databases / RAG** — justified by an actual need to ground responses in a retrievable knowledge base, not added because the system happens to use an LLM
- **Multiple LLMs / multi-region deployment** — justified by real latency, cost-tiering, or geographic/compliance requirements

When you do recommend one of these, say explicitly which driver justifies it — the justification is what distinguishes a real recommendation from the pattern this list exists to catch.
