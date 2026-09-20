#!/usr/bin/env bash
# pin-liveness — refuse a pinned digest that points at a file peers are still appending to.
#
# CREATION GATE, answered:
#   1. CONSUMER  — scripts/lane-status.sh's integrity check, and anyone adding a STATUS.tsv row.
#                  Wired via scripts/selftest-pin-liveness.sh, which foundation/gates.d/80
#                  auto-discovers by glob. No new stage.
#   2. GATE      — no STATUS.tsv row may pin a content digest to a file that is being appended to
#                  concurrently. Such a row is guaranteed to drift, so its integrity check is
#                  noise rather than signal.
#   3. DEFECT    — OBSERVED 3 times, the last one fatal to the lane:
#                    * 2026-09-20 lane-status exited 4, "1 of 33 integrity-checked receipts
#                      drifted": UP-R16 pinned to NEGATIVE_EVIDENCE.md, a peer appended R46,
#                      digest drifted within the hour.
#                    * twice earlier the same day a digest pinned to the wave ledger drifted
#                      between two runs of the same command.
#                  The conductor WROTE the rule against this ("a pinned digest cannot point at a
#                  live shared file") in the commit that created the offending row. Prose did not
#                  stop it. That is the whole argument for this file existing.
#   4. RETIREMENT — when receipts are immutable by construction (write-once, content-addressed
#                  paths). Then liveness is impossible and this check is dead weight.
#
# THRESHOLD, and why it is not 1. Measured on this repo today: at >=3 commits/24h the rule flags
# 3 files, two of which are ordinary receipts that got a couple of legitimate corrections --
# firing on those would make it a gate that fires on everything, which this lane refuses. At >=10
# it flags exactly the one pathological file (NEGATIVE_EVIDENCE.md, 32 commits in 24h). The
# threshold is the discriminating choice, not a round number, and it is overridable.
#
# Usage:
#   scripts/pin-liveness.sh [STATUS_TSV] [THRESHOLD]     # positional, like the other lane tools
#   exit 0 = no row pins to a hot file · 3 = at least one does · 2 = usage/IO error
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1

STATUS="${1:-docs/demos/STATUS.tsv}"
THRESH="${2:-10}"

[ -f "$STATUS" ] || { echo "pin-liveness: no such STATUS file: $STATUS" >&2; exit 2; }
[[ "$THRESH" =~ ^[0-9]+$ ]] || { echo "pin-liveness: threshold '$THRESH' is not a number" >&2; exit 2; }

rows=0; flagged=0
while IFS=$'\t' read -r cand _rung _score _verdict _author receipt _blocked _concur digest _rest; do
  [ -z "${cand:-}" ] && continue
  case "$cand" in \#*) continue ;; candidate|Candidate) continue ;; esac
  [ -z "${receipt:-}" ] && continue
  [ -z "${digest:-}" ] && continue          # unpinned rows are out of scope by design
  rows=$((rows + 1))
  n=$(git log --since=24.hours --oneline -- "$receipt" 2>/dev/null | grep -c . || true)
  if [ "${n:-0}" -ge "$THRESH" ]; then
    flagged=$((flagged + 1))
    echo "  HOT  $cand pins a digest to $receipt ($n commits in 24h, threshold $THRESH)"
    echo "       That digest will drift on the next peer append. Extract a stable per-section"
    echo "       receipt and pin to that; re-pinning the same path only resets the clock."
  fi
done < "$STATUS"

if [ "$rows" -eq 0 ]; then
  echo "pin-liveness: no pinned rows found in $STATUS — an empty scan set is NOT a pass" >&2
  exit 2
fi

if [ "$flagged" -gt 0 ]; then
  echo "pin-liveness: $flagged of $rows pinned row(s) point at a live file"
  exit 3
fi
echo "pin-liveness: $rows pinned row(s), none pointing at a file with >=$THRESH commits in 24h"
exit 0
