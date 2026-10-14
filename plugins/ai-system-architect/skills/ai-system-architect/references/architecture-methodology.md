# Architecture Methodology

Read this before starting any Greenfield, Comparison, or Enterprise-mode analysis, or any time you need the full workflow rather than the SKILL.md summary of it.

> **Using this with the structured output.** This file is the design method for a new system (Design new system, Requirements-to-architecture, Comparison, Implementation handoff modes). Record its results in the JSON sections of `output-schema.md`: drivers in `architecture_drivers` (`AD-nnn`), constraints in `constraints`, attributes in `quality_attributes`, options in `architecture_options`, the chosen style in `selected_architecture`, decisions in `decisions` (`ADR-nnn`). Tag every driver and scale figure with an evidence type from `evidence-model.md`: what the user or a document said is `USER_STATED` / `DOCUMENTED`, a planning figure is `ASSUMED` (with its basis), your proposal is `RECOMMENDED`, and a gap stays `Unknown`.

## The full workflow

Not every stage applies to every project — skip what the mode and available information don't call for — but this is the order dependencies actually flow in, so working out of order tends to produce architecture that contradicts itself later:

```
Understand business context
 → Validate requirements
 → Identify architecture drivers
 → Identify constraints
 → Identify quality attributes
 → Estimate scale
 → Identify architectural risks
 → Define architecture principles
 → Generate architecture options
 → Evaluate trade-offs
 → Select architecture style
 → Define system boundaries
 → Define components
 → Define data architecture
 → Define API architecture
 → Define integration architecture
 → Define security architecture
 → Define infrastructure
 → Define deployment
 → Define observability
 → Define AI architecture (if applicable)
 → Define failure handling
 → Define scaling strategy
 → Define cost considerations
 → Create ADRs
 → Create diagrams
 → Create implementation blueprint
 → Validate architecture
```

## Business context

Before any technical decision, pin down (ask or infer, and label whichever you did):

- **Business problem** — what's actually broken or missing today
- **Business objective** — why the system should exist at all
- **Users** — who uses it, and how that differs across user types
- **Business value** — what outcome the system should produce
- **Success criteria** — how success will be measured
- **Scope / out of scope** — what's inside the system boundary and what explicitly isn't

Skipping this and jumping to "what database should we use" is exactly the failure mode Principle 1 (business first) exists to prevent — a technology choice made before this section is filled in has nothing to be justified against.

## Architecture drivers

Architecture drivers are the requirements that materially shape the architecture — not every requirement is one. A driver is anything that would make you choose a different architecture if it changed: expected user count, transaction volume, response-time targets, uptime requirements, data sensitivity, regulatory obligations, geographic distribution, integration load, whether AI workloads are involved, budget, team size, development speed, expected growth, and deployment environment.

ID them sequentially as they're identified: `AD-001`, `AD-002`, `AD-003`... Each driver should be traceable to something the user actually said or a document actually supports — a driver you invented to make the architecture look more thorough is worse than not having it, because later decisions will cite it as justification.

## Quality attributes

Relevant attributes to weigh, though not every project needs all of them: performance, scalability, availability, reliability, security, maintainability, usability, observability, portability, interoperability, resilience, recoverability, cost efficiency. Naming an attribute "important" without connecting it to a driver or a stated constraint is decoration, not analysis — every attribute you call out should trace back to something concrete (an SLA, a compliance need, a team's stated priority).

## Scale analysis

Where the input gives you numbers, estimate: users, concurrent users, requests/sec, transactions/day, data volume, storage growth, file volume, AI request volume, token usage, geographic distribution.

Where it doesn't: write `Unknown`, or provide an explicitly labeled planning assumption ("Assumption: ~500 daily active users based on stated team size, revisit if this is materially off"). Never fabricate a specific number and present it as if it came from the user — a made-up "10,000 req/sec" baked into a database choice will silently mislead whoever inherits the document.
