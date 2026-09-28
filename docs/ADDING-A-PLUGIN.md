# Adding a plugin

One plugin per folder under `plugins/`. You never edit `marketplace.json` or the README plugin table by hand: `scripts/sync_repo.py` (run by CI after merge) generates both from your folder.

## Fast path

```bash
python3 scripts/new_plugin.py my-plugin \
  --display "My Plugin" \
  --description "What it does and when to use it."
# optional: --skill other-name   (skill folder name; defaults to the plugin name)
```

This copies `templates/plugin-template/` to `plugins/my-plugin/` and runs the sync. Then:

1. Write `plugins/my-plugin/skills/my-plugin/SKILL.md` (see rules below).
2. Add `references/` files for detail the skill links to, and `scripts/` only for deterministic work.
3. Fill in `README.md`; keep `CHANGELOG.md` current.
4. `python3 scripts/validate_all_plugins.py .` must print `No errors.`
5. Commit and push. CI validates, and the sync workflow updates `marketplace.json` and the README table.
6. To publish, tag it: see [`RELEASING.md`](RELEASING.md).

## Required layout

```
plugins/<plugin-name>/
├── .claude-plugin/plugin.json        # required
├── skills/<skill-name>/SKILL.md      # required, at least one skill
│   ├── references/*.md               # optional
│   └── scripts/*.py                  # optional, stdlib-only preferred
├── README.md                         # required
├── CHANGELOG.md                      # expected; needs a `## [<version>]` entry
└── ci-smoke.sh                       # optional; CI runs it automatically
```

## What the validator enforces

| Check | Level |
|---|---|
| `plugin.json` valid JSON; kebab-case `name`; semver `version`; real `description` | error |
| `README.md` exists | error |
| `SKILL.md` has frontmatter; `name` equals its folder name and is kebab-case | error |
| Skill `description` is 20–1024 characters | error |
| Every `references/…`, `scripts/…`, `assets/…` file mentioned in `SKILL.md` exists | error |
| `scripts/*.py` compile | error |
| No API keys, tokens, or private keys in any text file | error |
| `CHANGELOG.md` has an entry for the current version | warning |
| `SKILL.md` over 500 lines; description under 80 characters or still `TODO` | warning |
| Plugin folder not yet in `marketplace.json` | warning (sync fixes it) |

## SKILL.md rules of thumb

- **Description = what it does + when to use it.** It is the only thing Claude sees when deciding whether to trigger, so include the phrasings people actually type, not just the skill's name.
- **Keep `SKILL.md` lean.** Put long detail in `references/` and link to it from `SKILL.md` so it is loaded only when needed.
- **Explain why, not just what.** Rules with a reason generalize better than bare commands.
- **Don't invent capabilities.** If the skill can't verify something, it should say so.

## `ci-smoke.sh` (optional)

If your plugin ships scripts, add an executable `ci-smoke.sh` that runs them against fixtures in `examples/` and exits non-zero on failure. Resolve paths from the script's own location. See `plugins/ai-requirements-analyst/ci-smoke.sh`.

## Licensing

Plugins inherit the repository's MIT `LICENSE`. Only add a `LICENSE` inside a plugin folder if it truly needs different terms, and say so in its README.
