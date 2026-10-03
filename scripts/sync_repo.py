#!/usr/bin/env python3
"""Regenerate everything that is derived from plugins/.

Single source of truth: plugins/<name>/.claude-plugin/plugin.json (+ folder name).

Writes (or, with --check, only compares):
  1. plugins/<name>/.claude-plugin/plugin.json  normalized: name == folder, license
     forced to the repo license, author/homepage/repository/displayName filled
     in when missing, keys in canonical order. Your own values are kept.
  2. .claude-plugin/marketplace.json            rebuilt from all plugins.
  3. README.md                                  plugin table between
                                                <!-- PLUGINS:START --> and <!-- PLUGINS:END -->.

Deterministic (no timestamps), so running it twice changes nothing.

Usage: python3 scripts/sync_repo.py [--root DIR] [--check]
Exit codes: 0 in sync / written, 1 --check found drift, 2 error.
"""
import argparse
import json
import sys
from pathlib import Path

REPO = "Naxasware/Naxasware-Plugins"
REPO_URL = f"https://github.com/{REPO}"
MARKETPLACE_NAME = "naxasware-plugins"
OWNER = {"name": "Naxasware", "url": "https://github.com/Naxasware"}
LICENSE_ID = "Apache-2.0"
START, END = "<!-- PLUGINS:START -->", "<!-- PLUGINS:END -->"
KEY_ORDER = ["name", "displayName", "version", "description", "author", "homepage",
             "repository", "license", "keywords", "metadata"]


def title(name):
    return " ".join(w.capitalize() for w in name.split("-"))


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def normalize(pj, folder):
    pj = dict(pj)
    pj["name"] = folder
    pj.setdefault("displayName", title(folder))
    if not isinstance(pj.get("author"), dict) or not pj["author"].get("name"):
        pj["author"] = dict(OWNER)
    pj.setdefault("homepage", f"{REPO_URL}/tree/main/plugins/{folder}")
    pj.setdefault("repository", REPO_URL)
    pj["license"] = LICENSE_ID
    meta = pj.get("metadata") if isinstance(pj.get("metadata"), dict) else {}
    meta.setdefault("category", "general")
    pj["metadata"] = meta
    ordered = {k: pj[k] for k in KEY_ORDER if k in pj}
    ordered.update({k: v for k, v in pj.items() if k not in ordered})
    return ordered


def entry(pj, folder):
    e = {"name": folder, "source": f"./plugins/{folder}"}
    for k in ("description", "version", "author", "homepage", "repository", "license", "keywords"):
        if k in pj:
            e[k] = pj[k]
    e["category"] = pj["metadata"]["category"]
    return e


def cell(text):
    return " ".join(str(text).split()).replace("|", "\\|")


def table(plugins):
    if not plugins:
        return "_No plugins yet._"
    rows = ["| Plugin | Description | Version | Install |", "| --- | --- | --- | --- |"]
    for folder, pj in plugins:
        rows.append(f"| [{cell(pj['displayName'])}](plugins/{folder}) | {cell(pj.get('description', ''))} "
                    f"| {cell(pj.get('version', ''))} | `claude plugin install {folder}@{MARKETPLACE_NAME}` |")
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    outputs, plugins, failed = {}, [], False

    pdir = root / "plugins"
    for d in sorted(p for p in (pdir.iterdir() if pdir.is_dir() else []) if p.is_dir() and not p.name.startswith(".")):
        pj_path = d / ".claude-plugin" / "plugin.json"
        if not pj_path.exists():
            print(f"warning: {d.name}: no .claude-plugin/plugin.json, skipped", file=sys.stderr)
            continue
        try:
            raw = json.loads(pj_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("top level must be an object")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"error: {d.name}: invalid plugin.json - {e}", file=sys.stderr)
            failed = True
            continue
        pj = normalize(raw, d.name)
        outputs[pj_path] = dump(pj)
        plugins.append((d.name, pj))

    market = {"name": MARKETPLACE_NAME, "owner": OWNER,
              "metadata": {"description": "Naxasware's Claude Code plugin marketplace."},
              "plugins": [entry(pj, f) for f, pj in plugins]}
    outputs[root / ".claude-plugin" / "marketplace.json"] = dump(market)

    readme = root / "README.md"
    if not readme.exists():
        print("error: README.md not found", file=sys.stderr)
        failed = True
    else:
        text = readme.read_text(encoding="utf-8")
        if START not in text or END not in text or text.index(START) > text.index(END):
            print(f"error: README.md must contain {START} ... {END}", file=sys.stderr)
            failed = True
        else:
            head, rest = text.split(START, 1)
            tail = rest.split(END, 1)[1]
            outputs[readme] = f"{head}{START}\n{table(plugins)}\n{END}{tail}"

    if failed:
        sys.exit(2)
    changed = []
    for path, new in outputs.items():
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != new:
            changed.append(path.relative_to(root))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(new, encoding="utf-8", newline="\n")
    verb = "would change" if args.check else "updated"
    print(f"{len(plugins)} plugin(s). " + (f"{verb}: " + ", ".join(map(str, changed)) if changed else "Already in sync."))
    sys.exit(1 if (args.check and changed) else 0)


if __name__ == "__main__":
    main()
