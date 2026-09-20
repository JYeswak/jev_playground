#!/usr/bin/env bash
# selftest for scripts/pinned-denominator.sh — discovered automatically by foundation/gates.d/80.
#
# Every arm plants the real defect and requires the guard to FIRE. An arm that only proves the
# happy path would be the thing this repo calls a gate that fires on everything.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
P="$root/scripts/pinned-denominator.sh"
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

tmp=$(mktemp -d) || { echo "selftest-pinned-denominator: mktemp failed"; exit 1; }
trap 'rm -rf "$tmp"' EXIT
printf '42\n' > "$tmp/count.txt"

# 1. Agreement still passes and still prints.
arm "agree exits 0" 0 "$P" 42 cat "$tmp/count.txt"

# 2. THE DEFECT, verbatim numbers: 77,767 quoted, 78,242 fresh. Plain re-running and eyeballing
#    let this ship; the guard must refuse it.
arm "77767 vs 78242 exits 3" 3 "$P" 77767 printf '78242\n'

# 3. Second observed instance: matched=15525 quoted, 15618 fresh.
arm "15525 vs 15618 exits 3" 3 "$P" 15525 printf '15618\n'

# 4. Formatting is not drift: commas and whitespace on either side still agree.
arm "comma+space agree exits 0" 0 "$P" '77,767' printf '  77767\n'

# 5. But comma formatting must not HIDE drift: '77,767' vs 78242 fires.
arm "comma hides nothing, exits 3" 3 "$P" '77,767' printf '78,242\n'

# 6. A failed regeneration command is an error, never a pass.
arm "failing command exits 2" 2 "$P" 42 false

# 7. Non-count output (a log line, a table) is not a denominator.
arm "non-numeric output exits 2" 2 "$P" 42 printf 'n=42 (see above)\n'

# 8. Empty output is not zero — an explicit 0 must be printed to claim 0.
arm "empty output exits 2" 2 "$P" 0 printf ''

# 9. Explicit zero agrees with zero.
arm "zero agrees exits 0" 0 "$P" 0 printf '0\n'

# 10. A claim without a regeneration command is not a check.
arm "no command exits 2" 2 "$P" 42

# 11. A non-count CLAIM is refused too — the prose side can be the drifted part.
arm "non-numeric claim exits 2" 2 "$P" 'many' printf '42\n'

echo "scripts/selftest-pinned-denominator.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
