#!/usr/bin/env bash
# gates.sh -- aggregate gate for the Jev workspace. Runs every stage in
# foundation/gates.d/, one line per stage, nonzero exit on any RED.
# Usage: ./gates.sh [--selftest] [--portable] [--red-row-selftest]
#   --selftest runs each stage's planted-bad check, and proves a RED row names
#   the failing sub-check rather than the head of its log. --red-row-selftest
#   is that proof alone.
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
red_row_only=""
for arg in "$@"; do
    case "$arg" in
        --selftest) mode=--selftest ;;
        --portable) portable=1 ;;
        --red-row-selftest) red_row_only=1 ;;
        *) echo "gates.sh: unknown argument '$arg' (usage: gates.sh [--selftest] [--portable] [--red-row-selftest])" >&2; exit 2 ;;
    esac
done
if [ -n "$portable" ]; then export JEV_GATES_PORTABLE=1; else unset JEV_GATES_PORTABLE; fi

# A RED row names the failing sub-check and prints its last lines, never only
# the head. Stage 80 prints many PASS lines and then one RED; head -c 300 kept
# the PASS lines, so the failing arm was never named (jev-80lj).
red_detail() {
    local out="$1" names tail
    names=$(printf '%s\n' "$out" | grep -E '(^|[[:space:]])(RED|ABSENT|UNEXEC|FAIL|FAILED|ERROR|SELFTEST_FAIL|DRIFT)([[:space:]:]|$)' || true)
    tail=$(printf '%s\n' "$out" | tail -n 12)
    if [ -n "$names" ]; then
        printf 'failing:\n%s\n--- last lines ---\n%s\n' "$names" "$tail"
    else
        printf 'failing: unnamed\n--- last lines ---\n%s\n' "$tail"
    fi
}
prove_red_detail() {
    local i planted excerpt head_only
    planted=""
    for i in 1 2 3 4 5 6 7 8; do
        planted="${planted}  PASS    early-noise-line-that-must-not-be-the-only-evidence-$i"$'\n'
    done
    planted="${planted}  RED     scripts/selftest-planted-late.sh  FAIL planted-arm-9c42"$'\n'
    for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
        planted="${planted}  PASS    later-noise-$i"$'\n'
    done
    planted="${planted}  PASS    tail-nonce-3e91"$'\n'
    head_only=$(printf '%s' "$planted" | head -c 300)
    case "$head_only" in
        *planted-arm-9c42*)
            echo "RED-ROW SELFTEST FAIL: plant is inside the first 300 bytes; the arm cannot fail"
            return 1 ;;
    esac
    case "$(printf '%s\n' "$planted" | tail -n 12)" in
        *planted-arm-9c42*)
            echo "RED-ROW SELFTEST FAIL: plant is inside the last 12 lines; a tail-only formatter would pass"
            return 1 ;;
    esac
    excerpt=$(red_detail "$planted")
    case "$excerpt" in
        *selftest-planted-late.sh*) ;;
        *) echo "RED-ROW SELFTEST FAIL: late failing name not printed"; printf '%s\n' "$excerpt"; return 1 ;;
    esac
    case "$excerpt" in
        *planted-arm-9c42*) ;;
        *) echo "RED-ROW SELFTEST FAIL: failing arm nonce not printed"; printf '%s\n' "$excerpt"; return 1 ;;
    esac
    case "$excerpt" in
        *tail-nonce-3e91*) ;;
        *) echo "RED-ROW SELFTEST FAIL: last lines were dropped"; printf '%s\n' "$excerpt"; return 1 ;;
    esac
    excerpt=$(red_detail $'RED: missing fixture: short-fixture-name-7f3a\n')
    case "$excerpt" in
        *short-fixture-name-7f3a*) ;;
        *) echo "RED-ROW SELFTEST FAIL: short RED did not keep its name"; printf '%s\n' "$excerpt"; return 1 ;;
    esac
    echo "RED-ROW SELFTEST PASS: late name printed (head-300 and tail-12 both miss it); short RED still named"
}
if [ "$mode" = "--selftest" ] || [ -n "$red_row_only" ]; then
    prove_red_detail || exit 1
    if [ -n "$red_row_only" ]; then exit 0; fi
fi
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
    elif [ "$code" -eq 0 ]; then echo "PASS $name (${ms}s)"; else echo "RED  $name (exit=$code, ${ms}s)"; printf '%s\n' "$(red_detail "$out")"; rc=1; fi
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
