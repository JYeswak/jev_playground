#!/bin/bash
# Start jevcache with the Jev backend actually wired up.
#
# WHY THIS EXISTS: `jevcache serve` reads its backend configuration from ITS OWN environment
# at startup. A client cannot supply it per-request, so an instance started without
# JEVCACHE_BACKEND answers every /decide with:
#   "local backend: http://127.0.0.1:8080/v1/decide: status code 404"
# That is a configuration state, not a cache miss, and it looks like a broken model.
#
# Our key lives in Infisical as TYPESAFE_API_KEY; jevcache wants JEV_API_KEY. Mapped here,
# never printed.
#
#   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
#     bash work/jevcache-probe/serve-with-jev.sh
set -u
export JEVCACHE_BACKEND=jev
export JEV_API_KEY="${JEV_API_KEY:-${TYPESAFE_API_KEY:?TYPESAFE_API_KEY not in env — run under infisical, see .env.example}}"
PORT="${1:-9000}"
echo "starting jevcache serve --port ${PORT} with JEVCACHE_BACKEND=jev (key length ${#JEV_API_KEY})"
exec jevcache serve --port "${PORT}"
