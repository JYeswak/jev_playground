#!/bin/bash
# Round-3 v2 pilot: pinned-high on k01-k16, fresh copies.
cd /Users/josh/Developer/jev || exit 1
for tid in k01 k02 k03 k04 k05 k06 k07 k08 k09 k10 k11 k12 k13 k14 k15 k16; do
  rid="pilot2-high-$tid"
  workdir="work/thinking-duel-hard3/runs/$rid"
  mkdir -p "$workdir"
  cp "work/thinking-duel-hard3/v2/$tid/"* "$workdir/"
  prompt="Work in $PWD. Solve the task in prompt.md using only files in \$PWD (do not read anything outside it). $(cat "work/thinking-duel-hard3/v2/$tid/prompt.md")"
  start=$(date +%s)
  omp -p "$prompt" --thinking high --cwd "/Users/josh/Developer/jev/$workdir" --session-dir "/Users/josh/Developer/jev/work/thinking-duel-hard3/sessions/$rid" --approval-mode yolo --auto-approve --max-time 600 > "work/thinking-duel-hard3/out-$rid.txt" 2>&1
  echo "$rid exit=$? wall=$(( $(date +%s) - start ))s" >> work/thinking-duel-hard3/pilot2.log
done
echo PILOT2DONE >> work/thinking-duel-hard3/pilot2.log
