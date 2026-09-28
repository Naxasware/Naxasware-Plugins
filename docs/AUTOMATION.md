# Automation

Everything below is stdlib-only Python plus GitHub Actions.

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | push to `main`, every PR | JSON-checks every manifest; runs `scripts/validate_all_plugins.py` (all plugins and skills, Python 3.9 and 3.12); checks marketplace/README are in sync (informational); regression-tests the scaffolder; runs every `plugins/*/ci-smoke.sh`; runs `claude plugin validate` (best effort, non-blocking). The `CI passed` job is the one to mark required. |
| `sync.yml` | push to `main` touching `plugins/**` | Runs `scripts/sync_repo.py`, then commits regenerated `marketplace.json` and README plugin table as `github-actions[bot]`. |
| `release.yml` | tag `<plugin>-vX.Y.Z` | Checks the tag matches `plugin.json`, validates, smoke-tests, builds artifacts, creates a GitHub Release. |
| `dependabot.yml` | weekly | Keeps GitHub Action versions current. |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/validate_all_plugins.py` | Validate everything (see `docs/ADDING-A-PLUGIN.md` for the rule table). Writes a report to the workflow summary. |
| `scripts/sync_repo.py [--check]` | Regenerate `marketplace.json`, the README table, and the validator copy in `claude-project/knowledge/` from the sources of truth. |
| `scripts/new_plugin.py` | Scaffold a plugin from `templates/plugin-template/`. |
| `scripts/package_plugin.py` | Build `<plugin>-<version>.zip`, one `.skill` and one `.full.md` per skill, and release notes. |

## One-time repository settings (GitHub UI)

1. **Branch protection on `main`:** require pull requests and require the `CI passed` status check. Because `sync.yml` pushes to `main`, add `github-actions[bot]` to the bypass list, or the sync commit will be rejected.
2. **Actions → General → Workflow permissions:** "Read and write permissions" (needed by `sync.yml` and `release.yml`).
3. **Security:** enable secret scanning and push protection, Dependabot alerts, and private vulnerability reporting.
4. **CODEOWNERS:** edit `.github/CODEOWNERS` with a real user or team and uncomment it.

## Why the sync commit doesn't loop

`sync.yml` only triggers on `plugins/**` (and the sync script), and its commit changes only `README.md` and `marketplace.json`. Commits pushed with the built-in `GITHUB_TOKEN` also don't start new workflow runs.
