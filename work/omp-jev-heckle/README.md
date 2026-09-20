# omp-jev-heckle

Observe-only scorer for **error / empty / loading** copy. The planted dead
class (`An error occurred`, `Something went wrong`, `No data`, `Loading...`)
is a regex and never reaches Jev. The remainder asks one noul:

> Does the user know the next action from this copy?

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-heckle/test/
```

## Why this one calls Jev

`omp-jev-harm` dropped Jev because four regexes beat it. This surface is the
hybrid: regex takes the planted class; Jev takes paraphrase recovery copy,
which has no cheap expression.

## Stop-condition

If Jev on the planted class matches the regex, drop Jev. If `next_action` is
constant at 0.5 on the remainder fixtures, cut the question.

## Decision rows

| kind | meaning |
|---|---|
| `heckle_regex` | planted class; no model call |
| `heckle_scored` | Jev answered; `probabilities` present |
| `heckle_error` | key unset, transport failed, or a 200 with no probabilities |

Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
