#!/usr/bin/env bash
# Stage 97 — the README's typed counts must match what the repository actually contains.
#
#   CONSUMER            foundation/gates.sh (this stage)
#   GATE                the stage-count word in README.md equals the gates.d glob; no upstream repo
#                       is described as "not run" while a receipt for it exists
#   OBSERVED DEFECTS    four in one day, all typed next to something that grows: "not run" for a repo
#                       run hours earlier, "eight of ten" after an eleventh stage landed, "two of the
#                       nine gate stages", and a pasted ALL GREEN transcript ten lines long for an
#                       eleven-stage suite
#   RETIREMENT          when these counts are GENERATED into the README rather than typed, this stage
#                       has nothing left to check and should be deleted rather than kept green
#
# WHY A GATE RATHER THAN ANOTHER NOTE. The pattern was named in a commit message last tick and
# nothing enforced it, which is the definition of process. Every count it checks is derivable in one
# command, and every one of them was typed by hand anyway.
#
# WHAT IT DELIBERATELY DOES NOT CHECK: prose accuracy, the fresh-clone pass figure (which requires
# building a worktree and is too slow for a per-commit gate), and the pasted transcript's contents.
# A gate that tried to verify a transcript would have to run the suite from inside the suite.
set -euo pipefail

root="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$root"
readme="${JEV_README:-README.md}"

# Spelled numbers, because the README spells them. Extend when the suite outgrows the list; an
# unmatched count is reported rather than skipped, so this cannot silently stop checking.
num_word() {
  case "$1" in
    8) echo Eight ;; 9) echo Nine ;; 10) echo Ten ;; 11) echo Eleven ;; 12) echo Twelve ;;
    13) echo Thirteen ;; 14) echo Fourteen ;; 15) echo Fifteen ;; *) echo "" ;;
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
  arm "live README agrees" 0 "$readme"

  n_now="$(find "$root/foundation/gates.d" -name '*.sh' | grep -c . || true)"
  wrong="$(num_word $((n_now - 1)))"
  sed "s/$(num_word "$n_now") stages/${wrong} stages/" "$readme" > "$tmp/miscount.md"
  arm "stage count off by one -> RED" 1 "$tmp/miscount.md"

  # A repo marked "not run" while its receipt exists on disk.
  printf '|`jev-mcp`|x|not run|y|\n' > "$tmp/stalerow.md"
  cat "$readme" >> "$tmp/stalerow.md"
  arm "row says not-run but receipt exists -> RED" 1 "$tmp/stalerow.md"

  arm "missing README -> refuse" 2 "$tmp/absent.md"

  if (( fails > 0 )); then echo "stage 97 selftest: $fails arm(s) FAILED"; exit 1; fi
  echo "stage 97 selftest: $arms arms ok"
  exit 0
fi

[[ -f "$readme" ]] || { echo "FAIL  stage 97 readme counts            $readme missing"; exit 2; }

problems=""

n_stages="$(find "$root/foundation/gates.d" -name '*.sh' | grep -c . || true)"
word="$(num_word "$n_stages")"
if [[ -z "$word" ]]; then
  problems="$problems|no spelled form for $n_stages stages; extend num_word rather than skipping"
elif ! grep -q "$word stages" "$readme"; then
  claimed="$(grep -oE '\b(Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen) stages' "$readme" | head -1)"
  problems="$problems|README says '${claimed:-no stage count}' but foundation/gates.d holds $n_stages ($word)"
fi

# Any repo row claiming "not run" while docs/demos/upstream-repro holds a receipt naming it.
while IFS= read -r row; do
  repo="$(printf '%s' "$row" | sed -nE 's/^\|`([a-z0-9-]+)`.*/\1/p')"
  [[ -n "$repo" ]] || continue
  if find "$root/docs/demos/upstream-repro" -name "*${repo}*" 2>/dev/null | grep -q .; then
    problems="$problems|row for '$repo' says not run, but a receipt for it exists in docs/demos/upstream-repro"
  fi
done < <(grep -E '^\|`[a-z0-9-]+`.*not run' "$readme" || true)

if [[ -n "$problems" ]]; then
  echo "FAIL  stage 97 readme counts            a typed count no longer matches the repository."
  printf '%s' "$problems" | tr '|' '\n' | grep -v '^$' | sed 's/^/      /'
  echo "      Re-derive it; do not adjust it by arithmetic. That is how the last four went stale."
  exit 1
fi

echo "PASS  stage 97 readme counts             $n_stages stages stated as '$word'; no stale not-run row"
exit 0
