#!/bin/bash
# Round-2 duel: 12 hard tasks x auto/high, fresh copy per run, randomized order.
cd /Users/josh/Developer/jev || exit 1
SEED=77
n=0
for tid in u01 u02 u03 u04 u05 u06 u07 u08 u09 u10 u11 u12 u13 u14 u15 u16; do
  n=$((n+1))
order="high"
  echo "$tid order=$order" >> work/thinking-duel-hard3/runs.log
  for a in $order; do
    rid="${tid}-pilot"
    workdir="work/thinking-duel-hard3/runs/$rid"

    mkdir -p "$workdir"
    cp "work/thinking-duel-hard3/tasks/$tid/"* "$workdir/"
    prompt="Work in $PWD. Solve the task in prompt.md using only files in \$PWD (do not read anything outside it). $(cat "work/thinking-duel-hard3/tasks/$tid/prompt.md")"
    start=$(date +%s)
    omp -p "$prompt" --thinking high --cwd "/Users/josh/Developer/jev/$workdir" --session-dir "/Users/josh/Developer/jev/work/thinking-duel-hard3/sessions/$rid" --approval-mode yolo --auto-approve --max-time 600 > "work/thinking-duel-hard3/out-$rid.txt" 2>&1
    echo "$rid exit=$? wall=$(( $(date +%s) - start ))s" >> work/thinking-duel-hard3/runs.log
  done
done
echo ALLDONE >> work/thinking-duel-hard3/runs.log
