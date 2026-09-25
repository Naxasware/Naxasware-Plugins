# Security Policy

## Scope

This repository hosts multiple Claude Code plugins under `plugins/`. Each plugin ships:
- Markdown instructions (`SKILL.md`, `references/`) consumed by an LLM agent — not executable in themselves.
- Small, dependency-free Python scripts under each plugin's `scripts/` — no network calls, no execution of user-supplied code, unless a specific plugin's own `SECURITY.md` documents otherwise.

Check the individual plugin's `SECURITY.md` (e.g. [`plugins/ai-requirements-analyst/SECURITY.md`](plugins/ai-requirements-analyst/SECURITY.md)) for that plugin's specific behavioral posture (tool permissions, read/write defaults, etc.).

## Reporting a vulnerability

If you find a security issue — in a bundled script (e.g. path traversal, injection), in the CI workflow, or a way a plugin's instructions could be manipulated into bypassing its documented safety rules — please open a private security advisory on this repository (GitHub: **Security → Advisories → Report a vulnerability**) rather than a public issue. Include:

- The affected plugin, file, or prompt sequence that triggers the issue.
- A minimal reproduction.
- The impact you'd expect.

We'll acknowledge reports within a reasonable timeframe and credit reporters in the relevant plugin's changelog unless you prefer otherwise.

## Not in scope

- General LLM output quality/hallucination — report as a normal issue or PR per `CONTRIBUTING.md`.
- Vulnerabilities in Claude Code, claude.ai, or Anthropic's infrastructure — report those to Anthropic directly.
