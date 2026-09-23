#!/usr/bin/env bash
# 16-kit-readiness: the planning packet must pass the fixed readiness checker.
# --selftest refuses a sign-off that only says "design", and resolves a
# relative packet against the given root rather than the caller cwd.
set -uo pipefail
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
root=$(CDPATH='' cd -- "$here/.." && pwd -P)
checker=$here/kit/check-readiness.sh
if [ "${1:-}" = "--selftest" ]; then
  "$checker" --selftest
  exit $?
fi
if [ ! -x "$checker" ]; then
  echo "RED: readiness checker missing or not executable: $checker"
  exit 1
fi
"$checker" foundation/kit/packet.md "$root"
