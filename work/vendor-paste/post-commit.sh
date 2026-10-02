#!/usr/bin/env bash
# INSTALL (human with KIT_GATE_EDIT=1; kit-guard B7 denies agent writes here):
#   cp work/vendor-paste/post-commit.sh githooks/post-commit
# jev post-commit: vendor-paste shadow (bead jev-m94x). Scores HEAD's added hunks
# with the frozen vendor Noul into vendor-shadow.jsonl. Advisory-observer: NEVER
# blocks (post-commit cannot block by git construction), always exits 0. Skips
# print a named reason; only an unwritable log is silent.
set -uo pipefail

_repo=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
_runner="$_repo/work/vendor-paste/vendor-shadow.mjs"

if [ ! -f "$_runner" ]; then
  echo "VENDOR_SHADOW_SKIPPED reason=runner-missing path=$_runner" >&2
  exit 0
fi
if ! command -v node >/dev/null 2>&1; then
  echo "VENDOR_SHADOW_SKIPPED reason=node-missing" >&2
  exit 0
fi

node --experimental-strip-types --no-warnings "$_runner" >&2 || true
exit 0
