# omp-jev-jargon

Observe-only scorer for **engineering words in user-facing copy**. A local
stoptoken list is a GATE, not a verdict: if none of the tokens appear, the
extension records nothing and does not call Jev. When a token is present,
one noul:

> Would the client say this word for this thing, in their own language?

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-jargon/test/
```

## Why this one calls Jev

`omp-jev-harm` dropped Jev because four regexes beat it. This surface cannot
do that: a stoplist can name the suspects (`hydrate`, `payload`, `mutex`)
but cannot say whether the client would use that word. The list is a GATE.

## Stop-condition

If the stoplist hit-rate equals Jev on the remainder fixtures, ship the
stoptoken list and drop Jev. If `client_word` is constant at 0.5, cut the
question.

## Decision rows

| kind | meaning |
|---|---|
| `jargon_scored` | Jev answered; `probabilities` present |
| `jargon_error` | key unset, transport failed, or a 200 with no probabilities |

There is no `jargon_regex`. The stoplist decides whether to ask, not what
the copy is.

Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
