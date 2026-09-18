#!/usr/bin/env bash
# selftest-lane-status-integrity.sh — prove the receipt-integrity and kill-concurrence gates
# DISCRIMINATE. A check that fires on everything has not discriminated; a check that fires on nothing
# is decoration.
#
# SCHEMA (9 cols): candidate rung score verdict author receipt blocked_on kill_concurrence receipt_digest
#
#   ARM 1  pinned + untouched                -> drifted=0  exit 0   (GREEN)
#   ARM 2  pinned + TRAILING NEWLINE added   -> drifted=0  exit 0   (the point of ruling (c))
#   ARM 3  pinned + one non-terminal byte    -> drifted=1  exit 4   (RED, integrity)
#   ARM 4  receipt deleted                   -> missing=1  exit 3   (RED, existence)
#   ARM 5  no pinned digest                  -> existence-only, exit 0
#   ARM 6  RULED_OUT + empty concurrence     -> exit 3              (RED, authorship boundary)
#   ARM 7  RULED_OUT + concurrence recorded  -> exit 0              (GREEN)
#
# ARM 2 and ARM 3 differ by WHERE the byte changed, not how many. That is the whole claim of (c).
#
# FALSE-GREEN GUARD, added after this file caught itself: arms 1-3 ALSO assert integrity_checked=1.
# The first version of this selftest emitted an 8-column fixture against a 9-column schema, so the
# digest landed in the concurrence column, nothing was ever integrity-checked, and arms 1-2 passed
# with drifted=0 because no comparison happened at all. A witness that passes by construction is
# worse than no witness: it certifies the gate it never exercised.
set -uo pipefail
REPO="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
LS="$REPO/scripts/lane-status.sh"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
fail=0

mk() { # $1=receipt body [$2=verdict] [$3=kill_concurrence]  -> receipt + 9-col fixture w/ pinned digest
  printf '%s' "$1" > "$TMP/receipt.json"
  d=$(perl -0777 -pe 's/\s+\z//' "$TMP/receipt.json" | shasum -a 256 | cut -c1-16)
  printf '#\tfixture\n' > "$TMP/status.tsv"
  printf 'FIX-1\t2\t900\t%s\tCOD\t%s\t-\t%s\t%s\n' \
    "${2:-CLEARED}" "$TMP/receipt.json" "${3:-}" "$d" >> "$TMP/status.tsv"
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
    printf 'PASS  %-46s rc=%s drifted=%s missing=%s integrity_checked=%s\n' "$1" "$rc" "$dr" "$ms" "$ic"
  else
    printf 'FAIL  %-46s rc=%s(want %s) drifted=%s(want %s) missing=%s(want %s) integrity_checked=%s(want %s)\n' \
      "$1" "$rc" "$2" "${dr:-none}" "$3" "${ms:-none}" "$4" "${ic:-none}" "${5:-any}"; fail=$((fail+1))
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

mk '{"a":1}'; perl -i -pe 's/\t[0-9a-f]{16}$/\t/' "$TMP/status.tsv"
out=$(run); rc=$?
if printf '%s' "$out" | grep -q 'NOT integrity-checked (no pinned digest): 1' && [ "$rc" = 0 ]; then
  printf 'PASS  %-46s rc=0 counted as existence-only\n' 'ARM 5 no pinned digest'
else
  printf 'FAIL  %-46s rc=%s — unpinned row not reported as existence-only\n' 'ARM 5 no pinned digest' "$rc"
  fail=$((fail+1))
fi

# ARM 6 — concurrence missing ALONE. Was rc=3; now rc=5, because pane 2's non-author audit found that
# "lane rc3 conflates missing receipt and missing concurrence (output distinguishes, exit does not;
# missing branch MASKS concurrence if both)". Each class now has its own code.
mk '{"a":1}' RULED_OUT ''
out=$(run); rc=$?
if [ "$rc" = 5 ] && printf '%s' "$out" | grep -q 'NO kill_concurrence'; then
  printf 'PASS  %-46s rc=5 authorship boundary unrecorded\n' 'ARM 6 RULED_OUT, empty concurrence'
else
  printf 'FAIL  %-46s rc=%s (want 5)\n' 'ARM 6 RULED_OUT, empty concurrence' "$rc"; fail=$((fail+1))
fi

mk '{"a":1}' RULED_OUT 'author-self'
check 'ARM 7 RULED_OUT, concurrence recorded' 0 0 0 1

# ARM 8 — BOTH classes at once. This is the arm pane 2's finding demanded: under the old elif chain
# the missing-receipt branch fired and the verdict line said NOTHING about concurrence, so a caller
# reading the exit code could not tell one failure from two.
mk '{"a":1}' RULED_OUT ''; rm -f "$TMP/receipt.json"
out=$(run); rc=$?
if [ "$rc" = 6 ] && printf '%s' "$out" | grep -q 'RECEIPT MISSING' && printf '%s' "$out" | grep -q 'NO kill_concurrence'; then
  printf 'PASS  %-46s rc=6 both classes reported, neither masked\n' 'ARM 8 missing receipt AND concurrence'
else
  printf 'FAIL  %-46s rc=%s (want 6) — one class masked the other\n' 'ARM 8 missing receipt AND concurrence' "$rc"
  fail=$((fail+1))
fi

# ARM 9 — SHORT ROW (6 columns). REVISED: previously asserted rc=5 and PASSED FOR THE WRONG REASON.
# Pane 2, a915e11: "ARM9 returns rc5 because empty concurrence fires, NOT because schema width is
# validated; parser has no field-count check." The parser now checks width, so a short row must fail
# as SCHEMA (8), not as a downstream symptom that happens to fire.
printf '#\tfixture\n' > "$TMP/status.tsv"
printf '%s' '{"a":1}' > "$TMP/receipt.json"
printf 'FIX-1\t2\t900\tRULED_OUT\tCOD\t%s\n' "$TMP/receipt.json" >> "$TMP/status.tsv"
out=$(run); rc=$?
if [ "$rc" = 8 ] && printf '%s' "$out" | grep -q 'SCHEMA: 6 cols, want 9'; then
  printf 'PASS  %-46s rc=8 width validated, not inferred\n' 'ARM 9 short row (6 cols)'
else
  printf 'FAIL  %-46s rc=%s (want 8) — width not validated\n' 'ARM 9 short row (6 cols)' "$rc"
  fail=$((fail+1))
fi

# ARM 10 — EXTRA COLUMN. REVISED, and this is the arm that was actively DANGEROUS. It used to assert
# rc=4 (drift), pinning the behaviour that `read` folds trailing fields into the last variable and
# corrupts the digest. Pane 2 ruled that UNSAFE for Q19: "receipt_type column10 would break EVERY ROW
# until parser migrates to exact 10-column validation." A 10th column must now be a SCHEMA error, so
# the operator is told to fix the width instead of being shown 17 false drift reports.
mk '{"a":1}'; perl -i -pe 's/$/\tEXTRA/ if !/^#/' "$TMP/status.tsv"
out=$(run); rc=$?
if [ "$rc" = 8 ] && printf '%s' "$out" | grep -q 'SCHEMA: 10 cols, want 9'; then
  printf 'PASS  %-46s rc=8 schema takes precedence over false drift\n' 'ARM 10 extra column (10 cols)'
else
  printf 'FAIL  %-46s rc=%s (want 8) — extra column read as drift\n' 'ARM 10 extra column (10 cols)' "$rc"
  fail=$((fail+1))
fi

# ARM 11 — THE MIGRATION ITSELF. A 10-column file with JEV_EXPECTED_COLS=10 must come back GREEN.
# This is the proof pane 2's blocker demanded: bumping one constant is the whole migration, so
# receipt_type can land as column 10 without a parser rewrite.
mk '{"a":1}'
perl -i -pe 's/$/\tscore/ if !/^#/' "$TMP/status.tsv"
d=$(perl -0777 -pe 's/\s+\z//' "$TMP/receipt.json" | shasum -a 256 | cut -c1-16)
perl -i -pe "s/\t[0-9a-f]{16}\tscore\$/\t$d\tscore/ if !/^#/" "$TMP/status.tsv"
out=$(JEV_EXPECTED_COLS=10 JEV_STATUS="$TMP/status.tsv" "$LS" 2>/dev/null); rc=$?
if [ "$rc" = 0 ] && printf '%s' "$out" | grep -q 'expected_cols: 10'; then
  printf 'PASS  %-46s rc=0 one constant IS the migration\n' 'ARM 11 10-col file, EXPECTED_COLS=10'
else
  printf 'FAIL  %-46s rc=%s (want 0) — migration needs more than the constant\n' 'ARM 11 10-col file, EXPECTED_COLS=10' "$rc"
  fail=$((fail+1))
fi

# ARM 12 — rc=7, the multi-class code pane 2 flagged as "reachable in principle, not selftested".
# Drift AND missing concurrence, with no missing receipt and correct width.
mk '{"a":1}' RULED_OUT ''
printf '{"a":2}' > "$TMP/receipt.json"
out=$(run); rc=$?
if [ "$rc" = 7 ]; then
  printf 'PASS  %-46s rc=7 multi-class code is reachable and tested\n' 'ARM 12 drift AND concurrence'
else
  printf 'FAIL  %-46s rc=%s (want 7) — rc7 still unexercised\n' 'ARM 12 drift AND concurrence' "$rc"
  fail=$((fail+1))
fi

printf '\n%s\n' '----------------------------------------------------------------------'
[ "$fail" = 0 ] && { printf 'OK: both gates discriminate on all 12 arms.\n'; exit 0; }
printf 'FAIL: %d arm(s) did not discriminate.\n' "$fail"; exit 1
