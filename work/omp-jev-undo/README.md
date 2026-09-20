# omp-jev-undo

Observe-only scorer for **destructive UI**. A destructive verb
(`delete|remove|reset|…`) is the gate. An explicit way back (`undo|cancel|keep
it`) is a regex and never reaches Jev. The remainder asks one noul:

> Is there a way for the user to undo or leave this action without an extended dialogue?

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-undo/test/
```

## Why this one calls Jev

`omp-jev-harm` dropped Jev because four regexes beat it. This surface is the
hybrid: regex takes the planted exit; Jev takes paraphrase way-back copy,
which has no cheap expression.

## Stop-condition

If `undo|cancel` within the file equals the noul, drop Jev. If `way_back` is
constant at 0.5 on the remainder fixtures, cut the question.

## Decision rows

| kind | meaning |
|---|---|
| `undo_regex` | explicit way back; `hasExit: true`; no model call |
| `undo_scored` | Jev answered; `probabilities` present |
| `undo_error` | key unset, transport failed, or a 200 with no probabilities |

Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
