# Installing AI Requirements Analyst

This plugin is distributed through the **Naxasware-Plugins** marketplace — the monorepo at the root of this checkout. You don't host anything separately; the marketplace and every plugin (including this one) live in one repository.

## Claude Code — as a plugin (recommended)

### Directly from GitHub

```bash
claude plugin marketplace add Naxasware/Naxasware-Plugins
claude plugin install ai-requirements-analyst@naxasware-plugins
```

### From a local clone

```bash
git clone https://github.com/Naxasware/Naxasware-Plugins.git
claude plugin marketplace add ./Naxasware-Plugins
claude plugin install ai-requirements-analyst@naxasware-plugins
```

If the install summary says `Run /reload-plugins to activate.`, run that command in your session.

### Validate before installing (recommended for CI or before publishing a new version)

```bash
claude plugin validate .   # run from the repo root — checks marketplace.json and every plugin
```

This checks manifest schema correctness and every plugin's skill frontmatter. Pass `--strict` in CI to turn warnings into failures. See `../../.github/workflows/ci.yml` for how this repo runs it automatically (as a best-effort check alongside the fully-owned `scripts/validate_all_plugins.py`).

### Roll out to a whole team

Add the marketplace and enable this plugin by default in your project's `.claude/settings.json` so teammates get it automatically once they trust the project folder:

```json
{
  "extraKnownMarketplaces": {
    "naxasware-plugins": {
      "source": { "source": "github", "repo": "Naxasware/Naxasware-Plugins" }
    }
  },
  "enabledPlugins": {
    "ai-requirements-analyst@naxasware-plugins": true
  }
}
```

### Updating

```bash
claude plugin marketplace update naxasware-plugins
claude plugin update ai-requirements-analyst@naxasware-plugins
```

### Uninstalling

```bash
claude plugin uninstall ai-requirements-analyst@naxasware-plugins
```

## claude.ai / Claude Desktop / Cowork — as a standalone skill

These surfaces install **skills**, not plugins, so use this plugin's `skills/ai-requirements-analyst/` folder on its own — no marketplace involved:

1. Package it (dependency-free — no `pip install` needed):
   ```bash
   # from plugins/ai-requirements-analyst/
   python3 tools/package_skill.py skills/ai-requirements-analyst dist/
   ```
   This produces `dist/ai-requirements-analyst.skill`.
2. In claude.ai / Claude Desktop / Cowork, upload that `.skill` file from **Settings → Capabilities → Skills** (or your org's equivalent skill-upload flow).
3. For an organization-wide rollout, your Anthropic org admin can upload it under **Organization settings → Skills** instead, so it's available to everyone without individual uploads.

## Claude Code — as a bare skill instead of a full plugin

If you don't want the plugin/marketplace layer at all, just drop the skill folder where Claude Code looks for skills:

```bash
# project-local
cp -r plugins/ai-requirements-analyst/skills/ai-requirements-analyst /path/to/your/project/.claude/skills/

# or user-level, available across all your projects
cp -r plugins/ai-requirements-analyst/skills/ai-requirements-analyst ~/.claude/skills/
```

No manifest, no marketplace — Claude Code picks it up on the next session.

## Verifying it works

Run this plugin's smoke test (also what CI runs):

```bash
cd plugins/ai-requirements-analyst
./ci-smoke.sh
```

Then, in Claude Code (or wherever you installed it), try a prompt like *"I want an app that helps small gyms track member check-ins and class bookings — turn this into requirements"* and confirm you get a structured Discovery Report with labeled assumptions and open questions rather than invented facts.
