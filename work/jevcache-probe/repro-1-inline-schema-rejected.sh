#!/bin/bash
# repro-1 — the documented /decide example on jevcache.sh does not run.
#
# PREREQUISITES: jevcache on PATH (curl -fsSL jevcache.sh/install | sh), curl, python3.
#                NO API key, NO network, NO access to any repo. Uses the built-in `mock`
#                backend and a throwaway HOME so your real ~/.jevcache is untouched.
#
# WHAT IT SHOWS: the landing page says "schema is inline, nothing to pre-register" and posts
# { schema, state }. It never shows what `schema` contains. Every obvious construction is
# rejected, one requirement at a time, and the id/version split is never stated anywhere.
set -u

WORK=$(mktemp -d)
export HOME="$WORK/home"
mkdir -p "$HOME"
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')

JEVCACHE_BACKEND=mock jevcache serve --port "$PORT" > "$WORK/serve.log" 2>&1 &
SERVE_PID=$!
cleanup() { kill "$SERVE_PID" 2>/dev/null; }
trap cleanup EXIT
for _ in $(seq 1 40); do curl -sS -m1 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && break; sleep 0.1; done

echo "jevcache $(jevcache version)   serve on 127.0.0.1:$PORT   backend=mock   HOME=$HOME"
echo

STATE='{"subject":"double charged","body":"I was billed twice this month"}'
step () {
  echo "--- $1"
  echo "    body : $2"
  printf '    resp : '
  curl -sS -m10 -X POST "http://127.0.0.1:$PORT/decide" \
       -H 'content-type: application/json' -d "$2" -w '   [http=%{http_code}]\n'
}

step "A  the page's shape: a bare inline schema (question map)" \
  "{\"schema\":{\"billing\":\"is this ticket about billing?\"},\"state\":$STATE}"
step "B  wrap the questions, still no id" \
  "{\"schema\":{\"questions\":{\"billing\":\"is this ticket about billing?\"}},\"state\":$STATE}"
step "C  add an id the way the CLI writes one (name.vN)" \
  "{\"schema\":{\"id\":\"support.route.v1\",\"questions\":{\"billing\":\"is this ticket about billing?\"}},\"state\":$STATE}"
step "D  the site's own id style, harm.v1" \
  "{\"schema\":{\"id\":\"harm.v1\",\"questions\":{\"harmful\":\"is this harmful?\"}},\"state\":$STATE}"
step "E  version as a string" \
  "{\"schema\":{\"id\":\"harm\",\"version\":\"1\",\"questions\":{\"harmful\":\"is this harmful?\"}},\"state\":$STATE}"
step "F  WORKS on mock: id + integer version, question still a bare string" \
  "{\"schema\":{\"id\":\"harm\",\"version\":1,\"questions\":{\"harmful\":\"is this harmful?\"}},\"state\":$STATE}"
step "G  WORKS: id, integer version, question as {instructions,type}" \
  "{\"schema\":{\"id\":\"harm\",\"version\":1,\"questions\":{\"harmful\":{\"instructions\":\"is this harmful?\",\"type\":\"noul\"}}},\"state\":$STATE}"

echo
echo "Five rejections before the first success (A-E). None of schema.id, schema.version, or"
echo "the id/version split appears in the example the page tells you to copy."
echo
echo "Note: F passes here because the mock backend accepts a bare-string question. Against a"
echo "real backend (JEVCACHE_BACKEND=jev) the same body is a sixth failure, surfaced not by"
echo "jevcache's validator but as an opaque relayed error:"
echo '  {"error":"jev backend: https://api.typesafe.ai/v1/systemone: status code 400"}  [http=502]'
echo "so the question object shape is the one requirement no error message ever names."
