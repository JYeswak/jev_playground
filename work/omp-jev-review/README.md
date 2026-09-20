# omp-jev-review

Observe-only diff review scorer for omp. Watches `bash` tool calls, and when one is a
`git diff` / `git show`, asks Jev systemOne two questions about the change.

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

## Two questions, because measurement killed the third

It shipped with three. `measure.mjs` scored all three against seven diffs whose answers we know
by construction — comment-only, a changed exported default, a deleted admin check, a CORS
allowlist widened to `*`, 400 renamed lines sold as "tidy up", a new isolated test file, and a
dependency bump with its lockfile.

| question | behaviour across 7 cases | verdict |
|---|---|---|
| `behaviour` | 6/7; scores 0.03 → 0.81, fired on the changed default and both boundary cases | kept |
| `boundary` | 7/7; 0.97 and 0.94 on the two security cases, ≤0.21 on the other five | kept |
| `scope` | 6/7, but said **no** on all seven — constant at threshold 0.5 | cut |

Total agreement 19/21 against a coin-flip baseline of 10.5. The total is not the finding; the
split is. `scope`'s 6/7 is the base rate of a label that is false on six of seven cases, and it
missed the single case it exists for: the 400-line rename scored **0.39 / 0.40 / 0.41** across
three runs — *below* a three-line auth deletion at 0.43 / 0.40 / 0.44. So it is not a threshold
that needs lowering; the ordering is wrong too. **A question whose verdict does not change with
its input is not a cheap signal; it is noise with a confidence attached.**

`behaviour`'s one miss is the dependency bump (0.19–0.20), which we label true because a runtime
upgrade swaps executed code under unchanged call sites. That label is the measurement's only
judgement call and `measure.mjs` says so at the case.

Reproduce:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types work/omp-jev-review/measure.mjs
```

`measure.mjs` still asks all three, including the cut one, so the cut stays reproducible.

## What the measurement does NOT cover

It scores the questions against diff **text**. This extension sends `state: { diff: command }` —
the command *string*, `git diff HEAD~1 -- src/server/dashboard.ts`, not the diff body. A live
run of the shipped path returns `{behaviour: 0.41, boundary: 0.24}` from a filename. So 19/21 is
an **upper bound** the extension does not reach, and the numbers in the decision rows today are
scored on far less than the table above. Unmeasured, therefore unchanged: fixing the input is a
behaviour change and gets its own measurement.

Seven hand-built diffs, labelled by whoever wrote them, bound nothing about real review traffic.

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
node --experimental-strip-types --test test/review.test.mjs   # 7/7
```
