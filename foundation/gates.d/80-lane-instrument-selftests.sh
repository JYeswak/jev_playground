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
  # ARM 1 — a missing suite must be a RED, not a silent skip. That is the masking class this lane
  # keeps finding (an elif chain, a `continue` on a short row), so the stage refuses to pass when a
  # suite it names is absent.
  out=$(JEV_SELFTEST_FAKE_MISSING=1 "$0" 2>&1) && {
    echo "80-lane-instrument-selftests --selftest: FAILED — a missing suite did not RED"; exit 1; }
  printf '%s\n' "$out" | grep -q 'ABSENT' || {
    echo "80-lane-instrument-selftests --selftest: FAILED — no ABSENT line for the missing suite"; exit 1; }

  # ARM 2 — a suite that is PRESENT but has lost its +x bit must RED as UNEXEC, not as ABSENT.
  # Pane 3's Q95 found the old single `[ ! -x ]` branch reported both identically, and its own
  # recommendation carried back the SLB precedent: the arm runs on a TEMP COPY and NEVER chmods a real
  # script. Absence covered by ARM 1; this is the branch ARM 1 could not reach.
  tmp=$(mktemp -d) || { echo "80-lane-instrument-selftests --selftest: FAILED — mktemp"; exit 1; }
  cp "$root/scripts/selftest-other-reasons.sh" "$tmp/mode-dropped.sh" 2>/dev/null || {
    echo "80-lane-instrument-selftests --selftest: FAILED — could not copy a suite to $tmp"; exit 1; }
  chmod -x "$tmp/mode-dropped.sh"
  out2=$(JEV_SELFTEST_EXTRA_SUITE="$tmp/mode-dropped.sh" "$0" 2>&1) && {
    echo "80-lane-instrument-selftests --selftest: FAILED — a mode-dropped suite did not RED"; exit 1; }
  printf '%s\n' "$out2" | grep -q 'UNEXEC' || {
    echo "80-lane-instrument-selftests --selftest: FAILED — mode-dropped suite not named UNEXEC"; exit 1; }
  printf '%s\n' "$out2" | grep -q 'ABSENT.*mode-dropped' && {
    echo "80-lane-instrument-selftests --selftest: FAILED — mode drop reported as ABSENT (the conflation)"; exit 1; }

  echo "80-lane-instrument-selftests --selftest: OK (2 arms: missing REDs as ABSENT, mode-dropped REDs as UNEXEC)"
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
# Accepts an ABSOLUTE path so the mode-drop arm can point at a temp COPY. Pane 3's Q95 recommendation
# carried my own SLB lesson back at me: "never the real scripts, per the SLB refusal precedent. Do not
# chmod real scripts to test this."
[ -n "${JEV_SELFTEST_EXTRA_SUITE:-}" ] && suites+=("$JEV_SELFTEST_EXTRA_SUITE")
if [ "${#suites[@]}" -eq 0 ]; then
  echo "  ERROR   scripts/selftest-*.sh matched nothing — an empty scan set is NOT a pass (RULE 1)"
  exit 3
fi

for s in "${suites[@]}"; do
  case "$s" in /*) p="$s" ;; *) p="$root/$s" ;; esac
  # ABSENT and UNEXECUTABLE are SPLIT — pane 3, stage80-x-conflation-20260918T114656Z.json (9b9c639),
  # verdict SPLIT_WORTH_IT: "the conflation hides cause while the stage's job is to name what is
  # wrong." A suite that exists but lost its +x bit (fresh clone without exec bits, partial checkout,
  # a copy tool dropping the mode) reported IDENTICALLY to one that never landed. It also answered the
  # objection I raised — `git checkout -- <path>` repairs both, since git tracks content AND mode — and
  # kept the split anyway for diagnosis speed: absent is a SUPPLY problem, unexecutable is a MODE one.
  if [ ! -e "$p" ]; then
    echo "  ABSENT  $s — named by this stage and not on disk; restore it (git checkout -- $s) or remove it from the suite list"
    rc=1
    continue
  fi
  if [ ! -x "$p" ]; then
    echo "  UNEXEC  $s — on disk but mode dropped; chmod +x $s or git checkout -- $s (mode is tracked) to restore"
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
# SECOND SCAN SET — the stages' OWN selftests, which nothing invoked until now.
#
# Measured 2026-09-18 while wiring stage 95: EIGHT stages in gates.d ship a `--selftest`, and NOT ONE
# of them was ever run by anything. The glob above discovers scripts/selftest-*.sh and stops there, so
# a selftest co-located with its stage was invisible — the exact defect pane 3 named for this stage
# once already ("a 4th selftest lands silently unrun"), recurring in a different directory because the
# fix was applied to one glob instead of to the idea.
#
# This matters most for stage 95, whose arms pane 3 ruled must NOT be hand-run
# (stage95-arms-ruling-20260918T162059Z.json): "a comm-direction inversion would fail toward allowlist
# SILENTLY". Verified by mutation — swapping its two comm(1) directions leaves the gate green while it
# reports the opposite of the truth, and two of its five arms catch it.
#
# Support is DETECTED, never listed: a stage is only invoked with --selftest if its source contains
# the guard. Passing --selftest to a stage that ignores unknown args would run the STAGE and report
# its pass as an arm's pass, which is laundering.
stage_selftests=()
for p in "$root"/foundation/gates.d/*.sh; do
  [ -e "$p" ] || continue
  case "$(basename "$p")" in 80-*) continue ;; esac   # never recurse into this stage
  grep -qE '"\$\{1:-\}"[[:space:]]*(==|=)[[:space:]]*.--selftest' "$p" || continue
  stage_selftests+=("$p")
done

if [ "${#stage_selftests[@]}" -eq 0 ]; then
  echo "  ERROR   no gates.d stage exposes --selftest — an empty scan set is NOT a pass (RULE 1)"
  rc=1
else
  for p in "${stage_selftests[@]}"; do
    n="gates.d/$(basename "$p")"
    if out=$(cd "$root" && bash "$p" --selftest 2>&1); then
      printf '  PASS    %-44s %s\n' "$n --selftest" "$(printf '%s\n' "$out" | tail -1)"
    else
      printf '  RED     %-44s %s\n' "$n --selftest" "$(printf '%s\n' "$out" | tail -1)"
      rc=1
    fi
  done
fi


# Count DERIVED from the glob, never written down — the "3 suites PASS" literal this replaced would
# have staled on the fourth suite, which pane 3 flagged as cosmetic and is the same class as every
# other count this session got wrong.
# BOTH counts, because reporting only the first made the line WRONG the moment the second scan set
# landed: it printed "4 suites PASS" while eleven had run. Same class as the literal it replaced.
[ "$rc" -eq 0 ] && printf '80-lane-instrument-selftests: %d instrument suite(s) + %d stage selftest(s) PASS (hermetic; no shared state written)\n' "${#suites[@]}" "${#stage_selftests[@]}"
exit "$rc"
