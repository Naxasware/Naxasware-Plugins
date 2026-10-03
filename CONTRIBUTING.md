# Contributing

## Changing an existing plugin

1. Edit inside `plugins/<name>/`.
2. `python3 scripts/validate_all_plugins.py .` and, if the plugin has one, `bash plugins/<name>/ci-smoke.sh`.
3. If behavior changed: bump `version` in its `plugin.json` and add a `CHANGELOG.md` entry ([`docs/RELEASING.md`](docs/RELEASING.md) has the semver rules).
4. Open a PR. For a skill or instruction change, include a before/after example of the output; there is no unit-test equivalent for "did the model do the right thing", so examples are the best review evidence.

## Adding a plugin

`python3 scripts/new_plugin.py <name> --description "..."`, then follow [`docs/ADDING-A-PLUGIN.md`](docs/ADDING-A-PLUGIN.md). Don't hand-edit `marketplace.json` or the README plugin table; they are generated.

## Commit messages

Conventional style helps changelogs: `feat(plugin-name): ...`, `fix(plugin-name): ...`, `docs: ...`, `chore: ...`.

## Review

CI (`CI passed`) must be green. `claude plugin validate` is best-effort and non-blocking. See [`docs/AUTOMATION.md`](docs/AUTOMATION.md) for what each check does.

By contributing you agree your work is released under the repository's [Apache-2.0 license](LICENSE). Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).
