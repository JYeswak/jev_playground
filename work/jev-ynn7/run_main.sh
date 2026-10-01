#!/bin/bash
# jev-ynn7 main: 20 runs in committed schedule order.
cd /Users/josh/Developer/jev || exit 1
SRC="var/agent-tmp/ynn7-tasks/repo"
python3 -c "
import json
sched = json.load(open('work/jev-ynn7/schedule.json'))
for r in sorted(sched, key=lambda r: r['order']):
    print(r['task'], r['arm'])
" | while read -r tid arm; do
  rid="${tid}-${arm}"
  workdir="work/jev-ynn7/runs/$rid"
  mkdir -p "$workdir"
  cp -r "$SRC/"* "$workdir/"
  marker=$(python3 -c "import json;print(json.load(open('work/jev-ynn7/targets.json'))['$tid']['marker'])")
  prompt="Work in \$PWD. Find the file containing the string $marker, read it to confirm, and report its path and the full line containing the string. Use only files in \$PWD (do not read anything outside it)."
  start=$(date +%s)
  if [ "$arm" = "treat" ]; then
    omp -p "$prompt" --append-system-prompt "$(cat work/jev-ynn7/nudge.md)" --cwd "/Users/josh/Developer/jev/$workdir" --session-dir "/Users/josh/Developer/jev/work/jev-ynn7/sessions/$rid" --approval-mode yolo --auto-approve --max-time 600 < /dev/null > "work/jev-ynn7/out-$rid.txt" 2>&1
  else
    omp -p "$prompt" --cwd "/Users/josh/Developer/jev/$workdir" --session-dir "/Users/josh/Developer/jev/work/jev-ynn7/sessions/$rid" --approval-mode yolo --auto-approve --max-time 600 < /dev/null > "work/jev-ynn7/out-$rid.txt" 2>&1
  fi
  echo "$rid exit=$? wall=$(( $(date +%s) - start ))s" >> work/jev-ynn7/runs.log
done
echo MAIN-DONE >> work/jev-ynn7/runs.log
