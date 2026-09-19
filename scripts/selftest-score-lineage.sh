#!/usr/bin/env bash
# selftest-score-lineage.sh — prove the score-lineage watcher DISCRIMINATES on DECLARED TYPES.
#
# The condition it enforces was graded CONDITION_PROSE_SHAPED by pane 3 and called "the weakest of
# the three even after amendment — stated as such, not smoothed". The real history is clean of trips,
# so a watcher that simply reported OK would be indistinguishable from one that checks nothing. These
# arms supply the known-bad the history cannot.
#
# SCHEMA (10 cols): candidate rung score verdict author receipt blocked_on kill_concurrence
#                   receipt_digest receipt_type
#
# WHAT CHANGED, and why every arm below was rewritten: the gate used to infer "is this a score
# receipt" from the FILENAME. Measured against pane 3's opened-receipt typing of all 17 rows, that
# regex was right ONCE IN SIX — 5 false-GREEN, 0 false-RED, 1 correct. The gate now reads the DECLARED
# type (pane 2's Q19 ruling), so the arms must exercise TYPES, not filenames. An arm built on a
# filename would now be testing a retired mechanism.
#
#   ARM A  score UP    + verdict change + type != score   -> TRIP,    rc=5   (the known-bad)
#   ARM B  score down  + verdict change + type != score   -> TRIP,    rc=5   (direction-agnostic)
#   ARM C  score down  + verdict change + type == score   -> no trip, rc=0   (the legal shape)
#   ARM D  score change, NO verdict change                -> no trip, rc=0
#   ARM E  verdict change, NO score change                -> no trip, rc=0
#   ARM F  RECUSED->CLEARED + score change, type != score -> TRIP,    rc=5   (the amendment)
#   ARM G  type == hold-resolution                        -> TRIP,    rc=5   (the R17 class)
#   ARM H  PRE-MIGRATION 9-col row with a coincidence     -> UNTYPED, rc=6   (never clean)
#
# ARM F justifies pane 3's amendment: under its original HELD-exit-only definition that case is
# invisible, and it is the case its own hand-audit had to include manually.
# ARM G is the R17 defect made concrete: `HELD_demo2_demand_COD.md` matched the old regex via
# `demand_` and is a HOLD receipt. Declared typing catches what the filename could not.
# ARM H is the honest one: it pins that a pre-migration coincidence is UNJUDGED, not clean. The old
# "0 trips" over history came from the regex, and rc=6 is the retirement of that claim.
set -uo pipefail
REPO="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
AUD="$REPO/scripts/audit-score-lineage.sh"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
fail=0

# $1=id $2=score $3=verdict $4=receipt $5=receipt_type  (10 columns)
row() { printf 'CAND-%s\t2\t%s\t%s\tCOD\t%s\t-\t\tdeadbeefdeadbeef\t%s\n' "$1" "$2" "$3" "$4" "$5"; }
# 9 columns — pre-migration shape, no receipt_type at all
row9() { printf 'CAND-%s\t2\t%s\t%s\tCOD\t%s\t-\t\tdeadbeefdeadbeef\n' "$1" "$2" "$3" "$4"; }

arm() { # $1=label $2=want_rc $3=want_trips
  out=$("$AUD" --pair "$TMP/b.tsv" "$TMP/a.tsv" 2>&1); rc=$?
  tr_n=$(printf '%s' "$out" | sed -n 's/.*trips: *\([0-9]*\).*/\1/p' | head -1)
  if [ "$rc" = "$2" ] && [ "${tr_n:-x}" = "$3" ]; then
    printf 'PASS  %-54s rc=%s trips=%s\n' "$1" "$rc" "$tr_n"
  else
    printf 'FAIL  %-54s rc=%s(want %s) trips=%s(want %s)\n' "$1" "$rc" "$2" "${tr_n:-none}" "$3"
    fail=$((fail+1))
  fi
}

R=docs/demos/duel-2/HELD_thing_COD.md

# ARM A — upward score alongside a verdict change, changed row is not a score receipt
{ row 1 700 HELD    "$R" verdict; } > "$TMP/b.tsv"
{ row 1 900 CLEARED "$R" verdict; } > "$TMP/a.tsv"
arm 'ARM A score UP + verdict change + type=verdict' 5 1

# ARM B — same shape, downward. The rule is the coincidence, not the direction.
{ row 1 900 HELD    "$R" verdict; } > "$TMP/b.tsv"
{ row 1 700 CLEARED "$R" verdict; } > "$TMP/a.tsv"
arm 'ARM B score down + verdict change + type=verdict' 5 1

# ARM C — the legal shape: the changed row IS a declared score receipt
{ row 1 900 HELD    docs/demos/duel-2/DEMAND_SCORES_COD_ON_MU.md score; } > "$TMP/b.tsv"
{ row 1 820 CLEARED docs/demos/duel-2/DEMAND_SCORES_COD_ON_MU.md score; } > "$TMP/a.tsv"
arm 'ARM C score down + verdict change + type=score' 0 0

# ARM D — score moves alone
{ row 1 900 HELD "$R" verdict; } > "$TMP/b.tsv"
{ row 1 820 HELD "$R" verdict; } > "$TMP/a.tsv"
arm 'ARM D score change, no verdict change' 0 0

# ARM E — verdict moves alone
{ row 1 900 HELD    "$R" verdict; } > "$TMP/b.tsv"
{ row 1 900 CLEARED "$R" verdict; } > "$TMP/a.tsv"
arm 'ARM E verdict change, no score change' 0 0

# ARM F — the amendment: a non-HELD verdict transition, invisible to the original definition
{ row 1 700 RECUSED "$R" measurement; } > "$TMP/b.tsv"
{ row 1 550 CLEARED "$R" measurement; } > "$TMP/a.tsv"
arm 'ARM F RECUSED->CLEARED + score change (amendment)' 5 1

# ARM G — the R17 class: a HOLD receipt whose filename matched the retired regex via `demand_`
{ row 1 900 HELD    docs/demos/duel-2/HELD_demo2_demand_COD.md hold-resolution; } > "$TMP/b.tsv"
{ row 1 820 CLEARED docs/demos/duel-2/HELD_demo2_demand_COD.md hold-resolution; } > "$TMP/a.tsv"
arm 'ARM G type=hold-resolution (old regex said score)' 5 1

# ARM H — PRE-MIGRATION row. Must be UNTYPED at rc=6: not clean, not tripped, UNJUDGED.
{ row9 1 900 HELD    "$R"; } > "$TMP/b.tsv"
{ row9 1 820 CLEARED "$R"; } > "$TMP/a.tsv"
out=$("$AUD" --pair "$TMP/b.tsv" "$TMP/a.tsv" 2>&1); rc=$?
if [ "$rc" = 6 ] && printf '%s' "$out" | grep -q 'UNTYPED'; then
  printf 'PASS  %-54s rc=6 unjudged, not clean\n' 'ARM H pre-migration 9-col coincidence'
else
  printf 'FAIL  %-54s rc=%s (want 6) — untyped row was judged\n' 'ARM H pre-migration 9-col coincidence' "$rc"
  fail=$((fail+1))
fi

printf '\n%s\n' '----------------------------------------------------------------------'
[ "$fail" = 0 ] && { printf 'OK: score-lineage watcher discriminates on all 8 arms.\n'; exit 0; }
printf 'FAIL: %d arm(s) did not discriminate.\n' "$fail"; exit 1
