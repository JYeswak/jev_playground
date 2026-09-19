# omp-jev-review

Observe-only diff review scorer for omp. Watches `bash` tool calls, and when one is a
`git diff` / `git show`, asks Jev systemOne three questions about the change.

```bash
omp plugin install omp-jev-review
export TYPESAFE_API_KEY=...        # without it, rows record review_error, never a pass
```

## Why this one calls Jev and our other two do not

`omp-jev-harm` and `omp-jev-preaction` contain no model call, because on those surfaces four
regexes beat live Jev on a held-out split (12/12 vs 11/12, FP 0/38). That was a cost-benefit
ruling about **one surface**, not a ban on the model.

Review judgement is the opposite case. There is no regex for *this refactor silently changed a
default*. A judge earns its seat exactly where a rule cannot be written.

## Decision rows

| kind | meaning |
|---|---|
| `review_scored` | Jev answered; `probabilities` present |
| `review_error` | key unset, transport failed, or a 200 with no probabilities |

There is no third "clean" state. A failed call is never recorded as a pass — a crashed
classifier that logs a pass is indistinguishable from a real clean result.

Never blocks. Never throws into the host. Returns `undefined` on every path.

## Test

```bash
node --experimental-strip-types --test test/review.test.mjs   # 6/6
```
