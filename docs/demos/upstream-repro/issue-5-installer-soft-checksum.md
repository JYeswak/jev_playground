# Issue 5 — ready to post

**Repo:** `hyperspaceai/jevcache` · **Title:** `install.sh silently downgrades to an unverified install when the .sha256 sidecar cannot be fetched`

<!-- Everything below the line is the issue body. Paste as-is. -->

---

`jevcache.sh/install` verifies a SHA-256 checksum, and the README says so. It verifies it only
when the sidecar fetch succeeds: the fetch is silenced with `2>/dev/null` and the comparison
lives inside `if [ -n "$want" ]`, so a 404, a proxy error or a network blip turns a verified
install into an unverified one with no output saying so.

**This is a latent hazard, not an incident.** On the machine that found it the sidecar was
served (HTTP 200) and the installed binary is byte-identical to it — sha256
`68fcb95b908cf3ee73dbeb3df52b265f6b908a6a9cfd661c5c6429d32f7535d5`. Nothing bad happened. The
report is about the path where it would.

### Environment

- `install.sh` fetched 2026-09-20 from `https://jevcache.sh/install`, sha256
  `1da98e8e5be650db09f873b0ab7bcf6f365bbed4921a2952af18fcff911e1ebb`, 51 lines
- macOS 26.5.2 (Darwin 25.5.0), arm64
- no `jevcache` required to reproduce

### The code

```sh
# verify checksum
want=$(curl -fsSL "$url.sha256" 2>/dev/null | awk '{print $1}')
if [ -n "$want" ]; then
  if command -v shasum >/dev/null 2>&1; then got=$(shasum -a 256 "$tmp" | awk '{print $1}');
  else got=$(sha256sum "$tmp" | awk '{print $1}'); fi
  if [ "$want" != "$got" ]; then echo "jevcache: checksum mismatch — aborting." >&2; rm -f "$tmp"; exit 1; fi
fi
```

Empty `$want` — from a 404, a TLS failure, a captive portal, a stale CDN edge — is
indistinguishable from "no checksum published", and both mean "install it".

### Reproduction

`install.sh` honours `JEVCACHE_BASE`, so this needs no cooperation from your infrastructure.
Network is used only to fetch the installer itself; the "release" is served from a local
directory, and `HOME` is a throwaway so nothing real is replaced.

```sh
W=$(mktemp -d); cd "$W"; export HOME="$W/home"; mkdir -p "$HOME/.local/bin"
curl -fsSL https://jevcache.sh/install -o install.sh
os=$(uname -s); arch=$(uname -m)
case "$os" in Darwin) o=darwin ;; Linux) o=linux ;; esac
case "$arch" in arm64|aarch64) a=arm64 ;; x86_64|amd64) a=x64 ;; esac
NAME="jevcache-$o-$a"

mkdir -p www/bin
printf '#!/bin/sh\necho "NOT THE REAL JEVCACHE"\n' > "www/bin/$NAME"
( cd www && python3 -m http.server 0 --bind 127.0.0.1 > "$W/http.log" 2>&1 & )
sleep 1; PORT=$(sed -n 's/.*port \([0-9]*\).*/\1/p' "$W/http.log" | head -1)

# case 1 — sidecar absent (404)
JEVCACHE_BASE="http://127.0.0.1:$PORT" sh install.sh; echo "rc=$?"
"$HOME/.local/bin/jevcache"

# case 2 — sidecar present but wrong
printf '%s  %s\n' "0000000000000000000000000000000000000000000000000000000000000000" "$NAME" > "www/bin/$NAME.sha256"
rm -f "$HOME/.local/bin/jevcache"
JEVCACHE_BASE="http://127.0.0.1:$PORT" sh install.sh; echo "rc=$?"
```

### Observed

```text
=============== case 1: sidecar ABSENT (404) ===============
    GET /bin/jevcache-darwin-arm64.sha256 -> http=404
downloading jevcache-darwin-arm64...
installed jevcache → /tmp/.../home/.local/bin/jevcache
run 'jevcache' to get started.
    installer rc=0
    RESULT: installed anyway, unverified -> NOT THE REAL JEVCACHE

=============== case 2: sidecar PRESENT but WRONG ===============
downloading jevcache-darwin-arm64...
jevcache: checksum mismatch — aborting.
    installer rc=1
    RESULT: correctly aborted on mismatch
```

The mismatch path is correct and does its job. The missing-sidecar path installs an arbitrary
payload, exits 0, and prints the same cheerful `run 'jevcache' to get started.`

### Expected

A checksum that cannot be fetched is a failure, not an absence. Either abort, or say out loud
that the install is unverified.

### Suggested direction

One line: drop the `2>/dev/null` and make an empty `$want` fatal — the sidecar is always
published, so "we could not fetch it" is never the benign case it is currently treated as.

### Dedup

Checked before filing, 2026-09-20T03:33Z:

```sh
$ gh issue list --repo hyperspaceai/jevcache --state all --limit 30
1  OPEN  state_preview persists unredacted credentials to a world-readable ledger  2026-09-20T03:29:37Z

$ for q in state_preview ledger port checksum installer schema decide redact; do \
    gh issue list --repo hyperspaceai/jevcache --state all --search "$q" --limit 5; done
# only ever returns issue #1; "port", "checksum" and "installer" return nothing

$ gh release list --repo hyperspaceai/jevcache --limit 5
jevcache v0.1.0  Latest  v0.1.0  2026-09-19T17:44:40Z
```

Issue #1 is a different defect (unredacted credentials in `state_preview`). No duplicate of
this report exists, and `v0.1.0` is the only release, so this is not already fixed in a newer
tag.
