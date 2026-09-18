#!/usr/bin/env bash
# 80-lane-instrument-selftests.sh — run the three lane-instrument selftests as a foundation stage.
#
# AUTHORISED BY A RULING, not by preference. Pane 2's Q83/Q87
# (docs/demos/duel-2/RULE_gate_wiring_COD.md, 6eb5482 / 5f8ef5c) ruled per candidate:
#
#   lane-status.sh          HAND-RUN, tick only        — it reads mutable shared state
#   audit-score-lineage.sh  HAND-RUN, history only     — it exits 6 by design on this repo's untyped
#                                                        history; wiring it would block all panes
#   verify-other-reasons.sh FOUNDATION-STAGE CANDIDATE — "after copy-based selftest wrapper"
#   support selftests       "can be foundation stages ONCE WRAPPED HERMETICALLY"
#
# THE PRECONDITION IS NOW MET, which is the only reason this file exists: all three selftests build
# their own fixtures in a temp dir and drive the instruments through JEV_STATUS / JEV_SIDECAR, so
# none of them writes docs/demos/STATUS.tsv or the sidecar. That hook was added after the SLB
# two-person guard refused an arm script that briefly truncated the real state of record — correctly,
# since restore-after is not safety in a worktree three panes are reading.
#
# WHAT THIS STAGE DELIBERATELY DOES NOT RUN:
#   - `lane-status.sh` itself (mutable shared state; the tick runs it)
#   - `audit-score-lineage.sh` itself (legitimately nonzero here)
#   - `verify-other-reasons.sh` itself — its SELFTEST is hermetic, but the verifier reads the live
#     STATUS.tsv and sidecar, and pane 2's ruling made it a *candidate* pending exactly this wrapper.
#     Running the wrapper is what the ruling authorised; promoting the verifier itself is a separate
#     decision with its own re-examination condition, and this file does not take it.
#
# `foundation/gates.sh` is NOT wired to any commit hook (githooks/pre-commit mentions gates.d only in
# a comment), so a RED here blocks a suite run, never a pane's commit. Verified before this landed.
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../.." && pwd)"
rc=0

if [ "${1:-}" = '--selftest' ]; then
  # The stage's own known-bad: a missing suite must be a RED, not a silent skip. That is the masking
  # class this lane keeps finding (an elif chain, a `continue` on a short row), so the stage refuses
  # to pass when a suite it names is absent.
  out=$(JEV_SELFTEST_FAKE_MISSING=1 "$0" 2>&1) && {
    echo "80-lane-instrument-selftests --selftest: FAILED — a missing suite did not RED"; exit 1; }
  printf '%s\n' "$out" | grep -q 'ABSENT' || {
    echo "80-lane-instrument-selftests --selftest: FAILED — no ABSENT line for the missing suite"; exit 1; }
  echo "80-lane-instrument-selftests --selftest: OK (missing suite REDs and is named)"
  exit 0
fi

# GLOB, NOT A LIST — pane 3, audit-stage80-20260918T112921Z.json (71183c0):
#   "Suites enumerated literally; A 4TH SELFTEST LANDS SILENTLY UNRUN (the inverse of the guarded
#    missing-suite case: unlisted-new vs listed-missing). Recommend glob scripts/selftest-*.sh."
# It is right, and the irony is exact: this stage shipped with a hardcoded list in the same session
# that replaced GATES.md's hardcoded stage list with "the glob is the authority", for this defect.
# A listed-missing suite REDs loudly; an unlisted-new suite was invisible. Both directions now hold:
# the glob discovers every scripts/selftest-*.sh, and an empty glob is an ERROR, not a pass.
suites=()
for p in "$root"/scripts/selftest-*.sh; do
  [ -e "$p" ] || continue
  suites+=("scripts/$(basename "$p")")
done
[ -n "${JEV_SELFTEST_FAKE_MISSING:-}" ] && suites+=("scripts/selftest-does-not-exist.sh")
if [ "${#suites[@]}" -eq 0 ]; then
  echo "  ERROR   scripts/selftest-*.sh matched nothing — an empty scan set is NOT a pass (RULE 1)"
  exit 3
fi

for s in "${suites[@]}"; do
  p="$root/$s"
  if [ ! -x "$p" ]; then
    echo "  ABSENT  $s — named by this stage and not executable on disk"
    rc=1
    continue
  fi
  if out=$(cd "$root" && "$p" 2>&1); then
    printf '  PASS    %-44s %s\n' "$s" "$(printf '%s\n' "$out" | tail -1)"
  else
    printf '  RED     %-44s %s\n' "$s" "$(printf '%s\n' "$out" | tail -1)"
    rc=1
  fi
done

# Count DERIVED from the glob, never written down — the "3 suites PASS" literal this replaced would
# have staled on the fourth suite, which pane 3 flagged as cosmetic and is the same class as every
# other count this session got wrong.
[ "$rc" -eq 0 ] && printf '80-lane-instrument-selftests: %d suites PASS (hermetic; no shared state written)\n' "${#suites[@]}"
exit "$rc"
