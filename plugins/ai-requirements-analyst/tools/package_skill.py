#!/usr/bin/env python3
"""
Package a skill folder into a .skill file for upload to claude.ai, Claude
Desktop, or Cowork (Settings -> Capabilities -> Skills, or your org's
equivalent skill-upload flow).

Dependency-free — does a basic frontmatter sanity check with a regex rather
than requiring PyYAML. For the stricter, authoritative check Anthropic's
own tooling runs, use skill-creator's scripts/quick_validate.py if you have
it available (requires `pip install pyyaml`).

Usage:
    python3 tools/package_skill.py <path/to/skill-folder> [output-dir]

Example:
    python3 tools/package_skill.py skills/ai-requirements-analyst dist/
"""

import re
import sys
import zipfile
from pathlib import Path

EXCLUDE_DIR_NAMES = {"__pycache__", "node_modules", ".git"}
EXCLUDE_FILE_GLOBS = ("*.pyc", ".DS_Store")


def basic_validate(skill_path: Path):
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, f"SKILL.md not found in {skill_path}"

    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False, "SKILL.md has no YAML frontmatter"

    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return False, "SKILL.md frontmatter block is malformed"

    frontmatter = match.group(1)
    if not re.search(r"^name:\s*\S+", frontmatter, re.MULTILINE):
        return False, "SKILL.md frontmatter missing 'name'"
    if not re.search(r"^description:\s*\S+", frontmatter, re.MULTILINE):
        return False, "SKILL.md frontmatter missing 'description'"

    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE | re.DOTALL)
    if desc_match and len(desc_match.group(1).strip()) > 1024:
        return False, "SKILL.md description exceeds 1024 characters"

    return True, "OK"


def should_exclude(rel_path: Path) -> bool:
    if any(part in EXCLUDE_DIR_NAMES for part in rel_path.parts):
        return True
    return any(rel_path.name == pat or rel_path.match(pat) for pat in EXCLUDE_FILE_GLOBS)


def package_skill(skill_path: Path, output_dir: Path):
    skill_path = skill_path.resolve()
    if not skill_path.is_dir():
        print(f"Error: {skill_path} is not a directory")
        return None

    ok, msg = basic_validate(skill_path)
    print("Validating skill...")
    if not ok:
        print(f"Validation failed: {msg}")
        return None
    print(f"OK: {msg}\n")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{skill_path.name}.skill"

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(skill_path.rglob("*")):
            if file_path.is_dir():
                continue
            rel_path = file_path.relative_to(skill_path.parent)
            if should_exclude(rel_path):
                continue
            zf.write(file_path, arcname=str(rel_path))
            print(f"  Added: {rel_path}")

    print(f"\nPackaged: {out_path}")
    return out_path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    skill_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

    result = package_skill(skill_path, output_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
