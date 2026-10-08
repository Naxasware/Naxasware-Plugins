# Review, optimization, migration and modernization reports

## Contents
1. Recommendation format
2. Architecture review report
3. Optimization report
4. Migration report and modernization strategy
5. Architecture comparison
6. Validation questions
7. Evaluating the plugin's output

## 1. Recommendation format

Class: `REQUIRED`, `RECOMMENDED`, `OPTIONAL`, `FUTURE`, `EXPERIMENTAL`. Each recommendation states:

```text
Recommendation | Reason | Evidence | Expected Benefit | Trade-off | Implementation Impact
```

Tie the evidence to an evidence record or drift ID. A recommendation without evidence is `INFERRED` or `RECOMMENDED` and says so.

## 2. Architecture review report

```text
Executive Summary
Current Workflow
Observed Architecture            (observed only, with evidence)
Architecture Strengths
Architecture Problems
Reliability Issues
Security Issues
AI / Agent Issues
Performance Issues
Cost Issues
Maintainability Issues
Workflow Drift
Risks
Recommendations
Migration / Improvement Plan
Open Questions
```

Lead with what matters most. Include strengths: a review that only lists faults is less credible. Add an Evidence Report (`evidence-model.md`) as an appendix or companion for anything inspected.

## 3. Optimization report

```text
Current Workflow, Bottlenecks, Redundant Steps, AI Overuse, Tool Overuse, API Overuse,
Cost Drivers, Reliability Problems, Security Problems, Optimization Opportunities,
Expected Impact, Trade-offs, Implementation Plan
```

Look at performance (needless sequencing, blocking calls, repeated AI or API calls), cost (excess LLM use, redundant executions, costly APIs, idle infrastructure), reliability (missing retries, fallbacks, error handling), maintainability (giant workflows, duplicated logic, hidden dependencies) and security (excess permissions, exposed secrets, unsafe tools). Quantify only from observed data, with window and sample size; otherwise label estimates with their inputs (`workflow-cost.md`).

## 4. Migration report and modernization strategy

```text
Current State, Target State, Migration Constraints, Migration Risks, Transition Architecture,
Migration Strategy, Phase 1, Phase 2, Phase 3, Validation, Rollback Strategy, Success Criteria
```

Flow: current state, problems, constraints, target state, transition architecture, migration strategy, phases, validation. Strategies to choose from: incremental refactoring, workflow decomposition, strangler pattern, API facade, parallel execution, branch by abstraction, phased replacement, platform migration, workflow extraction. **Never recommend a full rewrite automatically**; if a rewrite is the answer, show why each incremental option fails against the stated constraints. Every phase needs validation and a rollback.

## 5. Architecture comparison

Compare competing designs on: requirement fit, complexity, reliability, performance, scalability, security, maintainability, observability, cost, operational burden, implementation difficulty, vendor dependency. Show trade-offs; do not assume a universal winner; then pick one for this case with a rationale.

## 6. Validation questions

Before delivery check whether: important requirements are addressed; all paths are defined; inputs and outputs are consistent; tool dependencies are available; AI outputs are validated; agent permissions are bounded; retry and failure paths exist; sensitive operations are protected; failures can be diagnosed; expected volume is handled; major cost drivers are identified; the team can realistically build it. For existing systems also check that observed and recommended statements are separated and that every drift record is complete.

## 7. Evaluating the plugin's output

Useful dimensions when testing the skill on a scenario: architecture correctness, requirements coverage, completeness, evidence accuracy, recommendation and trade-off quality, AI and agent architecture quality, security, reliability, scalability, cost awareness, practicality, diagram accuracy, traceability, consistency, drift detection accuracy, hallucination rate, tool efficiency. Scenario families: basic automations (CRUD, webhook, scheduled, API integration), business flows (lead qualification, support, invoices, onboarding), AI flows (classification, extraction, RAG, agent, tool-using agent), advanced (multi-agent, event-driven, real-time, high-volume, human approval) and existing systems (legacy automation, n8n workflow, repository workflow, API-heavy, database workflow) across review, optimization, migration, drift detection and change impact.
