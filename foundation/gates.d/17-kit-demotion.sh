#!/usr/bin/env bash
# 17-kit-demotion: enforce=yes rows whose proof is missing demote the claim.
# Port companion to 15-kit-claim: that stage proves the claim resolves to a
# proof; this one proves a missing proof trips. The checker is
# foundation/kit/check-demotion.sh, the rules it executes are the mechanical
# slice of foundation/kit/demotion-rules.md.
# --selftest plants a missing proof and requires RED naming the plant file,
# then runs the checker's own selftest and the real registry (whose
# enforce=yes row must NOT be demoted). A gate that cannot trip is not a gate.
set -uo pipefail
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
root=$(CDPATH='' cd -- "$here/.." && pwd -P)
checker=$here/kit/check-demotion.sh
if [ "${1:-}" = "--selftest" ]; then
  d=$(mktemp -d "${TMPDIR:-/tmp}/kit-demotion-stage-selftest.XXXXXX") || {
    echo "SELFTEST_FAIL: cannot make temp dir"
    exit 1
  }
  trap 'rm -rf "$d"' EXIT INT TERM
  printf 'label\treadme_pattern\tcapability_key\texpected_substr\tproof_path\tenforce\tnotes\n' > "$d/plant.tsv"
  printf 'stage-plant-missing\tpattern\tcap\tneedle\t%s\tyes\tplant\n' "$d/stage-plant-proof.txt" >> "$d/plant.tsv"
  plant_out=$("$checker" "$d/plant.tsv" "$d" 2>&1) && {
    echo "SELFTEST_FAIL: planted missing proof exited 0"
    printf '%s\n' "$plant_out"
    exit 1
  }
  case "$plant_out" in
    *stage-plant-missing*stage-plant-proof.txt*) ;;
    *) echo "SELFTEST_FAIL: RED did not name the plant file"; printf '%s\n' "$plant_out"; exit 1 ;;
  esac
  checker_out=$("$checker" --selftest 2>&1) || {
    echo "SELFTEST_FAIL: checker selftest exited nonzero"
    printf '%s\n' "$checker_out"
    exit 1
  }
  real_out=$("$checker" "$here/kit/claims.tsv" "$root" 2>&1) || {
    echo "SELFTEST_FAIL: real registry demoted an enforce=yes row"
    printf '%s\n' "$real_out"
    exit 1
  }
  echo "SELFTEST_PASS: plant demoted as $d/stage-plant-proof.txt; checker selftest: $checker_out; real registry: $real_out"
  exit 0
fi
if [ ! -x "$checker" ]; then
  echo "RED: demotion checker missing or not executable: $checker"
  exit 1
fi
"$checker" "$here/kit/claims.tsv" "$root"
