#!/usr/bin/env bash
# Stage 96 — the public verdict document must still agree with the state of record.
#
# Authorized by pane 2's ruling, which I did not get to make because I wrote both the register and
# the last two gates (docs/demos/duel-2/runs/ruling-verdict-status-coupling-20260918T171000Z.json,
# e448f00): "STATUS.tsv remains sole state of record; VERDICT.md stays hand-written for outsider
# persuasion, but requires a deterministic agreement gate."
#
#   CONSUMER            foundation/gates.sh (this stage) — publish cannot go green on a drifted verdict
#   GATE                per-candidate presence and category, per-category counts, zero-promotions claim
#   OBSERVED DEFECTS    "283,786 KLOC" for 283.786 (1000x, in two documents at once) · demo-1's kill
#                       citing the retracted 0.047% basis instead of the receipt's 0.0447%
#   RETIREMENT          a mechanically GENERATED verdict document, or a stronger semantic sync; never
#                       because the current run is green
#
# The duplication is deliberate: a 10-column TSV nobody outside the lane can read, and prose that a
# fresh-clone outsider grade rated PERSUADES. Two renderings of one truth is exactly the drift class
# this lane keeps finding in other people's work, so it gets a gate rather than a promise.
set -euo pipefail

root="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$root"

status="${JEV_STATUS:-docs/demos/STATUS.tsv}"
verdict="${JEV_VERDICT:-VERDICT.md}"
checker="foundation/verdict-status-agree.py"

if [[ "${1:-}" == "--selftest" ]]; then
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  fails=0; arms=0
  arm() { # name want_rc status_path verdict_path
    local name="$1" want="$2" got
    JEV_STATUS="$3" JEV_VERDICT="$4" JEV_REPO="$root" bash "${BASH_SOURCE[0]}" >/dev/null 2>&1 && got=0 || got=$?
    arms=$((arms+1))
    if [[ "$got" == "$want" ]]; then printf '  ok   %-38s rc=%s\n' "$name" "$got"
    else printf '  FAIL %-38s rc=%s want=%s\n' "$name" "$got" "$want"; fails=$((fails+1)); fi
  }

  arm "baseline: live pair agrees" 0 "$status" "$verdict"

  # A candidate silently dropped from the prose. This is the drift the gate exists for: STATUS keeps
  # judging it, the public document stops mentioning it, and nothing else notices.
  grep -v '\*\*COD-H5' "$verdict" > "$tmp/dropped.md"
  arm "candidate dropped from VERDICT -> RED" 1 "$status" "$tmp/dropped.md"

  # A verdict flipped in STATUS without the prose following. Category membership must catch it.
  sed 's/^COD-H5-compaction-integrity\t\([^\t]*\)\t\([^\t]*\)\tCLEARED/COD-H5-compaction-integrity\t\1\t\2\tRULED_OUT/' "$status" > "$tmp/flipped.tsv"
  arm "verdict flipped in STATUS -> RED" 1 "$tmp/flipped.tsv" "$verdict"

  # A heading count that no longer matches the rows beneath it — the staleness class this repo has
  # corrected six times in one day, every time in a number written down rather than derived.
  sed 's/## The four kills/## The three kills/' "$verdict" > "$tmp/miscount.md"
  arm "heading count contradicts STATUS -> RED" 1 "$status" "$tmp/miscount.md"

  # An empty scan set must never read as agreement.
  printf 'candidate\trung\tscore\tverdict\n' > "$tmp/empty.tsv"
  arm "empty STATUS -> RED, not agreement" 1 "$tmp/empty.tsv" "$verdict"

  # A missing input is a refusal, not a pass.
  arm "missing VERDICT -> refuse" 2 "$status" "$tmp/absent.md"

  if (( fails > 0 )); then echo "stage 96 selftest: $fails arm(s) FAILED"; exit 1; fi
  echo "stage 96 selftest: $arms arms ok"
  exit 0
fi

if [[ ! -f "$checker" ]]; then
  echo "FAIL  stage 96 verdict/status agreement  checker missing: $checker"
  exit 1
fi

out="$(python3 "$checker" "$status" "$verdict" 2>&1)" && rc=0 || rc=$?
case "$rc" in
  0) echo "PASS  stage 96 verdict/status agreement  ${out#PASS  }" ;;
  2) echo "FAIL  stage 96 verdict/status agreement  input unreadable — refusing to report agreement"
     printf '%s\n' "$out" | sed 's/^/      /' ;;
  *) echo "FAIL  stage 96 verdict/status agreement  the public verdict has drifted from the record"
     printf '%s\n' "$out" | sed 's/^/      /' ;;
esac
exit "$rc"
