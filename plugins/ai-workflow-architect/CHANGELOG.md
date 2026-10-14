# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).

## [1.1.0] - 2026-10-12
### Added
- `examples/chain-example/`: one project through all three stages, validated strictly by `ci-smoke.sh` together with regression tests (invented upstream ID, dropped locked decision, human step without a timeout, retry missing, unlabeled money figure, leaked token).
- Packaging parity with the other two plugins: `SECURITY.md`, `docs/INSTALL.md`, `docs/USING-WITH-OTHER-AGENTS.md`, `tools/package_skill.py`, `tools/build_context_bundle.py`.
- "Running the chain" section in the README.

### Changed
- `validate_chain.py` drift check now also compares its copies in the sibling plugins (`plugins/*/skills/*/scripts`); it previously looked only inside one plugin's own `skills/` folder and so could never find a difference. The script is byte-identical in all three plugins.
- `generate_report.py` builds the traceability table from the document's own Traceability table when there is one; it previously merged dependency columns, so a task that only depended on another task was reported as implementing the requirement.
- SKILL.md and the docs run the validators with `--strict` so that a missing timeout or retry fails the check instead of passing as a warning.

### Fixed
- The unlabeled-money warning printed a truncated figure (`$4` for `$40,000`).
- Removed the unrecognized `metadata` key from `plugin.json`.

## [1.0.0] - 2026-10-08
### Added
- Initial release of the AI Workflow Architect plugin: the workflow design method (modes, complexity ladder, reliability, human-in-the-loop, security, observability, cost, ADRs, diagrams, traceability, chain integration) plus validators and worked examples.
- Existing-workflow inspection layer: progressive discovery across automation platforms, repositories, APIs, databases, infrastructure, monitoring, AI/agent components, MCP and trackers.
- Evidence model (14 evidence types, confidence levels, technology detection states) and evidence report.
- Drift detection (`DRIFT-###` records), consistency checks, extended traceability, change-impact analysis and evidence-based debugging.
- Inspection safety rules: read-only default, secret masking, tool safety card, tool failure handling, offline mode.
- Review, optimization and migration report structures; `validate_evidence.py`; `examples/drift-review.md`.
