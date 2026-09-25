# omp-jev-review

Advisory diff review scorer for omp. Watches `bash` tool calls, and when one is a
`git diff` / `git show` on our own code, asks Jev systemOne two questions about the change and
logs the answer. When the boundary answer is at least 0.9 it appends one advisory line to that
call's git output. It never blocks and has no merge authority.

In this repo it loads in every omp session from `.omp/extensions/jev-review.ts`, which fetches the
key from Infisical into the session's memory when the environment has none. Without any key, rows
record `review_error`, never a pass.

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

The questions are scored on diff **text**: the extension runs the same `git diff|show` itself
and sends the body (vendored sections removed, first 12,000 characters), never the command
string. The 686-commit draw scored 125 real code diffs this way
(`docs/demos/upstream-repro/omp-jev-review-draw-20260923.md`). None of them has a label, so no
accuracy is claimed on real traffic.

Seven hand-built diffs, labelled by whoever wrote them, bound nothing about real review traffic.

## Decision rows

| kind | meaning |
|---|---|
| `review_scored` | Jev answered; `probabilities` and `comment` (whether the advisory line was queued) present |
| `review_not_applicable` | `applicable:false`, zero Jev calls; `reason` is `empty-diff`, `vendored-diff`, `thin-diff`, `non-code-diff` or `not-a-plain-diff-command` (a pipe, `&&`, `;` or redirect: the extension never re-runs such a command) |
| `review_error` | git failed, key unset, transport failed, or a 200 with no probabilities |

There is no "clean" state. A failed call is never recorded as a pass — a crashed
classifier that logs a pass is indistinguishable from a real clean result.

Vendored means a directory segment `node_modules`, `vendor`, `third_party`, `dist`, `build`,
`.venv`, `venv`, `site-packages`, `docs-mirror` or `upstream`, or a lockfile. Those sections are
cut before scoring; a diff that is only vendored code is `vendored-diff`.

## The advisory line (jev-k9z.2)

A scored diff with boundary >= 0.9 gets one line appended to the same call's git output:

```
[jev-review advisory, no merge authority] boundary 0.92: this diff may touch a security,
permission, or authentication boundary. Fires on about 2% of code diffs; accuracy unmeasured.
```

0.9 was chosen by fire rate: 3 of the draw's 125 real code diffs. Every other result is left
untouched, including a failed git call and every other tool call. Receipt with live sessions
both ways: `docs/demos/upstream-repro/omp-jev-review-advisory-20260925.md`.

## Test

```bash
node --experimental-strip-types --test test/review.test.mjs   # 21/21
```

## Real commits: `behaviour` does not beat its own constant

`measure-realdiffs.mjs` scores the last 14 **real commits of this repository**, with labels
**computed from the diff, not typed by a human**:

- `behaviour` = the diff modifies a non-test source file
- `boundary` = a changed line matches a key/auth/permission/secret pattern

```
behaviour  8/14 | said-yes 3/14 | truth-yes 9/14 | best constant 9/14 | NO BETTER THAN ITS CONSTANT
boundary   9/14 | said-yes 2/14 | truth-yes 7/14 | best constant 7/14 | DISCRIMINATES (+2, 0 near-threshold)
```

**`behaviour` scored 6/7 on hand-built diffs and does not beat always-yes on real ones.**

**But the misses are ambiguous and the ambiguity is mine.** The model answered `false` on
commits that added a sampler, a measurement script, and a hold-out harness. My label calls any
non-test source edit behaviour-changing; a reasonable reviewer would say adding a new
standalone script changes no existing caller's behaviour. **On those rows the model is
plausibly right and the label is blunt.**

So this result is *not* "the question is bad". It is:

1. the hand-built 6/7 **did not transfer** to real commits under any labelling, and
2. **our labelling proxy is the weak link**, which is itself the finding — the first
   real-traffic measurement in this lane produced an ambiguous verdict because nobody had
   built ground truth that survives contact with real diffs.

`boundary` clears its constant by 2 with zero near-threshold verdicts and a 0.85 spread. Thin,
but the only question here with real-traffic support.

Reproduce (set `REVIEW_MEASURE_N` for a different window):

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types work/omp-jev-review/measure-realdiffs.mjs
```

**Nothing is cut on this evidence.** Cutting `behaviour` because a crude label disagreed with
it would be the same error as keeping a question because a tuned set flattered it.
