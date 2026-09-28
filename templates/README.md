# Templates

`plugin-template/` is what `scripts/new_plugin.py` copies to create a new plugin. `{{PLACEHOLDERS}}` are filled in by the script; a folder named `__SKILL_NAME__` becomes the skill's folder name. This directory is intentionally outside `plugins/`, so it is never validated, synced, or published.
