#!/usr/bin/env bash
# scripts/git-commit-serialized.sh — fleet commit wrapper (jev-fxm2).
#
# WHY: 25 empty .git/index.lock abandons in ~24h (2026-10-01). Mechanism,
# proven by killing a real `git add` mid-run: a writer killed between lock
# creation and index write leaves an empty lock; every later writer fails
# until the watcher moves it. Fleet `seq 1 20` retry loops turn one stuck
# lock into contention across panes.
#
# WHAT: serialize jev-index writers fleet-wide (mkdir mutex, macOS-portable)
# and sweep a stale empty lock on entry (same predicate as the fleet
# watcher: empty + >=120s old + no git holder). Then exec git commit.
# Human/IDE commits bypass this wrapper (residual); the watcher still
# sweeps those. Adoption is a conductor broadcast, not automatic.
#
# Usage: scripts/git-commit-serialized.sh [--only <paths>...] -m "msg [level]"
set -u

repo="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "git-commit-serialized: not in a git repo" >&2; exit 2; }
mutex="$repo/.git/fleet-commit.lockdir"
deadline=$((SECONDS + ${JEV_COMMIT_MUTEX_TIMEOUT:-180}))
while ! mkdir "$mutex" 2>/dev/null; do
  # Reclaim a mutex whose holder died uncatchably (kill -9 skips traps).
  if [ -n "$(find "$mutex" -mmin +10 2>/dev/null)" ]; then rmdir "$mutex" 2>/dev/null; continue; fi
  if [ $SECONDS -ge $deadline ]; then echo "git-commit-serialized: mutex contended, giving up" >&2; exit 3; fi
  sleep 1
done
trap 'rmdir "$mutex" 2>/dev/null' EXIT

lock="$repo/.git/index.lock"
if [ -e "$lock" ] && [ ! -s "$lock" ]; then
  if stat -f %m "$lock" >/dev/null 2>&1; then mtime=$(stat -f %m "$lock"); else mtime=$(stat -c %Y "$lock"); fi
  age=$(( $(date +%s) - mtime ))
  # Holder check scoped to THIS lock (lsof), not machine-wide pgrep: any
  # pane's unrelated git must not veto the sweep. Empty output = no holder.
  if [ "$age" -ge 120 ] && [ -z "$(lsof -t "$lock" 2>/dev/null)" ]; then
    park="$repo/var/agent-tmp"
    mkdir -p "$park"
    mv "$lock" "$park/git-index.lock.stale-$(date -u +%Y%m%dT%H%M%SZ)"
  fi
fi

git commit "$@"
rc=$?
rmdir "$mutex" 2>/dev/null
exit $rc
