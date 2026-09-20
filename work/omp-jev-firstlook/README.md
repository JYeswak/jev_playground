# omp-jev-firstlook

Observe-only scorer for **first-screen job-to-be-done**. User-facing writes
to a first-look path (`index` / `home` / `landing` / `app` / `page` /
`welcome`) accumulate. On `session_stop`, one choice:

> How fast is the job-to-be-done obvious from this first screen copy?

`lost` | `hunting` | `got_it`

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-firstlook/test/
```

## Why this one calls Jev

The first-look *path* is a regex. Whether a first-time user can tell what
the product does from the copy on that path is not. Three independent noul
scores can say yes twice; a choice question cannot.

## Stop-condition

If a CTA-present heuristic matches the choice, kill at rung 2.

## Decision rows

| kind | meaning |
|---|---|
| `firstlook_scored` | Jev answered; `choice`, `confidence`, `probabilities` present |
| `firstlook_error` | key unset, transport failed, or a 200 with no choice; no `probabilities`, no `choice` |

An empty buffer on `session_stop` writes no row. Never blocks. Never throws
into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
