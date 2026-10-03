# File skeletons

## SKILL.md
```markdown
---
name: <skill-name>
description: <What it does, in one sentence.> Use when <situations>, including when the user says things like "<phrase>", "<phrase>", or doesn't name the skill but describes <the need>. <Optional: what it is NOT for.>
---

# <Display Name>

<One paragraph: purpose and the outcome it produces.>

## When to use / not use

## Workflow
1. ...

## Rules that always apply
- <rule> (<why it matters>)

## References
- `references/<file>.md`: <when to read it>
```

## README.md (plugin)
````markdown
# <Display Name>

<Description.>

Part of the [Naxasware-Plugins](../../README.md) marketplace.

## Install
```bash
claude plugin marketplace add Naxasware/Naxasware-Plugins
claude plugin install <plugin-name>@naxasware-plugins
```
Other agents: use the `<skill-name>.full.md` file attached to each release as a system prompt.

## What it does
## Example prompts
## Layout
## License
Inherits the repository's [Apache-2.0 license](../../LICENSE).
````

## CHANGELOG.md
```markdown
# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).

## [1.0.0] - YYYY-MM-DD
### Added
- Initial release: <summary>.
```

## ci-smoke.sh (only when the plugin ships scripts)
```bash
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$HERE/skills/<skill-name>/scripts/<script>.py" "$HERE/examples/<fixture>"
echo "<plugin-name>: smoke checks passed."
```
Make it executable (`chmod +x`); zip files created in a sandbox usually preserve this, but tell the owner to `chmod +x` if not.

## Script header
```python
#!/usr/bin/env python3
"""<What it does, inputs, outputs, exit codes.>"""
```
