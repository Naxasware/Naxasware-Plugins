# Releasing

1. Bump `version` in `plugins/<plugin>/.claude-plugin/plugin.json` (semver) and add `## [X.Y.Z] - YYYY-MM-DD` to its `CHANGELOG.md`.
2. Push to `main` and wait for CI + Sync to finish (`git pull` to pick up the bot commit).
3. Tag and push:
   ```bash
   git tag <plugin>-v<X.Y.Z>
   git push origin <plugin>-v<X.Y.Z>
   ```
Undo a bad tag: `git push --delete origin <plugin>-v<X.Y.Z> && git tag -d <plugin>-v<X.Y.Z>`.
