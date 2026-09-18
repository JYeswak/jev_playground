#!/usr/bin/env bash
# selftest-score-lineage.sh — prove the score-lineage watcher DISCRIMINATES.
#
# The condition it enforces was graded CONDITION_PROSE_SHAPED by pane 3 and called "the weakest of
# the three even after amendment — stated as such, not smoothed". The real history is clean (7 score
# changes, 0 upward, 0 trips), so a watcher that simply reported OK would be indistinguishable from
# a watcher that checks nothing. These arms supply the known-bad the history cannot.
#
#   ARM A  score UP    + verdict change + NO score receipt   -> TRIP,    rc=5   (the known-bad)
#   ARM B  score down  + verdict change + NO score receipt   -> TRIP,    rc=5   (direction-agnostic)
#   ARM C  score down  + verdict change + score receipt      -> no trip, rc=0   (the real history's shape)
#   ARM D  score change, NO verdict change                   -> no trip, rc=0
#   ARM E  verdict change, NO score change                   -> no trip, rc=0
#   ARM F  RECUSED->CLEARED + score change, no receipt       -> TRIP,    rc=5   (the amendment itself)
#
# ARM F is the one that justifies the amendment: under pane 3's original HELD-exit-only definition
# this case is invisible, and it is the case its own hand-audit had to include manually.
set -uo pipefail
REPO="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
AUD="$REPO/scripts/audit-score-lineage.sh"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
fail=0

row() { printf 'CAND-%s\t2\t%s\t%s\tCOD\t%s\t-\t\tdeadbeefdeadbeef\n' "$1" "$2" "$3" "$4"; }

arm() { # $1=label $2=want_rc $3=want_trips  (before/after already written)
  out=$("$AUD" --pair "$TMP/b.tsv" "$TMP/a.tsv" 2>&1); rc=$?
  tr_n=$(printf '%s' "$out" | sed -n 's/.*trips: *\([0-9]*\).*/\1/p' | head -1)
  if [ "$rc" = "$2" ] && [ "${tr_n:-x}" = "$3" ]; then
    printf 'PASS  %-56s rc=%s trips=%s\n' "$1" "$rc" "$tr_n"
  else
    printf 'FAIL  %-56s rc=%s(want %s) trips=%s(want %s)\n' "$1" "$rc" "$2" "${tr_n:-none}" "$3"
    fail=$((fail+1))
  fi
}

# ARM A — upward score alongside a verdict change, no score receipt cited
{ row 1 700 HELD    docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/b.tsv"
{ row 1 900 CLEARED docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/a.tsv"
arm 'ARM A score UP + verdict change + no score receipt' 5 1

# ARM B — same shape, downward. The rule is about the coincidence, not the direction.
{ row 1 900 HELD    docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/b.tsv"
{ row 1 700 CLEARED docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/a.tsv"
arm 'ARM B score down + verdict change + no score receipt' 5 1

# ARM C — the real history's shape: a distinct score receipt is cited
{ row 1 900 HELD    docs/demos/duel-2/HUNT_SCORES_COD_ON_MU.md; } > "$TMP/b.tsv"
{ row 1 820 CLEARED docs/demos/duel-2/HUNT_SCORES_COD_ON_MU.md; } > "$TMP/a.tsv"
arm 'ARM C score down + verdict change + score receipt cited' 0 0

# ARM D — score moves alone
{ row 1 900 HELD docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/b.tsv"
{ row 1 820 HELD docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/a.tsv"
arm 'ARM D score change, no verdict change' 0 0

# ARM E — verdict moves alone
{ row 1 900 HELD    docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/b.tsv"
{ row 1 900 CLEARED docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/a.tsv"
arm 'ARM E verdict change, no score change' 0 0

# ARM F — the amendment: a non-HELD verdict transition. Invisible to the original definition.
{ row 1 700 RECUSED docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/b.tsv"
{ row 1 550 CLEARED docs/demos/duel-2/HELD_thing_COD.md; } > "$TMP/a.tsv"
arm 'ARM F RECUSED->CLEARED + score change (amendment)' 5 1

# ARM G — the escape hatch that used to exist. The first version read
#   `SCORE_RECEIPT.search(msg) or <changed-row receipts>`
# so a commit message containing "RUNG2_" satisfied the gate — written by the conductor, who is the
# party the gate constrains. This arm proves the ROW-receipt branch is now the ONLY branch: a legal
# shape whose changed-row receipt is NOT a scoring artifact must TRIP.
{ row 1 900 HELD    docs/demos/duel-2/RULING_notes_COD.md; } > "$TMP/b.tsv"
{ row 1 820 CLEARED docs/demos/duel-2/RULING_notes_COD.md; } > "$TMP/a.tsv"
arm 'ARM G changed-row receipt is NOT a score receipt' 5 1

printf '\n%s\n' '----------------------------------------------------------------------'
[ "$fail" = 0 ] && { printf 'OK: score-lineage watcher discriminates on all 7 arms.\n'; exit 0; }
printf 'FAIL: %d arm(s) did not discriminate.\n' "$fail"; exit 1
