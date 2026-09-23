#!/bin/sh
# Fixed port of franken-assessments-44-v7 starter-kit/scripts/check-claim-discipline.sh.
#
# Measured 2026-09-23 on /bin/sh (bash 3.2): the zip splits TSV columns by
# translating tabs to SOH and `read`ing on that IFS. `read` does not split.
# An enforce=yes row is invisible, so the gate reports "0 enforced".
# This port splits on tab with awk. Two further fail-open holes from the same
# dogfood are closed: a missing claims file exits 1, and an enforce=yes row
# whose readme_pattern is absent from the README exits 1 instead of warning
# and continuing.
#
# Usage: check-claim-discipline.sh <claims.tsv> <README> <root>
#        check-claim-discipline.sh --selftest
# Exit 0: every enforced row passed. Exit 1: any enforced row failed, or
#         README is non-empty and nothing is enforced.
set -u

selftest() {
  d=$(mktemp -d "${TMPDIR:-/tmp}/kit-claim-selftest.XXXXXX") || {
    echo "SELFTEST_FAIL: cannot make temp dir"
    exit 1
  }
  trap 'rm -rf "$d"' EXIT INT TERM
  printf 'hello\n' > "$d/readme.md"
  printf 'new TypeSafeClient\n' > "$d/proof.txt"
  printf 'label\treadme_pattern\tcapability_key\texpected_substr\tproof_path\tenforce\tnotes\n' > "$d/bad.tsv"
  printf 'planted-miss\tTHIS PATTERN IS NOT IN THE README\tcap\tnew TypeSafeClient\t%s\tyes\tplant\n' "$d/proof.txt" >> "$d/bad.tsv"
  bad_out=$("$0" "$d/bad.tsv" "$d/readme.md" "$d" 2>&1) && {
    echo "SELFTEST_FAIL: planted unmatched enforce=yes was accepted"
    printf '%s\n' "$bad_out"
    exit 1
  }
  case "$bad_out" in
    *planted-miss*) ;;
    *) echo "SELFTEST_FAIL: RED did not name planted-miss"; printf '%s\n' "$bad_out"; exit 1 ;;
  esac
  case "$bad_out" in
    *"0 enforced"*) echo "SELFTEST_FAIL: still blind to enforce=yes"; printf '%s\n' "$bad_out"; exit 1 ;;
  esac
  printf 'label\treadme_pattern\tcapability_key\texpected_substr\tproof_path\tenforce\tnotes\n' > "$d/good.tsv"
  printf 'planted-hit\thello\tcap\tnew TypeSafeClient\t%s\tyes\tok\n' "$d/proof.txt" >> "$d/good.tsv"
  "$0" "$d/good.tsv" "$d/readme.md" "$d" >/dev/null || {
    echo "SELFTEST_FAIL: a matching enforce=yes row did not pass"
    exit 1
  }
  missing=$("$0" "$d/no-such.tsv" "$d/readme.md" "$d" 2>&1) && {
    echo "SELFTEST_FAIL: missing claims file exited 0"
    exit 1
  }
  case "$missing" in
    *no-such.tsv*) ;;
    *) echo "SELFTEST_FAIL: missing-file RED did not name the path"; printf '%s\n' "$missing"; exit 1 ;;
  esac
  echo "SELFTEST_PASS: unmatched enforce=yes refused, matching row passed, missing file refused"
  exit 0
}

if [ "${1:-}" = "--selftest" ]; then
  selftest
fi

CLAIMS=${1:?claims.tsv required}
README_F=${2:?README required}
ROOT=${3:?root required}

if [ ! -f "$CLAIMS" ]; then
  echo "FAIL: claims file not found: $CLAIMS"
  exit 1
fi

if [ -s "$README_F" ]; then
  nonempty=1
else
  nonempty=0
fi

awk -v readme="$README_F" -v root="$ROOT" -v nonempty="$nonempty" -F '\t' '
function slurp(path,   line, text, n) {
  text = ""
  n = 0
  while ((getline line < path) > 0) {
    text = (n++ ? text "\n" : "") line
  }
  close(path)
  return text
}
function is_abs(path) {
  return substr(path, 1, 1) == "/"
}
BEGIN {
  if (readme != "") body = slurp(readme)
}
$0 ~ /^#/ || $0 ~ /^[[:space:]]*$/ { next }
$1 == "label" { next }
{
  label = $1
  pattern = $2
  needle = $4
  proof = $5
  enforce = $6
  if (label == "") next
  if (enforce != "yes") { skipped++; next }
  enforced++
  if (pattern != "") {
    if (index(body, pattern) == 0) {
      printf "FAIL  %s: enforce=yes but pattern was not found in %s\n", label, readme
      fail++
      next
    }
  }
  if (proof == "") {
    printf "FAIL  %s: proof path empty\n", label
    fail++
    next
  }
  p = proof
  if (!is_abs(proof)) p = root "/" proof
  cmd = "test -s \"" p "\""
  if (system(cmd) != 0) {
    printf "FAIL  %s: proof artifact missing or empty: %s\n", label, proof
    fail++
    next
  }
  if (needle != "" && index(slurp(p), needle) == 0) {
    printf "FAIL  %s: proof %s lacks expected text: %s\n", label, proof, needle
    fail++
    next
  }
  printf "PASS  %s -> %s\n", label, proof
  pass++
}
END {
  if (enforced == 0 && nonempty == 1) {
    printf "FAIL: no enforced claims while %s is non-empty\n", readme
    fail++
  }
  printf "check-claim-discipline: %d passed, %d failed, %d skipped (%d enforced)\n", pass+0, fail+0, skipped+0, enforced+0
  exit (fail > 0 ? 1 : 0)
}
' "$CLAIMS"
