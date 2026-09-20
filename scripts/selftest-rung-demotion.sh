#!/usr/bin/env bash
# selftest for scripts/rung-demotion.sh — discovered by foundation/gates.d/80.
# Hermetic temp STATUS + receipts. Every arm plants the real defect.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
D="$root/scripts/rung-demotion.sh"
fail=0
pass=0

note() { printf '  %-4s %s\n' "$1" "$2"; }
tmp=$(mktemp -d) || { echo "selftest-rung-demotion: mktemp failed"; exit 1; }
trap 'rm -rf "$tmp"' EXIT
row() { printf 'C%d\t4\t0\tHELD\tt\t%s\t\t\tdeadbeefdeadbeef\tmeasurement\n' "$1" "$2"; }
{ echo '# fixture'; row 1 "$tmp/live.md"; row 2 "$tmp/pinned.md"; row 3 "$tmp/clean.md"; } > "$tmp/status.tsv"

# Arm 1 (trigger): cites live artifact, no as-of → FIRES.
printf 'counts from real-allowed.json show\n' > "$tmp/live.md"
# Arm 2 (satisfying): cites live artifact WITH as-of → passes.
printf 'counts from real-allowed.json, as-of 2026-09-20, re-derived\n' > "$tmp/pinned.md"
# Arm 3 (satisfying): no live citation → passes.
printf 'frozen corpus numbers, pinned fixture\n' > "$tmp/clean.md"

out=$("$D" "$tmp/status.tsv" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && grep -q 'DEMOTE C1' <<<"$out" && ! grep -q 'DEMOTE C[23]' <<<"$out"; then
  note ok "live-without-asof fires, others silent (rc=3)"; pass=$((pass + 1));
else
  note FAIL "wrong fire pattern (rc=$rc)"; printf '%s\n' "$out"; fail=$((fail + 1));
fi

# Arm 4: empty scan set is never a pass.
printf '# nothing\n' > "$tmp/empty.tsv"
"$D" "$tmp/empty.tsv" >/dev/null 2>&1
if [ "$?" -eq 2 ]; then note ok "empty scan exits 2"; pass=$((pass + 1));
else note FAIL "empty scan did not refuse"; fail=$((fail + 1)); fi

echo "scripts/selftest-rung-demotion.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
