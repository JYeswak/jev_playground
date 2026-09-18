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
rc=0
printf 'JEV LANE STATUS  %s  HEAD=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(git rev-parse --short HEAD)"
printf '%s\n' "----------------------------------------------------------------------"

# ---------------------------------------------------------------- gauntlet state
printf '\nGAUNTLET (state of record: %s)\n' "$STATUS"
printf '  %-30s %-4s %-5s %-10s %-6s %s\n' CANDIDATE RUNG SCORE VERDICT AUTHOR BLOCKED_ON
missing=0; rows=0
while IFS=$'\t' read -r cand rung score verdict author receipt blocked; do
  case "$cand" in '#'*|''|candidate) continue ;; esac
  rows=$((rows+1))
  mark=''
  if [ -n "$receipt" ] && [ ! -e "$receipt" ]; then mark='  <<< RECEIPT MISSING'; missing=$((missing+1)); fi
  printf '  %-30s %-4s %-5s %-10s %-6s %s%s\n' "$cand" "$rung" "$score" "$verdict" "$author" "$blocked" "$mark"
done < "$STATUS"

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
else
  printf 'OK: %d candidates, every cited receipt exists on disk.\n' "$rows"
fi
exit "$rc"
