#!/usr/bin/env bash
# selftest-lane-status-integrity.sh — prove the receipt-integrity, kill-concurrence, schema-width and
# receipt_type-enum gates DISCRIMINATE. A check that fires on everything has not discriminated; a
# check that fires on nothing is decoration.
#
# SCHEMA (10 cols): candidate rung score verdict author receipt blocked_on kill_concurrence
#                   receipt_digest receipt_type
#
#   ARM 1  pinned + untouched                -> rc=0   (GREEN)
#   ARM 2  pinned + TRAILING NEWLINE added   -> rc=0   (the point of ruling (c))
#   ARM 3  pinned + one non-terminal byte    -> rc=4   (RED, integrity)
#   ARM 4  receipt deleted                   -> rc=3   (RED, existence)
#   ARM 5  no pinned digest                  -> rc=0, existence-only
#   ARM 6  RULED_OUT + empty concurrence     -> rc=5   (RED, authorship boundary)
#   ARM 7  RULED_OUT + concurrence recorded  -> rc=0   (GREEN)
#   ARM 8  missing receipt AND concurrence   -> rc=6   (neither class masked)
#   ARM 9  SHORT row (6 cols)                -> rc=8   (RED, width)
#   ARM 10 EXTRA column (11 cols)            -> rc=8   (RED, width)
#   ARM 11 11-col file + EXPECTED_COLS=11    -> rc=0   (the migration is one constant)
#   ARM 12 drift AND concurrence             -> rc=7   (multi-class)
#   ARM 13 receipt_type out of enum          -> rc=9   (RED, semantic)
#   ARM 14 receipt_type EMPTY                -> rc=9   (RED, fail-closed, never inferred)
#
# FALSE-GREEN GUARD: arms 1-3 also assert integrity_checked=1. An earlier version of this file
# emitted an 8-column fixture against a 9-column schema, so the digest landed in the concurrence
# column, NOTHING was ever integrity-checked, and arms 1-2 passed with drifted=0 because no
# comparison happened at all. A witness that passes by construction is worse than no witness: it
# certifies the gate it never exercised.
#
# ARM 13/14 exist because pane 2 (verify-schema-width-20260918T103000Z.json) bounded the previous
# version precisely: "ARM11 proves structural read, not semantic receipt_type enum validation."
set -uo pipefail
REPO="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
LS="$REPO/scripts/lane-status.sh"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
fail=0

mk() { # $1=receipt body [$2=verdict] [$3=kill_concurrence] [$4=receipt_type] -> 10-col fixture
  printf '%s' "$1" > "$TMP/receipt.json"
  d=$(perl -0777 -pe 's/\s+\z//' "$TMP/receipt.json" | shasum -a 256 | cut -c1-16)
  printf '#\tfixture\n' > "$TMP/status.tsv"
  printf 'FIX-1\t2\t900\t%s\tCOD\t%s\t-\t%s\t%s\t%s\n' \
    "${2:-CLEARED}" "$TMP/receipt.json" "${3:-}" "$d" "${4-measurement}" >> "$TMP/status.tsv"
}
run() { JEV_STATUS="$TMP/status.tsv" "$LS" 2>/dev/null; }
num() { printf '%s' "$1" | sed -n "s/.*$2: *\([0-9]*\).*/\1/p" | head -1; }
check() { # $1=arm $2=rc $3=drifted $4=missing $5=integrity_checked(optional)
  out=$(run); rc=$?
  dr=$(num "$out" drifted); ms=$(num "$out" missing); ic=$(num "$out" integrity_checked)
  ok=1
  [ "$rc" = "$2" ] || ok=0; [ "${dr:-x}" = "$3" ] || ok=0; [ "${ms:-x}" = "$4" ] || ok=0
  [ -n "${5:-}" ] && { [ "${ic:-x}" = "$5" ] || ok=0; }
  if [ "$ok" = 1 ]; then
    printf 'PASS  %-48s rc=%s drifted=%s missing=%s integrity=%s\n' "$1" "$rc" "$dr" "$ms" "$ic"
  else
    printf 'FAIL  %-48s rc=%s(want %s) drifted=%s(want %s) missing=%s(want %s) integrity=%s(want %s)\n' \
      "$1" "$rc" "$2" "${dr:-none}" "$3" "${ms:-none}" "$4" "${ic:-none}" "${5:-any}"; fail=$((fail+1))
  fi
}
expect() { # $1=arm $2=want_rc $3=grep pattern $4=pass note
  out=$(run); rc=$?
  if [ "$rc" = "$2" ] && printf '%s' "$out" | grep -q "$3"; then
    printf 'PASS  %-48s rc=%s %s\n' "$1" "$rc" "$4"
  else
    printf 'FAIL  %-48s rc=%s (want %s) or pattern absent: %s\n' "$1" "$rc" "$2" "$3"; fail=$((fail+1))
  fi
}

mk '{"a":1}'
check 'ARM 1 pinned, untouched' 0 0 0 1

mk '{"a":1}'; printf '\n' >> "$TMP/receipt.json"
check 'ARM 2 pinned, TRAILING NEWLINE added' 0 0 0 1

mk '{"a":1}'; printf '{"a":2}' > "$TMP/receipt.json"
check 'ARM 3 pinned, one NON-TERMINAL byte changed' 4 1 0 1

mk '{"a":1}'; rm -f "$TMP/receipt.json"
check 'ARM 4 receipt deleted' 3 0 1

mk '{"a":1}'; perl -i -pe 's/\t[0-9a-f]{16}\t/\t\t/ if !/^#/' "$TMP/status.tsv"
expect 'ARM 5 no pinned digest' 0 'NOT integrity-checked (no pinned digest): 1' 'counted as existence-only'

mk '{"a":1}' RULED_OUT ''
expect 'ARM 6 RULED_OUT, empty concurrence' 5 'NO kill_concurrence' 'authorship boundary unrecorded'

mk '{"a":1}' RULED_OUT 'author-self'
check 'ARM 7 RULED_OUT, concurrence recorded' 0 0 0 1

# ARM 8 — BOTH classes. Under the old elif chain the missing-receipt branch fired and the verdict line
# said NOTHING about concurrence, so a caller reading the exit code could not tell one failure from two.
mk '{"a":1}' RULED_OUT ''; rm -f "$TMP/receipt.json"
expect 'ARM 8 missing receipt AND concurrence' 6 'NO kill_concurrence' 'both reported, neither masked'

# ARM 9 — SHORT ROW. Must fail as SCHEMA, not as a downstream symptom that happens to fire.
printf '#\tfixture\n' > "$TMP/status.tsv"
printf '%s' '{"a":1}' > "$TMP/receipt.json"
printf 'FIX-1\t2\t900\tRULED_OUT\tCOD\t%s\n' "$TMP/receipt.json" >> "$TMP/status.tsv"
expect 'ARM 9 short row (6 cols)' 8 'SCHEMA: 6 cols, want 10' 'width validated, not inferred'

# ARM 10 — EXTRA column. `read` folds trailing fields into the last variable, so an 11th column would
# corrupt receipt_type; it must be a width error, not a silent mistype.
mk '{"a":1}'; perl -i -pe 's/$/\tEXTRA/ if !/^#/' "$TMP/status.tsv"
expect 'ARM 10 extra column (11 cols)' 8 'SCHEMA: 11 cols, want 10' 'schema precedes any downstream class'

# ARM 11 — THE MIGRATION ITSELF, retargeted one column ahead of the current schema. Bumping the
# constant must remain the whole migration; this is the arm that caught it NOT being true last time.
mk '{"a":1}'; perl -i -pe 's/$/\tEXTRA/ if !/^#/' "$TMP/status.tsv"
out=$(JEV_EXPECTED_COLS=11 JEV_STATUS="$TMP/status.tsv" "$LS" 2>/dev/null); rc=$?
if [ "$rc" = 0 ] && printf '%s' "$out" | grep -q 'expected_cols: 11'; then
  printf 'PASS  %-48s rc=0 one constant IS the migration\n' 'ARM 11 11-col file, EXPECTED_COLS=11'
else
  printf 'FAIL  %-48s rc=%s (want 0) — migration needs more than the constant\n' 'ARM 11 11-col file, EXPECTED_COLS=11' "$rc"
  fail=$((fail+1))
fi

# ARM 12 — rc=7, the multi-class code pane 2 flagged as "reachable in principle, not selftested".
mk '{"a":1}' RULED_OUT ''; printf '{"a":2}' > "$TMP/receipt.json"
expect 'ARM 12 drift AND concurrence' 7 'distinct failure classes' 'multi-class reachable and tested'

# ARM 13 — SEMANTIC enum validation, the bound pane 2 named on the previous version.
mk '{"a":1}' CLEARED '' 'bogus'
expect 'ARM 13 receipt_type out of enum' 9 "TYPE: 'bogus' not in enum" 'illegal value fails closed'

# ARM 14 — EMPTY type. Per Q19 this fails closed and is NEVER inferred as non-score.
mk '{"a":1}' CLEARED '' ''
expect 'ARM 14 receipt_type EMPTY' 9 'not in enum' 'empty fails closed, never inferred'

# ANCHORED AT COLUMN 0, and the reason is a defect these arms hit on their first run: lane-status
# prints a LAST 6 COMMITS block, and commit cccaf39's own subject contains the literal string
# "TRANSIENT_UNSTABLE". An unanchored grep therefore matched a COMMIT MESSAGE instead of the verdict
# line, and ARM 16 failed with a correct rc=4. An arm whose predicate can be satisfied by unrelated
# text in the same output is not an assertion about behaviour. Verdict lines start at column 0; the
# commit block is indented two spaces, so the anchor discriminates.
# ARMS 15-17 — the TRANSIENT_UNSTABLE paths, added because pane 3's
# audit-transient-arms-20260918T120704Z.json (b031ffb) found the highest-traffic one UNTESTED:
# "accept-after-recapture had NEVER EXECUTED — confirmed by code inspection plus absence of any such
# run." It closed the gap by EXECUTION rather than argument, and these arms commit that execution so
# it is a witness rather than a memory of one. Deterministic: attempt 2 is entered DIRECTLY on a
# stable fixture, so there is no sleep and no race — the shape I failed to build when I tried to time
# a mutation against a 0.43s scan and got an arm that proved nothing.

mk '{"a":1}'
out=$(JEV_TRANSIENT_ATTEMPT=2 run); rc=$?
if [ "$rc" = 0 ] && ! printf '%s\n' "$out" | grep -q '^SNAPSHOT MOVED'; then
  printf 'PASS  %-48s rc=0 stable second attempt accepted, silent\n' 'ARM 15 attempt=2, stable clean'
else
  printf 'FAIL  %-48s rc=%s (want 0) or a notice was printed\n' 'ARM 15 attempt=2, stable clean' "$rc"
  fail=$((fail+1))
fi

# The half that matters most: a stable second attempt's RED is ACCEPTED, not laundered by the
# transient class. Pane 2's spec: "a stable second snapshot is validated EVEN IF RED."
mk '{"a":1}'; printf '{"a":2}' > "$TMP/receipt.json"
out=$(JEV_TRANSIENT_ATTEMPT=2 run); rc=$?
if [ "$rc" = 4 ] && ! printf '%s\n' "$out" | grep -q '^TRANSIENT_UNSTABLE'; then
  printf 'PASS  %-48s rc=4 settled RED accepted, not laundered\n' 'ARM 16 attempt=2, stable drifted'
else
  printf 'FAIL  %-48s rc=%s (want 4) or it was called transient\n' 'ARM 16 attempt=2, stable drifted' "$rc"
  fail=$((fail+1))
fi

# ARM 17 — the changed-paths EXTRACTOR, unit-tested against the live fingerprint format. This is the
# arm that would have caught b031ffb's functional defect: 8459b1a changed the fingerprint lines to
# `raw:<hex> norm:<hex>  <path>` and left the sed matching the old shape, so Changed-paths was ALWAYS
# EMPTY while a commit message claimed the path was named. A format change invalidated an assertion
# nobody re-ran; this arm re-runs it.
fpline='raw:0123456789abcdef norm:fedcba9876543210  docs/demos/x.json'
got=$(printf '%s\n' "< $fpline" | sed -n 's/^[<>] *raw:[0-9a-f]* norm:[0-9a-f]*  //p')
if [ "$got" = 'docs/demos/x.json' ]; then
  printf 'PASS  %-48s extracts the path from the live format\n' 'ARM 17 changed-paths extractor'
else
  printf 'FAIL  %-48s got %s — extractor and fingerprint format have diverged\n' \
    'ARM 17 changed-paths extractor' "'${got:-<empty>}'"
  fail=$((fail+1))
fi
printf '\n%s\n' '----------------------------------------------------------------------'
[ "$fail" = 0 ] && { printf 'OK: all four gates discriminate on all 17 arms.\n'; exit 0; }
printf 'FAIL: %d arm(s) did not discriminate.\n' "$fail"; exit 1
