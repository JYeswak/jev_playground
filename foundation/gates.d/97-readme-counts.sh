#!/usr/bin/env bash
# Stage 97 — the ledger's typed counts must match what the repository actually contains.
#
#   CONSUMER            foundation/gates.sh (this stage)
#   GATE                the stage-count word in docs/LEDGER.md equals the gates.d glob; every numeral
#                       "<N> gate stages", "<N> verdict rows", and "(A cleared, B held, C ruled out"
#                       in docs/LEDGER.md equals its machine source; no upstream repo is described as
#                       "not run" while a receipt for it exists
#   OBSERVED DEFECTS    four in one day, all typed next to something that grows: "not run" for a repo
#                       run hours earlier, "eight of ten" after an eleventh stage landed, "two of the
#                       nine gate stages", and a pasted ALL GREEN transcript ten lines long for an
#                       eleven-stage suite — plus three more the next day that sailed through 13 green
#                       stages: numeral "12 gate stages" for 13, and "25 verdict rows (7/9/8)" for 33
#                       (8/13/12), stated twice plus once more without a breakdown. The spelled-word
#                       check matched "Thirteen stages"; the numerals lived two lines below it.
#   RETIREMENT          when these counts are GENERATED into the ledger rather than typed, this stage
#                       has nothing left to check and should be deleted rather than kept green
#
# WHY A GATE RATHER THAN ANOTHER NOTE. The pattern was named in a commit message last tick and
# nothing enforced it, which is the definition of process. Every count it checks is derivable in one
# command, and every one of them was typed by hand anyway.
#
# SCOPE, RULED 2026-09-20 (not widened to all prose, not refused): only patterns with an exact
# machine source are checked — the gates.d glob, STATUS.tsv row and verdict counts. A numeral
# about anything else is free prose and out of scope for ever, because chasing every restatement
# of a number through prose false-positives by construction. The check is exact-equality on a
# fixed noun pattern, never "does this number appear somewhere", so a ledger that legitimately
# says "12" about something else cannot trip it.
#
# WHAT IT DELIBERATELY DOES NOT CHECK: prose accuracy, the fresh-clone pass figure (which requires
# building a worktree and is too slow for a per-commit gate), and the pasted transcript's contents.
# A gate that tried to verify a transcript would have to run the suite from inside the suite.
set -euo pipefail

root="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$root"
readme="${JEV_README:-docs/LEDGER.md}"

# Spelled numbers, because the ledger spells them. Extend when the suite outgrows the list; an
# unmatched count is reported rather than skipped, so this cannot silently stop checking.
num_word() {
  case "$1" in
    8) echo Eight ;; 9) echo Nine ;; 10) echo Ten ;; 11) echo Eleven ;; 12) echo Twelve ;;
    13) echo Thirteen ;; 14) echo Fourteen ;; 15) echo Fifteen ;; 16) echo Sixteen ;;
    17) echo Seventeen ;; 18) echo Eighteen ;; 19) echo Nineteen ;; 20) echo Twenty ;;
    21) echo Twenty-one ;; 22) echo Twenty-two ;; 23) echo Twenty-three ;; 24) echo Twenty-four ;;
    25) echo Twenty-five ;; *) echo "" ;;
  esac
}

if [[ "${1:-}" == "--selftest" ]]; then
  tmp="$(mktemp -d)"; trap 'find "$tmp" -mindepth 1 -delete 2>/dev/null; rmdir "$tmp" 2>/dev/null' EXIT
  fails=0; arms=0
  arm() {
    local name="$1" want="$2" file="$3" got
    JEV_README="$file" JEV_REPO="$root" bash "${BASH_SOURCE[0]}" >/dev/null 2>&1 && got=0 || got=$?
    arms=$((arms+1))
    if [[ "$got" == "$want" ]]; then printf '  ok   %-40s rc=%s\n' "$name" "$got"
    else printf '  FAIL %-40s rc=%s want=%s\n' "$name" "$got" "$want"; fails=$((fails+1)); fi
  }
  arm "live ledger agrees" 0 "$readme"

  n_now="$(find "$root/foundation/gates.d" -name '*.sh' | grep -c . || true)"
  wrong="$(num_word $((n_now - 1)))"
  sed "s/$(num_word "$n_now") stages/${wrong} stages/" "$readme" > "$tmp/miscount.md"
  arm "stage count off by one -> RED" 1 "$tmp/miscount.md"

  # A repo marked "not run" while its receipt exists on disk.
  printf '|`jev-mcp`|x|not run|y|\n' > "$tmp/stalerow.md"
  cat "$readme" >> "$tmp/stalerow.md"
  arm "row says not-run but receipt exists -> RED" 1 "$tmp/stalerow.md"

  # The exact escape of 2026-09-20: spelled word matched while the numerals below it
  # went stale ("12 gate stages" for 13, "25 verdict rows (7/9/8)" for 33 8/13/12).
  # The sed rewrites numerals the README already carries; the appended lines guarantee the
  # plant exists when the README states the count only in words (a sed over absent text
  # plants nothing, and this arm then passed vacuously on 2026-09-22).
  sed -E -e "s/[0-9]+ gate stages/$((n_now - 1)) gate stages/" \
         -e 's/[0-9]+ verdict rows/25 verdict rows/' \
         -e 's/\([0-9]+ cleared, [0-9]+ held, [0-9]+ ruled out/(7 cleared, 9 held, 8 ruled out/' \
         "$readme" > "$tmp/stalenumerals.md"
  printf '\n%s gate stages, 25 verdict rows (7 cleared, 9 held, 8 ruled out).\n' "$((n_now - 1))" \
    >> "$tmp/stalenumerals.md"
  arm "stale numerals under matching word -> RED" 1 "$tmp/stalenumerals.md"

  # The escape of 2026-09-22: a ledger generated through the Python eval kernel, whose `!` line
  # escape rewrote the hero line `![...](visual/hero.jpg)` into `__omp_shell("[...]")`.
  printf '__omp_shell("[hero](visual/hero.jpg)")\n' > "$tmp/harness.md"
  cat "$readme" >> "$tmp/harness.md"
  arm "harness markup in ledger -> RED" 1 "$tmp/harness.md"

  arm "missing ledger -> refuse" 2 "$tmp/absent.md"

  if (( fails > 0 )); then echo "stage 97 selftest: $fails arm(s) FAILED"; exit 1; fi
  echo "stage 97 selftest: $arms arms ok"
  exit 0
fi

[[ -f "$readme" ]] || { echo "FAIL  stage 97 ledger counts            $readme missing"; exit 2; }

problems=""

n_stages="$(find "$root/foundation/gates.d" -name '*.sh' | grep -c . || true)"
word="$(num_word "$n_stages")"
if [[ -z "$word" ]]; then
  problems="$problems|no spelled form for $n_stages stages; extend num_word rather than skipping"
elif ! grep -q "$word stages" "$readme"; then
  claimed="$(grep -oE '\b(Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen|Nineteen|Twenty(-[a-z]+)?) stages' "$readme" | head -1)"
  problems="$problems|ledger says '${claimed:-no stage count}' but foundation/gates.d holds $n_stages ($word)"
fi

# Numeral forms of the same two machine-sourced facts. Every occurrence must equal the
# machine count — the escape was a stale numeral two lines below a matching spelled word.
while IFS= read -r hit; do
  [[ "$hit" == "$n_stages" ]] || problems="$problems|ledger says '$hit gate stages' but foundation/gates.d holds $n_stages"
done < <(grep -oE '[0-9]+ gate stages' "$readme" | grep -oE '^[0-9]+' || true)

n_rows="$(grep -vc '^#\|^candidate\|^$' "$root/docs/demos/STATUS.tsv")"
n_cleared="$(awk -F'\t' '$4=="CLEARED"' "$root/docs/demos/STATUS.tsv" | grep -c . || true)"
n_held="$(awk -F'\t' '$4=="HELD"' "$root/docs/demos/STATUS.tsv" | grep -c . || true)"
n_out="$(awk -F'\t' '$4=="RULED_OUT"' "$root/docs/demos/STATUS.tsv" | grep -c . || true)"
while IFS= read -r hit; do
  [[ "$hit" == "$n_rows" ]] || problems="$problems|ledger says '$hit verdict rows' but STATUS.tsv holds $n_rows"
done < <(grep -oE '[0-9]+ verdict rows' "$readme" | grep -oE '^[0-9]+' || true)
while IFS= read -r triple; do
  want="($n_cleared cleared, $n_held held, $n_out ruled out"
  [[ "$triple" == "$want" ]] || problems="$problems|ledger breakdown '$triple)' differs from STATUS.tsv '$want)'"
done < <(grep -oE '\([0-9]+ cleared, [0-9]+ held, [0-9]+ ruled out' "$readme" || true)

# Any repo row claiming "not run" while docs/demos/upstream-repro holds a receipt naming it.
while IFS= read -r row; do
  repo="$(printf '%s' "$row" | sed -nE 's/^\|`([a-z0-9-]+)`.*/\1/p')"
  [[ -n "$repo" ]] || continue
  if find "$root/docs/demos/upstream-repro" -name "*${repo}*" 2>/dev/null | grep -q .; then
    problems="$problems|row for '$repo' says not run, but a receipt for it exists in docs/demos/upstream-repro"
  fi
done < <(grep -E '^\|`[a-z0-9-]+`.*not run' "$readme" || true)

# Harness markup that leaked into the public page instead of the Markdown it replaced.
while IFS= read -r hit; do
  problems="$problems|ledger line ${hit%%:*} carries harness markup instead of Markdown: ${hit#*:}"
done < <(grep -nE '__omp_shell\(|get_ipython\(\)' "$readme" | cut -c1-90 || true)

if [[ -n "$problems" ]]; then
  echo "FAIL  stage 97 ledger counts            a typed count no longer matches the repository."
  printf '%s' "$problems" | tr '|' '\n' | grep -v '^$' | sed 's/^/      /'
  echo "      Re-derive it; do not adjust it by arithmetic. That is how the last four went stale."
  exit 1
fi

echo "PASS  stage 97 ledger counts             $n_stages stages stated as '$word'; no stale not-run row"
exit 0
