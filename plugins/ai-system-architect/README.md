# AI System Architect

**Evidence-based system architecture for AI agents.** Turn business requirements — and, where available, a real repository, database, API, or infrastructure — into an architecture that's justified by evidence, constraints and explicit trade-offs, not just described.

> V1 designs architecture from requirements. V2 can inspect the actual system and design architecture based on evidence.

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-green)](../../LICENSE)

Part of the [Naxasware-Plugins](../../README.md) marketplace.

---

## What this is

A Claude Skill/Plugin (and a portable instruction set for other agent frameworks) that acts as a system architect:

- Designs a new architecture from requirements alone — no tools required.
- Analyzes an existing repository, database schema, API spec, or infrastructure config and reconstructs the *observed* architecture, labeling every claim with its evidence type and confidence.
- Reviews an existing architecture against requirements and quality attributes, using Covered / Partially Covered / Not Covered / Unknown — never a numeric score.
- Detects architecture drift (documented vs. observed) and architecture debt (Confirmed / Likely / Potential).
- Plans modernization and migration: current state, target state, transition architecture, phased rollout — never an automatic full rewrite.
- Compares options (monolith vs. microservices, PostgreSQL vs. MongoDB, cloud vs. self-hosted) without declaring a universal winner.
- Assesses the impact of a proposed change across application, data, API, deployment and cost.
- Produces ADR candidates, a risk register, Mermaid/PlantUML diagrams, and a developer handoff — kept separate from actually generating the application.

Full behavioral spec lives in [`skills/ai-system-architect/SKILL.md`](skills/ai-system-architect/SKILL.md) and its `references/` files — read those for the complete methodology; this README is about installing and running it.

## Layout

```
plugins/ai-system-architect/
├── .claude-plugin/
│   └── plugin.json           # plugin manifest (this plugin's identity, version, metadata)
├── skills/
│   └── ai-system-architect/
│       ├── SKILL.md                        # entry point — modes, workflow, rules
│       ├── references/
│       │   ├── evidence-model.md           # evidence types, confidence, tech detection, patterns
│       │   ├── discovery-playbook.md       # tool selection, progressive discovery, failure format
│       │   ├── analysis-workflows.md       # observed architecture, drift, debt, modernization, change impact
│       │   ├── comparison-and-validation.md# option comparison, fitness validation, consistency
│       │   ├── adr-and-risk.md             # ADR format, risk register
│       │   ├── diagrams.md                 # diagram types/formats, diagram-vs-architecture consistency
│       │   ├── ai-architecture.md          # discovering and designing AI components
│       │   ├── security-and-safety.md      # architecture-level security review, read-only/secrets rules
│       │   ├── handoff.md                  # developer handoff, task breakdown, testing strategy
│       │   └── output-schema.md            # structured JSON schema (versioned)
│       └── scripts/
│           ├── validate_architecture.py    # checks structure, evidence, classifications, secrets
│           ├── validate_diagrams.py        # diagram-vs-architecture component consistency
│           └── generate_report.py          # renders JSON → Markdown report (secrets masked)
├── examples/                  # sample inputs/outputs you can run scripts against
├── docs/                      # install & integration guides (Claude and non-Claude)
├── tools/                     # this plugin's dev tooling (skill packager, context bundler)
├── ci-smoke.sh                # what CI runs for this plugin (see ../../.github/workflows/ci.yml)
├── README.md                  # this file
├── CHANGELOG.md
└── SECURITY.md
```

This plugin has no `LICENSE` or top-level `CONTRIBUTING.md` of its own — it inherits the [org-wide LICENSE](../../LICENSE) and [contribution guide](../../CONTRIBUTING.md) from the repo root, per the monorepo convention documented in [`../../docs/ADDING-A-PLUGIN.md`](../../docs/ADDING-A-PLUGIN.md).

## Install

Full details in [`docs/INSTALL.md`](docs/INSTALL.md). Short version:

### Claude Code (plugin — recommended)

```bash
claude plugin marketplace add Naxasware/Naxasware-Plugins
claude plugin install ai-system-architect@naxasware-plugins
```

Then just ask Claude Code to design, review, or analyze a system's architecture — the skill triggers automatically.

### claude.ai / Claude Desktop / Cowork (skill only)

```bash
python3 tools/package_skill.py skills/ai-system-architect dist/
```

Upload the resulting `dist/ai-system-architect.skill` from **Settings → Capabilities → Skills**.

### Any other agent framework (LangChain, AutoGen, custom GPTs, Cursor, etc.)

This isn't Claude-proprietary: `SKILL.md` + `references/` are plain Markdown instructions, and `scripts/` are dependency-free Python. See [`docs/USING-WITH-OTHER-AGENTS.md`](docs/USING-WITH-OTHER-AGENTS.md) for how to bundle the instructions into a single system prompt and call the scripts as ordinary CLI tools from any pipeline.

## Quick example

```bash
cd skills/ai-system-architect
python3 scripts/validate_architecture.py ../../examples/sample-architecture.json
python3 scripts/validate_diagrams.py ../../examples/sample-architecture.json ../../examples/sample-diagram.mmd
python3 scripts/generate_report.py ../../examples/sample-architecture.json
```

See `examples/` for sample inputs and the kind of output each script produces, and run `./ci-smoke.sh` for an end-to-end check of every bundled script.

## Requirements

- Python 3.8+ for the bundled scripts (standard library only — no `pip install` needed).
- Claude Code (any reasonably recent version) if installing as a plugin; also works standalone as a skill in claude.ai, Claude Desktop, or Cowork.

## Security

This skill defaults to read-only inspection and never performs writes, mutations, or destructive operations as part of its normal workflow — see `skills/ai-system-architect/references/security-and-safety.md` for the full posture. See [`SECURITY.md`](SECURITY.md) for this plugin's specific notes, or the [org-wide `SECURITY.md`](../../SECURITY.md) to report a vulnerability.
