#!/bin/bash
# repro-2 — `jevcache serve` prints the port you ASKED for, not the port it BOUND.
#
# PREREQUISITES: jevcache on PATH (curl -fsSL jevcache.sh/install | sh), curl, lsof, python3.
#                NO API key, NO network, NO access to any repo. Throwaway HOME.
#
# WHAT IT SHOWS:
#   part 1  `serve --port 0` — the ordinary "give me any free port" idiom — prints
#           http://127.0.0.1:0, which is not an address you can connect to, while the
#           process is really listening on an OS-assigned ephemeral port.
#   part 2  an unparseable --port value is silently discarded rather than rejected.
set -u

WORK=$(mktemp -d)
export HOME="$WORK/home"
mkdir -p "$HOME"
echo "jevcache $(jevcache version)   HOME=$HOME"
echo

echo "=============== part 1:  serve --port 0 ==============="
JEVCACHE_BACKEND=mock jevcache serve --port 0 > "$WORK/p0.log" 2>&1 &
P0=$!
sleep 1.5
echo "--- what it printed:"
sed -n '1p' "$WORK/p0.log"
BOUND=$(lsof -nP -iTCP -sTCP:LISTEN -a -p "$P0" 2>/dev/null | awk 'NR==2{print $9}' | sed 's/.*://')
echo "--- what lsof says it bound:"
lsof -nP -iTCP -sTCP:LISTEN -a -p "$P0" 2>/dev/null | sed -n '2p'
echo "--- connecting to the printed address:"
curl -sS -m3 -o /dev/null -w '    http://127.0.0.1:0/health      -> http=%{http_code}\n' \
  http://127.0.0.1:0/health 2>&1 | sed 's/^/    /'
echo "--- connecting to the bound address:"
printf '    http://127.0.0.1:%s/health  -> ' "$BOUND"
curl -sS -m3 "http://127.0.0.1:$BOUND/health"; echo
kill "$P0" 2>/dev/null; wait "$P0" 2>/dev/null

echo
echo "=============== part 2:  an unparseable --port is discarded ==============="
FREE=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')
echo "--- JEVCACHE_PORT=$FREE  jevcache serve --port abc"
JEVCACHE_PORT="$FREE" JEVCACHE_BACKEND=mock jevcache serve --port abc > "$WORK/pabc.log" 2>&1 &
PA=$!
sleep 1.5
sed -n '1p' "$WORK/pabc.log"
echo "    (no warning that 'abc' was rejected; the flag is dropped and the env/default wins)"
kill "$PA" 2>/dev/null; wait "$PA" 2>/dev/null
exit 0
