# Issue 4 — ready to post

**Repo:** `hyperspaceai/jevcache` · **Title:** `serve --port: the startup line reports the requested port, not the bound one, and an unparseable value is silently discarded`

<!-- Everything below the line is the issue body. Paste as-is. -->

---

Two behaviours on the same flag. Both are cases of `serve` reporting the port it was *asked
for* rather than what it *did*.

1. `--port 0` prints `http://127.0.0.1:0` while the process listens on an OS-assigned
   ephemeral port. The printed URL cannot be connected to.
2. `--port abc` is not an error: the flag is dropped and resolution falls through to
   `JEVCACHE_PORT`, then to the 9000 default, with nothing printed about it.

### Environment

- `jevcache version` → **0.1.0**, installed via `curl -fsSL jevcache.sh/install | sh`
- binary sha256 `68fcb95b908cf3ee73dbeb3df52b265f6b908a6a9cfd661c5c6429d32f7535d5`
- macOS 26.5.2 (Darwin 25.5.0), arm64
- `JEVCACHE_BACKEND=mock` — no key, no network

### Reproduction

```sh
W=$(mktemp -d); export HOME="$W/home"; mkdir -p "$HOME"

# --- part 1: --port 0
JEVCACHE_BACKEND=mock jevcache serve --port 0 > "$W/p0.log" 2>&1 &
P0=$!; sleep 1.5
echo "printed:"; sed -n '1p' "$W/p0.log"
echo "bound:";   lsof -nP -iTCP -sTCP:LISTEN -a -p "$P0" | sed -n '2p'
BOUND=$(lsof -nP -iTCP -sTCP:LISTEN -a -p "$P0" | awk 'NR==2{print $9}' | sed 's/.*://')
curl -sS -m3 http://127.0.0.1:0/health
curl -sS -m3 "http://127.0.0.1:$BOUND/health"; echo
kill "$P0"

# --- part 2: --port abc, with a valid value in the environment to expose the fall-through
FREE=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')
JEVCACHE_PORT="$FREE" JEVCACHE_BACKEND=mock jevcache serve --port abc > "$W/a.log" 2>&1 &
sleep 1.5; sed -n '1p' "$W/a.log"; echo "free port offered in env was: $FREE"; kill %1
```

### Observed

**Part 1:**

```text
printed:
jevcache serving on http://127.0.0.1:0
bound:
jevcache 84448 user    3u  IPv4 0xe168e0173beb6b6c      0t0  TCP 127.0.0.1:57653 (LISTEN)

curl: (7) Failed to connect to 127.0.0.1 port 0 after 0 ms: Couldn't connect to server
{"ok":true}          <- 127.0.0.1:57653
```

The server is fine; the one line it prints is not an address. `--port 0` is the normal way to
start a server in CI, in a test fixture, or as a sidecar beside something that may already hold
9000 — and in all of those the caller reads the assigned port from stdout.

**Part 2:**

```text
jevcache serving on http://127.0.0.1:57657
free port offered in env was: 57657
```

`abc` is thrown away with no diagnostic and `JEVCACHE_PORT` wins. With no env var set, the same
invocation goes to the 9000 default — which is how you can tell it is fall-through rather than
a partial parse:

```text
$ jevcache serve --port abc          # something else already on 9000
jevcache: serve: Address already in use (os error 48)
```

`--port ''` and a valueless `--port` behave the same way. A typo'd port in a service file
starts a healthy-looking server on the wrong one.

For completeness, every well-formed invocation prints correctly, so part 1 is specifically the
requested-versus-bound distinction and not a formatting bug:

```text
jevcache serve --port 9138                  -> http://127.0.0.1:9138
jevcache serve --port=9138                  -> http://127.0.0.1:9138
jevcache serve --host 127.0.0.1 --port 9138 -> http://127.0.0.1:9138
jevcache serve --host 0.0.0.0   --port 9138 -> http://0.0.0.0:9138
JEVCACHE_PORT=9138 jevcache serve           -> http://127.0.0.1:9138
```

### Expected

1. The startup line reports the address the listener actually bound, so `--port 0` prints the
   ephemeral port.
2. A `--port` value that is not a valid port number is a startup error with a nonzero exit,
   naming the value.

### Suggested direction

One line: read the port back off the bound listener instead of echoing the parsed argument, and
make the parse fallible rather than falling back — a flag the user explicitly passed should
never be silently ignored.

### Dedup

Checked before filing, 2026-09-20T03:33Z:

```sh
$ gh issue list --repo hyperspaceai/jevcache --state all --limit 30
1  OPEN  state_preview persists unredacted credentials to a world-readable ledger  2026-09-20T03:29:37Z

$ for q in port serve bind listen; do \
    gh issue list --repo hyperspaceai/jevcache --state all --search "$q" --limit 5; done
# "port" returns nothing at all

$ gh release list --repo hyperspaceai/jevcache --limit 5
jevcache v0.1.0  Latest  v0.1.0  2026-09-19T17:44:40Z
```

No duplicate exists and `v0.1.0` is the only release, so this is not already fixed in a newer
tag.
