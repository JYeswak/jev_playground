#!/usr/bin/env bash
# 15-kit-claim: ledger claims with enforce=yes must resolve to a proof file, and the share of
# ledger claim units that are registered may only rise.
# Port of the franken-assessments starter-kit claim gate, with the /bin/sh column-split bug fixed
# in foundation/kit/check-claim-discipline.sh.
# Coverage ratchet (plan W2.3, extended here rather than as a new stage, per gate thrift):
# foundation/kit/claim-units.py applies the honesty census's candidate rule; the floor in
# foundation/kit/claim-coverage.floor pins covered/candidates and the unitizer's sha256.
# --selftest runs the checker's planted unmatched row, matching row, and missing-file arms, then
# plants an unregistered numeric sentence in a ledger copy: it must count as a candidate and turn
# the ratchet RED naming it. A gate that cannot see enforce=yes is not this stage.
set -uo pipefail
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
root=$(CDPATH='' cd -- "$here/.." && pwd -P)
checker=$here/kit/check-claim-discipline.sh
units=$here/kit/claim-units.py
floor=$here/kit/claim-coverage.floor

floor_value() { sed -n "s/^$1=//p" "$floor" | head -1; }

# coverage <ledger> <claims>: prints a verdict line; exit 0 at or above floor, 1 below, 2 error.
coverage() {
  local ledger=$1 claims=$2 out summary cand cov fcov fcand fsha sha
  [ -f "$floor" ] || { echo "RED: coverage floor missing: $floor"; return 2; }
  fcov=$(floor_value covered); fcand=$(floor_value candidates); fsha=$(floor_value unitizer_sha256)
  sha=$(shasum -a 256 "$units" | cut -d' ' -f1)
  if [ "$sha" != "$fsha" ]; then
    echo "RED: claim-units.py changed (sha $sha, floor pinned $fsha); re-derive the floor, do not compare across rules"
    return 2
  fi
  out=$(python3 "$units" "$ledger" "$claims") || { echo "RED: claim-units.py failed"; return 2; }
  summary=$(printf '%s\n' "$out" | tail -1)
  cand=$(printf '%s' "$summary" | sed -n 's/.*candidates=\([0-9]*\).*/\1/p')
  cov=$(printf '%s' "$summary" | sed -n 's/.*covered=\([0-9]*\).*/\1/p')
  if [ -z "$cand" ] || [ "$cand" -eq 0 ]; then
    echo "RED: no claim candidates found in $ledger (an empty scan set is not a pass)"
    return 2
  fi
  # cov/cand >= fcov/fcand, compared in integers.
  if [ $((cov * fcand)) -lt $((fcov * cand)) ]; then
    echo "RED: ledger claim coverage $cov/$cand fell below the floor $fcov/$fcand. Register these or remove them:"
    printf '%s\n' "$out" | awk -F'\t' 'NR>1 && $2=="n" {print "  line " $1 ": " $4}'
    return 1
  fi
  if [ $((cov * fcand)) -gt $((fcov * cand)) ]; then
    echo "PASS  ledger claim coverage $cov/$cand (floor $fcov/$fcand; the floor can be raised)"
  else
    echo "PASS  ledger claim coverage $cov/$cand (floor $fcov/$fcand)"
  fi
  return 0
}

if [ "${1:-}" = "--selftest" ]; then
  "$checker" --selftest || exit 1
  d=$(mktemp -d) || { echo "SELFTEST_FAIL: cannot make temp dir"; exit 1; }
  trap 'rm -rf "$d"' EXIT
  plant="The planted selftest claim beats every baseline by 99.9% on 12345 rows."
  cp "$root/docs/LEDGER.md" "$d/ledger.md"
  printf '\n%s\n' "$plant" >> "$d/ledger.md"
  # Capture first: `| grep -q` closes the pipe early, and under pipefail the writer's broken pipe
  # would read as "not a candidate" on a race (measured 2026-09-23, 1 of 2 runs).
  planted_units=$(python3 "$units" "$d/ledger.md" "$here/kit/claims.tsv") || { echo "SELFTEST_FAIL: claim-units.py failed on the planted copy"; exit 1; }
  if ! printf '%s\n' "$planted_units" | grep -F "$plant" >/dev/null; then
    echo "SELFTEST_FAIL: the planted sentence is not a candidate, so this arm cannot fail"
    exit 1
  fi
  red=$(coverage "$d/ledger.md" "$here/kit/claims.tsv"); rc=$?
  if [ "$rc" -ne 1 ]; then echo "SELFTEST_FAIL: planted unregistered claim did not turn the ratchet RED (rc=$rc): $red"; exit 1; fi
  case "$red" in *"$plant"*) ;; *) echo "SELFTEST_FAIL: RED did not name the planted sentence"; exit 1 ;; esac
  removed_pattern='on 640 in a fresh live run here'
  awk -v needle="$removed_pattern" 'index($0, needle) == 0' "$root/docs/LEDGER.md" > "$d/removed-claim.md"
  removed=$("$checker" "$here/kit/claims.tsv" "$d/removed-claim.md" "$root" 2>&1); rc=$?
  if [ "$rc" -eq 0 ]; then echo "SELFTEST_FAIL: removing a registered ledger claim stayed green"; exit 1; fi
  case "$removed" in *"pattern was not found"*) ;; *) echo "SELFTEST_FAIL: removed claim RED did not name the missing pattern: $removed"; exit 1 ;; esac
  removed_coverage=$(coverage "$d/removed-claim.md" "$here/kit/claims.tsv"); rc=$?
  if [ "$rc" -eq 0 ]; then echo "SELFTEST_FAIL: removed ledger claim stayed above the coverage floor: $removed_coverage"; exit 1; fi
  green=$(coverage "$root/docs/LEDGER.md" "$here/kit/claims.tsv"); rc=$?
  if [ "$rc" -ne 0 ]; then echo "SELFTEST_FAIL: the real ledger does not pass its own floor: $green"; exit 1; fi
  echo "SELFTEST_OK: checker arms, planted claim RED, removed registered claim RED, real ledger at or above floor"
  exit 0
fi

if [ ! -x "$checker" ]; then
  echo "RED: claim checker missing or not executable: $checker"
  exit 1
fi
"$checker" "$here/kit/claims.tsv" "$root/docs/LEDGER.md" "$root" || exit 1
coverage "$root/docs/LEDGER.md" "$here/kit/claims.tsv"
