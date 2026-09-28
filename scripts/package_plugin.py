#!/usr/bin/env python3
"""
Build release artifacts for one plugin (used by .github/workflows/release.yml,
also handy locally).

For plugins/<name>/ it writes into --out (default dist/):
  <name>-<version>.zip      the whole plugin folder
  <skill>.skill             one per skill, uploadable to claude.ai / Desktop / Cowork
  <skill>.full.md           one per skill: SKILL.md + references flattened into a single
                            Markdown file for non-Claude agents (system-prompt use)
and optionally --notes-out FILE with that version's CHANGELOG section.

Usage: python3 scripts/package_plugin.py <plugin-name> [--out dist] [--notes-out notes.md]
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", ".git", "node_modules", "dist"}
SKIP_SUFFIX = {".pyc"}


def files_under(base):
    for p in sorted(base.rglob("*")):
        if p.is_file() and not (SKIP_DIRS & set(p.relative_to(base).parts)) and p.suffix not in SKIP_SUFFIX \
                and p.name != ".DS_Store":
            yield p


def zip_dir(src, out_zip, arc_root):
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files_under(src):
            z.write(p, arcname=str(Path(arc_root) / p.relative_to(src)))


def strip_frontmatter(text):
    m = re.match(r"^---\r?\n.*?\r?\n---\r?\n?", text, re.DOTALL)
    return text[m.end():] if m else text


def flatten(skill_dir):
    parts = [f"# {skill_dir.name} - full instructions (bundled)\n\nGenerated file: edit SKILL.md and "
             f"references/ in the source repository, not this file.\n",
             strip_frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))]
    refs = skill_dir / "references"
    if refs.is_dir():
        for r in sorted(refs.glob("*.md")):
            parts.append(f"\n---\n\n## Reference: {r.stem}\n\n" + r.read_text(encoding="utf-8"))
    return "\n".join(parts)


def changelog_section(plugin_dir, version):
    cl = plugin_dir / "CHANGELOG.md"
    if not cl.exists():
        return f"Release {version}"
    text = cl.read_text(encoding="utf-8")
    m = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)", text, re.DOTALL | re.MULTILINE)
    return m.group(1).strip() if m else f"Release {version}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plugin")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--notes-out")
    a = ap.parse_args()
    pdir = ROOT / "plugins" / a.plugin
    pj_path = pdir / ".claude-plugin" / "plugin.json"
    if not pj_path.exists():
        sys.exit(f"No such plugin: {a.plugin}")
    version = json.loads(pj_path.read_text(encoding="utf-8"))["version"]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    zip_dir(pdir, out / f"{a.plugin}-{version}.zip", a.plugin)
    print(f"wrote {out / f'{a.plugin}-{version}.zip'}")
    skills = pdir / "skills"
    for sd in sorted(p for p in skills.iterdir() if p.is_dir()) if skills.is_dir() else []:
        zip_dir(sd, out / f"{sd.name}.skill", sd.name)
        (out / f"{sd.name}.full.md").write_text(flatten(sd), encoding="utf-8")
        print(f"wrote {out / (sd.name + '.skill')} and {sd.name}.full.md")
    if a.notes_out:
        Path(a.notes_out).write_text(changelog_section(pdir, version) + "\n", encoding="utf-8")
        print(f"wrote {a.notes_out}")


if __name__ == "__main__":
    main()
