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
# Claims and their regeneration commands (see denominator-audit-20260920.md):
#   138 locked dig questions — grep -c over the locked export
#   21  census packages — ls -d piped to wc -l (never `wc -l file`)
#   55  pinned replay rows — replay.mjs over the pinned fixture + awk field
#   0   pinned replay api calls — same run, value field
#   7846 frozen corpus rows — wc -l over stdin redirect
#   315 frozen isError — python count over the frozen file
#   29  routing-backtest tests — npm test TAP summary
#   19  export-YES packages — per-dir model+persist grep rule (export-resweep receipt)
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
P="$root/scripts/pinned-denominator.sh"
fail=0

check() { # check <label> <expected> <cmd...>
  local label="$1" expected="$2"; shift 2
  if "$P" "$expected" "$@" >/dev/null 2>&1; then
    printf '  ok   %s\n' "$label"
  else
    printf '  DRIFT %s (rc=%s)\n' "$label" "$?"
    fail=1
  fi
}

check "locked-dig-138" 138 grep -c . work/cass-mail-mines/exports/cass-dig-rows.jsonl
check "census-packages-21" 21 sh -c 'ls -d work/omp-jev-* work/omp-harm-rule | wc -l'
check "pinned-replay-55" 55 sh -c 'node work/jev-score-register/replay.mjs work/jev-score-register/fixtures/scores-pinned-20260920.jsonl | awk "/^rows/{print \$3}"'
check "pinned-replay-api0" 0 sh -c 'node work/jev-score-register/replay.mjs work/jev-score-register/fixtures/scores-pinned-20260920.jsonl | awk "/^api calls/{print \$5}"'
check "frozen-corpus-7846" 7846 sh -c 'wc -l < work/p3-calibration/toolcall-corpus-frozen.jsonl'
check "frozen-iserror-315" 315 grep -c '"isError": true' work/p3-calibration/toolcall-corpus-frozen.jsonl
check "backtest-29" 29 sh -c 'cd demos/routing-backtest && npm test 2>&1 | grep -c -E "^ok|ok [0-9]"'
check "export-yes-19" 19 sh -c 'n=0; for d in work/omp-jev-* work/omp-harm-rule; do grep -rl -E "appendEntry|writeFileSync|appendFileSync|recording|register" "$d/src/" >/dev/null 2>&1 && grep -rl -E "askJev|systemOne|askJevChoice|jevClient" "$d/src/" >/dev/null 2>&1 && n=$((n+1)); done; echo $n'

echo "scripts/denominator-sweep.sh: $([ "$fail" -eq 0 ] && echo ALL-AGREE || echo DRIFT-FOUND)"
exit "$fail"
