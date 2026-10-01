#!/bin/bash
# jev-ynn7 real-repo A/B: shared template cwd (read-only task), isolated session-dir.
cd /Users/josh/Developer/jev || exit 1
REPO="var/agent-tmp/ynn7-real/repo"
run_one() {
  tid=$1; arm=$2; rid="$3"
  token=$(python3 -c "import json;print(json.load(open('work/jev-ynn7/targets_real.json'))['$tid']['token'])")
  prompt="Work in \$PWD. Find A file containing the string $token, read it to confirm the string is present, and report its path and one line containing the string. Do not modify any file. Use only files in \$PWD (do not read anything outside it)."
  start=$(date +%s)
  if [ "$arm" = "treat" ]; then
    omp -p "$prompt" --append-system-prompt "$(cat work/jev-ynn7/nudge.md)" --cwd "/Users/josh/Developer/jev/$REPO" --session-dir "/Users/josh/Developer/jev/work/jev-ynn7/sessions-real/$rid" --approval-mode yolo --auto-approve --max-time 600 < /dev/null > "work/jev-ynn7/out-real-$rid.txt" 2>&1
  else
    omp -p "$prompt" --cwd "/Users/josh/Developer/jev/$REPO" --session-dir "/Users/josh/Developer/jev/work/jev-ynn7/sessions-real/$rid" --approval-mode yolo --auto-approve --max-time 600 < /dev/null > "work/jev-ynn7/out-real-$rid.txt" 2>&1
  fi
  echo "$rid exit=$? wall=$(( $(date +%s) - start ))s" >> work/jev-ynn7/runs-real.log
}
if [ $# -eq 0 ]; then
  run_one r01 control r01-control-pilotreal
  run_one r01 treat r01-treat-pilotreal
  echo PILOTREAL-DONE >> work/jev-ynn7/runs-real.log
else
  while read -r tid arm; do
    run_one "$tid" "$arm" "${tid}-${arm}-real"
  done < "$1"
  echo MAINREAL-DONE >> work/jev-ynn7/runs-real.log
fi
