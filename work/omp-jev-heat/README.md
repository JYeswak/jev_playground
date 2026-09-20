# omp-jev-heat

Observe-only **ATTENTION** scorer, not taste. It is in the taste-loop set
because the lane has session JSONL that can actually label it — not because
it is a second taste component, and not as a promotion.

Subscribes to `context` (not `tool_call`). One choice:

> Relative to the client's job, what is this turn?

`golden_path` | `supporting` | `yak` | `hygiene` | `none`

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-heat/test/
```

## Why this one calls Jev

Hardness-of-attention has no cheap regex. No literal distinguishes the
client's core job from engineer-fun infra. A judge earns its seat exactly
where a rule cannot be written.

## Stop-condition

If the choice cannot beat always-`hygiene` on frozen turns, cut.

## Decision rows

| kind | meaning |
|---|---|
| `heat_scored` | Jev answered; `choice`, `confidence`, `probabilities` present |
| `heat_error` | key unset, transport failed, or a 200 with no probabilities |

Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
Attention, not taste. Included because session logs exist.
