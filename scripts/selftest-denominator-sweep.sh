#!/usr/bin/env bash
# selftest for scripts/denominator-sweep.sh — discovered automatically by foundation/gates.d/80.
#
# The sweep is wired (not hand-run) because it is fast, read-only, and hermetic
# enough: every check regenerates from committed files or pinned fixtures, npm
# test runs the backtest suite without writing outside its own package, and no
# arm writes shared state.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
S="$root/scripts/denominator-sweep.sh"
P="$root/scripts/pinned-denominator.sh"
fail=0
pass=0

note() { printf '  %-4s %s\n' "$1" "$2"; }

# Arm 1: the sweep passes on a clean tree and says ALL-AGREE (an exit-0 that
# stays silent would be an empty success — require the verdict line).
out=$("$S" 2>&1); rc=$?
if [ "$rc" -eq 0 ] && grep -q "ALL-AGREE" <<<"$out"; then
  note ok "sweep ALL-AGREE (rc=0)"; pass=$((pass + 1));
else
  note FAIL "sweep did not agree: rc=$rc"; printf '%s\n' "$out"; fail=$((fail + 1));
fi

# Arm 2: the underlying guard still fires on a planted drift (end-to-end proof
# the sweep's checks are checks, using tonight's verbatim numbers).
"$P" 77767 printf '78242\n' >/dev/null 2>&1
if [ "$?" -eq 3 ]; then note ok "planted drift fires (rc=3)"; pass=$((pass + 1));
else note FAIL "planted drift did not fire"; fail=$((fail + 1)); fi

# Arm 3: the conductor's exact scenario — a copy run from /tmp must REFUSE
# (rc=2), never report eight confident DRIFTs that are all false.
tmp=$(mktemp -d) || { echo "selftest-denominator-sweep: mktemp failed"; exit 1; }
trap 'rm -rf "$tmp"' EXIT
cp "$S" "$tmp/sweep-copy.sh"
"$tmp/sweep-copy.sh" >/dev/null 2>&1
if [ "$?" -eq 2 ]; then note ok "relocated copy refuses (rc=2)"; pass=$((pass + 1));
else note FAIL "relocated copy did not refuse"; fail=$((fail + 1)); fi

echo "scripts/selftest-denominator-sweep.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
