# Security Policy

## Scope

This repository ships:
- Markdown instructions (`SKILL.md`, `references/`) consumed by an LLM agent — not executable in themselves.
- Three small, dependency-free Python scripts (`scripts/validate_architecture.py`, `scripts/validate_diagrams.py`, `scripts/generate_report.py`) that read local files and print/write text. They make no network calls and execute no user-supplied code.
- Two dev-tooling scripts (`tools/package_skill.py`, `tools/build_context_bundle.py`) used to package or bundle the skill; same posture — local file I/O only, no network calls.

## Design posture

The skill's own instructions default every external source (repository, database, API, infrastructure, project tracker, monitoring) to **read-only**, and explicitly prohibit:
- writing to or modifying a connected repository, database, API, infrastructure, or tracker as part of architecture analysis,
- any destructive operation (database deletion, production deployment, infrastructure destruction, credential modification, service shutdown, destructive migrations),
- placing passwords, API keys, tokens, or private credentials into generated architecture documents, diagrams, or JSON output — these are masked or omitted, with handling described instead (e.g. "secret stored in environment-based secret manager").

Any write/mutation is treated as a distinct, explicitly-authorized action outside the normal analysis workflow — see `skills/ai-system-architect/references/discovery-playbook.md` and `references/security-and-safety.md`.

This is a behavioral contract enforced by the instructions an LLM agent follows, not a sandboxed technical control. Don't rely on it as your only safeguard when connecting a powerful agent to production systems — use your platform's own permission scoping (read-only credentials, least-privilege service accounts) as the actual enforcement boundary.

`scripts/validate_architecture.py` and `scripts/generate_report.py` additionally scan for and mask common credential patterns (GitHub, AWS, Anthropic/OpenAI-style, Slack tokens, private-key blocks) as a defense-in-depth check on the JSON they process — not a substitute for the instruction-level rule above.

## Reporting a vulnerability

If you find an issue in the bundled scripts (e.g. a path-traversal or injection issue in how they read/write files) or a way the skill's instructions could be manipulated into bypassing the read-only/no-mutation rules above, please open a private security advisory on this repository (GitHub: **Security → Advisories → Report a vulnerability**) rather than a public issue. Include:

- The affected file/script or the prompt sequence that triggers the issue.
- A minimal reproduction.
- The impact you'd expect (e.g. "allows writing outside the intended output directory").

We'll acknowledge reports within a reasonable timeframe and credit reporters in the changelog unless you prefer otherwise.

## Not in scope

- The general behavior/quality of LLM output (hallucination, incorrect architecture) — report that as a normal issue/PR per `CONTRIBUTING.md`, not as a security report.
- This skill's architecture-level security review is not a complete security audit — see `references/security-and-safety.md` for what it does and does not cover.
- Vulnerabilities in Claude Code, claude.ai, or Anthropic's infrastructure itself — report those to Anthropic directly.
