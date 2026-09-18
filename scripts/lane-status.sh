#!/usr/bin/env bash
# lane-status.sh — DERIVE the jev lane's live status. Never report it from memory.
#
# WHY THIS EXISTS (Joshua, 2026-09-18): "your cron should remind you to pull live status - keep
# close tabs on what work has been done, what is left, it should not come from memory - it needs
# to be up to date."
#
# The deeper defect this fixes: the conductor's status reports were assembled from PROSE IT HAD
# WRITTEN ITSELF (PLAN.md sections, its own commit messages). Prose is memory with extra steps. A
# verdict recorded in a paragraph cannot be checked against the artifact it claims.
#
# So: docs/demos/STATUS.tsv is the machine-readable state of record, and this script
#   (a) renders it,
#   (b) VERIFIES every cited receipt actually exists on disk,
#   (c) derives everything else live — beads, commits, uncommitted deliveries, worker panes,
#       artifact inventory with byte counts.
#
# FAIL-CLOSED: a STATUS row citing a receipt that does not exist exits 3. That is the known-bad
# this script fires on: a verdict with no evidence behind it.
set -uo pipefail

REPO="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$REPO" || { echo "lane-status: repo missing: $REPO" >&2; exit 2; }
# Test hook: point at an alternate state file. Exists so the missing-receipt RED arm can be proven
# to DISCRIMINATE — real receipts present, one planted bogus row — without mutating the shared
# worktree, which three panes are reading. A detector that fires on every row has not discriminated.
STATUS="${JEV_STATUS:-docs/demos/STATUS.tsv}"
[ -f "$STATUS" ] || { echo "lane-status: $STATUS missing — no state of record" >&2; exit 2; }

# ------------------------------------------------- receipt integrity (pane 2, RULE_receipt_integrity_COD.md)
# Ruling (c): CONTENT-NORMALISED digests — strip only the final run of terminal whitespace bytes,
# hash everything else. Chosen because the autofix hook that runs on EVERY commit appends trailing
# newlines to JSON receipts; a raw-sha gate would be broken by our own hook on every commit, which
# by §3h doctrine is a dead gate on arrival ("a gate nothing can satisfy is not a high bar").
# Normalisation is deliberately minimal: any NON-terminal byte change still drifts.
#
# Pane 2's binding constraint, quoted: "current existence-only behavior must not be mislabeled
# integrity." Existence and integrity are reported as SEPARATE claims with separate counts below.
#
# Scope, stated because it is not a repair: when this landed, pane 2 measured ZERO digest-dependent
# lane claims (digest-dependency-20260918T085000Z.json). This prevents a future failure; it does not
# fix a past one.
norm_digest() { perl -0777 -pe 's/\s+\z//' "$1" 2>/dev/null | shasum -a 256 | cut -c1-16; }

# COLUMN COLLISION, resolved in the author's favour: pane 3's CONCURRENCE_archaeology_MU.md proposed
# `kill_concurrence` at column 8 with a fail-closed schema rule; this script had already implemented
# `receipt_digest` at column 8. Both said "append after blocked_on". Concurrence keeps 8 (it is a
# verdict-semantic field and its author specified it); the digest moves to 9 (an integrity artifact,
# last). Recorded rather than silently reassigned — two independent authors appending to the same
# state of record is a collision class that will recur.
#
#   col 8  kill_concurrence  author-self | nonauthor-kill:<receipt>@<sha> | concur:<pane>:<r>@<sha> | none
#          empty ==> row is not RULED_OUT. A RULED_OUT row with an empty col 8 is a SCHEMA VIOLATION.
#   col 9  receipt_digest    content-normalised sha256 (16 hex); empty ==> existence-only
#
# --pin: emit STATUS.tsv with column 9 recomputed, to STDOUT. Never mutates the shared state file in
# place — three panes read it, and a script that silently rewrites the state of record is the exact
# hazard the autofix hook already demonstrated.
if [ "${1:-}" = '--pin' ]; then
  changed=0
  while IFS= read -r line; do
    case "$line" in '#'*|'') printf '%s\n' "$line"; continue ;; esac
    IFS=$'\037' read -r c r s v a rcpt b concur old <<<"$(printf '%s' "$line" | tr '\t' '\037')"
    [ "$c" = candidate ] && { printf '%s\n' "$line"; continue; }
    new=''
    if [ -n "$rcpt" ] && [ -f "$rcpt" ]; then new=$(norm_digest "$rcpt"); fi
    [ "$new" != "${old:-}" ] && changed=$((changed+1))
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$r" "$s" "$v" "$a" "$rcpt" "$b" "$concur" "$new"
  done < "$STATUS"
  printf 'lane-status --pin: %d row digest(s) would change. Redirect to apply.\n' "$changed" >&2
  exit 0
fi
rc=0
printf 'JEV LANE STATUS  %s  HEAD=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(git rev-parse --short HEAD)"
printf '%s\n' "----------------------------------------------------------------------"

# ---------------------------------------------------------------- gauntlet state
printf '\nGAUNTLET (state of record: %s)\n' "$STATUS"
printf '  %-30s %-4s %-5s %-10s %-6s %s\n' CANDIDATE RUNG SCORE VERDICT AUTHOR BLOCKED_ON
missing=0; rows=0; with_receipt=0; pinned=0; drifted=0; unpinned=0
ruled_out=0; concur_missing=0
# TAB IS IFS-WHITESPACE IN BASH: `IFS=$'\t' read` COLLAPSES consecutive tabs, so an EMPTY middle
# column makes every later field shift left. Measured 2026-09-18: with col-8 empty on 13 rows, `concur`
# swallowed the digest and `digest` came back empty — integrity_checked reported 4 (exactly the 4
# RULED_OUT rows, whose col 8 is non-empty) instead of 17. Splitting on \037 (NOT whitespace) preserves
# empty fields. BSD tr has no \x hex escape — octal \037 is portable, \x1f silently corrupted the split.
# Do not "simplify" this back to a tab IFS.
while IFS=$'\037' read -r cand rung score verdict author receipt blocked concur digest; do
  case "$cand" in '#'*|''|candidate) continue ;; esac
  rows=$((rows+1))
  mark=''
  if [ -n "$receipt" ]; then
    with_receipt=$((with_receipt+1))
    if [ ! -e "$receipt" ]; then
      mark='  <<< RECEIPT MISSING'; missing=$((missing+1))
    elif [ ! -f "$receipt" ]; then
      mark='  (dir receipt: existence only)'; unpinned=$((unpinned+1))
    elif [ -n "${digest:-}" ]; then
      pinned=$((pinned+1)); have=$(norm_digest "$receipt")
      if [ "$have" != "$digest" ]; then
        mark="  <<< DIGEST DRIFT want=$digest have=$have"; drifted=$((drifted+1))
      fi
    else
      unpinned=$((unpinned+1))
    fi
  fi
  # Pane 3's mechanical watcher, promoted from prose into this gate: a RULED_OUT row with no
  # kill_concurrence value is a schema violation. "The condition fires observably or the file is red."
  # Deliberately OUTSIDE the receipt branch: a receiptless RULED_OUT row must still be caught.
  if [ "$verdict" = RULED_OUT ]; then
    ruled_out=$((ruled_out+1))
    if [ -z "${concur:-}" ]; then
      mark="$mark  <<< NO kill_concurrence"; concur_missing=$((concur_missing+1))
    fi
  fi
  printf '  %-30s %-4s %-5s %-10s %-6s %s%s\n' "$cand" "$rung" "$score" "$verdict" "$author" "$blocked" "$mark"
done < <(tr '\t' '\037' < "$STATUS")

printf '\nRECEIPT VERIFICATION (existence and integrity are SEPARATE claims — do not read one as the other)\n'
printf '  existence_checked: %-4d missing:  %d\n' "$with_receipt" "$missing"
printf '  integrity_checked: %-4d drifted:  %d   (content-normalised sha256; terminal whitespace stripped)\n' "$pinned" "$drifted"
printf '  NOT integrity-checked (no pinned digest): %d   <- existence proven, bytes unverified\n' "$unpinned"
printf '\nKILL CONCURRENCE (§3c rule 3, demoted to guidance — checked mechanically, not by a volunteer)\n'
printf '  ruled_out rows: %-4d missing kill_concurrence: %d\n' "$ruled_out" "$concur_missing"

# ---------------------------------------------------------------- derived counts
printf '\nDERIVED FROM %s (not from prose)\n' "$STATUS"
awk -F'\t' '!/^#/ && $1!="candidate" && NF>=4 {v[$4]++; r[$2]++} END {
  printf "  verdicts:"; for (k in v) printf " %s=%d", k, v[k]; printf "\n";
  printf "  by rung :"; for (k in r) printf " r%s=%d", k, r[k]; printf "\n";
}' "$STATUS"
printf '  promoted: %s   (rung-5 rows)\n' "$(awk -F'\t' '!/^#/ && $2==5' "$STATUS" | wc -l | tr -d ' ')"
printf '  highest unscored candidate: %s\n' \
  "$(awk -F'\t' '!/^#/ && $1!="candidate" && $2==0 {print $3"\t"$1}' "$STATUS" | sort -rn | head -1 | cut -f2)"

# ---------------------------------------------------------------- live surfaces
printf '\nBEADS (live)\n'
printf '  open/in-progress: %s   closed: %s\n' \
  "$(br list 2>/dev/null | grep -cE '^[○◐]' || echo '?')" \
  "$(br list --status closed 2>/dev/null | grep -cE '^✓' || echo '?')"

printf '\nARTIFACTS (bytes, derived)\n'
for d in docs/demos/contracts docs/demos/duel-1 docs/demos/duel-2; do
  [ -d "$d" ] || continue
  n=$(find "$d" -name '*.md' -o -name '*.json' | wc -l | tr -d ' ')
  b=$(find "$d" -type f \( -name '*.md' -o -name '*.json' \) -exec cat {} + 2>/dev/null | wc -c | tr -d ' ')
  printf '  %-26s %3s files  %9s bytes\n' "$d" "$n" "$b"
done
printf '  %-26s %3s files  %9s bytes\n' 'plan corpus' \
  "$(ls docs/demos/PLAN.md docs/demos/BEAD-TEMPLATE.md docs/demos/contracts/*.md 2>/dev/null | wc -l | tr -d ' ')" \
  "$(cat docs/demos/PLAN.md docs/demos/BEAD-TEMPLATE.md docs/demos/contracts/*.md 2>/dev/null | wc -c | tr -d ' ')"

printf '\nUNCOMMITTED DELIVERIES (work sitting in the tree)\n'
git status --porcelain | sed 's/^/  /' | head -12
[ -z "$(git status --porcelain)" ] && printf '  (clean)\n'

printf '\nLAST 6 COMMITS\n'
git log --oneline -6 | sed 's/^/  /'

printf '\nWORKER PANES (workers-only; pane_index 0 is the user shell)\n'
if [ -x "$HOME/.local/bin/fleet-idle-monitor" ]; then
  FLEET_SESSION=jev FLEET_QUEUE_REPO="$REPO" "$HOME/.local/bin/fleet-idle-monitor" --report-only 2>&1 \
    | grep -vE 'pane=%70' | sed 's/^/  /' | head -8
  printf '  NOTE: this binary has 3 recorded defects (PLAN.md §6). Do NOT read WORKING as proof.\n'
else
  printf '  fleet-idle-monitor not installed\n'
fi

# ---------------------------------------------------------------- verdict
printf '\n%s\n' "----------------------------------------------------------------------"
if [ "$missing" -gt 0 ]; then
  printf 'FAIL: %d of %d STATUS rows cite a receipt that does not exist.\n' "$missing" "$rows"
  printf 'A verdict with no artifact behind it is the known-bad this script fires on.\n'
  rc=3
elif [ "$concur_missing" -gt 0 ]; then
  printf 'FAIL: %d of %d RULED_OUT rows carry no kill_concurrence value.\n' "$concur_missing" "$ruled_out"
  printf 'A kill whose authorship boundary is unrecorded is the same known-bad as a missing receipt.\n'
  rc=3
elif [ "$drifted" -gt 0 ]; then
  printf 'FAIL: %d of %d integrity-checked receipts drifted from their pinned digest.\n' "$drifted" "$pinned"
  printf 'Content changed beyond terminal whitespace. Re-pin deliberately or explain the change.\n'
  rc=4
else
  printf 'OK: %d candidates. %d receipt(s) exist; %d integrity-checked, %d existence-only; %d/%d kills concurrence-recorded.\n' \
    "$rows" "$with_receipt" "$pinned" "$unpinned" "$((ruled_out-concur_missing))" "$ruled_out"
fi
exit "$rc"
