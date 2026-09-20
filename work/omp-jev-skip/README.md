# omp-jev-skip

Observe-only scorer for **onboarding exits**. Non-onboarding paths never
reach Jev. Presence of a skip (`skip`, `not now`, `later`, `maybe later`,
`no thanks`) is a regex and never reaches Jev. The remainder asks one noul:

> Can a returning user leave this onboarding without completing it?

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-skip/test/
```

## Why this one calls Jev

`skip` / `not now` is a regex. A wizard whose only control is Continue, or
whose exit is a paraphrase ("I'll do this later"), has no cheap expression.

## Stop-condition

If `skip|not now` presence equals noul, drop Jev. If `can_leave` is constant
at 0.5 on the remainder fixtures, cut the question.

## Decision rows

| kind | meaning |
|---|---|
| `skip_regex` | planted skip-exit; `hasExit: true`; no model call |
| `skip_scored` | Jev answered; `probabilities` present |
| `skip_error` | key unset, transport failed, or a 200 with no probabilities |

Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
