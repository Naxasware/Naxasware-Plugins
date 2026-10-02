# PR sync

`.github/workflows/sync-pr.yml` runs on every push to a non-`main` branch and on every pull request that touches `plugins/**`. It runs `scripts/normalize_plugins.py` (canonical `plugin.json` fields) and `scripts/sync_repo.py` (`marketplace.json` and the README plugin table), then commits the result to the same branch as `github-actions[bot]`. The PR therefore already contains its registry entries when you merge. `sync.yml` still covers pushes to `main`.

## Settings
1. Settings > Actions > General > Workflow permissions: **Read and write permissions**.
2. Optional but recommended: create a fine-grained PAT (Contents: read/write on this repo) and save it as the repository secret `SYNC_TOKEN`. Commits pushed with the default `GITHUB_TOKEN` do not start new workflow runs, so without the secret the `CI passed` check will not re-run on the bot's commit. With it, CI runs again on the synced head.
3. Fork PRs cannot be pushed to; they only get a `--check`. Sync them after merge (`sync.yml`) or pull the branch and run both scripts locally.

## Local equivalents
```bash
python3 scripts/normalize_plugins.py
python3 scripts/sync_repo.py
```

## Licensing
The repository is Apache-2.0. `normalize_plugins.py` sets `"license": "Apache-2.0"` in every plugin.json.
