#!/usr/bin/env bash
# 70-tests-registry-sync: every tracked test file is named in TESTS.md, and TESTS.md names no
# path that no longer exists.
#
# WHY. TESTS.md exists because an un-enumerated test surface is a coverage claim nobody can check.
# But a hand-written enumeration goes stale the moment a sibling pane lands a new suite — measured
# 2026-09-17: TESTS.md listed 2 files, a sibling added compaction/test/hook-compact.test.ts, and
# p4-tests-registry flipped back to FAIL within the hour. A registry nobody checks is worse than
# no registry: it reads authoritative while being wrong.
#
# So the doc becomes a checked artifact. This gate is the consumer that makes it stay true.
#
# --selftest plants a fake tracked test path that TESTS.md cannot name and requires RED, then
# proves the healthy tree passes — both directions.
#
# Exit: 0 in sync · 1 drift (a file unnamed, or a named path gone) · 3 not a git repo / TESTS.md
# absent (instrument error, never a content pass).

set -uo pipefail

REPO="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
REG="$REPO/TESTS.md"

[ -f "$REG" ] || { echo "ERROR: $REG absent — nothing to keep in sync" >&2; exit 3; }
git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 || { echo "ERROR: $REPO is not a git repo" >&2; exit 3; }

# The test-file shape this lane recognizes. Vendored clones are gitignored, so `git ls-files`
# already scopes this to first-party code — that is the whole reason it can be exhaustive.
list_tracked() {
    git -C "$REPO" ls-files \
      | grep -iE '(^|/)(test|tests)/|\.test\.[tj]s$|\.spec\.[tj]s$|_test\.py$|test_.*\.py$|probe.*\.mts$' \
      | sort
}

check() { # check <registry-file>
    local reg="$1" missing=0 stale=0 tracked
    tracked="$(list_tracked)"
    [ -n "$tracked" ] || { echo "ERROR: zero tracked test files matched — an empty scan set is not a pass" >&2; return 3; }

    while IFS= read -r f; do
        [ -n "$f" ] || continue
        if ! grep -Fq -- "$f" "$reg"; then
            echo "  DRIFT  tracked but not named in TESTS.md: $f"
            missing=$((missing + 1))
        fi
    done <<< "$tracked"

    # The reverse direction: a path named in the registry that no longer exists.
    while IFS= read -r f; do
        [ -n "$f" ] || continue
        [ -e "$REPO/$f" ] || { echo "  DRIFT  named in TESTS.md but absent from the tree: $f"; stale=$((stale + 1)); }
    done <<< "$(grep -oE '[A-Za-z0-9_./-]+\.(test|spec)\.[tj]s|[A-Za-z0-9_./-]*probe[A-Za-z0-9_./-]*\.mts' "$reg" | sort -u)"

    if [ "$missing" -eq 0 ] && [ "$stale" -eq 0 ]; then
        echo "70-tests-registry-sync: $(printf '%s\n' "$tracked" | grep -c .) tracked test file(s), all enumerated"
        return 0
    fi
    echo "70-tests-registry-sync: $missing unnamed, $stale stale" >&2
    return 1
}

if [ "${1:-}" = "--selftest" ]; then
    tmp="$(mktemp)"
    trap 'rm -f -- "$tmp"' EXIT
    # KNOWN-BAD: a registry with one real path removed must go RED.
    grep -v 'probes/fast-jev-probe.mts' "$REG" > "$tmp"
    if check "$tmp" >/dev/null 2>&1; then
        echo "SELFTEST FAIL: a registry missing a tracked test file passed" >&2
        exit 1
    fi
    echo "  selftest PASS  known-bad (registry with a path removed) went RED"
    # KNOWN-GOOD: the real registry must pass.
    if ! check "$REG" >/dev/null 2>&1; then
        echo "SELFTEST FAIL: the real registry does not pass — fix TESTS.md, not this gate" >&2
        exit 1
    fi
    echo "  selftest PASS  known-good (the committed registry) passed"
    echo "70-tests-registry-sync: both directions proven"
    exit 0
fi

check "$REG"
