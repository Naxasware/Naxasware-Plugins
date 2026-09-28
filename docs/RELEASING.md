# Releasing a plugin

Plugins are versioned independently (semver). A release is a tag named `<plugin-name>-v<version>`.

1. Bump `version` in `plugins/<name>/.claude-plugin/plugin.json`.
   - patch: fixes and wording; minor: new backward-compatible capability; major: changed output format, schema, or ID scheme.
2. Add a `## [<version>] - YYYY-MM-DD` section to that plugin's `CHANGELOG.md`. It becomes the release notes.
3. Merge to `main` (CI green, sync commit landed).
4. Tag and push:
   ```bash
   git pull
   git tag ai-requirements-analyst-v2.1.0
   git push origin ai-requirements-analyst-v2.1.0
   ```
5. `release.yml` verifies the tag matches `plugin.json`, validates, smoke-tests, and publishes a GitHub Release with:
   - `<plugin>-<version>.zip`: the whole plugin folder
   - `<skill>.skill`: upload to claude.ai / Claude Desktop / Cowork
   - `<skill>.full.md`: single-file instructions for non-Claude agents

Claude Code users get new versions with `claude plugin marketplace update naxasware-plugins` then `claude plugin update <name>@naxasware-plugins`.

**Wrong tag?** Delete it (`git push --delete origin <tag>` and `git tag -d <tag>`), fix, re-tag. The release job fails before publishing if the version doesn't match.
