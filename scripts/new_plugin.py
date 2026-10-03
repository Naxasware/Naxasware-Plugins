#!/usr/bin/env python3
"""Scaffold plugins/<name>/ from templates/plugin-template.

Usage: python3 scripts/new_plugin.py <name> --description "What it does and for whom."
         [--skill NAME] [--display "Human Name"] [--category productivity]
         [--keywords a,b,c] [--version 0.1.0] [--root DIR]
The new skill description ends with a TODO so the validator nags until you write
real trigger phrasings. Exit codes: 0 ok, 1 bad input or folder exists.
"""
import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("name")
    ap.add_argument("--description", required=True)
    ap.add_argument("--skill")
    ap.add_argument("--display")
    ap.add_argument("--category", default="general")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--version", default="0.1.0")
    ap.add_argument("--root")
    a = ap.parse_args()
    here = Path(__file__).resolve().parent.parent
    root = Path(a.root).resolve() if a.root else here
    tpl = here / "templates" / "plugin-template"
    skill = a.skill or a.name
    for label, v in (("plugin name", a.name), ("skill name", skill)):
        if not KEBAB.match(v):
            sys.exit(f"error: {label} '{v}' must be kebab-case (a-z, 0-9, single hyphens)")
    dest = root / "plugins" / a.name
    if dest.exists():
        sys.exit(f"error: {dest} already exists")
    display = a.display or " ".join(w.capitalize() for w in a.name.split("-"))
    kws = [k.strip().lower() for k in a.keywords.split(",") if k.strip()] or a.name.split("-") + [a.category]
    kws = list(dict.fromkeys(kws))[:8]
    skill_desc = a.description.strip() + " TODO: add 'Use when...' trigger phrasings."
    tokens = {
        "__DISPLAY_NAME_JSON__": json.dumps(display), "__DESCRIPTION_JSON__": json.dumps(a.description.strip()),
        "__SKILL_DESCRIPTION_JSON__": json.dumps(skill_desc), "__KEYWORDS_JSON__": json.dumps(kws),
        "__CATEGORY_JSON__": json.dumps(a.category), "__PLUGIN_NAME__": a.name, "__SKILL_NAME__": skill,
        "__DISPLAY_NAME__": display, "__DESCRIPTION__": a.description.strip(), "__VERSION__": a.version,
        "__DATE__": date.today().isoformat(),
    }
    for src in sorted(tpl.rglob("*")):
        if not src.is_file():
            continue
        out = dest / Path(*[p.replace("__SKILL_NAME__", skill) for p in src.relative_to(tpl).parts])
        out.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        for k, v in tokens.items():
            text = text.replace(k, v)
        out.write_text(text, encoding="utf-8", newline="\n")
        shutil.copymode(src, out)
    print(f"Created {dest.relative_to(root)}\nNext: edit skills/{skill}/SKILL.md, then run "
          f"scripts/validate_all_plugins.py and scripts/sync_repo.py")


if __name__ == "__main__":
    main()
