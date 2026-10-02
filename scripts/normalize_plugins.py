#!/usr/bin/env python3
"""Normalize plugins/*/.claude-plugin/plugin.json to the repo's canonical fields.

Forces: license ("Apache-2.0"), author, homepage, repository. Fills `name`
from the folder name when missing. Never touches version, description,
keywords or metadata. Idempotent: a second run changes nothing.

Usage: python3 scripts/normalize_plugins.py [repo_root] [--check]
  --check  write nothing; exit 1 if any file would change.
Exit codes: 0 ok / nothing to change, 1 changes needed (--check) or bad input.
"""
import json
import sys
from pathlib import Path

OWNER = "Naxasware"
REPO = "https://github.com/Naxasware/Naxasware-Plugins"
LICENSE_ID = "Apache-2.0"


def canonical(name):
    return {
        "author": {"name": OWNER, "url": "https://github.com/Naxasware"},
        "homepage": f"{REPO}/tree/main/plugins/{name}",
        "repository": REPO,
        "license": LICENSE_ID,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    root = Path(args[0] if args else ".").resolve()
    pdir = root / "plugins"
    bad = changed = 0
    for d in sorted(p for p in pdir.iterdir() if p.is_dir()) if pdir.is_dir() else []:
        path = d / ".claude-plugin" / "plugin.json"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"ERROR {path.relative_to(root)}: invalid JSON - {e}")
            bad += 1
            continue
        if not isinstance(data, dict):
            print(f"ERROR {path.relative_to(root)}: top level must be an object")
            bad += 1
            continue
        if data.get("name") not in (None, d.name):
            print(f"ERROR {path.relative_to(root)}: name '{data['name']}' != folder '{d.name}'")
            bad += 1
            continue
        new = dict(data)
        new.setdefault("name", d.name)
        new.update(canonical(d.name))
        if new != data:
            changed += 1
            fixed = sorted(k for k in new if data.get(k) != new[k])
            print(f"{'WOULD FIX' if check else 'fixed'} {path.relative_to(root)}: {', '.join(fixed)}")
            if not check:
                path.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{changed} file(s) {'need' if check else 'needed'} changes, {bad} error(s).")
    sys.exit(1 if bad or (check and changed) else 0)


if __name__ == "__main__":
    main()
