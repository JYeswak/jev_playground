#!/usr/bin/env bash
# 15-kit-claim: claims with enforce=yes must resolve to a proof file, and the share of claim units
# that are registered may only rise, for BOTH claim documents: docs/LEDGER.md and README.md.
# Port of the franken-assessments starter-kit claim gate, with the /bin/sh column-split bug fixed
# in foundation/kit/check-claim-discipline.sh.
# One registry, two documents: foundation/kit/claims.tsv holds both. A row whose label starts with
# `readme-` is a README.md claim; every other row is a docs/LEDGER.md claim. split_claims routes
# them, so a README row can never satisfy the ledger and a ledger row can never cover README prose.
# Coverage ratchet (plan W2.3, extended here rather than as a new stage, per gate thrift):
# foundation/kit/claim-units.py applies the honesty census's candidate rule; the floor in
# foundation/kit/claim-coverage.floor pins covered/candidates per document and the unitizer's
# sha256. README.md joined the gated documents under jev-qx7b; before that this stage checked the
# ledger only and README prose carried no claim gate at all (measured: 0 of 56 candidates covered).
# --selftest runs the checker's planted unmatched row, matching row, and missing-file arms, then,
# for EACH document, plants an unregistered numeric sentence in a copy: it must count as a
# candidate and turn the ratchet RED naming it. The ledger also blanks one registered phrase
# (checker and ratchet RED). The README instead drifts one registered figure by one digit: the
# checker must go RED, because a README that restates a number differently from its proof is the
# failure this gate exists for. A README with no registered rows must fail the checker too. A gate
# that cannot see enforce=yes is not this stage.
set -uo pipefail
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
root=$(CDPATH='' cd -- "$here/.." && pwd -P)
checker=$here/kit/check-claim-discipline.sh
units=$here/kit/claim-units.py
floor=$here/kit/claim-coverage.floor
registry=$here/kit/claims.tsv

floor_value() { sed -n "s/^$1=//p" "$floor" | head -1; }

# split_claims <ledger|readme> <out>: the registry's header plus the rows of one document.
split_claims() {
  awk -F'\t' -v want="$1" 'NR == 1 || (($1 ~ /^readme-/) == (want == "readme"))' "$registry" > "$2"
}

# coverage <doc> <claims> <name> <floor-covered-key> <floor-candidates-key>: prints a verdict line;
# exit 0 at or above floor, 1 below, 2 error.
coverage() {
  local doc=$1 claims=$2 name=$3 kcov=$4 kcand=$5 out summary cand cov fcov fcand fsha sha
  [ -f "$floor" ] || { echo "RED: coverage floor missing: $floor"; return 2; }
  fcov=$(floor_value "$kcov"); fcand=$(floor_value "$kcand"); fsha=$(floor_value unitizer_sha256)
  case "$fcov$fcand" in *[!0-9]* | "") echo "RED: floor keys $kcov/$kcand missing or not integers in $floor"; return 2 ;; esac
  sha=$(shasum -a 256 "$units" | cut -d' ' -f1)
  if [ "$sha" != "$fsha" ]; then
    echo "RED: claim-units.py changed (sha $sha, floor pinned $fsha); re-derive the floor, do not compare across rules"
    return 2
  fi
  out=$(python3 "$units" "$doc" "$claims") || { echo "RED: claim-units.py failed"; return 2; }
  summary=$(printf '%s\n' "$out" | tail -1)
  cand=$(printf '%s' "$summary" | sed -n 's/.*candidates=\([0-9]*\).*/\1/p')
  cov=$(printf '%s' "$summary" | sed -n 's/.*covered=\([0-9]*\).*/\1/p')
  if [ -z "$cand" ] || [ "$cand" -eq 0 ]; then
    echo "RED: no claim candidates found in $doc (an empty scan set is not a pass)"
    return 2
  fi
  # cov/cand >= fcov/fcand, compared in integers.
  if [ $((cov * fcand)) -lt $((fcov * cand)) ]; then
    echo "RED: $name claim coverage $cov/$cand fell below the floor $fcov/$fcand. Register these or remove them:"
    printf '%s\n' "$out" | awk -F'\t' 'NR>1 && $2=="n" {print "  line " $1 ": " $4}'
    return 1
  fi
  if [ $((cov * fcand)) -gt $((fcov * cand)) ]; then
    echo "PASS  $name claim coverage $cov/$cand (floor $fcov/$fcand; the floor can be raised)"
  else
    echo "PASS  $name claim coverage $cov/$cand (floor $fcov/$fcand)"
  fi
  return 0
}

# plant_arm <name> <doc> <claims> <floor-covered-key> <floor-candidates-key> <tmp>: an unregistered
# numeric sentence appended to a copy of <doc> must be a candidate and turn the ratchet RED naming
# it; the real <doc> must pass its own floor.
plant_arm() {
  local name=$1 doc=$2 claims=$3 kcov=$4 kcand=$5 d=$6 plant planted_units red green rc
  plant="The planted selftest claim beats every baseline by 99.9% on 12345 rows."
  cp "$doc" "$d/$name.planted.md"
  printf '\n%s\n' "$plant" >> "$d/$name.planted.md"
  # Capture first: `| grep -q` closes the pipe early, and under pipefail the writer's broken pipe
  # would read as "not a candidate" on a race (measured 2026-09-23, 1 of 2 runs).
  planted_units=$(python3 "$units" "$d/$name.planted.md" "$claims") || { echo "SELFTEST_FAIL: $name: claim-units.py failed on the planted copy"; return 1; }
  if ! printf '%s\n' "$planted_units" | grep -F "$plant" >/dev/null; then
    echo "SELFTEST_FAIL: $name: the planted sentence is not a candidate, so this arm cannot fail"
    return 1
  fi
  red=$(coverage "$d/$name.planted.md" "$claims" "$name" "$kcov" "$kcand"); rc=$?
  if [ "$rc" -ne 1 ]; then echo "SELFTEST_FAIL: $name: planted unregistered claim did not turn the ratchet RED (rc=$rc): $red"; return 1; fi
  case "$red" in *"$plant"*) ;; *) echo "SELFTEST_FAIL: $name: RED did not name the planted sentence"; return 1 ;; esac
  green=$(coverage "$doc" "$claims" "$name" "$kcov" "$kcand"); rc=$?
  if [ "$rc" -ne 0 ]; then echo "SELFTEST_FAIL: the real $name does not pass its own floor: $green"; return 1; fi
  return 0
}

# blank_arm <name> <doc> <claims> <floor-covered-key> <floor-candidates-key> <needle> <tmp>:
# blank every registered phrase inside the needle's sentence, not the whole line: LEDGER line 15
# packs three claim sentences, so a line drop vanishes three candidates and stays at 100% (jev-9q1g).
# <needle> must occur exactly once in <doc> and its sentence must stay a candidate once blanked.
blank_arm() {
  local name=$1 doc=$2 claims=$3 kcov=$4 kcand=$5 needle=$6 d=$7 removed removed_coverage rc
  python3 - "$claims" "$doc" "$d/$name.removed.md" "$needle" <<'EOF' || { echo "SELFTEST_FAIL: $name: sentence phrase-blanking failed"; return 1; }
import csv, re, sys
claims_p, doc_p, out_p, needle = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
lines = open(doc_p).read().split("\n")
hits = [i for i, l in enumerate(lines) if needle in l]
assert len(hits) == 1, "needle must occur exactly once"
i = hits[0]
tgt = [s for s in re.split(r"(?<=[.!])\s+|\s*\|\s*", lines[i]) if needle in s]
assert len(tgt) == 1, "needle must hit exactly one sentence"
with open(claims_p) as fh:
    pats = [r["readme_pattern"] for r in csv.DictReader(fh, delimiter="\t") if r.get("readme_pattern") and r["readme_pattern"].lower() in tgt[0].lower()]
assert pats, "no registered pattern in needle sentence"
new_line = lines[i]
for p in pats:
    new_line = re.sub(re.escape(p), "", new_line, flags=re.I)
assert len(new_line) >= 20 and re.search(r"\d", new_line), "remnant must stay a candidate"
lines[i] = new_line
open(out_p, "w").write("\n".join(lines))
EOF
  removed=$("$checker" "$claims" "$d/$name.removed.md" "$root" 2>&1); rc=$?
  if [ "$rc" -eq 0 ]; then echo "SELFTEST_FAIL: $name: removing a registered claim stayed green"; return 1; fi
  case "$removed" in *"pattern was not found"*) ;; *) echo "SELFTEST_FAIL: $name: removed claim RED did not name the missing pattern: $removed"; return 1 ;; esac
  removed_coverage=$(coverage "$d/$name.removed.md" "$claims" "$name" "$kcov" "$kcand"); rc=$?
  if [ "$rc" -eq 0 ]; then echo "SELFTEST_FAIL: $name: removed claim stayed above the coverage floor: $removed_coverage"; return 1; fi
  return 0
}

# drift_arm <name> <doc> <claims> <needle> <tmp>: change one registered figure by one digit in a
# copy of <doc>. The checker must go RED on a missing pattern. <needle> must be a registered phrase
# that occurs exactly once in <doc> and ends in a digit.
drift_arm() {
  local name=$1 doc=$2 claims=$3 needle=$4 d=$5 drifted rc
  python3 - "$doc" "$d/$name.drifted.md" "$needle" <<'EOF' || { echo "SELFTEST_FAIL: $name: figure drift failed"; return 1; }
import sys
doc_p, out_p, needle = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(doc_p).read()
assert text.count(needle) == 1, "needle must occur exactly once"
assert needle[-1].isdigit(), "needle must end in a digit"
last = needle[-1]
text = text.replace(needle, needle[:-1] + str((int(last) + 1) % 10))
open(out_p, "w").write(text)
EOF
  drifted=$("$checker" "$claims" "$d/$name.drifted.md" "$root" 2>&1); rc=$?
  if [ "$rc" -eq 0 ]; then echo "SELFTEST_FAIL: $name: a drifted registered figure stayed green"; return 1; fi
  case "$drifted" in *"pattern was not found"*) ;; *) echo "SELFTEST_FAIL: $name: drift RED did not name the missing pattern: $drifted"; return 1 ;; esac
  return 0
}

if [ "${1:-}" = "--selftest" ]; then
  "$checker" --selftest || exit 1
  d=$(mktemp -d) || { echo "SELFTEST_FAIL: cannot make temp dir"; exit 1; }
  trap 'rm -rf "$d"' EXIT
  split_claims ledger "$d/ledger.tsv"; split_claims readme "$d/readme.tsv"
  [ "$(wc -l < "$d/readme.tsv")" -gt 1 ] || { echo "SELFTEST_FAIL: no readme- rows are registered in $registry"; exit 1; }
  plant_arm ledger "$root/docs/LEDGER.md" "$d/ledger.tsv" covered candidates "$d" || exit 1
  blank_arm ledger "$root/docs/LEDGER.md" "$d/ledger.tsv" covered candidates 'on 640 in a fresh live run here' "$d" || exit 1
  plant_arm README "$root/README.md" "$d/readme.tsv" readme_covered readme_candidates "$d" || exit 1
  drift_arm README "$root/README.md" "$d/readme.tsv" 'v3 342/625' "$d" || exit 1
  # A README whose registered rows are all gone must fail the checker, not pass as "nothing to check".
  head -1 "$registry" > "$d/readme-empty.tsv"
  empty=$("$checker" "$d/readme-empty.tsv" "$root/README.md" "$root" 2>&1); rc=$?
  if [ "$rc" -eq 0 ]; then echo "SELFTEST_FAIL: a README with no registered claims passed the checker"; exit 1; fi
  case "$empty" in *"no enforced claims"*) ;; *) echo "SELFTEST_FAIL: empty-registry RED did not say so: $empty"; exit 1 ;; esac
  echo "SELFTEST_OK: checker arms; ledger: planted claim RED, removed registered claim RED; README: planted claim RED, drifted registered figure RED, no rows RED; both real documents at or above floor"
  exit 0
fi

if [ ! -x "$checker" ]; then
  echo "RED: claim checker missing or not executable: $checker"
  exit 1
fi
d=$(mktemp -d) || { echo "RED: cannot make temp dir"; exit 1; }
trap 'rm -rf "$d"' EXIT
split_claims ledger "$d/ledger.tsv"; split_claims readme "$d/readme.tsv"
"$checker" "$d/ledger.tsv" "$root/docs/LEDGER.md" "$root" || exit 1
coverage "$root/docs/LEDGER.md" "$d/ledger.tsv" ledger covered candidates || exit $?
"$checker" "$d/readme.tsv" "$root/README.md" "$root" || exit 1
coverage "$root/README.md" "$d/readme.tsv" README readme_covered readme_candidates
