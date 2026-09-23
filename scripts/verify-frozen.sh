#!/usr/bin/env bash
# Run the suites against a FROZEN CLONE of committed bytes, never the live worktree.
#
# ADOPTED FROM THE MENTOR under AGENTS.md RULE 12, smallest honest form. Jeffrey Emanuel closes beads
# in Dicklesworthstone/skillranker with evidence of this exact shape:
#
#   "The tree is 771a219 plus nine paths. The committed bytes were checked with cmp against the
#    tested clone." ... "All through RCH, remote only ... from a private clone under /data/projects"
#   -- sr-roadmap-l1i.5.4 close evidence
#
# We had no equivalent. Every "npm test 21/21" and "gates rc=0" claimed today was measured in a
# worktree that two other panes were editing concurrently, which is not a claim about anything
# durable.
#
# THE OBSERVED DEFECT CLASS, not speculative, all measured 2026-09-18 in this repo:
#   - a non-author pane graded demos/retransmit-whatif against a HOT worktree, saw two different code
#     versions across two runs, and by its own words "nearly filed a false defect";
#   - a shared-reader edit broke demos/routing-backtest test 17 while uncommitted;
#   - an uncommitted edit left demos/usage-shape/bin/shape.mjs throwing a SyntaxError while HEAD was
#     clean, so the live tree and the published tree disagreed about whether the tool ran at all;
#   - the conductor reported a corpus crash that a peer could not reproduce, because a fix had landed
#     between the two runs.
# Every one of those is the same defect: a verdict about bytes nobody pinned.
#
# CONSUMER: any agent about to claim a verification level above [pending] on this repo.
# GATE: a [test]/[mutation]/[live] claim in a commit subject. Run this first, cite its output.
# RETIREMENT: delete this when CI runs the same suites on every push, which is the strictly better
#   version of the same idea. Until then the only frozen runner we have is this one.
#
# NOT WIRED INTO foundation/gates.sh ON PURPOSE. It clones and runs npm; a gate stage must be fast
# and hermetic, and pane 2 has already ruled once that promotion needs a wrapper, not direct wiring.
set -euo pipefail

repo=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
ref=${1:-HEAD}
sha=$(git -C "$repo" rev-parse --short "$ref")

# A frozen clone is worthless if the thing you are about to claim is not committed. Say so loudly
# rather than producing a green result about bytes that are not the ones in your editor.
dirty=$(git -C "$repo" status --porcelain | wc -l | tr -d ' ')
if [ "$dirty" -ne 0 ]; then
    echo "NOTE  worktree has $dirty modified/untracked path(s). This run tests COMMITTED bytes at"
    echo "      $sha, NOT what is in your editor. That is the point, but know which you claimed."
fi

tmp=$(mktemp -d)
# A throwaway clone, not `git worktree add`: jev keeps exactly one worktree (Joshua, 2026-09-23:
# "strict no branch / worktree policy"). The worktree this script used to register was removed only
# on the success path, so every interrupted run left a stale entry in `git worktree list`. The trap
# removes the clone on any exit.
trap 'rm -rf "$tmp"' EXIT
git clone --quiet --local --no-checkout "$repo" "$tmp/frozen"
git -C "$tmp/frozen" checkout --quiet --detach "$sha"
cd "$tmp/frozen"
# The Beads database is gitignored, so a fresh copy has none, and foundation/gates.sh refuses to run
# without one. Build it from the committed JSONL, the fix gates.sh itself prescribes for fresh clones.
if ! br sync --import-only >/dev/null 2>&1; then
    echo "NOTE  br sync --import-only failed in the frozen clone; foundation/gates.sh will say why"
fi

echo "FROZEN CLONE of $sha at $tmp/frozen"
echo

rc=0
run() {
    local name=$1; shift
    local out
    if out=$("$@" 2>&1); then
        echo "PASS  $name"
    else
        echo "FAIL  $name"
        printf '%s\n' "$out" | tail -12 | sed 's/^/      /'
        rc=1
    fi
}

run "foundation/gates.sh" bash foundation/gates.sh
for d in demos/routing-backtest demos/usage-shape demos/retransmit-whatif; do
    if [ -f "$d/package.json" ]; then
        # A demo with no test script is reported as such, never silently skipped as if it passed —
        # the empty-scan-set lie this lane already recorded in NEGATIVE_EVIDENCE R6.
        if grep -q '"test"' "$d/package.json"; then
            run "$d npm test" npm --prefix "$d" test
        else
            echo "UNTESTED  $d has no test script (reported, not skipped)"
        fi
        if grep -q '"mutate"' "$d/package.json"; then
            run "$d npm run mutate" npm --prefix "$d" run mutate
        fi
    fi
done
run "scripts/jev-probe.mjs --replay" node scripts/jev-probe.mjs --replay

echo
# cmp the executable bytes, his check: prove the clone is the commit, not a stale copy.
differs=0
while IFS= read -r f; do
    cmp -s "$repo/$f" "$tmp/frozen/$f" || differs=$((differs + 1))
done < <(git -C "$repo" ls-files 'demos/**/*.mjs' 'scripts/*.sh' 'scripts/*.mjs')
echo "cmp live-vs-frozen over tracked executables: $differs differ (nonzero is expected on a dirty tree)"

cd "$repo"

if [ "$rc" -ne 0 ]; then
    echo "FROZEN VERIFY FAILED at $sha — do not claim a verification level above [pending]."
else
    echo "FROZEN VERIFY GREEN at $sha — committed bytes, not worktree bytes."
fi
exit "$rc"
