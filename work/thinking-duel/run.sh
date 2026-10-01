#!/bin/bash
# Thinking duel: 12 prompts x auto/high, randomized arm order, fresh sessions.
cd /Users/josh/Developer/jev
SEED=42
n=0
for pid in p01 p02 p03 p04 p05 p06 p07 p08 p09 p10 p11 p12; do
  n=$((n+1))
  prompt=$(python3 -c "import json; print([r['prompt'] for r in map(json.loads,open('work/thinking-duel/prompts.jsonl')) if r['id']=='$pid'][0])")
  if [ $(( (n*2654435761+SEED)%2 )) -eq 0 ]; then order="auto high"; else order="high auto"; fi
  echo "$pid order=$order" >> work/thinking-duel/runs.log
  for a in $order; do
    rid="${pid}-${a}"
    sdir="work/thinking-duel/sessions/$rid"
    mkdir -p "$sdir"
    start=$(date +%s)
    omp -p "$prompt" --thinking "$a" --session-dir "/Users/josh/Developer/jev/$sdir" --max-time 240 > "work/thinking-duel/out-$rid.txt" 2>&1
    echo "$rid exit=$? wall=$(( $(date +%s) - start ))s" >> work/thinking-duel/runs.log
  done
done
echo ALLDONE >> work/thinking-duel/runs.log
