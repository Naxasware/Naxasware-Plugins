# Changelog

All notable changes to this plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [Semantic Versioning](https://semver.org/).

## [2.0.0] — 2026-09-25

### Added
- Evidence model (`references/evidence-model.md`): eight evidence types, High/Medium/Low confidence tied to evidence quality, implementation-status classification (Implemented / Partially Implemented / Not Implemented / Conflict / Undocumented Functionality), contradiction and gap reporting formats.
- Tool architecture (`references/tool-architecture.md`): file/repository/database/API/project-management/CRM tool categories, a read-only-by-default permission model, and tool-selection rules.
- Two new analysis modes: Existing-System Reconstruction (reverse requirements engineering from a codebase) and Requirements-vs-Implementation Comparison.
- Change Impact Analysis and Requirements Diff workflows.
- `scripts/validate_requirements.py` — checks that every evidence-backed requirement has a source, evidence type, and confidence.
- `scripts/generate_report.py` — renders structured JSON requirements data into Markdown, CSV, or a traceability matrix.
- Structured JSON export schema (documented in `references/requirement-schema.md`).
- Code-to-requirement traceability chain (Requirement → API endpoint → Service → DB operation → Test).
- Plugin packaging: `.claude-plugin/plugin.json` and a self-hosting `.claude-plugin/marketplace.json`.

### Changed
- `references/output-templates.md`, `references/quality-framework.md`, `references/requirement-schema.md`, and `references/examples.md` extended in place to cover V2 modes and evidence-backed auditing, rather than forked into separate documents — V2 fully subsumes V1.

### Notes
- V1 behavior (pure conversational requirements analysis, no tools) is preserved as the "offline mode" fallback documented directly in `SKILL.md` — this plugin works identically to the original V1 skill when no tools are connected.

## [1.0.0]

Initial V1 skill: business-idea-to-requirements analysis, requirements audits, the stable ID scheme, and `validate_ids.py`.
