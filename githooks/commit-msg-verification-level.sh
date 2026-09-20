#!/usr/bin/env bash
# commit-msg-verification-level.sh — a commit subject must say what it PROVED, or it is refused.
#
# WHY THIS EXISTS. Measured 2026-08-22 from the Dicklesworthstone mirror: franken_lean shipped
# 1,353 commits in 24 h, avg 1.0 file / 61 lines, and 227 of the subjects literally say
# "code-first, batch-test pending". frankensqlite: "lexer-level-verified only". The subject
# carries the epistemic state of the commit, so the ledger never overclaims. Ours said
# "verified" with no level, and four gates shipped that night with a verdict they could not
# distinguish from its opposite (docs-staleness, composer_nonempty, check-lock, UNRUN→red).
#
# Jeff, in his own pre-commit header: "It is a missing mechanism, not a knowledge gap. Four
# separate agents violated the rule on 2026-07-25 alone, each of whom knew it and had followed
# it correctly earlier the same day... nothing fails at commit time, and the agent who forgets
# is never the one who sees the red." This is the mechanism.
#
# THE LEVELS, rank-ordered. A subject claims exactly one. Higher is stronger.
#   pending    code-first, nothing run            (Jeff: "code-first, batch-test pending")
#   selftest   the gate's own --selftest passed
#   test       the suite is green
#   mutation   named killers die on a planted mutant
#   receipt    the commit records or explains a result (markdown only). The most common
#              thing this repo commits — added 2026-09-20 after the level mine showed
#              docs-only oracle|live on 183 commits and the hook itself refused
#              '[receipt-candidate]': the vocabulary had no word, so prose borrowed one.
#
# FORM. Either `[level]` anywhere in the subject, or the Jeff-style prose tail
# `(…, <level> pending)` / `<level>-verified`. Merge commits, reverts, and fixups are exempt
# (they carry no new claim). A subject with NO level is refused with the list.
#
# FAIL-CLOSED. A malformed or unreadable message file refuses. An empty level list is an
# authoring error and refuses. --selftest proves both legs: known-bad refused, known-good passed.
set -uo pipefail

LEVELS=(pending receipt selftest test mutation oracle live)

usage() { printf 'usage: commit-msg-verification-level.sh <commit-msg-file> | --selftest\n' >&2; }

level_of() {
  # prints the level claimed by the subject, or nothing
  local subject="$1" lv
  for lv in "${LEVELS[@]}"; do
    if printf '%s' "$subject" | grep -qiE "\[${lv}\]|\b${lv}[- ](pending|verified)\b|\b${lv}-level\b"; then
      printf '%s' "$lv"; return 0
    fi
  done
  return 1
}

exempt() {
  local subject="$1"
  printf '%s' "$subject" | grep -qiE '^(Merge |Revert |fixup! |squash! )'
}

staged_docs_only() {
  # exit 0 iff the staged paths are ALL markdown/prose (or there are none we can
  # see — invisible means silent, never a suggestion). Never fails: any git error
  # or empty set returns 1, because a suggestion must not nag on uncertainty.
  local paths p
  paths=$(git diff --cached --name-only 2>/dev/null) || return 1
  [ -n "$paths" ] || return 1
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    case "$p" in *.md|*.mdx|*.txt|*.mdwn) ;; *) return 1 ;; esac
  done <<<"$paths"
  return 0
}

check_file() {
  local f="$1" subject lv
  [ -r "$f" ] || { printf 'verification-level REFUSE reason=unreadable-message-file path=%s\n' "$f"; return 1; }
  subject=$(grep -m1 -v '^#' "$f" | head -1)
  [ -n "$subject" ] || { printf 'verification-level REFUSE reason=empty-subject\n'; return 1; }
  if exempt "$subject"; then
    printf 'verification-level PASS exempt=%s\n' "${subject%% *}"; return 0
  fi
  if lv=$(level_of "$subject"); then
    if { [ "$lv" = oracle ] || [ "$lv" = live ]; } && staged_docs_only; then
      printf 'verification-level PASS level=%s\n' "$lv"
      printf '  suggestion: docs-only diff under [%s] — consider [receipt] (the commit records a result). Passing anyway; 15/15 sampled docs-only oracle|live were genuine records, not overclaims.\n' "$lv" >&2
    else
      printf 'verification-level PASS level=%s\n' "$lv"
    fi
    return 0
  fi
  printf 'verification-level REFUSE reason=no-level subject=%q\n' "$subject"
  printf '  a commit subject must say what it PROVED. add one of: %s\n' "${LEVELS[*]}" >&2
  printf '  forms: "[test]"  or  "(code-first, test pending)"  or  "selftest-verified"\n' >&2
  printf '  the level stands ALONE in its brackets: "[test]" not "[cp-123; test]" — a bead id is not a claim\n' >&2
  printf '  example: "fix(gate): split admission lock from worker lock [selftest]"\n' >&2
  return 1
}

selftest() {
  local tmp fails=0
  tmp=$(mktemp -d) || exit 2
  [ "${#LEVELS[@]}" -gt 0 ] || { echo "selftest: FAIL — empty level list (authoring error)"; exit 1; }

  # KNOWN-BAD: no level ⇒ must REFUSE
  printf 'feat(oracles): wire domain-indexed external oracle catalogue\n' >"$tmp/bad1"
  check_file "$tmp/bad1" >/dev/null 2>&1 && { echo "selftest: FAIL — bare subject accepted (known-bad leg)"; fails=$((fails+1)); }
  # KNOWN-BAD: the word "verified" with no level ⇒ must REFUSE (the overclaim we are killing)
  printf 'fix(controller): distinguish autosuggestion, verified\n' >"$tmp/bad2"
  check_file "$tmp/bad2" >/dev/null 2>&1 && { echo "selftest: FAIL — bare 'verified' accepted (overclaim leg)"; fails=$((fails+1)); }
  # KNOWN-BAD: level bundled with a bead id ⇒ must REFUSE (measured: control-plane wrote
  # "[cp-spcc; test]" on its first commit through the hook, 2026-08-22 05:5x; a bead id is not a claim)
  printf 'fix(loop): bound the tick wait [cp-spcc; test]\n' >"$tmp/bad3"
  check_file "$tmp/bad3" >/dev/null 2>&1 && { echo "selftest: FAIL — bundled [bead; level] accepted"; fails=$((fails+1)); }
  # KNOWN-BAD: unreadable file ⇒ must REFUSE (fail-closed)
  check_file "$tmp/does-not-exist" >/dev/null 2>&1 && { echo "selftest: FAIL — missing file accepted (fail-open)"; fails=$((fails+1)); }

  # KNOWN-GOOD: each form must PASS
  printf 'fix(gate): split admission lock [selftest]\n' >"$tmp/good1"
  check_file "$tmp/good1" >/dev/null 2>&1 || { echo "selftest: FAIL — [selftest] bracket form refused"; fails=$((fails+1)); }
  printf 'fln-l8f: nothing asked whether there was room (code-first, test pending)\n' >"$tmp/good2"
  check_file "$tmp/good2" >/dev/null 2>&1 || { echo "selftest: FAIL — Jeff prose form refused"; fails=$((fails+1)); }
  printf 'feat(p9): scripts registry, oracle-verified\n' >"$tmp/good3"
  check_file "$tmp/good3" >/dev/null 2>&1 || { echo "selftest: FAIL — '<level>-verified' form refused"; fails=$((fails+1)); }
  printf 'Merge remote-tracking branch origin/main\n' >"$tmp/good4"
  check_file "$tmp/good4" >/dev/null 2>&1 || { echo "selftest: FAIL — merge commit not exempt (over-strict leg)"; fails=$((fails+1)); }
  # KNOWN-GOOD: a level word used as ordinary prose must NOT count as a claim
  printf 'docs: note that the live demo row is still in production\n' >"$tmp/prose"
  check_file "$tmp/prose" >/dev/null 2>&1 && { echo "selftest: FAIL — 'live' as prose accepted as a level claim"; fails=$((fails+1)); }

  # RECEIPT LEVEL + SUGGESTION (2026-09-20): hermetic temp-repo arms, never the real index.
  t2=$(mktemp -d) || exit 2
  ( cd "$t2" && git init -q . && git config user.email t@t && git config user.name t \
    && printf 'x\n' > r.md && git add r.md && printf 'docs: record the verdict [receipt]\n' >"$tmp/goodR" )
  ( cd "$t2" && out=$(check_file "$tmp/goodR" 2>&1) && grep -q 'PASS level=receipt' <<<"$out" ) \
    || { echo "selftest: FAIL — [receipt] not accepted"; fails=$((fails+1)); }
  ( cd "$t2" && printf 'docs: record the verdict [oracle]\n' >"$tmp/sug" \
    && out=$(check_file "$tmp/sug" 2>&1) && grep -q 'suggestion:.*receipt' <<<"$out" ) \
    || { echo "selftest: FAIL — docs-only [oracle] passed WITHOUT suggestion"; fails=$((fails+1)); }
  ( cd "$t2" && printf 'x\n' > run.sh && git add run.sh && printf 'feat: wire the gate [oracle]\n' >"$tmp/nosug" \
    && out=$(check_file "$tmp/nosug" 2>&1) && ! grep -q 'suggestion:' <<<"$out" ) \
    || { echo "selftest: FAIL — runnable [oracle] wrongly suggested receipt"; fails=$((fails+1)); }
  rm -rf "$t2"

  rm -rf "$tmp"
  if [ "$fails" -eq 0 ]; then echo "selftest: PASS (4 known-bad refused, 4 known-good passed, 1 prose-not-claim refused, 3 receipt/suggestion arms)"; exit 0; fi
  echo "selftest: FAIL ($fails leg(s))"; exit 1
}

case "${1:-}" in
  --selftest) selftest ;;
  -h|--help|'') usage; exit 2 ;;
  *) check_file "$1" ;;
esac
