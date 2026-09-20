#!/bin/bash
# Start jevcache with the Jev backend wired AND the plaintext-state exposure contained.
#
#   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
#     bash work/jevcache-probe/serve-with-jev.sh [port]
#
# WHY THE BACKEND LINE EXISTS
# `jevcache serve` reads its backend from ITS OWN environment at startup; a client cannot
# supply it per-request. Started bare it falls back to a local model at 127.0.0.1:8080, so
# every /decide returns a 404 that READS LIKE A BROKEN MODEL and is actually an unconfigured
# server.
#
# WHY THE LEDGER LINES EXIST — MEASURED, NOT PRECAUTIONARY
# jevcache writes the first 200 characters of each canonicalized state to its ledger IN
# PLAINTEXT, at `/r/state_preview`, in a world-readable file. Verified on this machine:
#   ~/.jevcache/ledger.log  -rw-r--r--   /r/state_preview => {"command":"chmod -R 777 /etc/passwd"}
# Its redactor has four rules (email, phone, 9+ digit runs, volatile field NAMES) and NO RULE
# FOR CREDENTIALS: a probe state carrying `Authorization: Bearer <token>` had the email and
# account number masked and the BEARER TOKEN WRITTEN OUT IN FULL.
# There is no --no-preview, no retention setting and no `clear` command; the binary exposes
# only JEVCACHE_DIR. So containment is the only lever we have:
#   - a dedicated ledger directory OUTSIDE $HOME's default path, never the shared ~/.jevcache
#   - 0700 on the directory and 0600 on everything in it, re-applied on every start
#   - the directory is gitignored, so a state preview can never reach a commit
# Our states are commands and diffs. This lane withheld 813 real blocked commands from a
# receipt tonight because some carry secrets; the same text must not land in a 0644 file.
set -u

# files must be born 0600: jevcache creates ledger.log AFTER any chmod we run, so a
# post-hoc chmod loses the race. umask makes the mode a property of creation.
umask 077

PORT="${1:-9000}"
LEDGER="${JEVCACHE_DIR:-/Users/josh/Developer/jev/.jevcache-ledger}"

export JEVCACHE_BACKEND=jev
# jevcache reads TYPESAFE_API_KEY natively (it is in the binary's string table), but also
# accepts JEV_API_KEY. Set both from whichever infisical provides; never printed.
export JEV_API_KEY="${JEV_API_KEY:-${TYPESAFE_API_KEY:?TYPESAFE_API_KEY not in env — run under infisical, see .env.example}}"
export TYPESAFE_API_KEY="${TYPESAFE_API_KEY:-$JEV_API_KEY}"
export JEVCACHE_DIR="$LEDGER"

mkdir -p "$LEDGER" || { echo "cannot create ledger dir $LEDGER" >&2; exit 1; }
chmod 700 "$LEDGER"
find "$LEDGER" -type f -exec chmod 600 {} + 2>/dev/null

echo "jevcache serve --port ${PORT}"
echo "  backend : jev (key length ${#JEV_API_KEY})"
echo "  ledger  : ${LEDGER} (0700, files 0600 — plaintext state previews are contained here)"
echo "  NOTE    : jevcache writes the first 200 chars of state in plaintext. Do not point this"
echo "            at traffic whose state you would not paste into a file."

exec jevcache serve --port "${PORT}"
