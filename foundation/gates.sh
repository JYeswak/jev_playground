#!/usr/bin/env bash
# gates.sh -- aggregate gate for the Jev workspace. Runs every stage in
# foundation/gates.d/, one line per stage, nonzero exit on any RED.
# Usage: ./gates.sh [--selftest] [--portable]   (--selftest runs each stage's planted-bad
# check instead: every stage must prove it can go RED, or the gate is decoration.)
#
# --portable (jev-fmy): for a stranger's clone. Four stages need tools this machine has and a
# fresh clone does not (ast-grep/rg, the private foundry loop-kit, an omp install). Under
# --portable, JEV_GATES_PORTABLE=1 is exported and such a stage prints
# `SKIP (missing prerequisite: <name>, install: <how>)` and exits 8; the row prints SKIP, the
# summary counts it, and the run exits 0 if nothing is RED. EXIT 8 IS HONOURED ONLY UNDER
# --portable: in the default mode a stage never emits it, and if one did it is RED. The default
# mode is unchanged and fails closed on a missing prerequisite exactly as before.
set -uo pipefail
# `pipefail` added 2026-09-18 on pane 3's hardening plan (db97021), which graded all six of
# these SAFE-TO-HARDEN and behaviour-neutral TODAY. Its qualifier is the load-bearing half and
# is reproduced here rather than left in a receipt: neutrality holds ONLY because this file does
# not `set -e`. IF `set -e` IS EVER ADDED, RE-AUDIT — pipefail+errexit aborts on a middle-stage
# failure, and every pipe then existing needs explicit handling (see 30-no-secrets.sh:21, whose
# `grep … | head` is the feared shape and is already neutralised with `|| true`).
here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
mode=run
portable=""
for arg in "$@"; do
    case "$arg" in
        --selftest) mode=--selftest ;;
        --portable) portable=1 ;;
        *) echo "gates.sh: unknown argument '$arg' (usage: gates.sh [--selftest] [--portable])" >&2; exit 2 ;;
    esac
done
if [ -n "$portable" ]; then export JEV_GATES_PORTABLE=1; else unset JEV_GATES_PORTABLE; fi
rc=0
unmeasured=0
skipped=0
# Resolved ONCE, in a subshell cd rather than `git -C` (dcg denies the -C form), because the first
# version of the outcome log called git inside the loop: twelve extra git invocations per run, and
# a denied command per stage. It hung two runs before this fix.
head_sha=$( (CDPATH='' cd -- "$here/.." && git rev-parse --short HEAD) 2>/dev/null || echo unknown )
root=$(CDPATH='' cd -- "$here/.." && pwd -P)
beads_db=$(find "$root/.beads" -type f -name '*.db' -print -quit 2>/dev/null)
if [ -z "$beads_db" ]; then
    echo "RED  foundation gates require an imported Beads database under $root/.beads/*.db"
    echo "     Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun ./foundation/gates.sh"
    exit 1
fi
for stage in "$here"/gates.d/[0-9]*-*.sh; do
    [ -x "$stage" ] || continue
    name=$(basename "$stage" .sh)
    start=$(date +%s)
    if [ "$mode" = "--selftest" ]; then out=$("$stage" --selftest 2>&1); else out=$("$stage" 2>&1); fi
    code=$?
    ms=$(( $(date +%s) - start ))
    # EXIT 7 = UNMEASURED: the stage ran, declined to issue a verdict, and must NOT be laundered
    # into PASS. Pane 2, audit-stage90-wrapper-20260918T170000Z.json (2e7bab2): stage 90's mapping
    # was stage-locally correct but "foundation/gates.sh captures no stage stdout for rc0 and prints
    # PASS stage90, so AGGREGATE CURRENTLY ERASES UNMEASURED INTO PASS ... no claim ALL GREEN means
    # all verified." I introduced that by exiting 0 on a transient. Nonblocking, but never silent:
    # the row prints, the stage's own words print, and the summary carries the count.
    if [ "$code" -eq 7 ]; then
        echo "UNMEASURED $name (${ms}s): $(printf '%s' "$out" | head -c 300)"
        unmeasured=$(( unmeasured + 1 ))
    elif [ "$code" -eq 8 ] && [ -n "$portable" ] && skipline=$(printf '%s\n' "$out" | grep -m1 '^SKIP (missing prerequisite: '); then
        # The stage's own SKIP line names the prerequisite; print that, not the head of its log.
        # An exit 8 that names nothing falls through to RED: a skip nobody can act on is a defect.
        echo "SKIP $name (${ms}s): $skipline"
        skipped=$(( skipped + 1 ))
    elif [ "$code" -eq 0 ]; then echo "PASS $name (${ms}s)"; else echo "RED  $name (exit=$code, ${ms}s): $(printf '%s' "$out" | head -c 300)"; rc=1; fi
    # RECORD THE OUTCOME VECTOR. Until 2026-09-19 this loop persisted nothing, so "do two of our
    # twelve gates fail on the same commits?" was unanswerable — and that question decides whether
    # a gate earns its slot or is a second copy of one we already run (RECIPES.md recipe 4: two
    # checkers are only worth having if they fail on DIFFERENT things). One TSV line per stage per
    # run makes the phi measurement in ensemble/decorrelation.py applicable to our own instruments.
    # Append-only, best-effort: a log that cannot be written must never turn a gate RED.
    if [ "${JEV_GATE_LOG:-1}" != "0" ]; then
        printf '%s\t%s\t%s\t%s\t%s\n' \
            "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$name" "$code" "$mode" "$head_sha" \
            >> "$here/gate-outcomes.tsv" 2>/dev/null || true
    fi
done
if [ "$rc" -ne 0 ]; then
    echo "gates: FAILING (see RED rows)"
elif [ "$skipped" -ne 0 ]; then
    # Portable only. Never "ALL GREEN": the SKIP rows are stages that issued no verdict.
    echo "gates: GREEN WITH $skipped SKIPPED, $unmeasured UNMEASURED (portable) — not all stages issued a verdict"
elif [ "$unmeasured" -ne 0 ]; then
    # "ALL GREEN" would assert something no stage established. Say what is actually true.
    echo "gates: GREEN WITH $unmeasured UNMEASURED — not all stages issued a verdict"
else
    echo "gates: ALL GREEN"
fi
exit "$rc"
