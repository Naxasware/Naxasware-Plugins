# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-10-08
### Added
- Initial release of the AI Workflow Architect plugin: the workflow design method (modes, complexity ladder, reliability, human-in-the-loop, security, observability, cost, ADRs, diagrams, traceability, chain integration) plus validators and worked examples.
- Existing-workflow inspection layer: progressive discovery across automation platforms, repositories, APIs, databases, infrastructure, monitoring, AI/agent components, MCP and trackers.
- Evidence model (14 evidence types, confidence levels, technology detection states) and evidence report.
- Drift detection (`DRIFT-###` records), consistency checks, extended traceability, change-impact analysis and evidence-based debugging.
- Inspection safety rules: read-only default, secret masking, tool safety card, tool failure handling, offline mode.
- Review, optimization and migration report structures; `validate_evidence.py`; `examples/drift-review.md`.
