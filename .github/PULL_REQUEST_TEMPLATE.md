## What changed

<!-- Which plugin(s), and what changed. If this is a new plugin, say so. -->

## Why

<!-- The problem this solves, or the capability it adds. -->

## Checklist

- [ ] `python3 scripts/validate_all_plugins.py .` passes locally
- [ ] Ran the affected plugin's `ci-smoke.sh`, if it has one
- [ ] Bumped the plugin's `version` in `plugin.json` (if behavior changed) and added a `CHANGELOG.md` entry
- [ ] For a new plugin: added a `.claude-plugin/marketplace.json` entry and followed `docs/ADDING-A-PLUGIN.md`
- [ ] For a skill/behavior change: included a before/after example of the output where practical

## Before/after example (if applicable)

<!-- Especially useful for prompt/instruction changes, where there's no unit-test equivalent. -->
