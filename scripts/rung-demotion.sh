#!/usr/bin/env bash
# rung-demotion — report STATUS rows whose cited inputs rotted underneath them.
#
# CREATION GATE, answered:
#   1. CONSUMER — the rung ladder itself, and scripts/selftest-rung-demotion.sh
#      (stage 80 discovers it by glob — no new stage). A claim whose cited input
#      is live-monotonic and whose as_of predates its last use demotes one rung.
#   2. GATE — for each STATUS row, if its receipt cites a known-live artifact
#      (list below, measured-live tonight) with no as-of line, the row is
#      listed and the script exits 3. This is a REPORTER, not an auto-editor:
#      rewriting the state of record by script is the parallel-file danger
#      project.mjs already refuses. A human demotes; this names whom.
#   3. DEFECT — OBSERVED: the as-of audit proved 78,455 unrecoverable and
#      nothing demoted the claim citing it. Live counts measured 0/40 rows
#      firing today — a tripwire, not an alarm: it fires on future rows that
#      cite live inputs without as-of labels.
#   4. RETIREMENT — when receipts carry machine-readable input manifests
#      (closure inputs[] with as_of); then this grep-shape check is dead weight
#      and the closure verifier subsumes it.
#
# WHAT IT DELIBERATELY DOES NOT DO: it does not know every live source — only
# the two measured-live tonight (real-allowed.json 77,767→78,242;
# decisions_full.jsonl regenerated at new totals). A receipt citing a third
# live source it does not name passes silently; extend the list with evidence.
#
# Usage: scripts/rung-demotion.sh [STATUS_TSV]
#   exit 0 = no demotions · 3 = at least one row listed · 2 = usage/IO error.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
STATUS="${1:-docs/demos/STATUS.tsv}"
[ -f "$STATUS" ] || { echo "rung-demotion: no such STATUS file: $STATUS" >&2; exit 2; }

LIVE='real-allowed\.json|decisions_full\.jsonl'
flagged=0
checked=0
while IFS=$'\t' read -r cand _r _s _v _a receipt _b _c _d _r overflow; do
  [ -z "${cand:-}" ] && continue
  case "$cand" in \#*|candidate|Candidate) continue ;; esac
  [ -n "${receipt:-}" ] || continue
  [ -f "$receipt" ] || continue
  checked=$((checked + 1))
  if grep -qiE "$LIVE" "$receipt" 2>/dev/null && ! grep -qiE 'as[ -]of 2026-[0-9-]+' "$receipt" 2>/dev/null; then
    printf '  DEMOTE %s cites a live artifact with no as-of line: %s\n' "$cand" "$receipt"
    flagged=$((flagged + 1))
  fi
done < "$STATUS"

[ "$checked" -gt 0 ] || { echo "rung-demotion: no rows checked — an empty scan set is NOT a pass" >&2; exit 2; }
if [ "$flagged" -gt 0 ]; then
  echo "rung-demotion: $flagged of $checked row(s) would demote one rung"
  exit 3
fi
echo "rung-demotion: $checked row(s) checked, none cite live inputs without as-of"
exit 0
