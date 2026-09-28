#!/usr/bin/env python3
"""
Keep generated repo files in sync with what is actually in plugins/.

  * .claude-plugin/marketplace.json -> `plugins` array is rebuilt from every
    plugins/*/.claude-plugin/plugin.json (top-level keys are preserved)
  * README.md -> the table between <!-- PLUGINS:START --> and <!-- PLUGINS:END -->
  * claude-project/knowledge/05-validate_all_plugins.py -> copy of the validator, so a
    Claude Project can run the same checks as CI

So adding a plugin = adding its folder. Nothing to hand-edit.

Usage:
    python3 scripts/sync_repo.py            # write changes
    python3 scripts/sync_repo.py --check    # exit 1 if anything is out of date
"""
import argparse
import json
import re
import sys
from pathlib import Path

START, END = "<!-- PLUGINS:START -->", "<!-- PLUGINS:END -->"


def discover(root):
    out = []
    pdir = root / "plugins"
    if not pdir.is_dir():
        return out
    for d in sorted(p for p in pdir.iterdir() if p.is_dir()):
        pj = d / ".claude-plugin" / "plugin.json"
        if not pj.exists():
            continue
        data = json.loads(pj.read_text(encoding="utf-8"))
        skills = sorted(s.name for s in (d / "skills").iterdir()
                        if s.is_dir() and (s / "SKILL.md").exists()) if (d / "skills").is_dir() else []
        out.append((d, data, skills))
    return sorted(out, key=lambda t: t[1].get("name", t[0].name))


def build_marketplace(root, plugins):
    path = root / ".claude-plugin" / "marketplace.json"
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    old = {e.get("name"): e for e in existing.get("plugins", [])}
    entries = []
    for d, pj, _ in plugins:
        name = pj.get("name", d.name)
        entry = {
            "name": name,
            "source": f"./plugins/{d.name}",
            "displayName": pj.get("displayName", name),
            "description": pj.get("description", ""),
            "category": (pj.get("metadata") or {}).get("category") or old.get(name, {}).get("category", "general"),
            "tags": (pj.get("keywords") or [])[:5],
        }
        entries.append(entry)
    result = {k: v for k, v in existing.items() if k != "plugins"}
    result.setdefault("name", "naxasware-plugins")
    result.setdefault("owner", {"name": "Naxasware", "url": "https://github.com/Naxasware"})
    result["plugins"] = entries
    return json.dumps(result, indent=2, ensure_ascii=False) + "\n"


def esc(s):
    return s.replace("|", "\\|").replace("\n", " ").strip()


def build_table(plugins):
    if not plugins:
        return "_No plugins yet._"
    rows = ["| Plugin | What it does | Version | Skills |", "|---|---|---|---|"]
    for d, pj, skills in plugins:
        name = pj.get("name", d.name)
        title = pj.get("displayName", name)
        skill_txt = ", ".join(f"`{s}`" for s in skills) or "-"
        rows.append(f"| [{esc(title)}](plugins/{d.name}) | {esc(pj.get('description', ''))} | "
                    f"{esc(str(pj.get('version', '?')))} | {skill_txt} |")
    return "\n".join(rows)


def build_readme(root, plugins):
    path = root / "README.md"
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        sys.exit(f"README.md is missing the {START} / {END} markers")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    return pattern.sub(lambda _m: f"{START}\n{build_table(plugins)}\n{END}", text, count=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail instead of writing")
    ap.add_argument("root", nargs="?", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    plugins = discover(root)
    targets = {
        root / ".claude-plugin" / "marketplace.json": build_marketplace(root, plugins),
        root / "README.md": build_readme(root, plugins),
    }
    validator = root / "scripts" / "validate_all_plugins.py"
    if validator.exists():
        targets[root / "claude-project" / "knowledge" / "05-validate_all_plugins.py"] = \
            validator.read_text(encoding="utf-8")
    stale = []
    for path, new in targets.items():
        cur = path.read_text(encoding="utf-8") if path.exists() else ""
        if cur != new:
            stale.append(path.relative_to(root))
            if not args.check:
                path.write_text(new, encoding="utf-8")
    if args.check:
        if stale:
            print("Out of date: " + ", ".join(map(str, stale)) + "\nRun: python3 scripts/sync_repo.py")
            sys.exit(1)
        print(f"In sync ({len(plugins)} plugin(s)).")
    else:
        print(("Updated: " + ", ".join(map(str, stale))) if stale else "Already in sync.")


if __name__ == "__main__":
    main()
