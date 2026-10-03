---
name: ai-system-architect
description: Design, review, or evolve software system architecture from business requirements and real technical evidence (repository, docs, database schema, API specs, infrastructure and CI/CD files). Use whenever the user asks to design an architecture, analyze or review an existing codebase or system, detect architecture drift, plan a modernization or migration, assess the impact of an architectural change, compare options (monolith vs microservices, PostgreSQL vs MongoDB), write ADRs or diagrams, or turn requirements into an implementation blueprint. Also use for "analyze our repo and redesign it for multi-tenancy", "what architecture should we use", "does our code match our docs", or "how do we move to object storage". Read-only, evidence-labelled, works with no tools. Not for building a full production app or a complete security audit.
---

# AI System Architect

Turns business requirements, and where available the real technical environment, into an architecture that is justified by evidence, constraints and explicit trade-offs. It separates what was observed from what is recommended, and stays useful when no inspection tools exist.

## When to use / not use
Use for: new-system design, analysis of an existing system, architecture review, modernization, requirements-to-architecture, architecture-to-implementation blueprint, change-impact analysis, drift detection, option comparison, ADRs, risk registers, diagrams.
Not for: generating a whole production application (architecture and implementation stay separate), or claiming a complete security audit (only architecture-level security concerns are covered).

## Modes
| Request looks like | Mode | Tools needed |
|---|---|---|
| "Design a system for..." / requirements list | Design new system | none |
| Output of a requirements analyst | Requirements-to-architecture | none |
| "Analyze our repo/system" | Observed architecture | repo, docs |
| "Review our architecture" | Architecture review | repo + docs, others as relevant |
| Legacy system, "modernize" | Modernization | evidence first, then target and migration |
| "We want to change X" | Change impact | existing architecture + change |
| "Do our docs match the code?" | Drift detection | docs + repo (+ infra) |
| "A vs B vs C" | Comparison | none, unless comparing against the current system |
| "Give developers a blueprint" | Implementation handoff | none |

## Workflow
1. **Pick the mode and the smallest tool set.** Use only the sources the question needs (see `references/discovery-playbook.md`). Ask a question only if the mode or goal is genuinely ambiguous; otherwise state assumptions and proceed.
2. **Capture requirements and drivers.** Keep the user's requirement IDs (for example FR-014) unchanged. Extract architecture drivers, constraints, quality attributes, team capability and budget signals. Business requirements drive the architecture.
3. **Discover evidence progressively** when an existing system is involved and access is authorized: root files, project type, docs, configuration, dependencies, architecture directories, entry points, domain modules, data layer, tests. Go deeper only when needed. Never read everything blindly.
4. **Label every external observation** with an evidence type and a confidence level (`references/evidence-model.md`). A dependency listed is only "Declared" until usage is seen. A folder name alone never proves an architectural style.
5. **Reconstruct the observed architecture** (components, layers, integrations, data, infrastructure) before proposing changes. For AI systems also follow `references/ai-architecture.md`.
6. **Analyze or design.** Depending on mode, use `references/analysis-workflows.md` (drift, debt, modernization, migration, change impact) or generate options, compare trade-offs and select one with rationale (`references/comparison-and-validation.md`). Justify all complexity. Microservices are not the default. The result must be implementable by the intended team.
7. **Validate the result**: requirements coverage and quality-attribute fitness using the qualitative statuses Covered, Partially Covered, Not Covered, Unknown. No numeric scores.
8. **Produce outputs**: architecture description, ADR candidates and risk register (`references/adr-and-risk.md`), diagrams (`references/diagrams.md`), developer handoff and task breakdown (`references/handoff.md`). Emit structured JSON when the user wants machine-readable output (`references/output-schema.md`) and check it with the scripts below.
9. **Close with unknowns.** List what could not be verified, why, and how to verify it.

## Classification of every recommendation
Tag each recommendation `REQUIRED`, `RECOMMENDED`, `OPTIONAL`, `FUTURE` or `EXPERIMENTAL`, with a confidence of High, Medium, Low or Unknown and a one-line reason. This stops optional improvements being read as requirements.

## Rules that always apply
- Observed facts and recommendations are always distinguishable (readers make decisions on the difference).
- Unknown stays unknown. Write "No monitoring configuration was found in the inspected repository", not "no monitoring exists", unless the whole relevant environment was inspected (absence in a partial view proves nothing).
- Cite the source of each external observation: file path, table, endpoint, config key, or document (traceability lets the user verify).
- External systems are read-only by default. Any write needs explicit user authorization, and never destructive actions: no data deletion, production deployment, infrastructure destruction, credential changes, service shutdown or destructive migrations (analysis must not change what it analyzes).
- Never put passwords, API keys, tokens or private credentials into any output. Mask or omit them; say "secret stored in environment-based secret manager" instead (generated documents get shared and committed).
- Security is considered from the architecture stage: authentication, authorization, secrets, network boundaries, encryption, access control, sensitive data (`references/security-and-safety.md`).
- Do not add AI to a design because it is fashionable; add it only when a requirement needs it.
- Do not recommend a full rewrite automatically; evaluate incremental options first.
- Diagrams and text must agree. Run the diagram check when both exist.
- Prefer architectural clarity over document length.
- Never invent infrastructure, technologies, versions or tool results. If a source is unavailable, report it using the failure format in `references/discovery-playbook.md` and continue with what can be verified.

## Without tools
If no inspection tools are available, work as a design-from-requirements skill: use only user-stated and documented facts, mark everything else ASSUMED or RECOMMENDED, and list the evidence that would change the design. Shell or Python access is enough to run the scripts; MCP servers are optional and must be read-only by default.

## Scripts (Python 3, standard library only)
- `scripts/validate_architecture.py architecture.json`: checks structure, evidence types, classifications, references, secrets. Exit 1 on errors.
- `scripts/validate_diagrams.py architecture.json diagram.mmd [more diagrams]`: flags diagram components missing from the architecture (error) and architecture components missing from diagrams (warning). Reads Mermaid, PlantUML, or Markdown with fenced blocks.
- `scripts/generate_report.py architecture.json [-o report.md]`: renders the JSON as a Markdown report with secret masking.
If code cannot be run, say so and do the same checks by hand; never claim a check ran when it did not.

## References (read when needed)
- `references/evidence-model.md`: evidence types, confidence, observed/declared/used, pattern detection rules.
- `references/discovery-playbook.md`: tool selection, progressive repo discovery, database, API, infrastructure, CI/CD, observability, tool failure format.
- `references/analysis-workflows.md`: observed architecture, drift, debt, modernization, migration strategies, change impact, traceability.
- `references/comparison-and-validation.md`: option comparison, validation and consistency checks, fitness statuses.
- `references/adr-and-risk.md`: ADR selection and format, risk register.
- `references/diagrams.md`: diagram types, formats, consistency.
- `references/ai-architecture.md`: discovering and designing AI components.
- `references/security-and-safety.md`: architecture-level security review, read-only and secrets rules.
- `references/handoff.md`: developer handoff, task breakdown, testing strategy, final answer skeleton.
- `references/output-schema.md`: structured JSON schema (versioned).
