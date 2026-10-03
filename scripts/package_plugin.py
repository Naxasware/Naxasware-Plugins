#!/usr/bin/env python3
"""Package a plugin for release.

Usage: python3 scripts/package_plugin.py <plugin-name> [--root DIR] [--out dist] [--expect-version X.Y.Z]
Writes to --out:
  <plugin>-<version>.zip   the plugin folder
  <skill>.skill            one zip per skill (skill folder at archive top level)
  <skill>.full.md          SKILL.md body + references/*.md in one file, for non-Claude agents
  RELEASE_NOTES.md         the matching CHANGELOG.md section
Exit codes: 0 ok, 1 error (missing plugin, version mismatch with --expect-version).
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

SKIP = {"__pycache__", ".DS_Store"}


def files(base):
    for p in sorted(base.rglob("*")):
        if p.is_file() and not (SKIP & set(p.parts)) and p.suffix != ".pyc":
            yield p


def frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.DOTALL)
    return (m.group(1), text[m.end():]) if m else ("", text)


def zip_dir(src, zpath, prefix):
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files(src):
            z.write(p, f"{prefix}/{p.relative_to(src).as_posix()}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plugin")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--out", default="dist")
    ap.add_argument("--expect-version")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    pdir = root / "plugins" / a.plugin
    pj_path = pdir / ".claude-plugin" / "plugin.json"
    if not pj_path.exists():
        sys.exit(f"error: {pj_path} not found")
    version = json.loads(pj_path.read_text(encoding="utf-8")).get("version", "")
    if a.expect_version and a.expect_version != version:
        sys.exit(f"error: tag version {a.expect_version} != plugin.json version {version}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    zip_dir(pdir, out / f"{a.plugin}-{version}.zip", a.plugin)

    for sd in sorted(p for p in (pdir / "skills").glob("*") if p.is_dir()):
        zip_dir(sd, out / f"{sd.name}.skill", sd.name)
        fm, body = frontmatter((sd / "SKILL.md").read_text(encoding="utf-8"))
        parts = [f"---\n{fm}\n---\n", body.strip() + "\n"]
        for ref in sorted((sd / "references").glob("*.md")) if (sd / "references").is_dir() else []:
            parts.append(f"\n---\n\n# Reference: references/{ref.name}\n\n{ref.read_text(encoding='utf-8').strip()}\n")
        scripts = sorted(p.name for p in (sd / "scripts").glob("*")) if (sd / "scripts").is_dir() else []
        if scripts:
            parts.append("\n---\n\nNote: the full plugin also ships helper scripts (" + ", ".join(scripts)
                         + "); they are not inlined here.\n")
        (out / f"{sd.name}.full.md").write_text("".join(parts), encoding="utf-8")

    notes = f"Release of {a.plugin} {version}.\n"
    cl = pdir / "CHANGELOG.md"
    if cl.exists():
        m = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)", cl.read_text(encoding="utf-8"),
                      re.DOTALL | re.MULTILINE)
        if m and m.group(1).strip():
            notes = m.group(1).strip() + "\n"
    (out / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
    print(f"Packaged {a.plugin} {version} into {out}/: " + ", ".join(sorted(p.name for p in out.iterdir())))


if __name__ == "__main__":
    main()
