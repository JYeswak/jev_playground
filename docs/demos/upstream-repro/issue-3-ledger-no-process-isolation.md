# Issue 3 — ready to post

**Repo:** `hyperspaceai/jevcache` · **Title:** `one global ledger with no per-process isolation: unrelated processes share a cache, and concurrent writers corrupt the log and lose decisions`

<!-- Everything below the line is the issue body. Paste as-is. -->

---

`jevcache` keeps everything in a single append-only `$JEVCACHE_DIR/ledger.log`, defaulting to
`~/.jevcache`. There is no per-process, per-project or per-run namespace, no flag, and no lock
on the append. On a machine running several agents or services that is a correctness hazard,
not only a privacy one.

### Environment

- `jevcache version` → **0.1.0**, installed via `curl -fsSL jevcache.sh/install | sh`
- binary sha256 `68fcb95b908cf3ee73dbeb3df52b265f6b908a6a9cfd661c5c6429d32f7535d5`
- macOS 26.5.2 (Darwin 25.5.0), arm64, Apple M3 Ultra, APFS
- `JEVCACHE_BACKEND=mock` — no key and no network needed

### Reproduction

`HOME` is redirected to a temp dir **only** to keep the script harmless; nothing in jevcache
scopes below `$HOME/.jevcache` by itself.

```sh
W=$(mktemp -d); cd "$W"
cat > jevcache.schemas.json <<'EOF'
[{"id":"probe","version":1,"questions":{"q":{"instructions":"Is this destructive?","type":"noul"}}}]
EOF
export JEVCACHE_BACKEND=mock

# --- part 1: two unrelated processes share one ledger
export HOME="$W/home"; mkdir -p "$HOME"
echo '{"ticket":"agent-A state"}' > s_a.json
echo '{"ticket":"agent-B state"}' > s_b.json
jevcache decide --schema probe --state s_a.json --json >/dev/null   # process A
jevcache decide --schema probe --state s_b.json --json >/dev/null   # process B
ls -l "$HOME/.jevcache/ledger.log"
jevcache recall --schema probe --state s_a.json --json; echo "recall rc=$?"   # B hits A's decision

# --- part 2: JEVCACHE_DIR does isolate
JEVCACHE_DIR="$W/dirA" jevcache decide --schema probe --state s_a.json --json >/dev/null
JEVCACHE_DIR="$W/dirB" jevcache recall --schema probe --state s_a.json --json; echo "recall rc=$?"

# --- part 3: 20 trials x 16 concurrent writers on one ledger
PAD=$(printf 'x%.0s' $(seq 1 300))
for trial in $(seq 1 20); do
  H="$W/t$trial"; mkdir -p "$H"; export HOME="$H"
  for i in $(seq 1 16); do printf '{"t":%d,"n":%d,"pad":"%s"}\n' "$trial" "$i" "$PAD" > "$W/s${trial}_$i.json"; done
  for i in $(seq 1 16); do jevcache decide --schema probe --state "$W/s${trial}_$i.json" --json >/dev/null 2>&1 & done
  wait
  mal=$(python3 -c '
import sys, json
bad=0
for line in open(sys.argv[1]):
    line=line.strip()
    if not line: continue
    try: json.loads(line)
    except Exception: bad+=1
print(bad)' "$H/.jevcache/ledger.log")
  miss=0
  for i in $(seq 1 16); do
    jevcache recall --schema probe --state "$W/s${trial}_$i.json" --json >/dev/null 2>&1 || miss=$((miss+1))
  done
  printf 'trial %2d: malformed_lines=%s  written_then_unrecallable=%s/16\n' "$trial" "$mal" "$miss"
done
```

### Observed

**Part 1 — silent cross-process sharing.** Two processes that were never told they were related
share a cache. Process B's `recall` returns `rc=0` (HIT) for a decision only process A ever
made:

```text
-rw-r--r--@ 1 user staff 1033 ... /tmp/.../home/.jevcache/ledger.log
{"answers":{"q":{"confidence":0.9,"value":true}},"fingerprint":"d7f67f3d…","hit":true,"source":"mock"}
recall rc=0
```

Sharing is the point of a cache — but the unit of sharing here is the whole Unix account. Two
agents evaluating two different systems on one box pollute each other by default, and the
ledger carries a plaintext `state_preview` of each other's inputs (filed separately).

**Part 2 — `JEVCACHE_DIR` does work.** A clean miss across two scoped dirs:

```text
{"fingerprint":"d7f67f3d…","hit":false}
recall rc=3
```

It is opt-in environment, not a flag, not a default, absent from the landing page, and listed
once in the README config table as "ledger + schemas location". The isolation exists and is
undiscoverable from where a user starts.

**Part 3 — unlocked concurrent appends corrupt the ledger and lose decisions.** Records
interleave: a line ends up holding two concatenated JSON objects
(`json.loads` → `Extra data: line 1 column 529`), and a decision that jevcache reported as
written becomes permanently unrecallable — `recall` returns `rc=3` for a state it had already
decided and stored.

The rate is load-dependent, so here are three separate batches rather than one number, same
binary, same machine, same evening:

| batch | concurrent writers | trials | trials with a malformed line | decisions lost |
|---|---|---|---|---|
| 1 | 16 | 5 | 3/5 | 1/80 |
| 2 | 16 | 20 | 2/20 | 7/320 (6 of them in a single trial) |
| 3 | 16 | 20 | 1/20 | 2/320 |

Sample trial from batch 2:

```text
trial  4: malformed_lines=7  decisions_lost=6/16
```

No rate is being claimed — only that it is nonzero for processes that were never told they were
sharing a file, and that nothing surfaces the loss: `decide` returned success for all 16.

### Expected

Concurrent writers do not corrupt the log or lose committed decisions. Ledger scope is at
minimum discoverable, ideally a first-class flag rather than an environment variable found by
reading a config table.

### Suggested direction

One line: the append path needs a lock or a single-`write` `O_APPEND` discipline before
anything else — silent loss of a stored decision is the one failure a decision ledger cannot
have; scope and namespacing are a design conversation, atomic append is not.

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
