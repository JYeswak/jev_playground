#!/usr/bin/env bash
# jev-latest-canary-run.sh -- run the jev-latest canary under its secret
# manager, classify the outcome, notify on anything but OK, and append one
# history-readable log line.
#
# The secret-manager step is the boundary this runner exists to watch: the
# manager runs first and execs the canary only on success. If the manager
# itself fails (Infisical login failure), the canary never runs and the output
# carries the AUTH text with a nonzero exit. AUTH text always wins over the
# exit code, so a manager failure can never be mistaken for canary MOVED.
#
# Outcome table (the runner's own exit codes; asserted by test_jev_latest_canary_run.py):
#   AUTH text ("Failed to automatically trigger login flow") present -> AUTH, exit 4, notify.
#   canary rc 0  -> OK,      exit 0, no notification.
#   canary rc 1  -> MOVED,   exit 1, notify (unless AUTH text matched above).
#   canary rc 2  -> NOT_RUN, exit 2, notify.
#   canary rc 3  -> ERROR,   exit 3, notify.
#   any other rc -> ERROR,   exit 3, notify (fail closed).
# AUTH gets exit 4 (not 1) so it is never confused with MOVED. A notification
# is one stdout line `NOTIFY <OUTCOME>: <detail>`; the log line keeps today's
# shape `<UTC timestamp> rc=<runner rc> <last output line>`.
# The runner never embeds a repository path: the default canary resolves
# relative to this script's directory, and all locations come from flags/env.
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CANARY="$SCRIPT_DIR/jev-latest-canary.py"
SECRET_MANAGER="${JEV_CANARY_SECRET_MANAGER:-infisical}"
PROJECT_ID="${JEV_CANARY_PROJECT_ID:-42b194c3-89d7-4ebb-895f-dd77ddf005ba}"
LOG_FILE="${HOME}/.local/state/jev/jev-latest-canary.log"
AUTH_TEXT="Failed to automatically trigger login flow"

usage() {
  cat <<USAGE
Usage: jev-latest-canary-run.sh [--secret-manager CMD] [--canary PATH] [--project-id ID] [--log-file PATH] [--help]
Run the jev-latest canary once under its secret manager, classify the
outcome, print a notification unless OK, and append a log line. Keyless
offline operation is the caller's choice of doubles: pass stubs via
--secret-manager / --canary for hermetic runs.
Outcomes: OK(0) MOVED(1) NOT_RUN(2) ERROR(3) AUTH(4).
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --secret-manager) SECRET_MANAGER="$2"; shift 2;;
    --canary) CANARY="$2"; shift 2;;
    --project-id) PROJECT_ID="$2"; shift 2;;
    --log-file) LOG_FILE="$2"; shift 2;;
    --help|-h) usage; exit 0;;
    *) echo "unknown flag: $1 (see --help)" >&2; exit 64;;
  esac
done

if [ ! -f "$CANARY" ]; then
  echo "NOTIFY ERROR: canary not found"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) rc=3 canary not found" >> "$LOG_FILE"
  exit 3
fi

out="$("$SECRET_MANAGER" run --silent --projectId="$PROJECT_ID" -- "$CANARY" 2>&1)"; rc=$?
lastline=$(printf '%s' "$out" | tail -n 1)

outcome=""; exitcode=0; notify=0
case "$out" in
  *"$AUTH_TEXT"*) outcome="AUTH"; exitcode=4; notify=1;;
  *)
    case "$rc" in
      0) outcome="OK"; exitcode=0; notify=0;;
      1) outcome="MOVED"; exitcode=1; notify=1;;
      2) outcome="NOT_RUN"; exitcode=2; notify=1;;
      3) outcome="ERROR"; exitcode=3; notify=1;;
      *) outcome="ERROR"; exitcode=3; notify=1;;
    esac
    ;;
esac

mkdir -p "$(dirname "$LOG_FILE")"
if [ "$notify" -eq 1 ]; then
  echo "NOTIFY $outcome: $lastline"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) rc=$exitcode $lastline" >> "$LOG_FILE"
exit "$exitcode"
