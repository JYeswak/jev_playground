#!/usr/bin/env bash
# Wait before any local-model batch (ollama / mlx) while the Mac GPU is reserved.
#
# Two reservations, both owned outside this repo's labellers:
#   1. localbench: `localbench park --status` prints {"parked": [...]}; a non-empty list means a
#      localbench measurement run is active (localbench pane %20, 2026-09-27: jev labeller batches
#      holding the GPU at 70-90% voided 4 of its runs).
#   2. a hold file, ~/.local/state/jev/local-gpu-hold-until, containing a UTC epoch second; pane 1
#      writes it to grant localbench a quiet window.
#
# Usage: scripts/local-model-guard.sh [--timeout SECONDS]   (default: wait indefinitely)
# Exit:  0 GPU free, 2 timed out waiting, 3 localbench status unreadable (fail closed).
set -euo pipefail

timeout=0
if [[ "${1:-}" == "--timeout" ]]; then timeout="${2:?--timeout needs seconds}"; fi
hold_file="${JEV_GPU_HOLD_FILE:-$HOME/.local/state/jev/local-gpu-hold-until}"
localbench_bin="${LOCALBENCH_BIN:-localbench}"
start=$(date +%s)

while true; do
  now=$(date +%s)
  reason=""
  if [[ -f "$hold_file" ]]; then
    until_epoch=$(tr -dc '0-9' < "$hold_file")
    if [[ -n "$until_epoch" && "$now" -lt "$until_epoch" ]]; then
      reason="jev hold until $(date -u -r "$until_epoch" +%FT%TZ)"
    fi
  fi
  if [[ -z "$reason" ]]; then
    if ! status=$("$localbench_bin" park --status 2>/dev/null); then
      echo "local-model-guard: cannot read 'localbench park --status'; refusing (fail closed)" >&2
      exit 3
    fi
    parked=$(printf '%s' "$status" | python3 -c 'import json,sys; print(len(json.load(sys.stdin).get("parked") or []))' 2>/dev/null) || {
      echo "local-model-guard: unparseable localbench status; refusing (fail closed)" >&2
      exit 3
    }
    [[ "$parked" != "0" ]] && reason="localbench has $parked parked item(s)"
  fi
  if [[ -z "$reason" ]]; then
    echo "local-model-guard: GPU free"
    exit 0
  fi
  if [[ "$timeout" -gt 0 && $((now - start)) -ge "$timeout" ]]; then
    echo "local-model-guard: still waiting after ${timeout}s: $reason" >&2
    exit 2
  fi
  echo "local-model-guard: waiting: $reason"
  sleep 30
done
