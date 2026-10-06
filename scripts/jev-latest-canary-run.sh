#!/bin/bash
set -u

usage() {
  printf 'Usage: %s [--help]\nRun the installed jev-latest canary and report its outcome.\n' "${0##*/}"
}

if [ "$#" -gt 0 ]; then
  case "$1" in
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 64 ;;
  esac
fi

home=${HOME:?HOME must be set}
runner_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P) || exit 3
canary_script="$runner_dir/jev-latest-canary.py"
state_dir="$home/.local/state/jev"
log_file="$state_dir/jev-latest-canary.log"
infisical_bin=${JEV_CANARY_INFISICAL_BIN:-"$home/.local/bin/infisical"}
python_bin=${JEV_CANARY_PYTHON_BIN:-python3}
notify_bin=${JEV_CANARY_NOTIFY_BIN:-/usr/bin/osascript}

mkdir -p "$state_dir" || exit 3
started_file=$(mktemp "$state_dir/.jev-latest-canary-started.XXXXXX") || exit 3
trap 'rm -f "$started_file"' EXIT
export JEV_CANARY_STARTED_FILE="$started_file"

# Defer marker and argument expansion until the child shell runs under Infisical.
# shellcheck disable=SC2016
child_script='printf "started\n" > "$JEV_CANARY_STARTED_FILE"; exec "$@"'
infisical_args=(
  run
  --silent
  --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba
  --
  /bin/sh
  -c
  "$child_script"
  jev-latest-canary
  "$python_bin"
  "$canary_script"
)
out=$("$infisical_bin" "${infisical_args[@]}" 2>&1)
secret_manager_rc=$?

if [ ! -s "$started_file" ]; then
  rc=4
  outcome=AUTH
  notification='AUTH: Jev canary could not access Infisical'
else
  case "$secret_manager_rc" in
    0)
      rc=0
      outcome=OK
      notification=
      ;;
    1)
      rc=1
      outcome=MOVED
      notification='jev-latest moved off jev-1.13.0'
      ;;
    2)
      rc=2
      outcome=NOT_RUN
      notification='NOT_RUN: Jev canary did not run because the API key is unavailable'
      ;;
    *)
      rc=3
      outcome=ERROR
      notification='ERROR: Jev canary request or response failed'
      ;;
  esac
fi

last_line=$(printf '%s' "$out" | tail -n 1)
if [ -z "$last_line" ]; then
  last_line="$outcome"
fi
printf '%s rc=%s %s\n' "$(date -u +%FT%TZ)" "$rc" "$last_line" >> "$log_file" || exit 3

if [ "$rc" -ne 0 ]; then
  "$notify_bin" -e "display notification \"$notification\" with title \"Jev canary\"" >/dev/null 2>&1 || :
fi

exit "$rc"
