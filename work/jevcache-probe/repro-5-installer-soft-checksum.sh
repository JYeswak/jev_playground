#!/bin/bash
# repro-5 — jevcache.sh/install downgrades to an unverified install when the .sha256 sidecar
#           cannot be fetched, instead of aborting.
#
# PREREQUISITES: curl, python3, shasum. NO jevcache needed, NO API key, NO repo access.
#                Network is used ONLY to fetch the installer itself; the "release" it installs
#                is served from a local directory, and $HOME is a throwaway so nothing on your
#                machine is replaced.
#
# HOW: install.sh honours JEVCACHE_BASE. We point it at a local static server whose payload is
#      a harmless fake binary and whose .sha256 sidecar is DELIBERATELY ABSENT (case 1) or
#      DELIBERATELY WRONG (case 2). Case 2 must abort. Case 1 is the defect.
set -u

W=$(mktemp -d); cd "$W"
export HOME="$W/home"; mkdir -p "$HOME/.local/bin"   # must exist, else install.sh picks /usr/local/bin

curl -fsSL https://jevcache.sh/install -o install.sh
echo "installer sha256: $(shasum -a 256 install.sh | awk '{print $1}')"
echo "the guard, verbatim:"
sed -n '34,40p' install.sh | sed 's/^/    /'
echo

os=$(uname -s); arch=$(uname -m)
case "$os" in Darwin) o=darwin ;; Linux) o=linux ;; esac
case "$arch" in arm64|aarch64) a=arm64 ;; x86_64|amd64) a=x64 ;; esac
NAME="jevcache-$o-$a"

mkdir -p www/bin www/api/event
printf '#!/bin/sh\necho "NOT THE REAL JEVCACHE"\n' > "www/bin/$NAME"
REAL=$(shasum -a 256 "www/bin/$NAME" | awk '{print $1}')
( cd www && python3 -m http.server 0 --bind 127.0.0.1 > "$W/http.log" 2>&1 & echo $! > "$W/httpd.pid" )
sleep 1
PORT=$(sed -n 's/.*port \([0-9]*\).*/\1/p' "$W/http.log" | head -1)
BASE="http://127.0.0.1:$PORT"
trap 'kill "$(cat "$W/httpd.pid")" 2>/dev/null' EXIT
echo "local release server: $BASE   payload sha256 $REAL"
echo

echo "=============== case 1: sidecar ABSENT (404) ==============="
curl -sS -o /dev/null -w "    GET /bin/$NAME.sha256 -> http=%{http_code}\n" "$BASE/bin/$NAME.sha256"
rm -f "$HOME/.local/bin/jevcache"
JEVCACHE_BASE="$BASE" sh install.sh; echo "    installer rc=$?"
if [ -x "$HOME/.local/bin/jevcache" ]; then
  echo "    RESULT: installed anyway, unverified -> $("$HOME/.local/bin/jevcache")"
else
  echo "    RESULT: refused (no defect)"
fi

echo
echo "=============== case 2: sidecar PRESENT but WRONG ==============="
printf '%s  %s\n' "0000000000000000000000000000000000000000000000000000000000000000" "$NAME" \
  > "www/bin/$NAME.sha256"
rm -f "$HOME/.local/bin/jevcache"
JEVCACHE_BASE="$BASE" sh install.sh; echo "    installer rc=$?"
if [ -x "$HOME/.local/bin/jevcache" ]; then
  echo "    RESULT: installed despite a mismatch (would be far worse)"
else
  echo "    RESULT: correctly aborted on mismatch"
fi

echo
echo "The mismatch path works. The MISSING-sidecar path is the hole: a transient 404, a"
echo "proxy error or a 3-second network blip turns a verified install into an unverified one"
echo "with no output saying so."
exit 0
