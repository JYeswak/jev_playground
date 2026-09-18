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

# ARM 9 — SHORT ROW (6 columns, schema violation). Pane 2: "no malformed/short/extra STATUS schema
# arms". Pinning the behaviour rather than asserting it is safe: a short RULED_OUT row has no
# concurrence field, so it must fail closed on that, not pass quietly.
printf '#\tfixture\n' > "$TMP/status.tsv"
printf '%s' '{"a":1}' > "$TMP/receipt.json"
printf 'FIX-1\t2\t900\tRULED_OUT\tCOD\t%s\n' "$TMP/receipt.json" >> "$TMP/status.tsv"
out=$(run); rc=$?
if [ "$rc" = 5 ]; then
  printf 'PASS  %-46s rc=5 short row fails closed on concurrence\n' 'ARM 9 short row (6 cols)'
else
  printf 'FAIL  %-46s rc=%s (want 5) — schema violation passed\n' 'ARM 9 short row (6 cols)' "$rc"
  fail=$((fail+1))
fi

# ARM 10 — EXTRA COLUMN. `read` assigns every trailing field to the last variable, so an extra column
# corrupts the digest rather than being ignored. That must surface as LOUD drift, never as a pass.
mk '{"a":1}'; perl -i -pe 's/$/\tEXTRA/ if !/^#/' "$TMP/status.tsv"
out=$(run); rc=$?
if [ "$rc" = 4 ]; then
  printf 'PASS  %-46s rc=4 extra column surfaces as drift, not a pass\n' 'ARM 10 extra column (10 cols)'
else
  printf 'FAIL  %-46s rc=%s (want 4) — extra column silently tolerated\n' 'ARM 10 extra column (10 cols)' "$rc"
  fail=$((fail+1))
fi

printf '\n%s\n' '----------------------------------------------------------------------'
[ "$fail" = 0 ] && { printf 'OK: both gates discriminate on all 10 arms.\n'; exit 0; }
printf 'FAIL: %d arm(s) did not discriminate.\n' "$fail"; exit 1
