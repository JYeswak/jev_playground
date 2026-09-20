#!/usr/bin/env bash
# denominator-sweep — run every pinned-denominator check in one pass for the next audit.
#
# This is a RUNNER, not a guard and not a gate stage: it calls
# scripts/pinned-denominator.sh once per pinned claim and fails loudly on the
# first DRIFT. Do NOT add live-monotonic claims here — a moving target wired
# as an agree-check REDs forever (the nag class R46/R47 refused). Live claims
# (harvest family) keep as-of labels + regen commands in their receipts, per
# docs/demos/upstream-repro/harvest-asof-20260920.md.
#
# LOCATION SAFETY: the sentinel below refuses when the script is copied
# elsewhere (e.g. /tmp re-anchors $0, every relative path resolves to
# nothing, and eight confident DRIFTs would all be false — worse than no
# report). An empty scan set is never a pass.
#
# Claims and their regeneration commands (see denominator-audit-20260920.md):
#   138 locked dig questions — grep -c over the locked export
#   21  census packages — ls -d piped to wc -l (never `wc -l file`)
#   55  pinned replay rows — replay.mjs over the pinned fixture + awk field
#   0   pinned replay api calls — same run, value field
#   7846 frozen corpus rows — wc -l over stdin redirect
#   315 frozen isError — grep -c over the frozen file
#   29  routing-backtest tests — npm test TAP summary
#   19  export-YES packages — per-dir model+persist grep rule (export-resweep receipt)
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
[ -x "$root/scripts/pinned-denominator.sh" ] || {
  echo "denominator-sweep: REFUSE — not anchored at a repo root (missing scripts/pinned-denominator.sh under $root)." >&2
  exit 2
}
P="$root/scripts/pinned-denominator.sh"
fail=0
skipped=0

check() { # check <label> <expected> <cmd...>
  local label="$1" expected="$2"; shift 2
  "$P" "$expected" "$@" >/dev/null 2>&1
  local got=$?
  if [ "$got" -eq 0 ]; then
    printf '  ok   %s\n' "$label"
  elif [ "$got" -eq 3 ]; then
    printf '  DRIFT %s\n' "$label"
    fail=1
  else
    printf '  ERROR %s (rc=%s) — the check itself is broken, NOT a drift finding\n' "$label" "$got"
    fail=1
  fi
}

# check_needs <source-path> <label> <expected> <cmd...>
#
# ABSENT IS NOT BROKEN AND IT IS NOT OK (2026-09-20). Some pinned sources are gitignored on
# purpose -- mined agent mail, for one -- so a genuinely fresh clone does not have them. Before
# this, `check` ran anyway, the command exited non-zero for want of a file, and the sweep printed
# "ERROR ... the check itself is broken", turning gates.sh RED for any stranger who followed the
# README's Quick start. The guard built to stop published counts from drifting was what failed a
# first-time reader.
#
# Three outcomes now, never two: ok / DRIFT / ERROR when the source is present, and SKIP when it
# is absent from THIS checkout. A SKIP is never counted as agreement -- it is printed, counted,
# and named in the summary line, because this repo's dominant defect is silence read as a result.
check_needs() {
  local src="$1"; shift
  # TEST SEAM: a fresh clone's condition is reproducible without moving a real mined artifact
  # around (a gate that mv's a 20KB export and dies mid-run would destroy it). Set
  # JEV_SWEEP_FORCE_ABSENT=1 to exercise the SKIP branch. Never consulted in normal operation.
  if [ ! -e "$src" ] || [ -n "${JEV_SWEEP_FORCE_ABSENT:-}" ]; then
    printf '  SKIP %s — source absent from this checkout (%s); gitignored by design, so a fresh clone cannot hold it. NOT counted as agreement.\n' "$1" "$src"
    skipped=$((skipped+1))
    return 0
  fi
  check "$@"
}

# check_floor <label> <floor> <cmd...>
#
# THE NAG CLASS, CAUGHT IN OUR OWN RUNNER (2026-09-20). This file's header says: "Do NOT add
# live-monotonic claims here — a moving target wired as an agree-check REDs forever (the nag
# class R46/R47 refused)." Two checks broke that rule: census-packages-21 and export-yes-19 count
# DIRECTORIES UNDER work/, which grows every time the lane ships a package. Proven in a fresh
# clone: create one work/omp-jev-zzprobe/src and the sweep prints DRIFT census-packages-21,
# DRIFT-FOUND, rc=1 -> stage 80 RED -> gates.sh RED for every reader. Eleven unpromoted packages
# already live under work/, so this was armed to fire on the next one.
#
# The honest shape for an append-only set is a FLOOR, not an equality. Packages are never
# deleted, so growth is the lane working and a DECREASE is the real defect — a package removed,
# renamed out of the glob, or stripped of its wiring. The floor catches that and ignores growth.
# The current value is always printed, so a drifting number is still visible; it just is not a
# failure. RETIRE the floor for a given claim when its set stops growing (then re-pin equality).
check_floor() {
  local label="$1" floor="$2"; shift 2
  local got; got=$("$@" 2>/dev/null | tr -d ' \n')
  case "$got" in
    ''|*[!0-9]*)
      printf '  ERROR %s — produced no number (%q); the check itself is broken, NOT a drift finding\n' "$label" "$got"
      fail=1; return 0 ;;
  esac
  if [ "$got" -ge "$floor" ]; then
    printf '  ok   %s (floor %s, now %s%s)\n' "$label" "$floor" "$got" \
      "$([ "$got" -gt "$floor" ] && echo ' — grew, which is not drift')"
  else
    printf '  DRIFT %s — FELL BELOW FLOOR: %s < %s. An append-only set shrank; something was removed or unwired.\n' "$label" "$got" "$floor"
    fail=1
  fi
}

check_needs work/cass-mail-mines/exports/cass-dig-rows.jsonl "locked-dig-138" 138 grep -c . work/cass-mail-mines/exports/cass-dig-rows.jsonl
check_floor "census-packages-21" 21 sh -c 'ls -d work/omp-jev-* work/omp-harm-rule 2>/dev/null | wc -l'
check "pinned-replay-55" 55 sh -c 'node work/jev-score-register/replay.mjs work/jev-score-register/fixtures/scores-pinned-20260920.jsonl | awk "/^rows/{print \$3}"'
check "pinned-replay-api0" 0 sh -c 'node work/jev-score-register/replay.mjs work/jev-score-register/fixtures/scores-pinned-20260920.jsonl | awk "/^api calls/{print \$5}"'
check "frozen-corpus-7846" 7846 sh -c 'wc -l < work/p3-calibration/toolcall-corpus-frozen.jsonl'
check "frozen-iserror-315" 315 grep -c '"isError": true' work/p3-calibration/toolcall-corpus-frozen.jsonl
check "backtest-29" 29 sh -c 'cd demos/routing-backtest && npm test 2>&1 | grep -c -E "^ok|ok [0-9]"'
check_floor "export-yes-19" 19 sh -c 'n=0; for d in work/omp-jev-* work/omp-harm-rule; do grep -rl -E "appendEntry|writeFileSync|appendFileSync|recording|register" "$d/src/" >/dev/null 2>&1 && grep -rl -E "askJev|systemOne|askJevChoice|jevClient" "$d/src/" >/dev/null 2>&1 && n=$((n+1)); done; echo $n'

# The verdict NAMES the skips. "ALL-AGREE" over a set with an absent source would be a lie of
# exactly the kind this sweep exists to catch, one level up from the counts it checks.
if [ "$fail" -ne 0 ]; then
  verdict="DRIFT-FOUND"
elif [ "$skipped" -gt 0 ]; then
  verdict="AGREE-WITH-$skipped-SKIPPED (sources absent from this checkout; NOT verified here)"
else
  verdict="ALL-AGREE"
fi
echo "scripts/denominator-sweep.sh: $verdict"
exit "$fail"
