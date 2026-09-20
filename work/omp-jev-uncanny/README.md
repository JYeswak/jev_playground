# omp-jev-uncanny

Observe-only scorer for **product-as-observer** copy. A cheap prefilter
(`I noticed`, `I see you`, `you haven't`, `looks like you`, `I've been
watching`, `while you were`, `hey there`, `just checking in`) is a **GATE,
not a verdict**: a miss is 0 rows, never `uncanny_regex`. Ordinary copy
(`Save changes`) never reaches Jev.

v1 only fires when the prefilter hits, to keep call volume down. The
remainder still needs Jev — paraphrase (`Still here? I can help`) misses
the regex — but v1 does not send those yet.

One noul:

> Does this copy address the user as if the product is a person who is observing them?

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-uncanny/test/
```

## Why this one calls Jev

The planted observer phrases are a regex. Whether the product is addressing
the user as a person being watched, on paraphrase, is not. The prefilter
does not decide; it only throttles.

## Stop-condition

If Jev on the prefilter class matches the regex, drop Jev. If first-person
`we` is a constant, cut the question. If `watching` is constant at 0.5 on
the remainder fixtures, cut the question.

## Decision rows

| kind | meaning |
|---|---|
| `uncanny_scored` | Jev answered; `probabilities` present |
| `uncanny_error` | key unset, transport failed, or a 200 with no probabilities |

Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
