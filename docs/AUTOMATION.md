# Automation

| Workflow | Trigger | What it does |
| --- | --- | --- |
| `ci.yml` | push to `main`, every PR | Validates all plugins, runs each `plugins/*/ci-smoke.sh`, regression-tests scaffold + sync + package scripts. |
| `sync.yml` | push to `main` and PRs touching `plugins/**` | Runs `scripts/sync_repo.py`: rebuilds the README plugin table and `.claude-plugin/marketplace.json`, normalizes each `plugin.json` (name = folder, license `Apache-2.0`, author/homepage/repository filled when missing), commits the result back to the branch. |
| `release.yml` | push tag `<plugin>-v<X.Y.Z>` | Checks the tag matches `plugin.json`, validates, packages, publishes a release with `.zip`, `.skill` and `.full.md` files and the CHANGELOG section as notes. |

## Things to know
- Commits made by `GITHUB_TOKEN` do not trigger other workflows. After a bot sync commit on a PR, CI does not re-run automatically; re-run it from the Actions tab or push another commit if a required check is pending.
- PRs from forks cannot be pushed to (read-only token). Sync is skipped for them and runs on the push to `main` after merge.
- If `main` is protected, allow `github-actions[bot]` to bypass the rule (or the sync push on `main` will be rejected).
- Settings → Actions → General → Workflow permissions: leave "Read and write" enabled (the workflows also request `contents: write` explicitly).
- Run the same checks locally: `python3 scripts/validate_all_plugins.py .` and `python3 scripts/sync_repo.py --check`.
