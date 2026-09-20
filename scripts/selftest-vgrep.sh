#!/usr/bin/env bash
# selftest for scripts/vgrep.sh — discovered automatically by foundation/gates.d/80.
#
# Every arm plants the real defect and requires the guard to FIRE. An arm that only proves the
# happy path would be the thing this repo calls a gate that fires on everything.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
V="$root/scripts/vgrep.sh"
fail=0
pass=0

note() { printf '  %-4s %s\n' "$1" "$2"; }
arm() { # arm <name> <expected-rc> <cmd...>
  local name="$1" want="$2"; shift 2
  "$@" >/dev/null 2>&1
  local got=$?
  if [ "$got" -eq "$want" ]; then note ok "$name (rc=$got)"; pass=$((pass + 1));
  else note FAIL "$name — wanted rc=$want got rc=$got"; fail=$((fail + 1)); fi
}

tmp=$(mktemp -d) || { echo "selftest-vgrep: mktemp failed"; exit 1; }
trap 'rm -rf "$tmp"' EXIT
printf 'alpha\nbeta\n' > "$tmp/f.txt"

# 1. The happy path still works and still prints.
arm "match exits 0" 0 "$V" -n alpha "$tmp/f.txt"

# 2. THE DEFECT: zero matches must NOT look like success. Plain grep exits 1 here and a caller
#    reading `rc=0` as the only failure signal treats it as clean.
arm "zero matches exits 3" 3 "$V" -n 'nothing-here' "$tmp/f.txt"

# 3. The real-world shape that cost us twice: a COUNT selector that undercounts silently. Plain
#    `grep -c` on a missing token returns 0 with rc=1; the guard must refuse it.
arm "grep -c with no hits exits 3" 3 "$V" -c 'arm' "$tmp/f.txt"

# 4. A broken selector (bad regex) must be distinguishable from a clean result.
arm "grep error exits 2" 2 "$V" -E '[' "$tmp/f.txt"

# 5. An unreadable path is an error, not an absence — the class where a wrong path read as clean.
arm "missing file exits 2" 2 "$V" -n alpha "$tmp/does-not-exist.txt"

# 6. Legitimate absence-proof: --expect-zero passes when truly absent.
arm "--expect-zero passes on absence" 0 "$V" --expect-zero -n 'nothing-here' "$tmp/f.txt"

# 7. And --expect-zero must FIRE when the thing is present — otherwise the observe-only style
#    proof (`no block path in this file`) could pass on a file that has one.
arm "--expect-zero fires on presence" 3 "$V" --expect-zero -n alpha "$tmp/f.txt"

# 8. An empty invocation is not a pass (RULE 1: an empty scan set is never a pass).
arm "no arguments exits 2" 2 "$V"

echo "scripts/selftest-vgrep.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
