#!/bin/sh
# gates.sh -- aggregate gate for the Jev workspace. Runs every stage in
# foundation/gates.d/, one line per stage, nonzero exit on any RED.
# Usage: ./gates.sh [--selftest]   (--selftest runs each stage's planted-bad
# check instead: every stage must prove it can go RED, or the gate is decoration.)
set -u
here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
mode=${1:-run}
rc=0
for stage in "$here"/gates.d/[0-9]*-*.sh; do
    [ -x "$stage" ] || continue
    name=$(basename "$stage" .sh)
    start=$(date +%s)
    if [ "$mode" = "--selftest" ]; then out=$("$stage" --selftest 2>&1); else out=$("$stage" 2>&1); fi
    code=$?
    ms=$(( $(date +%s) - start ))
    if [ "$code" -eq 0 ]; then echo "PASS $name (${ms}s)"; else echo "RED  $name (exit=$code, ${ms}s): $(printf '%s' "$out" | head -c 300)"; rc=1; fi
done
[ "$rc" -eq 0 ] && echo "gates: ALL GREEN" || echo "gates: FAILING (see RED rows)"
exit "$rc"
