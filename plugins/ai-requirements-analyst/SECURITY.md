# Security Policy

## Scope

This repository ships:
- Markdown instructions (`SKILL.md`, `references/`) consumed by an LLM agent — not executable in themselves.
- Three small, dependency-free Python scripts (`scripts/validate_ids.py`, `scripts/validate_requirements.py`, `scripts/generate_report.py`) that read local files and print/write text. They make no network calls and execute no user-supplied code.

## Design posture

The skill's own instructions default every tool category (file, repository, database, API, project-management, CRM) to **read-only**, and explicitly prohibit:
- writing to or modifying a connected repository, database, API, or tracker as part of requirements analysis,
- bypassing authentication or exposing secrets/credentials (the instructions require masking API keys, tokens, and unnecessary personal data in output),
- offensive security testing of any kind,
- sending external communications (email, messages, tickets) without explicit separate authorization.

Any write/mutation is treated as a distinct, explicitly-authorized action outside the normal analysis workflow — see `skills/ai-requirements-analyst/references/tool-architecture.md`.

This is a behavioral contract enforced by the instructions an LLM agent follows, not a sandboxed technical control. Don't rely on it as your only safeguard when connecting a powerful agent to production systems — use your platform's own permission scoping (read-only credentials, least-privilege service accounts) as the actual enforcement boundary.

## Reporting a vulnerability

If you find an issue in the bundled scripts (e.g. a path-traversal or injection issue in how they read/write files) or a way the skill's instructions could be manipulated into bypassing the read-only/no-mutation rules above, please open a private security advisory on this repository (GitHub: **Security → Advisories → Report a vulnerability**) rather than a public issue. Include:

- The affected file/script or the prompt sequence that triggers the issue.
- A minimal reproduction.
- The impact you'd expect (e.g. "allows writing outside the intended output directory").

We'll acknowledge reports within a reasonable timeframe and credit reporters in the changelog unless you prefer otherwise.

## Not in scope

- The general behavior/quality of LLM output (hallucination, incorrect analysis) — report that as a normal issue/PR per `CONTRIBUTING.md`, not as a security report.
- Vulnerabilities in Claude Code, claude.ai, or Anthropic's infrastructure itself — report those to Anthropic directly.
