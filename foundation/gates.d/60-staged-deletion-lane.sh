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
# Exit: 0 proven · 1 a witness failed · 3 the hook files are missing (instrument error) · 8 SKIP,
# deletion lane proven but loop-kit absent, only under gates.sh --portable.

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
        printf 'x = 0\n' > own.py
        printf 'y = 0\n' > sibling.py
        git add -A
        git -c core.hooksPath=/dev/null commit -q -m 'base' --no-verify
    )
}

run_commit() { # run_commit <args...> ; echoes combined output, returns git's code
    (cd "$work/r" && git commit -m 'probe' "$@" 2>&1)
}

export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
# PORTABLE (jev-fmy): without loop-kit (foundry, private) the wrapper refuses every commit unless
# JEV_ALLOW_MISSING_AUTOFIX=1, the hook authors' own escape (CI sets it for the same reason,
# .github/workflows/gates.yml). Under `gates.sh --portable` this stage sets it, so the deletion lane
# still runs its trigger and five healthy witnesses for real; only the autofix lane is skipped, and
# the verdict says so with exit 8. Default mode never sets it: a missing loop-kit stays RED.
autofix_skip=""
if [ -n "${JEV_GATES_PORTABLE:-}" ] && [ ! -x "${LOOP_KIT:-$HOME/Developer/foundry/loop-kit}/autofix-precommit.sh" ]; then
    export JEV_ALLOW_MISSING_AUTOFIX=1
    autofix_skip=1
fi

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

# ---------------------------------------------------------------- lane 2: autofix (report-only)
# The wrapper runs loop-kit/autofix-precommit.sh --check --staged after the deletion lane. It must
# refuse an unclean staged set and stay silent on a clean one — and it must NEVER mutate, because
# the fixer does not re-stage and a mid-commit rewrite would land the unfixed bytes.
if [ -x "${LOOP_KIT:-$HOME/Developer/foundry/loop-kit}/autofix-precommit.sh" ]; then
    new_fixture
    (cd "$work/r" && printf 'trailing   \n' > dirty.txt && git add dirty.txt)
    before="$(cd "$work/r" && shasum -a 256 dirty.txt | cut -d' ' -f1)"
    out="$(run_commit)"; code=$?
    after="$(cd "$work/r" && shasum -a 256 dirty.txt | cut -d' ' -f1)"
    if [ "$code" -eq 0 ]; then
        fail "autofix trigger: unclean staged set" "commit SUCCEEDED — the autofix lane did not fire"
    elif ! printf '%s' "$out" | grep -q 'AUTOFIX_REFUSED'; then
        fail "autofix trigger: refusal not named" "$(printf '%s' "$out" | tail -2)"
    elif [ "$before" != "$after" ]; then
        fail "autofix trigger: hook MUTATED the file" "sha $before -> $after; --check must never write"
    else
        pass "autofix trigger: refused an unclean staged set, and did not mutate it"
    fi

    # A path-limited commit's temporary index excludes a sibling's independently staged file.
    # The printed fix instructions must stay scoped to that temporary index too.
    new_fixture
    (
        cd "$work/r" || exit 1
        printf 'x = 1   \n' > own.py
        printf 'y = 1   \n' > sibling.py
        git add sibling.py
    )
    out="$(run_commit --only -- own.py)"; code=$?
    if [ "$code" -eq 0 ] || ! printf '%s' "$out" | grep -q 'AUTOFIX_REFUSED'; then
        fail "autofix trigger: path-limited remedy" "unclean own.py did not cause AUTOFIX_REFUSED (rc=$code): $out"
    elif ! printf '%s\n' "$out" | grep -Eq 'autofix-precommit\.sh --repo .* -- own\.py$' \
      || ! printf '%s\n' "$out" | grep -Eq 'git add -- own\.py$' \
      || printf '%s' "$out" | grep -q 'sibling.py' \
      || printf '%s' "$out" | grep -q -- '--staged'; then
        fail "autofix trigger: path-limited remedy" "expected own.py only, without --staged: $out"
    else
        pass "autofix trigger: remedy names own.py, not staged sibling.py or --staged"
    fi

    new_fixture
    (cd "$work/r" && printf 'clean\n' > tidy.txt && git add tidy.txt)
    out="$(run_commit)"; code=$?
    if [ "$code" -eq 0 ]; then pass "autofix satisfying: clean staged set commits"
    else fail "autofix satisfying: clean staged set" "$(printf '%s' "$out" | tail -2)"; fi
else
    echo "  witness SKIP  autofix lane (loop-kit absent) — lane reports AUTOFIX_LANE_SKIPPED, not a pass"
fi

# ---------------------------------------------------------------- verdict
if [ "$fails" -eq 0 ] && [ -n "$autofix_skip" ]; then
    echo "60-staged-deletion-lane: deletion lane proven — 1 trigger + 5 satisfying witnesses; autofix lane not run"
    echo "SKIP (missing prerequisite: loop-kit autofix-precommit.sh, install: foundry is private (JYeswak/foundry); with access, clone it and set LOOP_KIT=<clone>/loop-kit)"
    exit 8
fi
if [ "$fails" -eq 0 ]; then
    echo "60-staged-deletion-lane: pre-commit wrapper proven — 3 triggers + 6 satisfying witnesses"
    exit 0
fi
echo "60-staged-deletion-lane: $fails witness(es) failed" >&2
exit 1
