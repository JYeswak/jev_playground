# Issue 2 — ready to post

**Repo:** `hyperspaceai/jevcache` · **Title:** `canonicalization drops any *_id field before hashing, so materially different states share one fingerprint and receive each other's cached answers`

<!-- Everything below the line is the issue body. Paste as-is. -->

---

The volatile-field rule that keeps ids out of the cache key removes them from the canonical
state entirely, by field-name suffix, with no check on whether the value is decision-relevant.
Two states that differ only inside a `*_id` field therefore hash to the same fingerprint, and
the second one is served the first one's answer.

This is not a privacy report. It is a correctness one: a cache returns a stored answer for a
question it was never asked.

### Environment

- `jevcache version` → **0.1.0**, installed via `curl -fsSL jevcache.sh/install | sh`
- binary sha256 `68fcb95b908cf3ee73dbeb3df52b265f6b908a6a9cfd661c5c6429d32f7535d5`, byte-identical
  to the published `jevcache.sh/bin/jevcache-darwin-arm64`
- macOS 26.5.2 (Darwin 25.5.0), arm64
- shown below on both `JEVCACHE_BACKEND=mock` (no key, no network) and a real backend
  (`JEVCACHE_BACKEND=jev`, `typesafe/jev-1.13.0`), because the real backend is what shows the
  two states deserve different answers

### Reproduction

```sh
W=$(mktemp -d); cd "$W"; export HOME="$W/home"; mkdir -p "$HOME"
cat > jevcache.schemas.json <<'EOF'
[{"id":"harm","version":1,"questions":{"harm":{"instructions":"Is this command destructive?","type":"noul"}}}]
EOF
export JEVCACHE_BACKEND=mock      # or: jev, with a key, to see the answers differ

ask () {   # label, state, ledger dir
  printf '%s' "$2" > st.json
  out=$(JEVCACHE_DIR="$W/$3" jevcache decide --schema harm --state st.json --json)
  printf '  %-32s %s\n' "$1" "$(python3 -c '
import sys, json
o=json.loads(sys.stdin.read())
print("fp="+o["fingerprint"][:16], "cached="+str(o["cached"]), "answer="+json.dumps(o["answers"]))' <<<"$out")"
}

# control: the differing content lives in a field called "command"
ask "command = rm -rf /"      '{"command":"rm -rf --no-preserve-root /"}' c1
ask "command = echo hello"    '{"command":"echo hello"}'                  c2

# defect: identical content, field renamed to "command_id", one shared ledger
ask "command_id = echo hello" '{"command_id":"echo hello"}'                  d
ask "command_id = rm -rf /"   '{"command_id":"rm -rf --no-preserve-root /"}' d
```

### Observed

With a real backend (`JEVCACHE_BACKEND=jev`, `typesafe/jev-1.13.0`), 2026-09-20:

```text
=== control: field named 'command', separate ledgers ===
  command = rm -rf /               fp=53c3348a9fcc850f cached=False answer={"harm": {"noul": 0.99}}
  command = echo hello             fp=f5f5569d5a0930ed cached=False answer={"harm": {"noul": 0.01}}

=== defect: field named 'command_id', one ledger, benign decided first ===
  command_id = echo hello          fp=9aaa9da807f4cc37 cached=False answer={"harm": {"noul": 0.01}}
  command_id = rm -rf /            fp=9aaa9da807f4cc37 cached=True  answer={"harm": {"noul": 0.01}}
```

The model's own judgement, when asked, is `0.99` destructive for `rm -rf --no-preserve-root /`
and `0.01` for `echo hello` — the control proves the two states are not equivalent. Rename the
field to `command_id` and they collapse onto one fingerprint, so **`rm -rf --no-preserve-root /`
is answered `0.01` — not destructive — from cache**, attributed to the real model:

```text
$ jevcache recall --schema harm --state st.json --json     # recall never calls a backend
{"answers":{"harm":{"noul":0.01,"type":"noul"}},
 "fingerprint":"9aaa9da807f4cc377b0a911bdcdab10d32ad960eb5a73b2d787bc5a6ecaa50ca",
 "hit":true,"source":"jev-1.13.0"}
```

It is symmetric — decide the destructive one first and `echo hello` comes back `0.99`
destructive — so the failure is not biased toward safe or unsafe; it is whichever arrived
first.

The mechanism is visible in the ledger: the canonical state that was hashed and stored is
empty.

```text
   state_preview: {}
```

Same run on `JEVCACHE_BACKEND=mock` produces the identical fingerprints
(`53c3348a…`, `f5f5569d…`, `9aaa9da8…`) and the same `cached=True`, so this is the
canonicalizer, not the backend.

The rule appears to be a field-name suffix. The same value under two names behaves oppositely:

```text
{"aws_access_key_id":"AKIAIOSFODNN7EXAMPLE"}  -> canonical state {}
{"aws":"AKIAIOSFODNN7EXAMPLE"}                -> stored in full
```

### Why it bites in practice

`*_id` is the normal name for the thing a decision is *about* — `ticket_id`, `command_id`,
`document_id`, `target_id`, `customer_id`. The README's example schema is a support-ticket
router; a state shaped `{"ticket_id": …, "priority": …}` loses the ticket. And for anything
safety-shaped — a harm gate, a permission check — the collision can return a stored "safe" for
an unsafe input, from `recall`, offline, with no backend call and no signal that anything
merged.

It also interacts with the shared-ledger behaviour reported separately: the bigger and more
shared the ledger, the more likely a colliding entry is already present.

### Expected

The canonicalizer excludes a field from the *key* only when its value is genuinely volatile,
or at minimum does not silently discard the only content that distinguishes two states.
Whatever the policy, two states a human would call different should not produce one
fingerprint.

### Suggested direction

One line: name-suffix matching is doing value-semantics work — a `*_id` field whose value is
not id-shaped (a UUID, a digit run, a timestamp) is almost always the payload, and collapsing
it is the difference between a cache and a wrong answer.

### Dedup

Checked before filing, 2026-09-20T03:36Z:

```sh
$ gh issue list --repo hyperspaceai/jevcache --state all --limit 30
1  OPEN  state_preview persists unredacted credentials to a world-readable ledger  2026-09-20T03:29:37Z

$ for q in fingerprint collision canonical volatile _id cache key; do \
    gh issue list --repo hyperspaceai/jevcache --state all --search "$q" --limit 5; done
# no match other than #1

$ gh release list --repo hyperspaceai/jevcache --limit 5
jevcache v0.1.0  Latest  v0.1.0  2026-09-19T17:44:40Z
```

Issue #1 is the privacy side of the same redactor (credentials persisted in `state_preview`).
This report is the correctness side and shares no expected behaviour with it. `v0.1.0` is the
only release.
