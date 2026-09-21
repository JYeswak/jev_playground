#!/usr/bin/env bash
# ttsr-assert-disabled.sh — a disable that is not enumerated did not happen.
#
# WHY: CALLBACK-P1-CORRECTION 2026-09-20. `omp config set ttsr.disabledRules`
# replaced rather than appended, so a live rule survived a reported disable.
# `omp ttsr test` silence under repeatMode once cannot distinguish DISABLED
# from ALREADY-FIRED-THIS-SESSION (ARC.md measurement error 2). The only valid
# check is enumeration of `omp ttsr list` in BOTH scopes (project vs
# outside-repo), because those registries differ.
#
# Usage: scripts/ttsr-assert-disabled.sh <rule-name>
#   exit 0  absent in both scopes
#   exit 1  still present; stdout names the failing scope(s) and counts
#   exit 2  usage / omp missing / enumeration failed
#
# NEVER fires a probe. NEVER reads ttsr.disabledRules. NEVER runs `omp ttsr test`.
# Capture-first throughout (this lane's bash-pipe-exit class). Exact `name`
# field match, not a substring grep — `grep -c <rule>` on the text list can
# hit a condition body.
set -uo pipefail

rule="${1:-}"
[ -n "$rule" ] || { echo "usage: $0 <rule-name>" >&2; exit 2; }
command -v omp >/dev/null 2>&1 || { echo "ENUMERATION_FAILED: omp not on PATH" >&2; exit 2; }

root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
global_dir=/tmp/ttsr-assert-disabled-scope
mkdir -p "$global_dir"
if [ -e "$global_dir/.omp" ]; then
  echo "ENUMERATION_FAILED global: $global_dir has .omp — not an outside-repo scope" >&2
  exit 2
fi

count_in() {
  local cwd="$1"
  local out
  out=$(CDPATH='' cd -- "$cwd" && omp ttsr list --json)
  [ -n "$out" ] || return 2
  printf '%s\n' "$out" | python3 -c '
import json, sys
name = sys.argv[1]
raw = sys.stdin.read()
rules = json.loads(raw)
if not isinstance(rules, list):
    sys.exit(2)
print(sum(1 for r in rules if isinstance(r, dict) and r.get("name") == name))
' "$rule"
}

project_n=$(count_in "$root") || { echo "ENUMERATION_FAILED project" >&2; exit 2; }
global_n=$(count_in "$global_dir") || { echo "ENUMERATION_FAILED global" >&2; exit 2; }

rc=0
if [ "$project_n" -ne 0 ]; then
  echo "ttsr-assert-disabled: $rule still present in project (count=$project_n)"
  rc=1
fi
if [ "$global_n" -ne 0 ]; then
  echo "ttsr-assert-disabled: $rule still present in global (count=$global_n)"
  rc=1
fi
if [ "$rc" -eq 0 ]; then
  echo "ttsr-assert-disabled: $rule absent in project (0) and global (0)"
fi
exit "$rc"
