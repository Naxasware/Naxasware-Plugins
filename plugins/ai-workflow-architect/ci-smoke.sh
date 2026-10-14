#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/skills/ai-workflow-architect"
for f in "$S"/examples/*.md; do
  [ "$(basename "$f")" = "drift-review.md" ] && continue
  python3 "$S/scripts/validate_workflow.py" "$f" >/dev/null
  python3 "$S/scripts/validate_ids.py" "$f" >/dev/null
  python3 "$S/scripts/validate_diagrams.py" "$f" >/dev/null
done
python3 "$S/scripts/validate_evidence.py" "$S/examples/drift-review.md"

# --- chain example, strict -------------------------------------------------
CH="$HERE/examples/chain-example"
python3 "$S/scripts/validate_workflow.py" "$CH/03-workflow.md" --strict >/dev/null
python3 "$S/scripts/validate_ids.py" "$CH/03-workflow.md" >/dev/null
python3 "$S/scripts/validate_diagrams.py" "$CH/03-workflow.md" >/dev/null
python3 "$S/scripts/validate_chain.py" "$CH/01-requirements.md" "$CH/02-architecture.md" "$CH/03-workflow.md" --strict >/dev/null
python3 "$S/scripts/generate_report.py" "$CH/03-workflow.md" >/dev/null

# --- regressions: each broken copy must be rejected ------------------------
TMP="$(mktemp -d)"
cp "$CH"/*.md "$TMP/"
expect_fail() {  # name, python edit applied to 03-workflow.md, command that must fail
  local name="$1" edit="$2"; shift 2
  cp "$CH/03-workflow.md" "$TMP/03-workflow.md"
  python3 - "$TMP/03-workflow.md" "$edit" <<'PY'
import sys
p, edit = sys.argv[1], sys.argv[2]
t = open(p, encoding="utf-8").read()
old, new = edit.split("=>", 1)
assert old in t, "regression edit target not found: " + old
open(p, "w", encoding="utf-8").write(t.replace(old, new))
PY
  if "$@" >/dev/null 2>&1; then echo "FAIL: $name was accepted"; rm -rf "$TMP"; exit 1; fi
}
V="python3 $S/scripts/validate_workflow.py"
expect_fail "invented upstream id" "FR-009, NFR-004 |=>FR-099, NFR-004 |" $V "$TMP/03-workflow.md" --strict
expect_fail "human step without timeout" "\`NOT PROVIDED\` wait limit (Q-006); reminder then escalation=>N/A" $V "$TMP/03-workflow.md" --strict
expect_fail "unlabeled money figure" "Volume is \`UNKNOWN\` (Q-001), so=>Volume costs \$40,000 a year, so" $V "$TMP/03-workflow.md" --strict
expect_fail "leaked token" "## Open Questions=>ERP_TOKEN=ghp_$(printf 'a%.0s' $(seq 1 36))\n\n## Open Questions" $V "$TMP/03-workflow.md" --strict
expect_fail "dropped locked decision" "BR-001=>BR-00X" python3 "$S/scripts/validate_chain.py" "$TMP/01-requirements.md" "$TMP/02-architecture.md" "$TMP/03-workflow.md"
rm -rf "$TMP"

echo "ai-workflow-architect: smoke checks passed."
