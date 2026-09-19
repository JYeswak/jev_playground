#!/usr/bin/env bash
# bootstrap-compaction.sh — make stage 40 runnable from a fresh clone.
#
# A stranger clone of this repo does not carry compaction/node_modules (gitignored)
# or the fast-jev-compaction sibling (not on the allowlist). `npm install --prefix
# compaction` alone is NOT enough: package.json depends on file:../fast-jev-compaction,
# so npm creates a dangling symlink and `tsc` still fails
# (NEGATIVE_EVIDENCE.md R32). This script fetches the pinned sibling, builds it
# (dist/ is not in git), then npm-installs compaction/.
#
# Usage:
#   ./scripts/bootstrap-compaction.sh           # install if missing
#   ./scripts/bootstrap-compaction.sh --check   # exit 0 if ready, 1 if not
#
# Does not commit anything. Does not register OMP hooks. Network on first run.
set -uo pipefail

root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
sibling="$root/fast-jev-compaction"
comp="$root/compaction"
# Pin from EVAL.md §1. Moving this SHA silently would invalidate every number
# taken against that clone; a human changes the pin, then re-runs the lane.
PINNED_SHA=6e1da50
CLONE_URL=https://github.com/tamaratran/fast-jev-compaction

fail() { echo "RED: $*" >&2; exit 1; }

ready() {
  [ -f "$sibling/package.json" ] || return 1
  [ -f "$sibling/dist/index.js" ] || return 1
  [ -f "$comp/node_modules/fast-jev-compaction/package.json" ] || return 1
  [ -x "$comp/node_modules/.bin/tsc" ] || return 1
  [ -x "$comp/node_modules/.bin/tsx" ] || return 1
}

if [ "${1:-}" = "--check" ]; then
  if ready; then
    echo "PASS: compaction deps ready (sibling + dist + compaction/node_modules)"
    exit 0
  fi
  echo "MISSING: compaction deps (need pinned sibling build + npm install)"
  echo "FIX: from repository root run ./scripts/bootstrap-compaction.sh, then rerun ./compaction/install-jev-compact.sh --check"
  exit 1
fi

if ready; then
  echo "bootstrap-compaction: already ready"
  exit 0
fi

command -v git >/dev/null 2>&1 || fail "needs git on PATH"
command -v npm >/dev/null 2>&1 || fail "needs npm on PATH"
command -v node >/dev/null 2>&1 || fail "needs node >= 20 on PATH"

if [ ! -f "$sibling/package.json" ]; then
  if [ -e "$sibling" ]; then
    fail "$sibling exists but has no package.json; not overwriting. Fix or move it, then re-run."
  fi
  echo "bootstrap-compaction: cloning $CLONE_URL @ $PINNED_SHA"
  git clone -- "$CLONE_URL" "$sibling" || fail "git clone of fast-jev-compaction failed"
  git -C "$sibling" checkout --detach "$PINNED_SHA" \
    || fail "could not checkout pin $PINNED_SHA (EVAL.md §1). Refusing to float HEAD."
else
  have=$(git -C "$sibling" rev-parse --short HEAD 2>/dev/null || echo unknown)
  echo "bootstrap-compaction: using existing sibling at $have (pin is $PINNED_SHA; not moved)"
fi

if [ ! -f "$sibling/dist/index.js" ]; then
  echo "bootstrap-compaction: building sibling (exports ./dist/index.js; git does not carry it)"
  (cd "$sibling" && npm install --no-audit --no-fund && npm run build) \
    || fail "sibling npm install/build failed"
fi
[ -f "$sibling/dist/index.js" ] || fail "sibling build produced no dist/index.js"

echo "bootstrap-compaction: npm install --prefix compaction"
(cd "$comp" && npm install --no-audit --no-fund) || fail "npm install --prefix compaction failed"

ready || fail "install finished but ready-check still fails"
echo "PASS: compaction deps ready"
exit 0
