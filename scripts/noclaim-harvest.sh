#!/bin/sh
# noclaim-harvest.sh — the lane's own exhaust, read back as a work frontier.
#
# WHY THIS EXISTS. On 2026-09-19 `br ready` hit EMPTY TWICE IN NINETY MINUTES: four beads filed at
# 02:10 were claimed and closed by 03:40, and the panes starved while the conductor slept between
# ticks. In the same window the lane wrote SIXTEEN `NO-CLAIM:` lines into commit messages and
# converted ZERO of them into beads. Every one is already a bounded, authored, evidence-anchored
# open question — the best commit of that night (88fd55b, recipe 4 promoted from mechanism to
# tested predictor) came from re-reading one by hand.
#
# CREATION GATE (tick.md §1), all four named:
#   1. CONSUMER — any pane running `br ready`, and the conductor's dry-queue branch.
#   2. GATE — a QUEUE DRY callback is WRONG while this prints rows. Dry means the lane has no
#      open questions, not that someone closed the last bead.
#   3. OBSERVED DEFECT — 16 produced / 0 harvested, frontier starved twice in one night.
#   4. RETIREMENT — when two consecutive harvests produce beads no pane claims, delete this.
#
# It creates NOTHING. It prints candidates and a human or conductor decides. A generator that filed
# beads automatically would manufacture work to look busy, which is the failure this lane audits
# itself for.
#
# Usage: scripts/noclaim-harvest.sh [since]        default: the last 24 hours
set -eu
since=${1:-"24 hours ago"}
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$root"

# Beads carry their source sha in the description when harvested, so a converted NO-CLAIM is
# recognisable without a side ledger that could drift from the bead store.
harvested=$(br list --json 2>/dev/null | grep -oE 'harvested-from:[0-9a-f]{7}' | sort -u || true)

printf 'UNHARVESTED NO-CLAIM lines since %s\n\n' "$since"
found=0
for sha in $(git log --format='%h' --since="$since" --no-merges); do
    case "$harvested" in *"harvested-from:$sha"*) continue ;; esac
    # One commit can carry a multi-line NO-CLAIM paragraph; take it to the blank line.
    body=$(git log -1 --format='%B' "$sha" | awk '/^NO-CLAIM/{f=1} f{print} /^$/{if(f)exit}')
    [ -n "$body" ] || continue
    found=$((found + 1))
    printf '%s  %s\n' "$sha" "$(git log -1 --format='%s' "$sha" | cut -c1-64)"
    printf '%s\n\n' "$(printf '%s' "$body" | fold -s -w 96 | sed 's/^/    /')"
done

if [ "$found" -eq 0 ]; then
    echo 'none — every NO-CLAIM in the window is harvested or the window is empty.'
    echo 'QUEUE DRY is defensible on this axis.'
else
    printf '%s unharvested. A QUEUE DRY callback is WRONG while this is non-zero.\n' "$found"
    echo 'Harvest by filing a bead whose description contains: harvested-from:<sha>'
fi
