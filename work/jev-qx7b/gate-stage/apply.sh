#!/bin/sh
# jev-qx7b: put the staged stage-15 README pass into foundation/gates.d and turn the README claim
# rows on. Run from the repository root in a session launched with KIT_GATE_EDIT=1: kit-guard B7
# refuses agent edits to foundation/gates.d/*, and this change needs exactly one of them.
#
# Before this runs, the 184 `readme-` rows already sit in foundation/kit/claims.tsv with enforce=no,
# so the current stage 15 skips them (they are not in docs/LEDGER.md) and stays green. The staged
# 15-kit-claim.sh routes `readme-` rows to README.md and every other row to docs/LEDGER.md.
# After this runs, delete work/jev-qx7b/gate-stage/ (git rm) in the same commit: the live gate then
# lives in foundation/gates.d/ and the staged copy would only drift.
set -eu
stage=work/jev-qx7b/gate-stage
want_sha=$(cat "$stage/15-kit-claim.sh.sha256")
[ "$(shasum -a 256 "$stage/15-kit-claim.sh" | cut -d' ' -f1)" = "$want_sha" ] || {
  echo "refuse: staged gate does not match its recorded sha256 (edited after it was tested)"; exit 1; }
off=$(awk -F'\t' '$1 ~ /^readme-/ && $6 == "no"' foundation/kit/claims.tsv | wc -l | tr -d ' ')
on=$(awk -F'\t' '$1 ~ /^readme-/ && $6 == "yes"' foundation/kit/claims.tsv | wc -l | tr -d ' ')
[ "$off" -gt 0 ] && [ "$on" -eq 0 ] || { echo "refuse: expected only enforce=no readme- rows (no=$off yes=$on)"; exit 1; }
cp "$stage/15-kit-claim.sh" foundation/gates.d/15-kit-claim.sh
tmp=$(mktemp)
awk -F'\t' -v OFS='\t' '$1 ~ /^readme-/ && $6 == "no" { $6 = "yes" } { print }' foundation/kit/claims.tsv > "$tmp"
cat "$tmp" > foundation/kit/claims.tsv
rm -f "$tmp"
echo "flipped $off readme- rows to enforce=yes"
# The two prose statements that describe stage 15 change in the same step, each anchored on an exact
# sentence that must occur once (the edit refuses otherwise).
python3 - <<'PY'
def sub(path, old, new):
    text = open(path).read()
    assert text.count(old) == 1, (path, "anchor must occur exactly once")
    open(path, "w").write(text.replace(old, new))
sub("README.md",
    "It does not check the prose of this README. Run it for the current counts.",
    "It also checks this README: each number-bearing or pass/fail sentence must match a row labelled `readme-` in that file, so a changed figure, a new unregistered claim, or a proof file that lost its text turns the stage red. Run it for the current counts.")
sub("GATES.md",
    "and removed-claim RED arms. | `foundation/gates.sh` |",
    "and removed-claim RED arms. Rows labelled `readme-` are `README.md` claims, checked the same way against `README.md` (floor keys `readme_covered`, `readme_candidates`); the selftest also proves the README's planted-claim, drifted-figure and no-rows RED arms (jev-qx7b). | `foundation/gates.sh` |")
PY
bash foundation/gates.d/15-kit-claim.sh | tail -3
bash foundation/gates.d/15-kit-claim.sh --selftest
bash foundation/gates.d/17-kit-demotion.sh | tail -2
