#!/usr/bin/env bash
# selftest for scripts/pin-liveness.sh — discovered by foundation/gates.d/80 via the
# scripts/selftest-*.sh glob. Every arm plants a real condition and requires the stated outcome.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
S="$root/scripts/pin-liveness.sh"
pass=0; fail=0
note() { printf '  %-4s %s\n' "$1" "$2"; }
arm() { local name="$1" want="$2"; shift 2; "$@" >/dev/null 2>&1; local got=$?
  if [ "$got" -eq "$want" ]; then note ok "$name (rc=$got)"; pass=$((pass+1));
  else note FAIL "$name — wanted rc=$want got rc=$got"; fail=$((fail+1)); fi; }

tmp=$(mktemp -d) || { echo "selftest-pin-liveness: mktemp failed"; exit 1; }
trap 'rm -rf "$tmp"' EXIT
hdr=$(head -1 docs/demos/STATUS.tsv)

# 1. THE REAL DEFECT, replayed: a row pinned to NEGATIVE_EVIDENCE.md, the file that actually
#    drifted tonight. Threshold 1 guarantees the hot-file condition regardless of today's rate,
#    so this arm cannot silently stop testing anything as commit activity changes.
{ printf '%s\n' "$hdr"
  printf 'replayed-UP-R16\t2\t0\tRULED_OUT\tpane1\tNEGATIVE_EVIDENCE.md\treason\t\tdeadbeefdeadbeef\tmeasurement\n'
} > "$tmp/hot.tsv"
arm "row pinned to a hot file exits 3" 3 bash "$S" "$tmp/hot.tsv" 1

# 2. The fix that was actually applied must PASS: same row repointed at the extracted receipt.
{ printf '%s\n' "$hdr"
  printf 'fixed-UP-R16\t2\t0\tRULED_OUT\tpane1\tdocs/demos/upstream-repro/ubs-gate-ruling-20260920.md\treason\t\t3a4796428ddbd003\tmeasurement\n'
} > "$tmp/fixed.tsv"
arm "the applied fix passes at a sane threshold" 0 bash "$S" "$tmp/fixed.tsv" 10

# 3. NOT a gate that fires on everything: the same hot file at a high threshold must not fire
#    unless it is genuinely pathological. Guards the discrimination, not just the detection.
arm "high threshold does not fire on ordinary churn" 0 bash "$S" "$tmp/fixed.tsv" 9999

# 4. Unpinned rows are out of scope — an empty digest column must not be flagged.
{ printf '%s\n' "$hdr"
  printf 'unpinned\t2\t0\tHELD\tpane1\tNEGATIVE_EVIDENCE.md\treason\t\t\tmeasurement\n'
} > "$tmp/unpinned.tsv"
arm "unpinned row is out of scope" 2 bash "$S" "$tmp/unpinned.tsv" 1

# 5. An empty scan set is never a pass (RULE 1).
printf '%s\n' "$hdr" > "$tmp/empty.tsv"
arm "empty scan set exits 2" 2 bash "$S" "$tmp/empty.tsv" 1

# 6. Missing file and bad threshold are errors, not clean results.
arm "missing STATUS exits 2" 2 bash "$S" "$tmp/nope.tsv" 1
arm "non-numeric threshold exits 2" 2 bash "$S" "$tmp/fixed.tsv" abc

# 7. The live STATUS.tsv must be clean at the shipped default — this is the regression arm for
#    tonight's lane-red. If someone re-pins to a hot file, this fires in the suite.
arm "live STATUS clean at default threshold" 0 bash "$S"

echo "scripts/selftest-pin-liveness.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
