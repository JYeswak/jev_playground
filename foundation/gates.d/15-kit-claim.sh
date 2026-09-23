#!/usr/bin/env bash
# 15-kit-claim: README claims with enforce=yes must resolve to a proof file.
# Port of the franken-assessments starter-kit claim gate, with the /bin/sh
# column-split bug fixed in foundation/kit/check-claim-discipline.sh.
# --selftest runs that checker's planted unmatched row, matching row, and
# missing-file arms. A gate that cannot see enforce=yes is not this stage.
set -uo pipefail
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
root=$(CDPATH='' cd -- "$here/.." && pwd -P)
checker=$here/kit/check-claim-discipline.sh
if [ "${1:-}" = "--selftest" ]; then
  "$checker" --selftest
  exit $?
fi
if [ ! -x "$checker" ]; then
  echo "RED: claim checker missing or not executable: $checker"
  exit 1
fi
"$checker" "$here/kit/claims.tsv" "$root/README.md" "$root"
