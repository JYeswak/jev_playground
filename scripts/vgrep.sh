#!/usr/bin/env bash
# vgrep — a grep that CANNOT silently report "clean" when its pattern found nothing.
#
# CREATION GATE, answered:
#   1. CONSUMER  — any lane script or operator using grep as PROOF of a claim, and
#                  scripts/selftest-vgrep.sh, which foundation/gates.d/80 auto-discovers.
#   2. GATE      — a verification grep that matches zero lines exits 3 (INCONCLUSIVE), never 0 or 1.
#                  A caller using `set -e` or checking `rc=0` can no longer read "found nothing"
#                  as "verified nothing wrong".
#   3. DEFECT    — OBSERVED, 2026-09-20, 26 times in one session. The three that cost the most:
#                    * `grep -c 'arm'` returned 1 against a suite with 5 real arms -> nearly filed
#                      a false defect against a peer's correct work.
#                    * a link checker using `tr -d '](.)'` stripped the dot in `.md` and reported
#                      4 of 4 links missing -> nearly filed a second false defect.
#                    * `STATUS_TSV=...` passed as an env var to a script taking a POSITIONAL arg:
#                      it scanned the real file, printed 0 PROMOTED, and that looked exactly like
#                      the gate correctly refusing junk. It was reading a different file.
#                  Every one of these is the same shape: THE SELECTOR WAS WRONG AND THE SILENCE
#                  READ AS A RESULT. Prose rules did not stop it; this session has a 200-line tick
#                  file warning about it and it still recurred 26 times.
#   4. RETIREMENT — when no verification path in this repo calls bare grep for proof. Measure with
#                  `grep -rc 'grep -[cq]' scripts/ foundation/`: it was 35 sites at creation.
#
# WHAT IT DELIBERATELY DOES NOT DO: it does not check that your pattern is CORRECT. A wrong
# pattern that happens to match something still exits 0. It converts exactly one failure — the
# silent zero — from invisible into loud. That is the whole claim.
#
# Usage:
#   scripts/vgrep.sh [grep args...]        # exit 0 = matched, 3 = ZERO MATCHES, 2 = grep error
#   scripts/vgrep.sh --expect-zero [args]  # invert: zero is the PASS, any match exits 3
#
# The --expect-zero mode exists because "prove this string is absent" is a legitimate check
# (the repo's own observe-only proof is `grep -qE '\b(block|deny)\b' || echo observe-only`), and
# without it a caller would work around the guard instead of using it.
set -uo pipefail

expect_zero=0
if [ "${1:-}" = '--expect-zero' ]; then expect_zero=1; shift; fi

if [ "$#" -eq 0 ]; then
  echo "vgrep: no grep arguments given — an empty invocation is not a pass" >&2
  exit 2
fi

out=$(grep "$@")
rc=$?

# grep: 0 = matched, 1 = no match, >1 = real error (bad regex, unreadable file).
if [ "$rc" -gt 1 ]; then
  echo "vgrep: grep ERROR rc=$rc — the selector or the path is broken, NOT a clean result" >&2
  exit 2
fi

if [ "$expect_zero" -eq 1 ]; then
  if [ "$rc" -eq 1 ]; then exit 0; fi
  echo "vgrep: --expect-zero but the pattern MATCHED:" >&2
  printf '%s\n' "$out" >&2
  exit 3
fi

if [ "$rc" -eq 1 ]; then
  echo "vgrep: ZERO MATCHES for: $*" >&2
  echo "vgrep: this is INCONCLUSIVE, not clean. Re-derive a second way before claiming anything." >&2
  echo "vgrep: if absence is what you are proving, say so explicitly with --expect-zero." >&2
  exit 3
fi

printf '%s\n' "$out"
exit 0
