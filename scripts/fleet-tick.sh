#!/usr/bin/env bash
# fleet-tick.sh — one command the conductor runs EVERY tick, so an idle worker cannot be missed.
#
# WHY. Measured 2026-09-20: pane 4 sat idle through a full tick and Joshua caught it, not me.
# Twice. The conductor's attention is the scarce resource and "I'll remember to check" is not a
# mechanism. This is.
#
# WHAT IT REFUSES TO DO:
#   * It does NOT dispatch. Two agents racing one unit is worse than one waiting a tick, and the
#     selection rules (ground-truth-exists > prevalence > cost > leverage) are the conductor's job.
#   * It does NOT read another agent's transcript to infer intent. Ask the pane; that is what the
#     ntm callback exists for.
#
# HONEST LIMIT, stated because the alternative is a fooled certificate: working-vs-idle here is a
# HEURISTIC on the rendered footer (omp draws a braille spinner and an elapsed clock while a turn
# is in flight). ntm's own health binary has four recorded defects (PLAN.md §6), so neither oracle
# is authoritative. A pane reported IDLE that is actually mid-turn costs an interrupted agent; the
# conservative read is to confirm with a cheap question before dispatching into a busy pane.
set -uo pipefail
session=${1:-jev}

tmux has-session -t "$session" 2>/dev/null || { echo "no tmux session '$session'"; exit 2; }

printf '%-6s %-28s %-8s %s\n' PANE MODEL STATE TAIL
idle_list=""
# Pane 0 is the human, pane 1 is the conductor; workers are 2+.
for idx in $(tmux list-panes -t "$session" -F '#{pane_index}' | sort -n); do
    [ "$idx" -ge 2 ] || continue
    tail3=$(tmux capture-pane -p -t "$session.$idx" -S -6 | grep -vE '^[[:space:]]*$' | tail -3)
    model=$(printf '%s' "$tail3" | grep -oE '(Muse Spark [0-9.]+|Grok [0-9.]+|Opus [0-9]+|GPT[- ][0-9.]+)' | head -1)
    # A braille spinner or an elapsed clock in the footer means a turn is in flight.
    if printf '%s' "$tail3" | grep -qE '[⠁-⣿]|· [0-9]+m ·|> [0-9]+m >'; then
        state=working
    else
        state=IDLE
        idle_list="$idle_list $idx"
    fi
    printf '%-6s %-28s %-8s %s\n' "$idx" "${model:-unknown}" "$state" "$(printf '%s' "$tail3" | tail -1 | cut -c1-48)"
done

echo
if [ -n "$idle_list" ]; then
    echo "IDLE PANES:$idle_list — dispatch or park them THIS tick, do not carry them."
    echo "Every dispatch MUST end with the callback, or the pane is invisible to you:"
    echo '  ntm --robot-send=jev --panes=1 --msg="CALLBACK-P<n>-<UNIT>-<DONE|BLOCKED|REFUSE>: <result>. NEXT <unit>. NO-CLAIM <limit>."'
    echo "Do NOT tell a pane to use agent-mail: mcp-agent-mail fails to connect in this fleet, so"
    echo "the sender believes it reported and nobody receives it."
else
    echo "no idle workers."
fi
