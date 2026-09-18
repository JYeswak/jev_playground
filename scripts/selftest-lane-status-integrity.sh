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

mk '{"a":1}' RULED_OUT ''
out=$(run); rc=$?
if [ "$rc" = 3 ] && printf '%s' "$out" | grep -q 'NO kill_concurrence'; then
  printf 'PASS  %-46s rc=3 authorship boundary unrecorded\n' 'ARM 6 RULED_OUT, empty concurrence'
else
  printf 'FAIL  %-46s rc=%s (want 3)\n' 'ARM 6 RULED_OUT, empty concurrence' "$rc"; fail=$((fail+1))
fi

mk '{"a":1}' RULED_OUT 'author-self'
check 'ARM 7 RULED_OUT, concurrence recorded' 0 0 0 1

printf '\n%s\n' '----------------------------------------------------------------------'
[ "$fail" = 0 ] && { printf 'OK: both gates discriminate on all 7 arms.\n'; exit 0; }
printf 'FAIL: %d arm(s) did not discriminate.\n' "$fail"; exit 1
