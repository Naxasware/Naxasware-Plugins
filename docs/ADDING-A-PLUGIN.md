# Adding a plugin

```bash
python3 scripts/new_plugin.py my-plugin --description "What it does and for whom." --category productivity
# edit plugins/my-plugin/skills/my-plugin/SKILL.md (write real trigger phrasings, remove the TODO)
python3 scripts/validate_all_plugins.py .   # expect: No errors.
git add plugins/my-plugin && git commit -m "feat(my-plugin): initial release" && git push
```
You do not need to run `sync_repo.py` or touch `README.md` / `marketplace.json`: the Sync workflow does it on push and on PRs. Running it locally is harmless (`python3 scripts/sync_repo.py`).

Rules: kebab-case names; folder name == `plugin.json` name; skill folder == SKILL.md `name`; description 20-1024 chars saying what it does AND when to use it; SKILL.md under 500 lines (detail goes in `references/`); every referenced file exists; scripts are stdlib-only Python; no secrets; license is Apache-2.0 (inherited, no per-plugin LICENSE). Add `ci-smoke.sh` (executable) when a plugin ships scripts.
