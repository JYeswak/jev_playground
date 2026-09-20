# omp-jev-fork

Observe-only scorer for **successive copy variants**. Remembers the last
content per user-facing path. On a second write to the same path with
*different* content, one choice:

> Which variant is clearer for a first-time client?

`A` | `B` | `none`

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-fork/test/
```

## Why this one calls Jev

Two writes to one path is a Map. Which variant a first-time client would
actually read is not. `none` is first-class so "both fine" / "both bad" is
sayable; a forced A/B is a fake choice.

## Stop-condition

If `none` never wins on "both fine", the choice is fake — cut it.

## Decision rows

| kind | meaning |
|---|---|
| `fork_scored` | Jev answered; `choice`, `confidence`, `probabilities` present |
| `fork_error` | key unset, transport failed, or a 200 with no choice; no `probabilities`, no `choice` |

A first write stores and writes no row. Same content does not call Jev.
Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
