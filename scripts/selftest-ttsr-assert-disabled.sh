#!/usr/bin/env bash
# selftest-ttsr-assert-disabled.sh — acceptance arms for ttsr-assert-disabled.
#
# ARM1 is the RED arm: a rule that IS live must exit 1 AND name a scope.
# A tool that goes green on a live rule is the defect this exists to catch
# (the reported disable that did not take). Live name is discovered from
# `omp ttsr list --json` in the project, never hardcoded — a hardcoded live
# name that later gets disabled would turn this arm into a false pass.
#
# ARM2 is the GREEN arm / disable wire: every name in EXPECTED_DISABLED
# must be absent in both scopes (exit 0). Adding a disable without adding
# the name here is not the wire; adding the name without the assert passing
# is a failed disable. A disable that is not enumerated did not happen.
#
# ARM3 is usage: no args → exit 2.
#
# Capture-first throughout. NEVER runs `omp ttsr test`. NEVER sets
# ttsr.disabledRules.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
command -v omp >/dev/null 2>&1 || { echo "  SKIP omp not on PATH — NOT counted as agreement"; echo "scripts/selftest-ttsr-assert-disabled.sh: skipped"; exit 0; }
pass=0; fail=0
note() { printf '  %-4s %s\n' "$1" "$2"; }

S="./scripts/ttsr-assert-disabled.sh"

EXPECTED_DISABLED=(absence-from-one-probe)

live=""
list_json=$(omp ttsr list --json) || { echo "ENUMERATION_FAILED: omp ttsr list --json"; exit 1; }
live=$(printf '%s\n' "$list_json" | python3 -c '
import json, sys
skip = set(sys.argv[1].split(",")) if sys.argv[1] else set()
rules = json.loads(sys.stdin.read())
for r in rules:
    n = r.get("name") if isinstance(r, dict) else None
    if n and n not in skip:
        print(n)
        break
' "$(IFS=,; echo "${EXPECTED_DISABLED[*]}")")

if [ -z "$live" ]; then
  note FAIL "RED arm: empty live-rule scan set — cannot prove the tool fails closed"
  fail=$((fail+1))
else
  out1=""; rc1=0
  out1=$("$S" "$live" 2>&1) || rc1=$?
  if [ "$rc1" -eq 1 ]; then note ok "RED: live $live exits 1"; pass=$((pass+1))
  else note FAIL "RED: live $live exit=$rc1, want 1"; fail=$((fail+1)); fi
  case "$out1" in
    *'still present in project'*|*'still present in global'*) note ok "RED: names a scope"; pass=$((pass+1)) ;;
    *) note FAIL "RED: did not name project or global scope"; fail=$((fail+1)) ;;
  esac
fi

for r in "${EXPECTED_DISABLED[@]}"; do
  out2=""; rc2=0
  out2=$("$S" "$r" 2>&1) || rc2=$?
  if [ "$rc2" -eq 0 ]; then note ok "GREEN: $r absent both scopes"; pass=$((pass+1))
  else note FAIL "GREEN: $r exit=$rc2 (still present — disable did not take)"; fail=$((fail+1)); fi
  case "$out2" in
    *'still present'*) note FAIL "GREEN: $r output claims present"; fail=$((fail+1)) ;;
  esac
done

out3=""; rc3=0
out3=$("$S" 2>&1) || rc3=$?
if [ "$rc3" -eq 2 ]; then note ok "usage: no args exits 2"; pass=$((pass+1))
else note FAIL "usage: no args exit=$rc3, want 2"; fail=$((fail+1)); fi

echo "scripts/selftest-ttsr-assert-disabled.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ]
