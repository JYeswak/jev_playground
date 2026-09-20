# jevcache probe — what it does for us, measured

[jevcache](https://jevcache.sh/) memoizes Jev decisions by `(model, schema, state)`. This
directory holds what we ran and what we found, not what the site claims.

## It works. Verified here.

```
miss   0.613s   cached:false   noul 0.99   source jev-1.13.0
hit    0.00083s cached:true    noul 0.99   (738x faster, $0)
```

## Running it correctly

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  bash work/jevcache-probe/serve-with-jev.sh 9000
```

**`jevcache serve` reads its backend from its OWN environment at startup**, and a client cannot
supply it per-request. Started bare it falls back to a local model at `127.0.0.1:8080`, so every
`/decide` returns a 502 whose first line is a 404 against an address you never configured. That
cost us two restarts before anyone noticed.

An earlier version of this file called that message one that "reads like a broken model". That
was unfair and is corrected: the full body does name the fix
(`set JEVCACHE_BACKEND=jev (with JEV_API_KEY), or =mock to try it out`). What holds is narrower —
the banner says `backend: local` where nobody looks, and `/health` answers `{"ok":true}` while
the server cannot decide anything. See
[`docs/demos/upstream-repro/jevcache-upstream-reports-20260920.md`](../../docs/demos/upstream-repro/jevcache-upstream-reports-20260920.md).

The launcher also maps `TYPESAFE_API_KEY` → `JEV_API_KEY` (jevcache uses a different name),
fails loudly if the key is absent, and prints only the key's length.

## The impact on us is close to zero, and we measured it

`repeat-rate.mjs` computes our real recurrence from live decision rows:

| extension | calls | distinct | repeat |
|---|---|---|---|
| `omp-jev-route` | 134 | 11 | **92%** |
| `omp-jev-preaction` | 49 | 45 | 8% |
| `omp-jev-review` | 3 | 3 | 0% |
| `omp-jev-failure` | 1 | 1 | 0% |
| **total** | **187** | **60** | **67.9%** |

**Do not quote the 67.9%.** It is carried entirely by `route`, and route's 92% is *us
re-probing one turn 24 times* — a testing artifact, not production behaviour. For extensions
doing varied real work the repeat rate is **0–8%**, and `preaction` (the 8%) makes no model
call at all.

Our states are commands, diffs and prompts. They are nearly all distinct. jevcache's 60–80%
recurrence figure is real for ticket-routing workloads; **ours is not that workload.**

A first cut of this measurement reported **99.1%** because the extractor fell back to a
constant key for rows with no state field, and counted non-model bridge rows. Rows without a
stored state are now **excluded, not guessed** — the same crude-proxy failure that made the
`review` real-diff labels ambiguous.

## Where it must never go

**The measurement harness.** Every `measure*.mjs` runs three times on byte-identical input to
detect drift. `argument` moved `0.47 → 0.50 → 0.48` and flipped HIT→MISS→MISS that way. Through
a cache, runs 2 and 3 are replays of run 1, drift reads as exactly zero, and an unstable
question ships as stable. Verified: four identical calls returned `0.51` every time.

## Where it is genuinely useful

**Deterministic offline replay** — `jevcache recall` exits 3 on a miss, so a CI gate can pin a
decision instead of depending on a live model. That is the property we want, and the site
treats it as secondary to cost.

## Upstream defects found

Six, written up with reproductions in
[`docs/demos/upstream-repro/jevcache-upstream-reports-20260920.md`](../../docs/demos/upstream-repro/jevcache-upstream-reports-20260920.md);
one is filed as [jevcache#1](https://github.com/hyperspaceai/jevcache/issues/1) and five are
drafted. Reproductions are `repro-1` … `repro-6` in this directory, all key-free and offline.

1. `state_preview` writes raw state to a 0644 ledger — PII redacted, credentials not. **Filed.**
2. Any `*_id` field is dropped **before** hashing, so different states collide on one
   fingerprint and get each other's cached answers. Measured live: after deciding `echo hello`,
   `rm -rf --no-preserve-root /` comes back `noul 0.01`, cached, from `jev-1.13.0`. This is the
   serious one.
3. One global append-only ledger with **no per-process isolation** — concurrent agents silently
   share a cache, and unlocked concurrent appends corrupt it and lose written decisions.
   `JEVCACHE_DIR` scopes it, but by convention only.
4. `serve` prints the *requested* port, not the bound one: `--port 0` prints `:0` while
   listening on an ephemeral port. `--port abc` is silently discarded.
5. The installer's checksum is soft — a failed `.sha256` fetch installs anyway, rc=0.
6. The documented `/decide` example does not run — `schema.id` and `schema.version` are both
   required as separate fields, revealed one error at a time. `harm.v1` is rejected as an id.

**Retracted:** an earlier version of this list claimed `serve --port 9000` prints "port 0" on
startup. It does not; that was inferred from an `lsof` reading and never observed. Item 4 is the
real defect in that line, and it needs `--port 0` to trigger.

## NO-CLAIM

One machine, one evening, 187 model-scored rows. The repeat rate is ours and does not
generalise. We have not tested `publish`, the hosted index, or whether anything is transmitted
without an explicit publish — that arm is open.
