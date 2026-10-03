#!/usr/bin/env python3
"""
Dependency-free validator for the whole monorepo.

Validates every plugin under plugins/ (not only those already listed in the
marketplace), so a brand-new skill is checked the moment it is added.

Per plugin:
  - .claude-plugin/plugin.json: valid JSON, kebab-case name, semver version,
    description present and free of TODO placeholders
  - README.md present (error); CHANGELOG.md present and mentioning the
    current version (warning)
  - every skills/<dir>/SKILL.md:
      * frontmatter present, `name` == directory name, kebab-case
      * `description` 20-1024 chars, no TODO placeholder
      * body under 500 lines (warning above that)
      * every referenced references/, scripts/, assets/ file exists
      * scripts/*.py compile
  - no obvious secrets (API keys, private keys) in any text file
  - license consistency: plugin.json license must be Apache-2.0 and no file may
    still say "MIT license" (warnings; scripts/sync_repo.py fixes plugin.json)
Repo-wide:
  - marketplace.json valid, no duplicate names, sources resolve, names match
    each plugin.json
  - plugin folders not yet in the marketplace -> warning (sync_repo.py fixes)

Exit code 1 if any error. If $GITHUB_STEP_SUMMARY is set, a Markdown report is
appended to it so results show on the workflow run page.

Usage: python3 scripts/validate_all_plugins.py [repo_root]
"""
import json
import os
import py_compile
import re
import sys
from pathlib import Path

EXPECTED_LICENSE = "Apache-2.0"
MAX_DESC = 1024
MIN_DESC = 20
MAX_SKILL_LINES = 500
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$")
REF_PATH = re.compile(r"(?<![\w/.-])((?:references|scripts|assets)/[A-Za-z0-9_\-/]+\.[A-Za-z0-9]+)")
SECRETS = [
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("Anthropic/OpenAI-style key", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{32,}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
]
TEXT_EXT = {".md", ".json", ".py", ".sh", ".yml", ".yaml", ".txt", ".toml", ".csv", ".html", ".js", ".ts"}
MIT_MENTION = re.compile(r'\bMIT[ -]licen[sc]e[d]?\b|"license"\s*:\s*"MIT"|\blicen[sc]e:\s*MIT\b', re.IGNORECASE)
SKIP_DIRS = {".git", "__pycache__", "node_modules", "dist"}


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.DOTALL)
    if not m:
        return None, text
    fm, lines, key, buf = {}, m.group(1).splitlines(), None, []
    for line in lines:
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km and not line.startswith((" ", "\t")):
            if key:
                fm[key] = " ".join(buf).strip()
            key, val = km.group(1), km.group(2)
            buf = [] if val in (">", "|", ">-", "|-") else [val]
        elif key:
            buf.append(line.strip())
    if key:
        fm[key] = " ".join(buf).strip()
    for k, v in fm.items():
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            fm[k] = v[1:-1]
    return fm, text[m.end():]


def check_skill(skill_dir, rep, rel):
    md = skill_dir / "SKILL.md"
    if not md.exists():
        rep.err(f"{rel}: missing SKILL.md")
        return
    text = md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm is None:
        rep.err(f"{rel}/SKILL.md: no YAML frontmatter")
        return
    name, desc = fm.get("name", ""), fm.get("description", "")
    if not name:
        rep.err(f"{rel}/SKILL.md: frontmatter missing 'name'")
    else:
        if not KEBAB.match(name):
            rep.err(f"{rel}/SKILL.md: name '{name}' is not kebab-case")
        if name != skill_dir.name:
            rep.err(f"{rel}/SKILL.md: name '{name}' must equal its folder name '{skill_dir.name}'")
    if not desc:
        rep.err(f"{rel}/SKILL.md: frontmatter missing 'description'")
    else:
        if len(desc) > MAX_DESC:
            rep.err(f"{rel}/SKILL.md: description is {len(desc)} chars (max {MAX_DESC})")
        if len(desc) < MIN_DESC:
            rep.err(f"{rel}/SKILL.md: description is only {len(desc)} chars (min {MIN_DESC})")
        elif len(desc) < 80:
            rep.warn(f"{rel}/SKILL.md: description is short ({len(desc)} chars) - say what it does AND when to use it")
        if "TODO" in desc:
            rep.warn(f"{rel}/SKILL.md: description still contains a TODO placeholder")
    n = len(text.splitlines())
    if n > MAX_SKILL_LINES:
        rep.warn(f"{rel}/SKILL.md: {n} lines (guideline max {MAX_SKILL_LINES}) - move detail into references/")
    seen = set()
    for ref in REF_PATH.findall(body):
        if ref in seen:
            continue
        seen.add(ref)
        if not (skill_dir / ref).exists():
            rep.err(f"{rel}/SKILL.md: references '{ref}' but that file does not exist")
    scripts = skill_dir / "scripts"
    if scripts.is_dir():
        for py in sorted(scripts.glob("*.py")):
            try:
                py_compile.compile(str(py), doraise=True)
            except py_compile.PyCompileError as e:
                rep.err(f"{rel}/scripts/{py.name}: does not compile - {e}")


def scan_secrets(plugin_dir, rep, root):
    for p in plugin_dir.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXT or SKIP_DIRS & set(p.parts):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for label, rx in SECRETS:
            if rx.search(txt):
                rep.err(f"{p.relative_to(root)}: looks like it contains a secret ({label})")


def scan_license_mentions(plugin_dir, rep, root):
    for p in plugin_dir.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".md", ".json", ".txt", ".toml"} or SKIP_DIRS & set(p.parts):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if MIT_MENTION.search(txt):
            rep.warn(f"{p.relative_to(root)}: mentions the MIT license; this repo is {EXPECTED_LICENSE}")


def check_plugin(plugin_dir, root, rep, expected_name=None):
    rel = str(plugin_dir.relative_to(root))
    pj_path = plugin_dir / ".claude-plugin" / "plugin.json"
    version = None
    if not pj_path.exists():
        rep.err(f"{rel}: missing .claude-plugin/plugin.json")
    else:
        try:
            pj = load_json(pj_path)
        except json.JSONDecodeError as e:
            rep.err(f"{rel}/.claude-plugin/plugin.json: invalid JSON - {e}")
            pj = {}
        name = pj.get("name")
        if not name:
            rep.err(f"{rel}/.claude-plugin/plugin.json: missing 'name'")
        else:
            if not KEBAB.match(name):
                rep.err(f"{rel}/.claude-plugin/plugin.json: name '{name}' is not kebab-case")
            if expected_name and name != expected_name:
                rep.err(f"{rel}: plugin.json name '{name}' != marketplace entry '{expected_name}'")
            if name != plugin_dir.name:
                rep.warn(f"{rel}: folder name differs from plugin name '{name}'")
        version = pj.get("version")
        if not version:
            rep.err(f"{rel}/.claude-plugin/plugin.json: missing 'version'")
        elif not SEMVER.match(version):
            rep.err(f"{rel}/.claude-plugin/plugin.json: version '{version}' is not semver (X.Y.Z)")
        d = pj.get("description", "")
        if not d:
            rep.err(f"{rel}/.claude-plugin/plugin.json: missing 'description'")
        elif "TODO" in d:
            rep.err(f"{rel}/.claude-plugin/plugin.json: description still has a TODO placeholder")
        for f in ("author", "license"):
            if f not in pj:
                rep.warn(f"{rel}/.claude-plugin/plugin.json: missing recommended '{f}'")
        if pj.get("license") and pj["license"] != EXPECTED_LICENSE:
            rep.warn(f"{rel}/.claude-plugin/plugin.json: license '{pj['license']}' should be {EXPECTED_LICENSE}")
    if not (plugin_dir / "README.md").exists():
        rep.err(f"{rel}: missing README.md")
    cl = plugin_dir / "CHANGELOG.md"
    if not cl.exists():
        rep.warn(f"{rel}: missing CHANGELOG.md")
    elif version and f"[{version}]" not in cl.read_text(encoding="utf-8"):
        rep.warn(f"{rel}: CHANGELOG.md has no '## [{version}]' entry for the current version")
    smoke = plugin_dir / "ci-smoke.sh"
    if smoke.exists() and not smoke.stat().st_mode & 0o111:
        rep.warn(f"{rel}/ci-smoke.sh: not executable (CI runs it via bash, but run: chmod +x)")
    skills = plugin_dir / "skills"
    found = False
    if skills.is_dir():
        for sd in sorted(p for p in skills.iterdir() if p.is_dir()):
            found = True
            check_skill(sd, rep, f"{rel}/skills/{sd.name}")
    if not found:
        rep.warn(f"{rel}: no skills/<name>/SKILL.md found")
    scan_secrets(plugin_dir, rep, root)
    scan_license_mentions(plugin_dir, rep, root)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    rep = Report()
    mp_path = root / ".claude-plugin" / "marketplace.json"
    listed = {}
    if not mp_path.exists():
        rep.err(".claude-plugin/marketplace.json not found")
    else:
        try:
            mp = load_json(mp_path)
        except json.JSONDecodeError as e:
            rep.err(f"marketplace.json: invalid JSON - {e}")
            mp = {}
        for req in ("name", "owner", "plugins"):
            if req not in mp:
                rep.err(f"marketplace.json: missing '{req}'")
        for i, e in enumerate(mp.get("plugins", [])):
            if "name" not in e or "source" not in e:
                rep.err(f"marketplace.json: plugins[{i}] needs 'name' and 'source'")
                continue
            if e["name"] in listed:
                rep.err(f"marketplace.json: duplicate plugin '{e['name']}'")
            listed[e["name"]] = e
            src = e["source"]
            if isinstance(src, str) and src.startswith("./") and not (root / src).is_dir():
                rep.err(f"marketplace.json: '{e['name']}' source '{src}' does not exist")
    lic = root / "LICENSE"
    if not lic.exists():
        rep.warn("LICENSE file not found at repo root")
    elif "Apache License" not in lic.read_text(encoding="utf-8", errors="ignore"):
        rep.warn(f"LICENSE does not look like {EXPECTED_LICENSE}")
    readme = root / "README.md"
    if readme.exists() and MIT_MENTION.search(readme.read_text(encoding="utf-8", errors="ignore")):
        rep.warn("README.md mentions the MIT license; this repo is " + EXPECTED_LICENSE)
    plugins_dir = root / "plugins"
    dirs = sorted(p for p in plugins_dir.iterdir() if p.is_dir()) if plugins_dir.is_dir() else []
    if not dirs:
        rep.warn("no plugin folders found under plugins/")
    listed_sources = {str((root / e["source"]).resolve()) for e in listed.values()
                      if isinstance(e.get("source"), str) and e["source"].startswith("./")}
    for d in dirs:
        expected = next((n for n, e in listed.items()
                         if isinstance(e.get("source"), str) and (root / e["source"]).resolve() == d.resolve()), None)
        if str(d.resolve()) not in listed_sources:
            rep.warn(f"plugins/{d.name}: not listed in marketplace.json - run `python3 scripts/sync_repo.py`")
        check_plugin(d, root, rep, expected)

    print(f"Validated {root} - {len(dirs)} plugin folder(s), {len(listed)} listed in marketplace\n")
    print(f"ERRORS ({len(rep.errors)}):" if rep.errors else "No errors.")
    for e in rep.errors:
        print(f"  - {e}")
    if rep.warnings:
        print(f"\nWARNINGS ({len(rep.warnings)}):")
        for w in rep.warnings:
            print(f"  - {w}")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### Plugin validation: {'FAILED' if rep.errors else 'passed'}\n\n")
            f.write(f"{len(dirs)} plugin folder(s) checked.\n\n")
            for label, items in (("Errors", rep.errors), ("Warnings", rep.warnings)):
                if items:
                    f.write(f"**{label} ({len(items)})**\n\n" + "\n".join(f"- {i}" for i in items) + "\n\n")
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
