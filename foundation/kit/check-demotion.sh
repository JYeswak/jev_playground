#!/bin/sh
# check-demotion.sh: mechanical demotion teeth for the kit claim registry.
#
# For every enforce=yes row in claims.tsv, the proof file must exist and be
# non-empty. A missing proof DEMOTES the claim: the row is printed as DEMOTE
# and the exit is 1. enforce=no rows are advisory and never demote.
# Same 7-column TSV as check-claim-discipline.sh; tab-split with awk, because
# on /bin/sh `read` does not split and an enforce=yes row goes invisible.
#
# Usage: check-demotion.sh <claims.tsv> <root>
#        check-demotion.sh --selftest
# Exit 0: no enforced row is demoted. Exit 1: any enforced row demoted, or the
#         claims file itself is missing.
set -u

selftest() {
  d=$(mktemp -d "${TMPDIR:-/tmp}/kit-demotion-selftest.XXXXXX") || {
    echo "SELFTEST_FAIL: cannot make temp dir"
    exit 1
  }
  trap 'rm -rf "$d"' EXIT INT TERM
  printf 'evidence\n' > "$d/proof.txt"
  printf 'label\treadme_pattern\tcapability_key\texpected_substr\tproof_path\tenforce\tnotes\n' > "$d/bad.tsv"
  printf 'planted-gone\tpattern\tcap\tneedle\t%s\tyes\tplant\n' "$d/no-such-proof.txt" >> "$d/bad.tsv"
  bad_out=$("$0" "$d/bad.tsv" "$d" 2>&1) && {
    echo "SELFTEST_FAIL: planted missing enforce=yes proof was accepted"
    printf '%s\n' "$bad_out"
    exit 1
  }
  case "$bad_out" in
    *planted-gone*) ;;
    *) echo "SELFTEST_FAIL: RED did not name planted-gone"; printf '%s\n' "$bad_out"; exit 1 ;;
  esac
  case "$bad_out" in
    *DEMOTE*) ;;
    *) echo "SELFTEST_FAIL: RED did not say DEMOTE"; printf '%s\n' "$bad_out"; exit 1 ;;
  esac
  printf 'label\treadme_pattern\tcapability_key\texpected_substr\tproof_path\tenforce\tnotes\n' > "$d/good.tsv"
  printf 'planted-kept\tpattern\tcap\tneedle\t%s\tyes\tok\n' "$d/proof.txt" >> "$d/good.tsv"
  printf 'planted-advisory\tpattern\tcap\tneedle\t%s\tno\tok\n' "$d/no-such-proof.txt" >> "$d/good.tsv"
  "$0" "$d/good.tsv" "$d" >/dev/null || {
    echo "SELFTEST_FAIL: a present enforce=yes proof was demoted"
    exit 1
  }
  missing=$("$0" "$d/no-such.tsv" "$d" 2>&1) && {
    echo "SELFTEST_FAIL: missing claims file exited 0"
    exit 1
  }
  case "$missing" in
    *no-such.tsv*) ;;
    *) echo "SELFTEST_FAIL: missing-file RED did not name the path"; printf '%s\n' "$missing"; exit 1 ;;
  esac
  echo "SELFTEST_PASS: missing enforce=yes proof demoted, present proof kept, missing file refused"
  exit 0
}

if [ "${1:-}" = "--selftest" ]; then
  selftest
fi

CLAIMS=${1:?claims.tsv required}
ROOT=${2:?root required}

if [ ! -f "$CLAIMS" ]; then
  echo "DEMOTE: claims file missing: $CLAIMS"
  exit 1
fi

awk -v root="$ROOT" -F '\t' '
function is_abs(path) {
  return substr(path, 1, 1) == "/"
}
$0 ~ /^#/ || $0 ~ /^[[:space:]]*$/ { next }
$1 == "label" { next }
{
  label = $1
  proof = $5
  enforce = $6
  if (label == "") next
  if (enforce != "yes") { held++; next }
  enforced++
  if (proof == "") {
    printf "DEMOTE  %s: proof path empty\n", label
    demoted++
    next
  }
  p = proof
  if (!is_abs(proof)) p = root "/" proof
  cmd = "test -s \"" p "\""
  if (system(cmd) != 0) {
    printf "DEMOTE  %s: proof artifact missing or empty: %s\n", label, proof
    demoted++
    next
  }
  printf "HELD  %s -> %s\n", label, proof
  held++
}
END {
  printf "check-demotion: %d held, %d demoted (%d enforced)\n", held+0, demoted+0, enforced+0
  exit (demoted > 0 ? 1 : 0)
}
' "$CLAIMS"
