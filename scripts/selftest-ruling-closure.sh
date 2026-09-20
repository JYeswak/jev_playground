#!/usr/bin/env bash
# selftest for work/ruling-closure/{emit,project}.mjs — discovered by foundation/gates.d/80.
#
# Hermetic: temp dirs only, never the real closures/ or STATUS.tsv. Every arm
# plants the real defect and requires the instrument to FIRE.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
E="$root/work/ruling-closure/emit.mjs"
P="$root/work/ruling-closure/project.mjs"
fail=0
pass=0

note() { printf '  %-4s %s\n' "$1" "$2"; }
tmp=$(mktemp -d) || { echo "selftest-ruling-closure: mktemp failed"; exit 1; }
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/closures"
printf '# test receipt\nbody line\n' > "$tmp/receipt.md"
printf '# falsifier\n' > "$tmp/fals.md"

# Setup: one honest closure.
node "$E" --candidate T1 --rung 4 --verdict HELD --author t \
  --receipt "$tmp/receipt.md" --falsifier "$tmp/fals.md" \
  --falsifier-sha deadbee --falsifier-fired no \
  --out "$tmp/closures" >/dev/null 2>&1 || { echo "selftest: setup emit failed"; exit 2; }

# Arm 1: closure whose digest disagrees with its receipt must FIRE.
printf 'tampered body\n' >> "$tmp/receipt.md"
node "$P" --dir "$tmp/closures" >/dev/null 2>&1
if [ "$?" -ne 0 ]; then note ok "digest disagreement fires"; pass=$((pass + 1));
else note FAIL "digest disagreement passed"; fail=$((fail + 1)); fi
printf '# test receipt\nbody line\n' > "$tmp/receipt.md"  # restore

# Arm 2: closure citing a live-monotonic input with no as_of must FIRE.
node "$E" --candidate T2 --rung 4 --verdict HELD --author t \
  --receipt "$tmp/receipt.md" --falsifier "$tmp/fals.md" \
  --falsifier-sha deadbee --falsifier-fired no \
  --live-input /tmp/live.db --out "$tmp/closures" >/dev/null 2>&1 \
  && { echo "selftest: setup error — emit accepted live input without as_of"; exit 2; }
printf '{"candidate":"T2","rung":4,"verdict":"HELD","author":"t","receipt":{"path":"%s","digest":"%s"},"falsifier":{"path":"%s","commit_sha":"x","fired":false},"inputs":[{"path":"/tmp/live.db","sha":null,"live":true,"as_of":null}],"guards":{}}' \
  "$tmp/receipt.md" "$(perl -0777 -pe 's/\s+\z//' "$tmp/receipt.md" | shasum -a 256 | cut -c1-16)" "$tmp/fals.md" \
  > "$tmp/closures/T2.closure.json"
node "$P" --dir "$tmp/closures" >/dev/null 2>&1
if [ "$?" -ne 0 ]; then note ok "live input without as_of fires"; pass=$((pass + 1));
else note FAIL "live input without as_of passed"; fail=$((fail + 1)); fi
rm -f "$tmp/closures/T2.closure.json"

# Arm 3: strict diff with a dropped row must FIRE; lax diff reports it.
printf 'C1\t4\t0\tHELD\tt\tr.md\t\t\tdeadbeefdeadbeef\tmeasurement\nC2\t4\t0\tHELD\tt\tr.md\t\t\tdeadbeefdeadbeef\tmeasurement\n' > "$tmp/status.tsv"
node "$P" --dir "$tmp/closures" --diff "$tmp/status.tsv" --strict-diff >/dev/null 2>&1
if [ "$?" -ne 0 ]; then note ok "strict diff on dropped row fires"; pass=$((pass + 1));
else note FAIL "strict diff passed on dropped row"; fail=$((fail + 1)); fi
node "$P" --dir "$tmp/closures" --diff "$tmp/status.tsv" >/dev/null 2>&1
if [ "$?" -eq 0 ]; then note ok "lax diff reports without failing"; pass=$((pass + 1));
else note FAIL "lax diff failed on reportable delta"; fail=$((fail + 1)); fi

echo "scripts/selftest-ruling-closure.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
