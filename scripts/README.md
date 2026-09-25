# Org-level scripts

Dependency-free tooling that operates across every plugin in this monorepo, driven by `.claude-plugin/marketplace.json` — add a plugin folder and a marketplace entry, and these automatically cover it.

| Script | Purpose |
|---|---|
| `validate_all_plugins.py` | Validates `marketplace.json` and every plugin it lists: manifest schema, name consistency, `SKILL.md` frontmatter, and that all bundled Python scripts compile. This is the check CI runs on every push/PR. |

```bash
python3 scripts/validate_all_plugins.py .
```

For tooling specific to one plugin (packaging a `.skill` file, bundling instructions for non-Claude agents), see that plugin's own `tools/` directory, e.g. `plugins/ai-requirements-analyst/tools/`.
