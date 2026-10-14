# Repo support patch (files outside plugins/)

Unzip at the repo root and overwrite. Needed because scripts/sync_repo.py otherwise re-adds the `metadata` key to every plugin.json on each push.

| File | Change |
|---|---|
| scripts/sync_repo.py | Stops writing `metadata`, removes `$schema` and `metadata`, takes the marketplace category from CATEGORIES (default general) |
| scripts/new_plugin.py | Docstring only |
| scripts/validate_all_plugins.py | Warns when plugin.json has `$schema` or `metadata` |
| templates/plugin-template/.claude-plugin/plugin.json | `metadata` block removed |
| claude-project/05-validate_all_plugins.py | Copy of the validator (re-upload to the Project) |
| claude-project/01-REPO-CONVENTIONS.md | plugin.json rules updated, chain note added (re-upload to the Project) |
