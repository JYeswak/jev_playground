# Issue 6 — ready to post

**Repo:** `hyperspaceai/jevcache` · **Title:** `the /decide example on jevcache.sh cannot be run as written: schema.id and schema.version are required and revealed one error at a time`

<!-- Everything below the line is the issue body. Paste as-is. -->

---

The landing page's "in your app" example is the first thing a new user copies. It posts a
`schema` variable it never defines, and every obvious way of filling that variable in is
rejected — one missing requirement per round-trip.

### Environment

- `jevcache version` → **0.1.0**, installed via `curl -fsSL jevcache.sh/install | sh`
- binary sha256 `68fcb95b908cf3ee73dbeb3df52b265f6b908a6a9cfd661c5c6429d32f7535d5`
- macOS 26.5.2 (Darwin 25.5.0), arm64
- page fetched 2026-09-20 from `https://jevcache.sh/` (30,319 bytes)
- reproduction uses `JEVCACHE_BACKEND=mock` — no key, no network

### What the page says

> The same binary runs as a local cache your app talks to over HTTP. No library to install, no
> per-call process to spawn, and it works from any language — **you just POST a schema and some
> state.**

```js
// then, from your app — schema is inline, nothing to pre-register
const res = await fetch("http://localhost:9000/decide", {
  method: "POST",
  body: JSON.stringify({ schema, state: ticket }),
})
```

`schema` is a free variable and there is no schema literal anywhere on the page — searching the
HTML for `questions` returns zero hits. The README repeats the same
`POST /decide { schema, state }` shape without expanding it either.

### Reproduction

```sh
W=$(mktemp -d); export HOME="$W/home"; mkdir -p "$HOME"
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')
JEVCACHE_BACKEND=mock jevcache serve --port "$PORT" >/dev/null 2>&1 &
sleep 1
S='{"subject":"double charged","body":"I was billed twice this month"}'
post () { curl -sS -X POST "http://127.0.0.1:$PORT/decide" -H 'content-type: application/json' -d "$1"; echo; }

post "{\"schema\":{\"billing\":\"is this ticket about billing?\"},\"state\":$S}"
post "{\"schema\":{\"questions\":{\"billing\":\"is this ticket about billing?\"}},\"state\":$S}"
post "{\"schema\":{\"id\":\"support.route.v1\",\"questions\":{\"billing\":\"x\"}},\"state\":$S}"
post "{\"schema\":{\"id\":\"harm.v1\",\"questions\":{\"harmful\":\"x\"}},\"state\":$S}"
post "{\"schema\":{\"id\":\"harm\",\"version\":\"1\",\"questions\":{\"harmful\":\"x\"}},\"state\":$S}"
post "{\"schema\":{\"id\":\"harm\",\"version\":1,\"questions\":{\"harmful\":{\"instructions\":\"x\",\"type\":\"noul\"}}},\"state\":$S}"
kill %1
```

### Observed

```text
{"error":"schema.id must be a non-empty string"}                              [400]
{"error":"schema.id must be a non-empty string"}                              [400]
{"error":"schema.version must be an integer >= 1 (support.route.v1)"}         [400]
{"error":"schema.version must be an integer >= 1 (harm.v1)"}                  [400]
{"error":"schema.version must be an integer >= 1 (harm)"}                     [400]
{"answers":{"harmful":{"confidence":0.9,"value":true}},"cached":false,...}    [200]
```

Five rejections before the first success, each naming exactly one missing requirement.

Three things make this harder than "you must supply id and version":

1. **`version` cannot be folded into `id`.** `harm.v1` and `support.route.v1` are exactly how
   the CLI and README write schema references (`--schema support.route.v3`,
   `bundled support.route.v3@3`), and both are rejected. The `@` form is rejected too, with a
   third distinct message:
   `{"error":"schema.id \"failure.argument@1\" is invalid — use letters, digits, dot, dash, underscore (no slashes or \"..\")"}`
2. **The version error names the id**, so `schema.version must be an integer >= 1 (support.route.v1)`
   reads like a complaint about that schema's version rather than "you sent no `version` field".
3. **The question object shape is never validated locally.** A bare-string question passes
   jevcache's validator and then fails at the backend as an opaque relay:
   `{"error":"jev backend: https://api.typesafe.ai/v1/systemone: status code 400"}` with HTTP
   502. The working form —
   `{"instructions": "...", "type": "noul"}` — had to be reverse-engineered out of
   `~/.jevcache/ledger.log`, where a `{"t":"schema", ...}` row records it.

### Expected

The copyable example contains the `schema` literal it assumes, and the first rejection reports
every missing schema field rather than returning after the first one.

### Suggested direction

One line: put a complete inline schema in the page's example and validate the whole schema
object in one pass — the `id`/`version` split in particular is invisible to anyone who has only
ever seen the CLI's `name.vN` form.

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
