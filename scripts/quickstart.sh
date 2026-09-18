#!/usr/bin/env bash
# quickstart — everything an outside reader can run, in one command, from a fresh clone.
#
# WHY THIS EXISTS. `scripts/verify-frozen.sh` proved the published `ALL GREEN` is NOT reproducible
# from a clone: two of ten foundation stages need local state a clone does not carry (`npm install`
# in compaction/, a `br import`). That is honest about the gate suite, but it left an outside reader
# with no command at all — they would clone this repo, find ten stages, run them, get exit 1, and
# reasonably conclude the repo is broken.
#
# It is not broken. Every DEMO here is zero-dependency: all three run on `node --test` with no
# install step, no network, no API key, and no lane state. Nobody had written that down, so the
# fastest true thing a stranger could do with this repo was invisible.
#
# This script is deliberately NOT a gate and NOT wired to foundation. It has one consumer — a human
# who just cloned the repo — and it makes no claim about lane state, verdicts, or receipts.
#
# Usage:  ./scripts/quickstart.sh          run everything a clone can run
#         ./scripts/quickstart.sh --list   print what it would run, and exit
set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

# name<TAB>dir<TAB>command<TAB>what a reader learns from it
units=$(cat <<'UNITS'
routing-backtest	demos/routing-backtest	npm test --silent	does a cheap-model router actually save money on recorded traffic
routing-mutations	demos/routing-backtest	npm run mutate --silent	whether that demo's tests can still fail — seven planted mutations
usage-shape	demos/usage-shape	npm test --silent	how much of a coding agent's context is retransmitted each turn
retransmit-whatif	demos/retransmit-whatif	npm test --silent	what a retransmission cap would have cost, per turn
probe-replay	.	node scripts/jev-probe.mjs --replay docs/demos/jev-probe/probe-response-20260918.json	one recorded Jev judgment, decoded offline with no key
UNITS
)

if [[ "${1:-}" == "--list" ]]; then
  printf '%s\n' "$units" | while IFS=$'\t' read -r name dir cmd why; do
    printf '  %-20s %s\n                       %s\n' "$name" "$cmd" "$why"
  done
  exit 0
fi

node_v="$(node --version 2>/dev/null || echo MISSING)"
if [[ "$node_v" == MISSING ]]; then
  echo "quickstart: node is not on PATH. Everything here needs node >= 20 and nothing else."
  exit 2
fi

echo "quickstart — node $node_v, no install step, no network, no API key"
echo

pass=0 fail=0 failed_names=""
while IFS=$'\t' read -r name dir cmd why; do
  printf '=== %s\n    %s\n' "$name" "$why"
  if ( cd "$dir" && eval "$cmd" ) >/tmp/qs-$$.log 2>&1; then
    # Surface the counts the suite itself printed, rather than restating them.
    grep -E '^# (tests|pass|fail)|mutations (caught|escaped)|MUTATION|verdict' /tmp/qs-$$.log \
      | head -4 | sed 's/^/    /'
    printf '    PASS\n\n'
    pass=$((pass+1))
  else
    tail -6 /tmp/qs-$$.log | sed 's/^/    /'
    printf '    FAIL\n\n'
    fail=$((fail+1)); failed_names="$failed_names $name"
  fi
  rm -f /tmp/qs-$$.log
done <<< "$units"

echo "quickstart: $pass passed, $fail failed"
if (( fail > 0 )); then
  echo "failed:$failed_names"
  echo
  echo "These run from committed bytes with no setup, so a failure here is a real defect in this"
  echo "repo and not a missing dependency on your machine. Please open an issue with this output."
  exit 1
fi
echo
echo "Next, if you want the lane's actual product rather than its demos:"
echo "  docs/demos/STATUS.tsv   17 adjudicated candidates, 0 promoted, with a receipt for each"
echo "  NEGATIVE_EVIDENCE.md    what was ruled out and what would reopen it"
echo "  README.md               why a gauntlet's honest headline is zero promotions"
exit 0
