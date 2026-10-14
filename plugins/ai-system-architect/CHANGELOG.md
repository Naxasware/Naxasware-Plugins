# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).

## [1.1.0] - 2026-10-12
### Added
- Chain support as stage 2 of requirements → architecture → workflow: `references/chaining.md`, `scripts/idscan.py`, `scripts/validate_chain.py`, `scripts/validate_ids.py` (shared with the other two plugins), a "Running as stage 2 of the chain" section in SKILL.md, and `examples/chain-example/`.
- Output schema 1.1 (1.0 files still validate): `project.chain`, `upstream_coverage`, `carried_forward`, `handoff`, `integration_architecture.interfaces` with `INT-nnn` ids, `A-` / `Q-` items with ids, and `cites` on constraints.
- `validate_architecture.py --upstream <requirements.md>` and `--strict`: cited requirements must exist upstream, Must items and locked decisions must be covered, upstream IDs must not be restated, new A-/Q- numbers must continue, and a handoff is expected in chain mode. Unknown top-level sections now produce a warning.
- Component origin `stated` (an existing system the user or a document says exists); previously such systems had to be mislabelled `observed`.
- Design guidance for new systems, previously missing from this plugin: `architecture-methodology.md`, `architecture-patterns.md`, `technology-domains.md`, `operations.md`.

### Changed
- `generate_report.py` keeps ID-like keys as written (`INT-001` was rendered as `Int-001`), renders sections it does not know under their own heading instead of dropping them, and in chain mode writes the `> Chain:` header, the coverage table and the handoff block.

### Fixed
- A traceability row citing a requirement that does not exist (for example FR-099), or an architecture that left a Must requirement uncovered, passed validation unnoticed.
- Removed the unrecognized `$schema` and `metadata` keys from `plugin.json`.

## [1.0.0] - 2026-09-28
### Added
- Initial release of the Naxasware AI System Architect (product V2): evidence-based architecture design, review, drift detection, modernization, comparison and change-impact analysis.
- Evidence model (12 evidence types, confidence levels, observed vs recommended separation).
- Read-only discovery playbooks for repository, database, API, infrastructure, CI/CD, observability, security and AI systems.
- Structured JSON output schema plus `validate_architecture.py`, `validate_diagrams.py` and `generate_report.py`.
