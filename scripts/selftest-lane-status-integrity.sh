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

# ARMS 19-25 — the trace join (jev-sjl8). Arms 1-18 use FIX-1, which shares no
# candidate with the live trace, so they never enter the join. These fixtures
# set JEV_TRACE and overlap it. A regression that skips the join, matches a
# substring, or reports a trace miss as a digest-matched receipt stays green
# without them.
digest_of() { perl -0777 -pe 's/\s+\z//' "$1" | shasum -a 256 | cut -c1-16; }
status_row() { # $1=id $2=score $3=receipt $4=digest
  printf '%s\t2\t%s\tCLEARED\tCOD\t%s\t-\t\t%s\tmeasurement\n' "$1" "$2" "$3" "$4"
}
trace_row() { # $1=id $2=score $3=class $4=source
  printf '%s\t%s\t%s\t%s\tnote\n' "$1" "$2" "$3" "$4"
}
trun() { JEV_STATUS="$TMP/status.tsv" JEV_TRACE="$TMP/trace.tsv" "$LS" 2>/dev/null; }
texpect() { # $1=arm $2=want_rc $3=must-have pattern $4=must-not pattern (optional) $5=note
  out=$(trun); rc=$?
  ok=1
  [ "$rc" = "$2" ] || ok=0
  printf '%s\n' "$out" | grep -q "$3" || ok=0
  if [ -n "${4:-}" ] && printf '%s\n' "$out" | grep -q "$4"; then ok=0; fi
  if [ "$ok" = 1 ]; then
    printf 'PASS  %-48s rc=%s %s\n' "$1" "$rc" "$5"
  else
    printf 'FAIL  %-48s rc=%s (want %s) pattern=%s\n' "$1" "$rc" "$2" "$3"
    fail=$((fail+1))
  fi
}

# ARM 19 — join green. One overlapping row, line contains the score, digest matches.
printf 'the score is 900 here\n' > "$TMP/cited.txt"
d=$(digest_of "$TMP/cited.txt")
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-G 900 "$TMP/cited.txt" "$d" >> "$TMP/status.tsv"
printf 'candidate\tscore\tclass\tsource\tnote\n' > "$TMP/trace.tsv"
trace_row ARM-G 900 CITED "$TMP/cited.txt:1" >> "$TMP/trace.tsv"
texpect 'ARM 19 trace join green' 0 'value_checked: 1 of 1' 'disagree with the trace' '1 of 1, no trace FAIL'

# ARM 20 — score edited. Receipt still says 900 and its digest matches; the score column is 901.
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-G 901 "$TMP/cited.txt" "$d" >> "$TMP/status.tsv"
texpect 'ARM 20 score edited' 12 '<<< TRACE ARM-G' 'match their digest' 'rc 12, trace named, digest sentence absent'

# ARM 21 — missing trace row, with another row overlapping so the join cannot skip.
printf 'the score is 900 here\n' > "$TMP/other.txt"
od=$(digest_of "$TMP/other.txt")
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-G 900 "$TMP/cited.txt" "$d" >> "$TMP/status.tsv"
status_row ARM-MISS 900 "$TMP/other.txt" "$od" >> "$TMP/status.tsv"
printf 'candidate\tscore\tclass\tsource\tnote\n' > "$TMP/trace.tsv"
trace_row ARM-G 900 CITED "$TMP/cited.txt:1" >> "$TMP/trace.tsv"
texpect 'ARM 21 missing trace row, overlap' 12 'missing trace row' 'match their digest' 'rc 12, the other row kept the join on'


# ARM 22 — cited line edited, digest not re-pinned. Two classes: drift and trace. Exit 7, both lines.
printf 'the score is 900.\n' > "$TMP/cited.txt"
d=$(digest_of "$TMP/cited.txt")
printf 'the score is 901.\n' > "$TMP/cited.txt"
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-G 900 "$TMP/cited.txt" "$d" >> "$TMP/status.tsv"
printf 'candidate\tscore\tclass\tsource\tnote\n' > "$TMP/trace.tsv"
trace_row ARM-G 900 CITED "$TMP/cited.txt:1" >> "$TMP/trace.tsv"
out=$(trun); rc=$?
if [ "$rc" = 7 ] && printf '%s\n' "$out" | grep -q 'drifted from their pinned digest' \
  && printf '%s\n' "$out" | grep -q '<<< TRACE ARM-G'; then
  printf 'PASS  %-48s rc=7 both drift and TRACE lines\n' 'ARM 22 line edited, digest stale'
else
  printf 'FAIL  %-48s rc=%s (want 7) or a required line is missing\n' 'ARM 22 line edited, digest stale' "$rc"
  fail=$((fail+1))
fi

# ARM 23 — same line edit, digest re-pinned. Trace disagreement alone. Exit 12.
d=$(digest_of "$TMP/cited.txt")
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-G 900 "$TMP/cited.txt" "$d" >> "$TMP/status.tsv"
texpect 'ARM 23 line edited, digest re-pinned' 12 '<<< TRACE ARM-G' 'drifted from their pinned digest' 'rc 12, drift line absent'

# ARM 24 — whole-number boundary. The line says 9001. Score 900 must not match inside it.
printf 'the score is 9001.\n' > "$TMP/cited.txt"
d=$(digest_of "$TMP/cited.txt")
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-G 900 "$TMP/cited.txt" "$d" >> "$TMP/status.tsv"
texpect 'ARM 24 900 vs 9001' 12 '<<< TRACE ARM-G' '' 'substring 900 inside 9001 is not a match'

# ARM 25 — DERIVED recompute red. round(1/2*1000)=500, status says 900.
printf '%s\n' '{"main_correct": 1, "n": 2}' > "$TMP/derived.json"
d=$(digest_of "$TMP/derived.json")
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-D 900 "$TMP/derived.json" "$d" >> "$TMP/status.tsv"
printf 'candidate\tscore\tclass\tsource\tnote\n' > "$TMP/trace.tsv"
trace_row ARM-D 900 DERIVED "$TMP/derived.json:/main_correct,/n" >> "$TMP/trace.tsv"
texpect 'ARM 25 DERIVED recompute red' 12 '<<< TRACE ARM-D' 'match their digest' 'rc 12, formula did not yield 900'

# ARM 26 — sentence-final period is a whole number. 900. matches; 900.5 would not.
printf 'the score is 900.\n' > "$TMP/cited.txt"
d=$(digest_of "$TMP/cited.txt")
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-G 900 "$TMP/cited.txt" "$d" >> "$TMP/status.tsv"
printf 'candidate\tscore\tclass\tsource\tnote\n' > "$TMP/trace.tsv"
trace_row ARM-G 900 CITED "$TMP/cited.txt:1" >> "$TMP/trace.tsv"
texpect 'ARM 26 sentence-final 900.' 0 'value_checked: 1 of 1' '<<< TRACE' 'period does not hide the score'

# ARM 27 — DERIVED green. round(9/10*1000)=900. Planting got=-1 fails this arm.
printf '%s\n' '{"main_correct": 9, "n": 10}' > "$TMP/derived.json"
d=$(digest_of "$TMP/derived.json")
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-D 900 "$TMP/derived.json" "$d" >> "$TMP/status.tsv"
printf 'candidate\tscore\tclass\tsource\tnote\n' > "$TMP/trace.tsv"
trace_row ARM-D 900 DERIVED "$TMP/derived.json:/main_correct,/n" >> "$TMP/trace.tsv"
texpect 'ARM 27 DERIVED recompute green' 0 'value_checked: 1 of 1' '<<< TRACE' 'formula yielded 900'

# ARM 28 — class check. An illegal class exits 12 and must not say a score disagreed.
# Removing the class call from lane-status leaves this arm green, which is the hole.
printf 'the score is 900 here\n' > "$TMP/cited.txt"
d=$(digest_of "$TMP/cited.txt")
printf '#\tfixture\n' > "$TMP/status.tsv"
status_row ARM-C 900 "$TMP/cited.txt" "$d" >> "$TMP/status.tsv"
printf 'candidate\tscore\tclass\tsource\tnote\n' > "$TMP/trace.tsv"
trace_row ARM-C 900 NOTFOUND "$TMP/cited.txt:1" >> "$TMP/trace.tsv"
out=$(trun); rc=$?
if [ "$rc" = 12 ] && printf '%s\n' "$out" | grep -q '<<< TRACE CLASS' \
  && printf '%s\n' "$out" | grep -q 'trace class invalid' \
  && ! printf '%s\n' "$out" | grep -q 'score(s) disagree' \
  && ! printf '%s\n' "$out" | grep -q 'disagree with the score column'; then
  printf 'PASS  %-48s rc=12 class fail is not a score disagreement\n' 'ARM 28 class invalid'
else
  printf 'FAIL  %-48s rc=%s (want 12) or the FAIL line names a score\n' 'ARM 28 class invalid' "$rc"
  fail=$((fail+1))
fi

printf '\n%s\n' '----------------------------------------------------------------------'
if [ "$fail" = 0 ] && [ "$transient" = 0 ]; then
  printf 'OK: all four gates discriminate on all 28 arms.\n'; exit 0
fi
if [ "$fail" = 0 ]; then
  printf 'TRANSIENT: %d arm(s) could not be verified — HEAD moved during both attempts.\n' "$transient"
  printf 'This is NOT a pass. Re-run when the lane settles; nothing here is a defect claim.\n'
  exit 6
fi
printf 'FAIL: %d arm(s) did not discriminate.\n' "$fail"; exit 1
