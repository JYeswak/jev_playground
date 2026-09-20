#!/usr/bin/env bash
# selftest-consumer-check.sh — both acceptance arms for consumer-check.
# ARM1 is the RED arm: 'ee preflight' must refuse (exit 1) AND name the two
# live ee callers (orient + journal). A tool that cannot tell those apart
# is not the tool. ARM2 is the live arm: 'dcg' must exit 0 naming
# dcg-tool-bridge.ts. Capture-first throughout: exit codes come from
# separate unpiped runs (this lane's own bash-pipe-exit class).
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
pass=0; fail=0
note() { printf '  %-4s %s\n' "$1" "$2"; }

out1=""; rc1=""
out1=$(./scripts/consumer-check.sh "ee preflight" 2>&1); rc1=$?
if [ "$rc1" -eq 1 ]; then note ok "ee-preflight exits 1 (ZERO)"; pass=$((pass+1));
else note FAIL "ee-preflight exit=$rc1, want 1"; fail=$((fail+1)); fi
case "$out1" in
  *ZERO\ CONSUMERS*) note ok "ee-preflight says ZERO CONSUMERS"; pass=$((pass+1));;
  *) note FAIL "ee-preflight missing ZERO CONSUMERS"; fail=$((fail+1));;
esac
case "$out1" in
  *ee-ambient-session-start.ts*orient*) note ok "names ambient-start + orient"; pass=$((pass+1));;
  *) note FAIL "missing ambient-start/orient"; fail=$((fail+1));;
esac
case "$out1" in
  *ee-failure-journal.ts*journal*) note ok "names failure-journal + journal"; pass=$((pass+1));;
  *) note FAIL "missing failure-journal/journal"; fail=$((fail+1));;
esac

out2=""; rc2=""
out2=$(./scripts/consumer-check.sh dcg 2>&1); rc2=$?
if [ "$rc2" -eq 0 ]; then note ok "dcg exits 0 (consumers)"; pass=$((pass+1));
else note FAIL "dcg exit=$rc2, want 0"; fail=$((fail+1)); fi
case "$out2" in
  *dcg-tool-bridge.ts*) note ok "names dcg-tool-bridge.ts"; pass=$((pass+1));;
  *) note FAIL "missing dcg-tool-bridge.ts"; fail=$((fail+1));;
esac

echo "scripts/selftest-consumer-check.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ]
