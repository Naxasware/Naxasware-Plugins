#!/usr/bin/env python3
"""One-time: switch every MIT reference in the repo to Apache-2.0.

The LICENSE file is already Apache-2.0; READMEs, plugin.json files, templates,
docs and the claude-project knowledge still say MIT. This rewrites the known
phrasings, then lists any remaining standalone "MIT" for manual review.
Skips .git, LICENSE, node_modules, dist.

Usage: python3 scripts/fix_license.py [repo_root] [--dry-run]
"""
import re
import sys
from pathlib import Path

EXT = {".md", ".json", ".py", ".sh", ".yml", ".yaml", ".txt", ".toml"}
SKIP = {".git", "node_modules", "dist", "__pycache__"}
RULES = [
    (r"license-MIT-[A-Za-z]+", "license-Apache--2.0-blue"),
    (r"License: MIT", "License: Apache 2.0"),
    (r"([\"']license[\"']\s*:\s*[\"'])MIT([\"'])", r"\1Apache-2.0\2"),
    (r"\[MIT license\]", "[Apache-2.0 license]"),
    (r"\bMIT license\b", "Apache-2.0 license"),
    (r"\blicense MIT\b", "license Apache-2.0"),
    (r"(?m)^MIT, see", "Apache-2.0, see"),
    (r"\(MIT\)", "(Apache-2.0)"),
    (r"\bMIT-licensed\b", "Apache-2.0-licensed"),
]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    root = Path(args[0] if args else ".").resolve()
    me = Path(__file__).resolve()
    left = []
    for p in sorted(root.rglob("*")):
        if (not p.is_file() or p.name == "LICENSE" or p.resolve() == me
                or p.suffix.lower() not in EXT or SKIP & set(p.parts)):
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        new = txt
        for pat, rep in RULES:
            new = re.sub(pat, rep, new)
        if new != txt:
            print(f"{'would update' if dry else 'updated'} {p.relative_to(root)}")
            if not dry:
                p.write_text(new, encoding="utf-8")
        for n, line in enumerate(new.splitlines(), 1):
            if re.search(r"\bMIT\b", line):
                left.append(f"{p.relative_to(root)}:{n}: {line.strip()[:100]}")
    print("\nStill mentions MIT (review by hand):" if left else "\nNo MIT mentions left.")
    for l in left:
        print("  " + l)


if __name__ == "__main__":
    main()
