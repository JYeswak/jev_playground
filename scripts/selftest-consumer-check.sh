#!/usr/bin/env bash
# selftest-consumer-check.sh — acceptance arms for consumer-check.
# ARM1 is the refusal arm: 'ee preflight' must refuse (exit 1) AND name the
# two live ee callers (orient + journal). A tool that cannot tell those apart
# is not the tool. ARM1b is the anti-false-zero arm (CHALLENGE-P2 2026-09-20):
# 'ee orient' must EXIT 0 — the args-array form (EE_BIN + COMMAND_ARGS spread)
# fooled v1 into ZERO, the dangerous direction (retires live wiring).
# ARM2 is the live arm: 'dcg' must exit 0 naming dcg-tool-bridge.ts.
# ARM3/ARM4 are the transitive-chain arms (R68 2026-09-21): denominator-sweep
# and exposure-check must refuse (exit 1, no NON-TEST consumer) AND show the
# gate-80 -> selftest -> instrument chain. A missing chain is the failure.
# Capture-first throughout: exit codes come from separate unpiped runs
# (this lane's own bash-pipe-exit class).
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
pass=0; fail=0
note() { printf '  %-4s %s\n' "$1" "$2"; }

out1=""; rc1=""
out1=$(./scripts/consumer-check.sh "ee preflight" 2>&1); rc1=$?
if [ "$rc1" -eq 1 ]; then note ok "ee-preflight exits 1 (refusal)"; pass=$((pass+1));
else note FAIL "ee-preflight exit=$rc1, want 1"; fail=$((fail+1)); fi
case "$out1" in
  *NO\ NON-TEST\ CONSUMER*) note ok "ee-preflight says NO NON-TEST CONSUMER (R68 wording)"; pass=$((pass+1));;
  *) note FAIL "ee-preflight missing R68 verdict"; fail=$((fail+1));;
esac
case "$out1" in
  *ee-ambient-session-start.ts*orient*) note ok "names ambient-start + orient"; pass=$((pass+1));;
  *) note FAIL "missing ambient-start/orient"; fail=$((fail+1));;
esac
case "$out1" in
  *ee-failure-journal.ts*journal*) note ok "names failure-journal + journal"; pass=$((pass+1));;
  *) note FAIL "missing failure-journal/journal"; fail=$((fail+1));;
esac

out1b=""; rc1b=""
out1b=$(./scripts/consumer-check.sh "ee orient" 2>&1); rc1b=$?
if [ "$rc1b" -eq 0 ]; then note ok "ee-orient exits 0 (CONSUMERS)"; pass=$((pass+1));
else note FAIL "ee-orient exit=$rc1b, want 0 — false ZERO"; fail=$((fail+1)); fi
case "$out1b" in
  *ee-ambient-session-start.ts*COMMAND_ARGS*orient*) note ok "names ambient-start argv-array evidence"; pass=$((pass+1));;
  *) note FAIL "missing ambient-start argv evidence"; fail=$((fail+1));;
esac

out2=""; rc2=""
out2=$(./scripts/consumer-check.sh dcg 2>&1); rc2=$?
if [ "$rc2" -eq 0 ]; then note ok "dcg exits 0 (consumers)"; pass=$((pass+1));
else note FAIL "dcg exit=$rc2, want 0"; fail=$((fail+1)); fi
case "$out2" in
  *dcg-tool-bridge.ts*) note ok "names dcg-tool-bridge.ts"; pass=$((pass+1));;
  *) note FAIL "missing dcg-tool-bridge.ts"; fail=$((fail+1));;
esac

out3=""; rc3=""
out3=$(./scripts/consumer-check.sh denominator-sweep 2>&1); rc3=$?
if [ "$rc3" -eq 1 ]; then note ok "denominator-sweep exits 1 (no non-test consumer)"; pass=$((pass+1));
else note FAIL "denominator-sweep exit=$rc3, want 1"; fail=$((fail+1)); fi
case "$out3" in
  *80-lane-instrument-selftests.sh*glob*denominator-sweep*) note ok "denominator chain: gate80 -> selftest -> instrument"; pass=$((pass+1));;
  *) note FAIL "denominator chain missing"; fail=$((fail+1));;
esac

out4=""; rc4=""
out4=$(./scripts/consumer-check.sh exposure-check 2>&1); rc4=$?
if [ "$rc4" -eq 1 ]; then note ok "exposure-check exits 1 (no non-test consumer)"; pass=$((pass+1));
else note FAIL "exposure-check exit=$rc4, want 1"; fail=$((fail+1)); fi
case "$out4" in
  *80-lane-instrument-selftests.sh*glob*exposure-check*) note ok "exposure chain: gate80 -> selftest -> instrument"; pass=$((pass+1));;
  *) note FAIL "exposure chain missing"; fail=$((fail+1));;
esac

echo "scripts/selftest-consumer-check.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ]
