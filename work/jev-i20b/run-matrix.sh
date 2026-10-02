#!/usr/bin/env bash
# jev-i20b volume matrix: one (task, arm) cell. Args: ARM OVERLAY TASKID PROMPT
# Single-turn fresh session per cell: only fresh runs receive live recall.
# The filter cannot see recall (lands post-fire), so volume comes from bank
# queries per task (ON) with caps as mechanical top-k; success from graded
# answers here. VOLCAP tags mark attribution.
ARM="$1"; OVERLAY="$2"; TASKID="$3"; PROMPT="$4"
EXTRA=""
if [ -n "$OVERLAY" ]; then EXTRA="--config $OVERLAY"; fi
LOG="/tmp/volcap-${ARM}-${TASKID}.log"
(echo "{\"id\":\"${TASKID}m\",\"type\":\"prompt\",\"message\":\"VOLCAP-${ARM}-${TASKID}: ${PROMPT}\"}"; sleep 75) | omp --mode=rpc --no-ui $EXTRA > "$LOG" 2>&1
echo "exit=$? arm=$ARM task=$TASKID turns=$(grep -c prompt_result $LOG)"
