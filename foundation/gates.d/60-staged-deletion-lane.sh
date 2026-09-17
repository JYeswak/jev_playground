#!/usr/bin/env bash
# 60-staged-deletion-lane: the causal proof for githooks/pre-commit +
# githooks/pre-commit-staged-deletion-survives.sh.
#
# WHAT THE LANE PROTECTS. Git hands a pre-commit hook the PROSPECTIVE index in GIT_INDEX_FILE.
# A path-limited commit (`git commit -- some/path`) rebuilds that prospective index from the
# working tree, which can silently DROP a staged deletion that is still in the real index. The
# commit then looks green while the deletion never happened — or worse, a file another agent
# still has on disk is recorded as deleted. In a worktree three agents share, that is RULE 1
# ("never delete a file without permission") failing mechanically rather than by intent.
#
# WHY THIS FILE EXISTS SEPARATELY FROM THE HOOK. The stamp manifest is explicit that the
# implementation is house-owned and "the target repo's causal selftest is the proof surface".
# The hook is copied byte-identical from foundry (sha 934d4cc0d843 / 17f7abceac05); the PROOF
# that it fires here, and that it stays silent on healthy commits, is ours.
#
# BOTH DIRECTIONS, which is the whole point:
#   trigger witness    — a staged deletion whose file is still on disk, dropped by a
#                        path-limited commit => REFUSED, and the refusal names the path.
#   satisfying witness — five healthy commit shapes => exit 0, hook emits nothing.
# A check with a trigger and no satisfying witness is a permanent blocker wearing a gate's
# clothes (registry-check pattern).
#
# HERMETIC. GIT_CONFIG_GLOBAL/SYSTEM are neutralized: this machine sets
# init.templateDir=~/.git-templates, which installs the commit-msg verification-level hook into
# every new repo and would refuse this fixture's plain commit subjects at fixture-setup time.
# Measured 2026-09-17 — the same trap that broke commit-evidence-lint.sh --selftest.
#
# Exit: 0 proven · 1 a witness failed · 3 the hook files are missing (instrument error).

set -uo pipefail

LANE_DIR="$(cd -- "$(dirname -- "$0")/../../githooks" && pwd)"
WRAPPER="$LANE_DIR/pre-commit"
IMPL="$LANE_DIR/pre-commit-staged-deletion-survives.sh"

for f in "$WRAPPER" "$IMPL"; do
    [ -x "$f" ] || { echo "ERROR: $f missing or not executable" >&2; exit 3; }
done
bash -n "$WRAPPER" || exit 3
bash -n "$IMPL" || exit 3

work="$(mktemp -d)"
trap 'rm -rf -- "$work"' EXIT
fails=0
pass() { echo "  witness PASS  $1"; }
fail() { echo "  witness FAIL  $1: $2"; fails=$((fails + 1)); }

# The fixture must exercise ONLY the lane under test. jev's githooks/ also carries the
# commit-msg verification-level hook, and pointing core.hooksPath at it made all five healthy
# witnesses fail on subject formatting — a refusal from a DIFFERENT hook reads exactly like the
# lane misfiring. So: a scratch hooks dir holding just the pre-commit pair.
HOOKDIR="$work/hooks"
mkdir -p "$HOOKDIR"
cp -p "$WRAPPER" "$IMPL" "$HOOKDIR/"
chmod +x "$HOOKDIR/pre-commit" "$HOOKDIR/pre-commit-staged-deletion-survives.sh"

new_fixture() {
    rm -rf -- "$work/r"
    mkdir -p "$work/r"
    (
        cd "$work/r" || exit 1
        git init -q -b main
        git config user.email t@example.com
        git config user.name t
        git config core.hooksPath "$HOOKDIR"
        printf 'keep\n' > keep.txt
        printf 'doomed\n' > doomed.txt
        printf 'other\n' > other.txt
        git add -A
        git -c core.hooksPath=/dev/null commit -q -m 'base' --no-verify
    )
}

run_commit() { # run_commit <args...> ; echoes combined output, returns git's code
    (cd "$work/r" && git commit -m 'probe' "$@" 2>&1)
}

export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null

# ---------------------------------------------------------------- trigger witness
new_fixture
(
    cd "$work/r" || exit 1
    git rm -q --cached doomed.txt          # staged deletion; doomed.txt is STILL on disk
    printf 'touched\n' >> other.txt
    git add other.txt
)
out="$(run_commit -- other.txt)"; code=$?
if [ "$code" -eq 0 ]; then
    fail "trigger: path-limited commit dropped a staged deletion" "commit SUCCEEDED (exit 0) — the lane did not fire"
elif printf '%s' "$out" | grep -q 'doomed.txt'; then
    pass "trigger: refused and named the dropped path (doomed.txt)"
else
    fail "trigger: refusal does not name the path" "$(printf '%s' "$out" | tail -2)"
fi

# ---------------------------------------------------------------- satisfying witnesses
new_fixture
(cd "$work/r" && printf 'edit\n' >> keep.txt && git add keep.txt)
out="$(run_commit)"; code=$?
if [ "$code" -eq 0 ]; then pass "healthy 1: plain modification commit"
else fail "healthy 1: plain modification commit" "$(printf '%s' "$out" | tail -2)"; fi

new_fixture
(cd "$work/r" && git rm -q doomed.txt)     # genuine deletion: gone from index AND disk
out="$(run_commit)"; code=$?
if [ "$code" -eq 0 ]; then pass "healthy 2: genuine deletion (file removed from disk too)"
else fail "healthy 2: genuine deletion" "$(printf '%s' "$out" | tail -2)"; fi

new_fixture
(cd "$work/r" && printf 'edit\n' >> other.txt && git add other.txt)
out="$(run_commit -- other.txt)"; code=$?
if [ "$code" -eq 0 ]; then pass "healthy 3: path-limited commit with no staged deletion"
else fail "healthy 3: path-limited commit" "$(printf '%s' "$out" | tail -2)"; fi

new_fixture
(cd "$work/r" && printf 'fresh\n' > added.txt && git add added.txt)
out="$(run_commit)"; code=$?
if [ "$code" -eq 0 ]; then pass "healthy 4: new-file commit"
else fail "healthy 4: new-file commit" "$(printf '%s' "$out" | tail -2)"; fi

new_fixture
(cd "$work/r" && printf 'edit\n' >> keep.txt && git add keep.txt && git commit -q -m 'pre-amend')
out="$(cd "$work/r" && git commit -q --amend -m 'amended' 2>&1)"; code=$?
if [ "$code" -eq 0 ]; then pass "healthy 5: amend"
else fail "healthy 5: amend" "$(printf '%s' "$out" | tail -2)"; fi

# ---------------------------------------------------------------- verdict
if [ "$fails" -eq 0 ]; then
    echo "60-staged-deletion-lane: 1 trigger + 5 satisfying witnesses proven"
    exit 0
fi
echo "60-staged-deletion-lane: $fails witness(es) failed" >&2
exit 1
