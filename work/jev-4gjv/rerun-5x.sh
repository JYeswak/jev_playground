#!/bin/bash
cd /Users/josh/Developer/jev || exit 1
for i in 1 2 3 4; do
  id=$(gh run rerun 36956512317 --json databaseId -q .databaseId 2>/dev/null)
  echo "rerun $i -> $id $(date -u +%FT%TZ)"
  sleep 420
done
echo RERUNS-DONE
