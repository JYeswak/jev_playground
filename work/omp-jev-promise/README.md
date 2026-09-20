# omp-jev-promise

Observe-only scorer for **headline vs CTA**. An exact verb from the headline
that also appears in a control is a regex and never reaches Jev. Files with
no headline or no CTA record nothing. The remainder asks one noul:

> Does a control in this file do what the headline promises?

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-promise/test/
```

## Why this one calls Jev

`omp-jev-harm` dropped Jev because four regexes beat it. This surface is the
hybrid: regex takes the exact-verb class (`Export payroll` / `Export CSV`);
Jev takes paraphrase (`Take control of payroll` / `Get started`), which has
no cheap expression.

## Stop-condition

If Jev on the exact-verb match equals the regex, drop Jev. If `keeps_promise`
is constant at 0.5 on the paraphrase fixtures, cut the question.

## Decision rows

| kind | meaning |
|---|---|
| `promise_regex` | headline word (≥4 chars) is a substring of the joined CTAs; no model call; `matched: true` |
| `promise_scored` | Jev answered; `probabilities` present |
| `promise_error` | key unset, transport failed, or a 200 with no probabilities |

Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.
