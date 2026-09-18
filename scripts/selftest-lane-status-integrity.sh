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
# Transients are tallied SEPARATELY and still exit nonzero. Counting them as passes would let a peer
# commit launder an unverified arm into a green suite, which is the laundering the whole transient
# contract exists to prevent.
transient=0

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

# HEAD-BRACKETED, with one bounded retry — pane 3, 4221cc6: "my runs HEAD-bracketed; ARMS DO NOT — a
# concurrent lane commit mid-arm drives attempt-2 to rc=10 and FAILS THE ARM SPURIOUSLY. Windows are
# ~1s in a lane committing every few minutes: rare, real, and INDISTINGUISHABLE FROM A TRUE FAILURE
# without bracketing." The fingerprint binds git HEAD, so a peer commit during the arm is exactly the
# transient the thing under test exists to report — and an arm that cannot tell that apart from a
# defect is the false-RED class this lane calls worse than a missed trip.
#
# The retry is BOUNDED AT ONE, mirroring the contract under test. A second movement is reported as
# TRANSIENT and counted in its own tally: NOT a pass, NOT a fail. The suite exits nonzero on it, so a
# transient can never be read as a clean run.
bracketed_arm() { # $1=label $2=want_rc $3=forbidden_pattern $4=pass_note
  local attempt=1 h0 h1 out rc
  while :; do
    h0=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)
    out=$(JEV_TRANSIENT_ATTEMPT=2 run); rc=$?
    h1=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)
    [ "$h0" = "$h1" ] && break
    if [ "$attempt" -ge 2 ]; then
      printf 'TRANS %-48s HEAD moved during both attempts (%s -> %s); NOT a pass, NOT a fail\n' \
        "$1" "${h0:0:7}" "${h1:0:7}"
      transient=$((transient+1)); return
    fi
    attempt=2
  done
  if [ "$rc" = "$2" ] && ! printf '%s\n' "$out" | grep -q "$3"; then
    printf 'PASS  %-48s rc=%s %s\n' "$1" "$rc" "$4"
  else
    printf 'FAIL  %-48s rc=%s (want %s) or forbidden pattern %s present\n' "$1" "$rc" "$2" "$3"
    fail=$((fail+1))
  fi
}

mk '{"a":1}'
bracketed_arm 'ARM 15 attempt=2, stable clean' 0 '^SNAPSHOT MOVED' 'stable second attempt accepted, silent'

# The half that matters most: a stable second attempt's RED is ACCEPTED, not laundered by the
# transient class. Pane 2's spec: "a stable second snapshot is validated EVEN IF RED."
mk '{"a":1}'; printf '{"a":2}' > "$TMP/receipt.json"
bracketed_arm 'ARM 16 attempt=2, stable drifted' 4 '^TRANSIENT_UNSTABLE' 'settled RED accepted, not laundered'

# ARM 17 — the changed-paths EXTRACTOR. It EXTRACTS THE PRODUCTION SED FROM lane-status.sh AT TEST
# TIME rather than carrying a copy, which was pane 3's finding on the first version
# (audit-arms-15-17-20260918T122235Z.json, 4221cc6, REAL_DEFECT_LATENT): "ARM 17 feeds a HAND-WRITTEN
# line through a HAND-COPIED sed. If lane-status.sh's sed changes again, the arm keeps passing on its
# frozen pair while production diverges — the stale-assertion class ONE LEVEL UP. b031ffb's defect was
# an un-re-run assertion; THIS IS AN ASSERTION THAT CANNOT OBSERVE THE NEXT CHANGE."
#
# Its proposed honest form, implemented here: pull the expression out of the source and apply it to
# the fixture line. A format change now FAILS this arm until a human updates the fixture — the forced
# re-examination, not a convenience. If the expression cannot be located at all that is ALSO a FAIL:
# an arm that silently stops testing anything is the defect it exists to catch.
fpline='raw:0123456789abcdef norm:fedcba9876543210  docs/demos/x.json'
prod_sed=$(sed -n "s/.*| *sed -n '\(.*\)' *| *sort -u.*/\1/p" "$REPO/scripts/lane-status.sh" | head -1)
if [ -z "$prod_sed" ]; then
  printf 'FAIL  %-48s could not extract the production sed from lane-status.sh\n' \
    'ARM 17 changed-paths extractor'
  fail=$((fail+1))
else
  got=$(printf '%s\n' "< $fpline" | sed -n "$prod_sed")
  if [ "$got" = 'docs/demos/x.json' ]; then
    printf 'PASS  %-48s production sed extracted and applied\n' 'ARM 17 changed-paths extractor'
  else
    printf 'FAIL  %-48s got %s — production sed and this fixture have diverged\n' \
      'ARM 17 changed-paths extractor' "'${got:-<empty>}'"
    fail=$((fail+1))
  fi
fi

# ARM 18 — UNSTABLE-SELF. Pane 3 retired its own broadcast discipline (0/9 compliance, and hub sends
# leave no auditable trace) and replaced it with a mechanism: lane-status fingerprints its inputs but
# not its own code, "the one input that can splice it". This arm proves the branch DETERMINISTICALLY
# via JEV_SELF_DIGEST_OVERRIDE, because racing a mid-run edit against a ~1s scan produced an arm that
# proved nothing twice in this session and tuning the sleep until it passed would be a false witness.
# The override is fail-safe: it can only manufacture a FALSE TRANSIENT, never a false pass.
mk '{"a":1}'
out=$(JEV_SELF_DIGEST_OVERRIDE=0000000000000000 run); rc=$?
if [ "$rc" = 11 ] && printf '%s\n' "$out" | grep -q '^UNSTABLE-SELF'; then
  printf 'PASS  %-48s rc=11 spliced self reports NO VERDICT\n' 'ARM 18 UNSTABLE-SELF'
else
  printf 'FAIL  %-48s rc=%s (want 11) or no UNSTABLE-SELF line\n' 'ARM 18 UNSTABLE-SELF' "$rc"
  fail=$((fail+1))
fi
printf '\n%s\n' '----------------------------------------------------------------------'
if [ "$fail" = 0 ] && [ "$transient" = 0 ]; then
  printf 'OK: all four gates discriminate on all 18 arms.\n'; exit 0
fi
if [ "$fail" = 0 ]; then
  printf 'TRANSIENT: %d arm(s) could not be verified — HEAD moved during both attempts.\n' "$transient"
  printf 'This is NOT a pass. Re-run when the lane settles; nothing here is a defect claim.\n'
  exit 6
fi
printf 'FAIL: %d arm(s) did not discriminate.\n' "$fail"; exit 1
