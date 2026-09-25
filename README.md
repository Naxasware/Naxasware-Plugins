# Naxasware Plugins

Naxasware's official Claude Code plugin marketplace — one plugin per folder, one repo to add.

```bash
claude plugin marketplace add Naxasware/Naxasware-Plugins
claude plugin install <plugin-name>@naxasware-plugins
```

[![CI](https://github.com/Naxasware/Naxasware-Plugins/actions/workflows/ci.yml/badge.svg)](https://github.com/Naxasware/Naxasware-Plugins/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Plugins

| Plugin | What it does | Version | Docs |
|---|---|---|---|
| [`ai-requirements-analyst`](plugins/ai-requirements-analyst) | Evidence-based requirements engineering — turns ideas, docs, and connected repos/DBs/APIs into structured requirements, and verifies documented requirements against what's actually built. | 2.0.0 | [README](plugins/ai-requirements-analyst/README.md) · [Install](plugins/ai-requirements-analyst/docs/INSTALL.md) |

## How this repo is organized

```
Naxasware-Plugins/
├── .claude-plugin/
│   └── marketplace.json      # the ONE marketplace catalog — lists every plugin below
├── plugins/
│   └── <plugin-name>/        # one self-contained plugin per folder
│       ├── .claude-plugin/plugin.json
│       ├── skills/<skill-name>/SKILL.md ...
│       ├── docs/, examples/, tools/
│       ├── ci-smoke.sh       # optional — CI runs this automatically if present
│       ├── README.md, CHANGELOG.md, SECURITY.md
├── scripts/
│   └── validate_all_plugins.py   # org-wide, dependency-free validator (drives CI)
├── docs/
│   └── ADDING-A-PLUGIN.md    # how to add the next plugin
├── .github/workflows/ci.yml
├── LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
```

Each plugin folder is self-contained (its own manifest, skill, docs, examples) but shares the repo's `LICENSE`, `CONTRIBUTING.md`, and CI. Adding a plugin means adding a folder under `plugins/` and one entry in `.claude-plugin/marketplace.json` — see [`docs/ADDING-A-PLUGIN.md`](docs/ADDING-A-PLUGIN.md).

## Install a plugin

```bash
claude plugin marketplace add Naxasware/Naxasware-Plugins
claude plugin install ai-requirements-analyst@naxasware-plugins
```

Browse what's installable:

```bash
/plugin marketplace add Naxasware/Naxasware-Plugins
/plugin install
```

Per-plugin install options (skill-only upload for claude.ai/Desktop/Cowork, non-Claude agent integration, team rollout) are documented in each plugin's own `docs/INSTALL.md`.

## CI

Every push and PR runs (`.github/workflows/ci.yml`):
1. **`validate-manifests`** — JSON-validates every `plugin.json`/`marketplace.json`, then runs `scripts/validate_all_plugins.py`, which reads the marketplace catalog and validates every plugin it lists (manifest schema, name consistency, `SKILL.md` frontmatter, and that all bundled Python scripts compile). Pure Python standard library — no external dependency, nothing that can go down.
2. **`plugin-smoke-tests`** — discovers and runs every `plugins/*/ci-smoke.sh`, so each plugin owns its own end-to-end check.
3. **`claude-plugin-validate`** — best-effort: installs Anthropic's `claude` CLI and runs `claude plugin validate . --strict` for the authoritative schema check. Non-blocking, since it depends on an external package this repo doesn't control.

Only (1) and (2) are required to merge.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the general process and [`docs/ADDING-A-PLUGIN.md`](docs/ADDING-A-PLUGIN.md) for adding a new plugin specifically. Please also read [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Security

See [`SECURITY.md`](SECURITY.md).

## License

MIT — see [`LICENSE`](LICENSE). This covers the repository as a whole; an individual plugin can override this with its own `LICENSE` file in its folder if it needs different terms (see `docs/ADDING-A-PLUGIN.md`).
