# Contributing to Naxasware-Plugins

Thanks for considering a contribution. This repo hosts multiple Claude Code plugins, one per folder under `plugins/`.

## Two kinds of contribution

1. **Changing an existing plugin** — bug fixes, new reference material, better examples. Work inside that plugin's folder; each has its own README and (where applicable) `CONTRIBUTING`-relevant notes in its docs. General process below still applies.
2. **Adding a new plugin** — see [`docs/ADDING-A-PLUGIN.md`](docs/ADDING-A-PLUGIN.md) for the full checklist (folder structure, manifest, marketplace entry, CI hook).

## Before you open a PR

1. **Validate locally.** From the repo root:
   ```bash
   python3 scripts/validate_all_plugins.py .
   ```
   This is the same check CI runs and requires nothing beyond Python 3.
2. **Run the affected plugin's smoke test**, if it has one:
   ```bash
   ./plugins/<plugin-name>/ci-smoke.sh
   ```
3. **Bump versions.** If you changed a plugin's behavior, bump `version` in that plugin's `.claude-plugin/plugin.json` (semantic versioning: patch for fixes, minor for new non-breaking capability, major for a breaking change to output format, schema, or the ID scheme) and add a `CHANGELOG.md` entry in that plugin's folder.
4. **Keep `SKILL.md` lean.** Claude Code loads a skill's `SKILL.md` in full whenever it triggers, then pulls in `references/*.md` only as needed (progressive disclosure). If you're adding substantial new behavior, prefer extending or adding a reference file over growing `SKILL.md` itself.

## Pull request description

Include:
- What changed and why.
- For a behavior change to a skill: a before/after example of its output, if you have one (the most useful kind of review evidence for prompt/instruction changes, since there's no unit-test equivalent for "did the model do the right thing").
- Confirmation you ran the validator and any relevant `ci-smoke.sh`.

## Review and merge

CI must pass (`validate-manifests` and `plugin-smoke-tests` are required; `claude-plugin-validate` is best-effort and non-blocking — see the root README's CI section for why). A maintainer will review for consistency with the plugin's existing methodology before merging.

## Code of conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
