# AI Requirements Analyst

**Evidence-based requirements engineering for AI agents.** Turn a business idea, an existing requirements doc, a codebase, or a connected repo/database/API into structured, implementation-ready requirements — and verify what's documented against what's actually built.

> V1 understands what you tell it. V2 can go check.

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](../../LICENSE)

Part of the [Naxasware-Plugins](../../README.md) marketplace.

---

## What this is

A Claude Skill/Plugin (and a portable instruction set for other agent frameworks) that acts as a professional Business Analyst / Requirements Engineer:

- Turns a vague idea into a structured spec — problem, objectives, actors, functional requirements, business rules, data requirements, NFRs, acceptance criteria — with every guess clearly labeled as an assumption or open question, never silently presented as fact.
- Audits an existing requirements doc for gaps, ambiguity, and contradictions.
- **(V2)** When connected to a repository, file system, database, or API, investigates the actual system and attaches evidence (source, evidence type, confidence) to every finding, instead of relying only on what a user describes.
- **(V2)** Compares documented requirements against real implementation and classifies each as Implemented / Partially Implemented / Not Implemented / Conflict / Undocumented Functionality.
- **(V2)** Runs change-impact analysis and requirement diffs using stable IDs.

Full behavioral spec lives in [`skills/ai-requirements-analyst/SKILL.md`](skills/ai-requirements-analyst/SKILL.md) and its `references/` files — read those for the complete methodology; this README is about installing and running it.

## Layout

```
plugins/ai-requirements-analyst/
├── .claude-plugin/
│   └── plugin.json           # plugin manifest (this plugin's identity, version, metadata)
├── skills/
│   └── ai-requirements-analyst/
│       ├── SKILL.md                     # entry point — routing, discipline, workflow
│       ├── references/
│       │   ├── evidence-model.md        # evidence types, confidence, status classification
│       │   ├── tool-architecture.md     # tool categories, permission model, tool selection
│       │   ├── requirement-schema.md    # ID scheme, field structures, JSON export schema
│       │   ├── output-templates.md      # analysis modes, output shapes, export formats
│       │   ├── quality-framework.md     # 7-point quality check, audit process
│       │   └── examples.md              # two worked examples (offline + evidence-based)
│       └── scripts/
│           ├── validate_ids.py          # catches duplicate/malformed requirement IDs
│           ├── validate_requirements.py # checks evidence-backed requirements are complete
│           └── generate_report.py       # renders JSON → Markdown / CSV / traceability matrix
├── examples/                 # sample inputs/outputs you can run scripts against
├── docs/                     # install & integration guides (Claude and non-Claude)
├── tools/                    # this plugin's dev tooling (skill packager, context bundler)
├── ci-smoke.sh               # what CI runs for this plugin (see ../../.github/workflows/ci.yml)
├── README.md                 # this file
├── CHANGELOG.md
└── SECURITY.md
```

This plugin has no `LICENSE` or top-level `CONTRIBUTING.md` of its own — it inherits the [org-wide LICENSE](../../LICENSE) and [contribution guide](../../CONTRIBUTING.md) from the repo root, per the monorepo convention documented in [`../../docs/ADDING-A-PLUGIN.md`](../../docs/ADDING-A-PLUGIN.md).

## Install

Full details in [`docs/INSTALL.md`](docs/INSTALL.md). Short version:

### Claude Code (plugin — recommended)

```bash
claude plugin marketplace add Naxasware/Naxasware-Plugins
claude plugin install ai-requirements-analyst@naxasware-plugins
```

Then just ask Claude Code to plan, spec, or audit something — the skill triggers automatically.

### claude.ai / Claude Desktop / Cowork (skill only)

```bash
python3 tools/package_skill.py skills/ai-requirements-analyst dist/
```

Upload the resulting `dist/ai-requirements-analyst.skill` from **Settings → Capabilities → Skills**.

### Any other agent framework (LangChain, AutoGen, custom GPTs, Cursor, etc.)

This isn't Claude-proprietary: `SKILL.md` + `references/` are plain Markdown instructions, and `scripts/` are dependency-free Python. See [`docs/USING-WITH-OTHER-AGENTS.md`](docs/USING-WITH-OTHER-AGENTS.md) for how to bundle the instructions into a single system prompt and call the scripts as ordinary CLI tools from any pipeline.

## Quick example

```bash
cd skills/ai-requirements-analyst
python3 scripts/validate_ids.py path/to/your-requirements.md
python3 scripts/validate_requirements.py path/to/your-evidence-backed-doc.md
python3 scripts/generate_report.py ../../examples/sample-requirements.json --format markdown
```

See `examples/` for sample inputs and the kind of output each mode produces, and run `./ci-smoke.sh` for an end-to-end check of every bundled script.

## Requirements

- Python 3.8+ for the bundled scripts (standard library only — no `pip install` needed).
- Claude Code (any reasonably recent version) if installing as a plugin; also works standalone as a skill in claude.ai, Claude Desktop, or Cowork.

## Security

This skill defaults to read-only analysis and never performs writes, mutations, or offensive security testing as part of its normal workflow — see `skills/ai-requirements-analyst/references/tool-architecture.md` for the full permission model. See [`SECURITY.md`](SECURITY.md) for this plugin's specific notes, or the [org-wide `SECURITY.md`](../../SECURITY.md) to report a vulnerability.
