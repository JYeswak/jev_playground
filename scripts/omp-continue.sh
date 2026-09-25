#!/bin/sh
# Loop gate for omp `/loop --while`. Adapted from omp-kit (1).zip.
# The zip looks for scripts/check-claim-discipline.sh with no args. That file
# is absent here. A missing-file check that only skips would drop the honesty
# gate. This copy calls foundation/kit/check-claim-discipline.sh with the
# three arguments that checker requires, and stops if the checker is absent.
#
# omp 18.2.10: exit 0 = next iteration, exit 1 = stop cleanly, exit >1 = broken.
set -u
MAX="${KIT_LOOP_MAX:-40}"
STALL="${KIT_LOOP_STALL:-3}"
STATE="${KIT_LOOP_STATE:-.omp/loop-state}"
say() { printf 'omp-continue: %s\n' "$*"; }

top=$(git rev-parse --show-toplevel 2>/dev/null) || { say "not a git repo"; exit 2; }
cd "$top" || exit 2
mkdir -p "$(dirname "$STATE")"

if [ -e .omp/STOP ]; then say "found .omp/STOP; stopping"; exit 1; fi

if command -v br >/dev/null 2>&1; then
  br_err=$(mktemp)
  br_out=$(br ready --json 2>"$br_err")
  br_rc=$?
  if [ "$br_rc" -ne 0 ]; then
    say "br ready failed exit $br_rc: $(tr '\n' ' ' < "$br_err") $(printf '%s' "$br_out" | tr '\n' ' ')"
    rm -f "$br_err"
    exit 2
  fi
  rm -f "$br_err"
  ready=$(printf '%s' "$br_out" | grep -o '"id"[[:space:]]*:' | wc -l | tr -d ' ')
  src="br ready"
elif [ -f .beads/issues.jsonl ]; then
  ready=$(grep -Ec '"status"[[:space:]]*:[[:space:]]*"(open|in_progress)"' .beads/issues.jsonl)
  src=".beads/issues.jsonl (open/in_progress; deps not evaluated)"
else
  say "no tracker (.beads/issues.jsonl or br) found"; exit 2
fi
if [ "${ready:-0}" -eq 0 ]; then say "no ready work in $src; stopping"; exit 1; fi

checker=foundation/kit/check-claim-discipline.sh
if [ ! -f "$checker" ]; then
  say "claim checker missing: $checker"; exit 2
fi
if ! sh "$checker" foundation/kit/claims.tsv docs/LEDGER.md "$top" >/dev/null 2>&1; then
  say "claim-discipline gate is RED; stopping so it gets fixed, not routed around"; exit 1
fi

head=$(git rev-parse HEAD 2>/dev/null || echo none)
iter=0; last=""; still=0
[ -f "$STATE" ] && . "$STATE"
iter=$((iter + 1))
if [ "$head" = "$last" ]; then still=$((still + 1)); else still=0; fi
printf 'iter=%s\nlast=%s\nstill=%s\n' "$iter" "$head" "$still" > "$STATE"
if [ "$iter" -gt "$MAX" ]; then say "iteration cap $MAX reached; stopping"; exit 1; fi
if [ "$still" -ge "$STALL" ]; then
  say "no new commit in $STALL iterations; stopping instead of pumping"; exit 1
fi

say "continue: $ready ready in $src; iteration $iter/$MAX; commit $head"
exit 0
