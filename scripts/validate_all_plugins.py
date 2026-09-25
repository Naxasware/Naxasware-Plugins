#!/usr/bin/env python3
"""
Dependency-free validator for this monorepo. Reads .claude-plugin/marketplace.json
and validates every plugin it lists — so adding a new plugin folder + a
marketplace entry automatically gets covered by CI with no workflow changes.

Checks:
  - .claude-plugin/marketplace.json parses and has required fields
  - no duplicate plugin names in the marketplace
  - each entry's relative `source` path exists and contains a plugin
  - each plugin's .claude-plugin/plugin.json (if present) parses and has
    required fields, and its `name` matches the marketplace entry's `name`
  - each plugin's skills/*/SKILL.md has valid frontmatter (name + description,
    description under the 1024-char platform limit)
  - every .py file under each plugin's scripts/ directories compiles

Usage:
    python3 scripts/validate_all_plugins.py [repo_root]

Exit code 0 if no errors, 1 if errors found. Intended to be the single
required check in CI (see .github/workflows/ci.yml) — it needs nothing
beyond the Python standard library.
"""

import json
import py_compile
import re
import sys
from pathlib import Path

MAX_DESCRIPTION_LEN = 1024


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_skill_md(skill_md: Path, errors, warnings):
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append(f"{skill_md}: no YAML frontmatter found")
        return

    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        errors.append(f"{skill_md}: malformed frontmatter block")
        return
    frontmatter = fm_match.group(1)

    if not re.search(r"^name:\s*\S+", frontmatter, re.MULTILINE):
        errors.append(f"{skill_md}: frontmatter missing 'name'")

    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE | re.DOTALL)
    if not desc_match:
        errors.append(f"{skill_md}: frontmatter missing 'description'")
    else:
        desc = desc_match.group(1).strip().strip('"')
        if len(desc) > MAX_DESCRIPTION_LEN:
            errors.append(f"{skill_md}: description is {len(desc)} chars, "
                           f"exceeds the {MAX_DESCRIPTION_LEN}-char limit")


def check_plugin_dir(plugin_dir: Path, expected_name: str, errors, warnings):
    plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if plugin_json_path.exists():
        try:
            data = load_json(plugin_json_path)
        except json.JSONDecodeError as e:
            errors.append(f"{plugin_json_path}: invalid JSON — {e}")
            data = None
        if data is not None:
            if "name" not in data:
                errors.append(f"{plugin_json_path}: missing required field 'name'")
            elif data["name"] != expected_name:
                errors.append(f"{plugin_json_path}: name '{data['name']}' does not match "
                               f"marketplace entry name '{expected_name}'")
            elif not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", data["name"]):
                warnings.append(f"{plugin_json_path}: name '{data['name']}' is not kebab-case")
            for recommended in ("version", "description", "author", "license"):
                if recommended not in data:
                    warnings.append(f"{plugin_json_path}: missing recommended field '{recommended}'")
    else:
        warnings.append(f"{plugin_dir}: no .claude-plugin/plugin.json — "
                         f"relying entirely on the marketplace entry's fields")

    skills_dir = plugin_dir / "skills"
    if not skills_dir.exists():
        warnings.append(f"{plugin_dir}: no skills/ directory found")
    else:
        found_any = False
        for skill_path in sorted(skills_dir.iterdir()):
            if not skill_path.is_dir():
                continue
            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                errors.append(f"{skill_path}: missing SKILL.md")
                continue
            found_any = True
            check_skill_md(skill_md, errors, warnings)

            scripts_dir = skill_path / "scripts"
            if scripts_dir.exists():
                for py_file in scripts_dir.glob("*.py"):
                    try:
                        py_compile.compile(str(py_file), doraise=True)
                    except py_compile.PyCompileError as e:
                        errors.append(f"{py_file}: fails to compile — {e}")
        if not found_any:
            warnings.append(f"{skills_dir}: no <name>/SKILL.md folders found")

    # Optional per-plugin CI hook, run separately by the CI workflow — just
    # verify it's executable-looking if present, don't run it here.
    smoke = plugin_dir / "ci-smoke.sh"
    if smoke.exists() and not smoke.stat().st_mode & 0o111:
        warnings.append(f"{smoke}: exists but is not executable (chmod +x)")


def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    repo_root = repo_root.resolve()

    errors, warnings = [], []

    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"
    if not marketplace_path.exists():
        print(f"ERROR: {marketplace_path} not found")
        sys.exit(1)

    try:
        marketplace = load_json(marketplace_path)
    except json.JSONDecodeError as e:
        print(f"ERROR: {marketplace_path}: invalid JSON — {e}")
        sys.exit(1)

    for required in ("name", "owner", "plugins"):
        if required not in marketplace:
            errors.append(f"{marketplace_path}: missing required field '{required}'")

    plugins = marketplace.get("plugins", [])
    if not plugins:
        warnings.append(f"{marketplace_path}: 'plugins' array is empty")

    names_seen = set()
    for i, entry in enumerate(plugins):
        if "name" not in entry or "source" not in entry:
            errors.append(f"{marketplace_path}: plugins[{i}] missing 'name' or 'source'")
            continue
        name = entry["name"]
        if name in names_seen:
            errors.append(f"{marketplace_path}: duplicate plugin name '{name}'")
        names_seen.add(name)

        source = entry["source"]
        if not isinstance(source, str) or not source.startswith("./"):
            warnings.append(f"{marketplace_path}: plugins[{i}] ('{name}') source '{source}' "
                             f"is not a simple relative path — skipping directory checks for it")
            continue

        plugin_dir = (repo_root / source).resolve()
        if not plugin_dir.exists():
            errors.append(f"{marketplace_path}: plugins[{i}] ('{name}') source '{source}' "
                           f"does not resolve to an existing directory")
            continue

        check_plugin_dir(plugin_dir, name, errors, warnings)

    print(f"Validated {repo_root} ({len(plugins)} plugin(s) listed)\n")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("No errors.")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
