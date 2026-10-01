#!/bin/bash
# Round-2 duel: 12 hard tasks x auto/high, fresh copy per run, randomized order.
cd /Users/josh/Developer/jev || exit 1
SEED=77
n=0
for tid in t01 t02 t03 t04 t05 t06 t07 t08 t09 t10 t11 t12; do
  n=$((n+1))
  if [ $(( (n*2654435761+SEED)%2 )) -eq 0 ]; then order="auto high"; else order="high auto"; fi
  echo "$tid order=$order" >> work/thinking-duel-hard/runs.log
  for a in $order; do
    rid="${tid}-${a}"
    workdir="work/thinking-duel-hard/runs/$rid"

    mkdir -p "$workdir"
    cp "work/thinking-duel-hard/tasks/$tid/"* "$workdir/"
    prompt="Work in $PWD. Solve the task in prompt.md using only files in \$PWD (do not read anything outside it). $(cat "work/thinking-duel-hard/tasks/$tid/prompt.md")"
    start=$(date +%s)
    omp -p "$prompt" --thinking "$a" --cwd "/Users/josh/Developer/jev/$workdir" --session-dir "/Users/josh/Developer/jev/work/thinking-duel-hard/sessions/$rid" --approval-mode yolo --auto-approve --max-time 600 > "work/thinking-duel-hard/out-$rid.txt" 2>&1
    echo "$rid exit=$? wall=$(( $(date +%s) - start ))s" >> work/thinking-duel-hard/runs.log
  done
done
echo ALLDONE >> work/thinking-duel-hard/runs.log
