#!/bin/sh
# feed-idle-panes.sh — wake an IDLE pane when the frontier has work, and nothing else.
#
# WHY. The cron tick wakes pane 1 only (`*/20 ntm --robot-send=jev --panes=1`), and the companion
# `fleet-idle-monitor` job is `--report-only` with four recorded defects. So panes 2 and 3 move
# only when the conductor dispatches, and the conductor is asleep between ticks or busy inside one.
# On 2026-09-19 `br ready` hit empty twice in ninety minutes while panes sat idle.
#
# WHAT IT REFUSES TO DO, because these are the ways this breaks the lane:
#   * It NEVER sends to a pane reporting is_working. tick.md: "Never push into a working pane —
#     robot-send types into its prompt and the interruption is invisible to you."
#   * It sends NOTHING when `br ready` is empty. No work, no poke. A wake with nothing to claim
#     trains panes to treat the signal as noise.
#   * It does NOT claim, file, or close beads. It points a pane at `br ready`; the pane self-claims,
#     which is the coordination this lane already decided on.
#   * It sends ONE message per run to ONE pane. Two idle panes racing for one bead is worse than a
#     pane waiting twenty minutes.
#
# --dry-run prints the decision and sends nothing. Run that first, always.
set -eu
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$root"
dry=${1:-}

ready=$(br ready 2>/dev/null | grep -cE '^[0-9]+\. \[' || true)
if [ "${ready:-0}" -eq 0 ]; then
    echo 'frontier empty — sending nothing. A wake with no work is noise.'
    exit 0
fi
if [ "${JEV_RERANK_SHADOW:-0}" = "1" ]; then
    br ready --json 2>/dev/null | node --experimental-strip-types "$root/scripts/br-rerank-shadow.mjs" >/dev/null 2>&1 || true
fi

# Health IDLE is a candidate, not proof. Capture-gap panes report
# is_idle=false and is_working=false while sitting at a prompt. Those are
# the panes that starve. Never send to is_working or rate-limited.
target=$(ntm --robot-agent-health=jev 2>/dev/null | python3 -c '
import json, sys
try:
    panes = json.load(sys.stdin).get("panes", {})
except Exception:
    sys.exit(0)
for name, v in sorted(panes.items(), key=lambda kv: kv[0]):
    if name == "1":
        continue
    st = v.get("local_state", {})
    if st.get("is_working") or st.get("is_rate_limited"):
        continue
    print(name)
    break
' 2>/dev/null || true)
if [ -z "$target" ]; then
    echo "frontier has $ready ready, but every worker is working or rate-limited — sending nothing."
    exit 0
fi

msg="AUTO-FEED: br ready has $ready item(s) and you are idle. Claim the highest-priority bead you did not author, move it in_progress under your actor name, and work it. Check the acceptance is OBTAINABLE before starting - re-derive any count or capability it asserts, from source, not from a README. If it is not obtainable, mark the bead blocked with the exact boundary instead of grinding. No dispatch is coming; this is the frontier feeding itself."

if [ "$dry" = '--dry-run' ]; then
    printf 'WOULD send to pane %s (ready=%s):\n  %s\n' "$target" "$ready" "$msg"
    exit 0
fi
msgfile=$(mktemp)
printf '%s\n' "$msg" > "$msgfile"
ntm send jev --pane="$target" --file "$msgfile" --json
rm -f "$msgfile"
printf 'fed pane %s (ready=%s)\n' "$target" "$ready"
