#!/usr/bin/env bash
# pinned-denominator — a claimed denominator that CANNOT silently survive the store moving.
#
# CREATION GATE, answered:
#   1. CONSUMER  — any receipt, README, or callback quoting a share (a count with a
#                  denominator), and scripts/selftest-pinned-denominator.sh, which
#                  foundation/gates.d/80 auto-discovers via its scripts/selftest-*.sh glob.
#   2. GATE      — takes a claimed denominator and the command that regenerates it, runs
#                  the command fresh, and exits 0 only on agreement. Disagreement exits 3
#                  (DRIFT); a failed command or non-count output exits 2 (ERROR, never a pass).
#   3. DEFECT    — OBSERVED, 2026-09-20, 8 instances in one session. The four that cost the most:
#                    * a harvest share quoted 77,767 after the corpus regenerated to 78,242.
#                    * `matched=15525` quoted after the rerun printed 15618.
#                    * a `bv` actionable count quoted as 23, then 20, then 19 across three runs.
#                    * a README claimed "22 of 22" while the census held 24 clones and 11 RUN rows.
#                  Every one is the same shape: THE SENTENCE NEVER CHANGED AND THE STORE DID.
#                  Prose review did not stop it; only a re-running check can.
#   4. RETIREMENT — when no published share in this repo carries a bare denominator without a
#                  pinned regeneration command beside it. Measure with
#                  `grep -rn 'of [0-9]\|n=[0-9]\|/[0-9][0-9]*$' docs/demos/ | wc -l` trending down;
#                  retire only when a second session lands zero new drift defects.
#
# WHAT IT DELIBERATELY DOES NOT DO:
#   - It does not check that your regeneration command is the RIGHT one. A stale-but-stable
#     command that prints the same wrong number as the claim exits 0. Agreement is not truth;
#     only disagreement is news.
#   - It cannot catch drift that happens between two runs of the same command — it compares
#     the claim against one fresh run at call time. Pin the claim at authoring time or the
#     first run after is already the audit, not the proof.
#   That is the whole claim: a moved denominator becomes loud instead of silently wrong.
#
# Usage:
#   scripts/pinned-denominator.sh <expected> <command...>
#     <expected> is the quoted denominator; commas and surrounding whitespace are ignored.
#     <command...> must print the denominator as its whole stdout (commas tolerated).
#     exit 0 = agree, 3 = DRIFT, 2 = command failed / output is not a count / bad invocation.
set -uo pipefail

if [ "$#" -lt 2 ]; then
  echo "pinned-denominator: usage: pinned-denominator.sh <expected> <command...>" >&2
  echo "pinned-denominator: a claim without a regeneration command is not a check" >&2
  exit 2
fi

expected="$1"; shift

norm() { tr -d ' ,\t\n' <<<"$1"; }

exp_n=$(norm "$expected")
if ! [[ "$exp_n" =~ ^[0-9]+$ ]]; then
  echo "pinned-denominator: expected value '$expected' is not a count — refusing" >&2
  exit 2
fi

out=$("$@") || {
  rc=$?
  echo "pinned-denominator: regeneration command failed rc=$rc — not a pass" >&2
  exit 2
}

got_n=$(norm "$out")
if ! [[ "$got_n" =~ ^[0-9]+$ ]]; then
  echo "pinned-denominator: command output is not a single count: '$out' — refusing" >&2
  exit 2
fi

# Base-10 force: counts with leading zeros must not parse as octal.
if [ "$((10#$exp_n))" -ne "$((10#$got_n))" ]; then
  echo "pinned-denominator: DRIFT — claimed $exp_n, fresh run says $got_n" >&2
  echo "pinned-denominator: the sentence is wrong even though nobody edited it" >&2
  exit 3
fi

echo "pinned-denominator: agree ($got_n)"
exit 0
