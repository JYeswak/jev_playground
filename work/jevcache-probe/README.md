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
supply it per-request. Started bare it silently falls back to a local model at
`127.0.0.1:8080`, so every `/decide` returns a 404 that *reads like a broken model* and is
actually an unconfigured server. That cost us two restarts before anyone noticed.

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

1. The documented `/decide` example does not run — `schema.id` and `schema.version` are both
   required as separate fields, revealed one error at a time. `harm.v1` is rejected as an id.
2. `serve --port 9000` prints "port 0" on startup while binding 9000 correctly. Cosmetic, but
   it is what made us think the bind had failed.
3. One global append-only ledger at `~/.jevcache/ledger.log` with **no per-process isolation** —
   concurrent agents silently share a cache. `JEVCACHE_DIR` scopes it, but by convention only.

## NO-CLAIM

One machine, one evening, 187 model-scored rows. The repeat rate is ours and does not
generalise. We have not tested `publish`, the hosted index, or whether anything is transmitted
without an explicit publish — that arm is open.
