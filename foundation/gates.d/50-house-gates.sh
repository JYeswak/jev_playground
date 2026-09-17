#!/bin/sh
# 50-house-gates: run the foundry house gates that have a REAL consumer in this lane, against
# this repo. Three of the four:
#
#   dag-validate-gate.sh     our bead store must be a valid DAG before anything dispatches from it
#   close-evidence-gate.sh   a bead close must CARRY its proof, not assert "done"
#   commit-evidence-lint.sh  a perf(/fix( subject must carry a quantified delta + a verification token
#
# The fourth, neg-evidence-gate.sh, is NOT wired here and that is an argued refusal, not an
# oversight: it enforces "a RED tick appended to NEGATIVE_EVIDENCE.md" and takes --verdict from a
# tick ledger. This lane runs no tick loop, so the gate would have no consumer — and a gate whose
# only consumer is another agent is refused by value-bearing-gates. Wire it the day this lane gets
# a loop driver (which is also when p12-loop-integrity stops being N/A).
#
# These are WRAPPED, never re-implemented: the house scripts are the single source of truth, and
# each one ships its own --selftest. --selftest here delegates to theirs, so our RED arm is
# exactly their proven RED arm.
#
# Exit: 0 all green · 1 a gate refused · 3 the house gates are unreachable (instrument error,
# never a content pass).

set -u

KIT="${LOOP_KIT:-$HOME/Developer/foundry/loop-kit}"
REPO="$(unset CDPATH; cd -- "$(dirname -- "$0")/../.." && pwd)"
GATES="dag-validate-gate.sh close-evidence-gate.sh commit-evidence-lint.sh"

for g in $GATES; do
    if [ ! -x "$KIT/$g" ]; then
        echo "ERROR: $KIT/$g missing or not executable — house gates unreachable (set LOOP_KIT)" >&2
        exit 3
    fi
done

if [ "${1:-}" = "--selftest" ]; then
    rc=0
    for g in $GATES; do
        # HERMETIC, and the isolation is load-bearing, not hygiene theater.
        # Measured 2026-09-17: `init.templateDir = ~/.git-templates` installs this machine's
        # commit-msg verification-level hook into EVERY newly created repo. A house gate whose
        # selftest builds a throwaway fixture repo and commits plain messages therefore fails at
        # "fixture repo setup" — the hook refuses a level-less subject, exactly as designed.
        # commit-evidence-lint.sh --selftest fails with the ambient config and PASSES with
        # GIT_CONFIG_GLOBAL=/dev/null ("3 known-bad flagged, 3 clean controls passed"), which is
        # the discriminating proof that the fixture, not the gate, was broken.
        out=$(GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null "$KIT/$g" --selftest 2>&1)
        code=$?
        if [ "$code" -eq 0 ]; then
            echo "  selftest PASS  $g"
        else
            echo "  selftest RED   $g (exit=$code): $(printf '%s' "$out" | tail -3)"
            rc=1
        fi
    done
    [ "$rc" -eq 0 ] && echo "50-house-gates: all three house gates prove their own RED arm"
    exit "$rc"
fi

rc=0
for g in $GATES; do
    out=$("$KIT/$g" --repo "$REPO" 2>&1)
    code=$?
    case "$code" in
        0) echo "  PASS  $g" ;;
        *) echo "  REFUSE $g (exit=$code): $(printf '%s' "$out" | tail -5)"; rc=1 ;;
    esac
done

[ "$rc" -eq 0 ] && echo "50-house-gates: dag + close-evidence + commit-evidence green on $REPO"
exit "$rc"
