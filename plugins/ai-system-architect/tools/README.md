# Plugin tooling

Dev tools specific to this plugin — not needed by end users just installing it, and not part of the skill runtime itself. For repo-wide validation across all plugins, see `../../../scripts/validate_all_plugins.py` (or `../../../scripts/README.md`).

| Script | Purpose |
|---|---|
| `package_skill.py` | Zips `skills/ai-system-architect/` into a `.skill` file for upload to claude.ai / Claude Desktop / Cowork. |
| `build_context_bundle.py` | Flattens `SKILL.md` + `references/*.md` into one Markdown file (`dist/ai-system-architect.full.md`) for non-Claude agent frameworks — see `../docs/USING-WITH-OTHER-AGENTS.md`. |

```bash
# from plugins/ai-system-architect/
python3 tools/package_skill.py skills/ai-system-architect dist/
python3 tools/build_context_bundle.py
```

Both are pure Python 3 standard library — nothing to install.
