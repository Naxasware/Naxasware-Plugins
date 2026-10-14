# AI Workflow Architect

Designs, reviews, debugs and optimizes AI and automation workflows, and inspects existing ones read-only (exports, repositories, APIs, databases, logs) with evidence tracking and drift detection. Useful with or without tools.

Part of the [Naxasware-Plugins](../../README.md) marketplace.

## Install
```bash
claude plugin marketplace add Naxasware/Naxasware-Plugins
claude plugin install ai-workflow-architect@naxasware-plugins
```
Other agents: use the `ai-workflow-architect.full.md` file attached to each release as a system prompt.

## What it does
- **Design (works with no tools):** turns a business process into a workflow architecture: triggers, steps, where plain logic, an LLM or an agent belongs, tools, human approval, failure handling, retries, idempotency, security, observability, cost and scale, then an implementation blueprint with traceable requirements, tasks and tests.
- **Inspect existing workflows (when the environment gives access):** progressive, read-only discovery of automation platforms, repositories, APIs, databases, infrastructure, execution logs, MCP servers and trackers, using the smallest tool set that answers the question.
- **Evidence model:** every important fact carries an evidence type, source, confidence, observation and interpretation. Observed, documented and recommended stay separate; unknown stays unknown.
- **Drift and consistency:** `DRIFT-###` records compare documented, configured and observed behavior; traceability extends from requirement to step to code to test; change-impact and debugging procedures never claim a root cause without evidence.
- **Reports:** architecture review, optimization, migration and modernization (never an automatic full rewrite), with classified recommendations.
- **Safety:** read-only by default, secrets always masked, tool failures reported as limits rather than papered over.
- Stage 3 of the `ai-requirements-analyst` → `ai-system-architect` → `ai-workflow-architect` chain.

## Running the chain

This plugin is stage 3 of `ai-requirements-analyst` → `ai-system-architect` → `ai-workflow-architect`. Give it `01-requirements.md` and `02-architecture.md` and ask for "run the chain": every upstream item is cited and covered (or deferred with a reason), locked decisions are kept, and steps that wait for a person or an outside reply get a wait limit and an expiry path. `examples/chain-example/` holds a complete, validated example of all three documents.

```bash
python3 skills/ai-workflow-architect/scripts/validate_workflow.py 03-workflow.md --strict
python3 skills/ai-workflow-architect/scripts/validate_chain.py 01-requirements.md 02-architecture.md 03-workflow.md --strict
```

## Example prompts
- "Design the workflow for qualifying inbound leads, with a human approval step for large deals."
- "Should this be an agent or a single LLM call?"
- "Review our n8n invoice workflow export and tell me what is wrong."
- "Does the repository still match the workflow documentation? List the drift."
- "Why does this scheduled automation keep failing? Here are the last runs."
- "What breaks if I change the extraction prompt in step 4?"
- "Plan a migration of our legacy Zapier flows without a rewrite."

## Layout
```text
ai-workflow-architect/
├── .claude-plugin/plugin.json
├── skills/ai-workflow-architect/
│   ├── SKILL.md          instructions (start here)
│   ├── references/       methodology, reliability, security, AI/agents, MCP, evidence model,
│   │                     discovery, drift, inspection safety, report structures
│   ├── examples/         worked architectures and an existing-system drift review (invented)
│   └── scripts/          optional stdlib-only validators, chain checks and report generator
├── examples/chain-example/   one project through all three stages (01, 02, 03), validated in CI
├── docs/                     install and non-Claude usage guides
├── tools/                    skill packager and context bundler
├── ci-smoke.sh
├── README.md
├── SECURITY.md
└── CHANGELOG.md
```

## Notes
- Exact inspection tool names come from your environment; the plugin does not invent them and does not require MCP or any particular platform.
- Without tools it runs as the design method on what you supply and labels everything accordingly.

## License
Inherits the repository's [Apache-2.0 license](../../LICENSE).
