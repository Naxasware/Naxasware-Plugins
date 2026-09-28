#!/usr/bin/env python3
"""
Scaffold a new plugin from templates/plugin-template/ and sync the repo.

    python3 scripts/new_plugin.py my-plugin \
        --display "My Plugin" --description "What it does and when to use it."
        [--skill my-skill]   # defaults to the plugin name
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def fill(text, values, is_json):
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", json.dumps(v)[1:-1] if is_json else v)
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name")
    ap.add_argument("--display")
    ap.add_argument("--description", default="TODO - one or two sentences on what this plugin does.")
    ap.add_argument("--skill")
    a = ap.parse_args()
    skill = a.skill or a.name
    for label, v in (("plugin name", a.name), ("skill name", skill)):
        if not KEBAB.match(v):
            sys.exit(f"{label} '{v}' must be kebab-case (a-z, 0-9, hyphens)")
    dest = ROOT / "plugins" / a.name
    if dest.exists():
        sys.exit(f"{dest} already exists")
    display = a.display or a.name.replace("-", " ").title()
    values = {"PLUGIN_NAME": a.name, "DISPLAY_NAME": display, "DESCRIPTION": a.description,
              "SKILL_NAME": skill, "DATE": datetime.date.today().isoformat()}
    tpl = ROOT / "templates" / "plugin-template"
    for src in sorted(tpl.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(tpl)
        parts = [skill if p == "__SKILL_NAME__" else p for p in rel.parts]
        out = dest.joinpath(*parts)
        out.parent.mkdir(parents=True, exist_ok=True)
        text = fill(src.read_text(encoding="utf-8"), values, src.suffix == ".json")
        out.write_text(text, encoding="utf-8")
        shutil.copymode(src, out)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_repo.py")], check=True)
    print(f"\nCreated plugins/{a.name}/ (skill: {skill})\nNext: edit SKILL.md, then run "
          f"python3 scripts/validate_all_plugins.py .")


if __name__ == "__main__":
    main()
