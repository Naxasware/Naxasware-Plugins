#!/usr/bin/env bash
# CI smoke test for the ai-system-architect plugin.
# Run from anywhere; resolves paths relative to this file.
# Exits non-zero on the first failure (set -e), which CI treats as a failed check.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$HERE/skills/ai-system-architect/scripts"
EXAMPLES="$HERE/examples"

echo "== validate_architecture.py against sample-architecture.json =="
python3 "$SCRIPTS/validate_architecture.py" "$EXAMPLES/sample-architecture.json"

echo
echo "== validate_diagrams.py against sample-architecture.json + sample-diagram.mmd =="
python3 "$SCRIPTS/validate_diagrams.py" "$EXAMPLES/sample-architecture.json" "$EXAMPLES/sample-diagram.mmd"

echo
echo "== generate_report.py against sample-architecture.json =="
python3 "$SCRIPTS/generate_report.py" "$EXAMPLES/sample-architecture.json" > /dev/null

echo
echo
echo "== chain example: validate against its upstream requirements (strict) =="
CH="$EXAMPLES/chain-example"
python3 "$SCRIPTS/validate_architecture.py" "$CH/02-architecture.json" --upstream "$CH/01-requirements.md" --strict
python3 "$SCRIPTS/validate_diagrams.py" "$CH/02-architecture.json" "$CH/02-diagram.mmd"

echo
echo "== chain example: rendered report is current, chain-ready and complete =="
TMP_R="$(mktemp -d)"
python3 "$SCRIPTS/generate_report.py" "$CH/02-architecture.json" -o "$TMP_R/02-architecture.md"
cmp "$TMP_R/02-architecture.md" "$CH/02-architecture.md" || { echo "FAIL: 02-architecture.md is stale; regenerate it"; exit 1; }
grep -q '^### INT-\|^| INT-001 |' "$TMP_R/02-architecture.md" || { echo "FAIL: INT ids not rendered as written"; exit 1; }
grep -q '^## Handoff to next stage' "$TMP_R/02-architecture.md" || { echo "FAIL: handoff block missing"; exit 1; }
cp "$CH/01-requirements.md" "$TMP_R/"
python3 "$SCRIPTS/validate_ids.py" "$TMP_R/02-architecture.md" >/dev/null
python3 "$SCRIPTS/validate_chain.py" "$TMP_R/01-requirements.md" "$TMP_R/02-architecture.md" --strict

echo
echo "== regression: invented or uncovered requirements must fail =="
python3 - "$CH/02-architecture.json" "$TMP_R" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
a = json.loads(json.dumps(d)); a["traceability"].append({"requirement": "FR-099", "driver": "AD-001", "decision": "ADR-002", "component": "COMP-008"})
b = json.loads(json.dumps(d))
b["upstream_coverage"] = [c for c in b["upstream_coverage"] if c["upstream"] != "FR-004"]
b["traceability"] = [t for t in b["traceability"] if t["requirement"] != "FR-004"]
b["architecture_drivers"][1]["requirement_ids"] = ["BR-003", "FR-007"]
json.dump(a, open(sys.argv[2] + "/invented.json", "w")); json.dump(b, open(sys.argv[2] + "/uncovered.json", "w"))
PY
for f in invented uncovered; do
  if python3 "$SCRIPTS/validate_architecture.py" "$TMP_R/$f.json" --upstream "$CH/01-requirements.md" >/dev/null; then
    echo "FAIL: $f architecture was accepted"; exit 1; fi
done
rm -rf "$TMP_R"

echo
echo "== chain scripts identical across plugins (drift check) =="
python3 - "$SCRIPTS" "$HERE" <<'PY'
import hashlib, sys
from pathlib import Path
mine_dir, here = Path(sys.argv[1]), Path(sys.argv[2])
bad = []
for name in ("idscan.py", "validate_chain.py"):
    mine = hashlib.sha256((mine_dir / name).read_bytes()).hexdigest()
    for sib in sorted(here.parent.glob(f"ai-*/skills/ai-*/scripts/{name}")):
        if hashlib.sha256(sib.read_bytes()).hexdigest() != mine:
            bad.append(f"{name} differs from {sib}")
if bad:
    print("FAIL: " + "; ".join(bad)); sys.exit(1)
print("chain scripts identical")
PY

echo "== package_skill.py dry run (packages to a temp dir) =="
TMP_OUT="$(mktemp -d)"
python3 "$HERE/tools/package_skill.py" "$HERE/skills/ai-system-architect" "$TMP_OUT"
test -f "$TMP_OUT/ai-system-architect.skill"
rm -rf "$TMP_OUT"

echo
echo "== build_context_bundle.py dry run =="
TMP_MD="$(mktemp -d)/bundle.md"
python3 "$HERE/tools/build_context_bundle.py" -o "$TMP_MD"
test -s "$TMP_MD"
rm -f "$TMP_MD"

echo
echo "ai-system-architect: all smoke checks passed."
