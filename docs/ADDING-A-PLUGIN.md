# Adding a plugin

This repo is folder-wise: one plugin per directory under `plugins/`, listed once in the shared `.claude-plugin/marketplace.json`. Follow this checklist to add a new one.

## 1. Scaffold the folder

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── references/        # optional — detail SKILL.md links out to
│       └── scripts/           # optional — dependency-free where possible
├── docs/
│   └── INSTALL.md             # at minimum
├── examples/                  # optional but recommended
├── tools/                     # optional — plugin-specific dev tooling
├── ci-smoke.sh                # optional but recommended — see step 4
├── README.md
├── CHANGELOG.md
└── SECURITY.md                # optional — only if the plugin has its own tool/permission model worth documenting
```

Use `plugins/ai-requirements-analyst/` as the reference example for all of the above.

## 2. Write `plugin.json`

Minimum viable manifest:

```json
{
  "name": "<plugin-name>",
  "displayName": "<Human Readable Name>",
  "version": "1.0.0",
  "description": "One or two sentences on what it does.",
  "author": { "name": "Naxasware", "url": "https://github.com/Naxasware" },
  "homepage": "https://github.com/Naxasware/Naxasware-Plugins/tree/main/plugins/<plugin-name>",
  "repository": "https://github.com/Naxasware/Naxasware-Plugins",
  "license": "MIT",
  "keywords": ["..."]
}
```

`name` must be kebab-case and must match the `name` you use in the marketplace entry (step 3). Don't set `skills` in the manifest unless your skill(s) live somewhere other than the default `skills/` directory — the default scan already picks them up.

## 3. Add the marketplace entry

Edit the root `.claude-plugin/marketplace.json` and add one entry to the `plugins` array:

```json
{
  "name": "<plugin-name>",
  "source": "./plugins/<plugin-name>",
  "displayName": "<Human Readable Name>",
  "description": "Same one-liner as plugin.json's description.",
  "category": "productivity",
  "tags": ["..."]
}
```

Keep `source` as an explicit `./plugins/<name>` path (not a bare name) for maximum Claude Code version compatibility.

## 4. Add a CI smoke test (recommended)

Create `plugins/<plugin-name>/ci-smoke.sh`, executable (`chmod +x`), that exercises whatever your plugin ships (validation scripts, report generators, anything else with a deterministic pass/fail). CI (`.github/workflows/ci.yml`) automatically discovers and runs every `plugins/*/ci-smoke.sh` — no workflow edits needed. Use `plugins/ai-requirements-analyst/ci-smoke.sh` as a template: resolve paths relative to the script's own location (`BASH_SOURCE[0]`), `set -euo pipefail`, and exit non-zero on any real failure.

If your plugin has no scripts to test (pure-instruction skill, nothing executable), you can skip `ci-smoke.sh` entirely — `scripts/validate_all_plugins.py` still validates the manifest and `SKILL.md` frontmatter.

## 5. Validate locally

```bash
python3 scripts/validate_all_plugins.py .
./plugins/<plugin-name>/ci-smoke.sh   # if you added one
```

Both should exit 0 before you open a PR.

## 6. Write the plugin's own README and CHANGELOG

Follow `plugins/ai-requirements-analyst/README.md`'s structure: what it is, layout, install instructions (link to `docs/INSTALL.md`), a quick example, requirements, and a pointer to security notes if relevant. Start `CHANGELOG.md` with a `[1.0.0]` entry describing the initial release.

## 7. License

The plugin inherits the repo-root `LICENSE` (MIT) by default — no per-plugin `LICENSE` file needed. Only add one to the plugin's own folder if that specific plugin needs different terms; note this clearly in its README if you do, since a per-folder `LICENSE` overriding the root one is non-obvious to someone browsing the repo.

## 8. Open the PR

See `CONTRIBUTING.md` for the general PR checklist. Mention in the description that this is a new plugin addition so reviewers know to check the marketplace entry and manifest carefully (these are the two files a typo in breaks installability for everyone, not just this plugin).
