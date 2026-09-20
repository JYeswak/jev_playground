# One multiclass question beats three binary ones — re-run, not inherited

**Date:** 2026-09-19 · **Level:** `[live]` · **Unit:** `work/omp-jev-failure`, `work/jev-client`

`docs/demos/upstream-repro/jev-align-20260919.md` ended with a recommendation: replace this unit's
three binary questions with one multiclass question, because that restructuring — not GEPA — took
the failure set to 11/11 across four repeats. That result came out of jev-align's saved AI Function.
**Until it is re-run through our own client it is a claim, not evidence.** This is the re-run, plus
the conversion it licenses.

Everything below was produced by
`infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types
work/omp-jev-failure/measure-multiclass.mjs`, one command, three arms, three runs each,
`model=jev-1.13.0`.

## What the API actually supports, read before it was called

An invented request body got HTTP 400 in this lane earlier the same night, so no shape here was
guessed:

- `@typesafe-ai/sdk` v0.6.0 `dist/index.d.mts:63-68` — `ChoiceQuestion { type:"choice";
  instructions?; criteria: {label: description} }`; `:93-101` — `ChoiceResponse { choice;
  confidence; probabilities }`. There is no `.distribution`.
- `dist/index.mjs:339` — the SDK itself throws if `criteria` is a list rather than a map.
- jev-align builds exactly this for its multiclass task: `src/jev_align/jev.py:82-88` wraps the
  seed question in `Choice(instructions, criteria)`, and `cli.py:2419-2422` shows `--question`
  and `--class` reaching it unwrapped — so the receipt's 11/11 and this one are the same request.
- Confirmed live before writing any code: a hand-posted choice question returned
  `{"choice":"argument","confidence":0.97,"probabilities":{"transient":0.0,"argument":0.98,"bug":0.02}}`.

`askJevChoice` in `work/jev-client/src/index.ts` is that shape and only that shape. Both callers
now share one `postSystemOne`, so a body can be wrong in one place at most.

## The measurement

Same eleven committed cases, lifted out of `work/omp-jev-failure/measure.mjs` by the literal-slice
trick `work/jev-align-probe/export-failure-gold.mjs` already uses — not copied, because a
duplicated gold table drifts. Same `state`. **Only the question shape differs.** Scoring is
case-level for every arm: a binary case counts as correct only if all three of its verdicts are
right, which is the only way one label is comparable to three.

The harness prints the sha256 of the file it read (`07fcfd98d73d`) and the exact strings of each
arm, because `measure.mjs` was reworded by another lane at 18:27 while this work was running.

| arm | wording | case-level, 3 runs | drift | structurally impossible answers |
|---|---|---|---|---|
| `binary` | the three binary questions the extension shipped, **post-rescue wording** | 9/11, 9/11, 9/11 | none in this block | **2 per run** |
| `ours` | one choice question; our binary question strings verbatim as class text | 11/11, 11/11, 11/11 | none | 0 |
| `receipt` | one choice question; the receipt's declarative `--class` text | 11/11, 11/11, 11/11 | none | 0 |

Both adversarial arms — the two cases built so the misleading keyword leads and the disambiguating
evidence follows — passed in all six multiclass runs. No multiclass verdict was decided by a
top-1/top-2 margin under 0.10; the narrowest was `permission-denied-system-path` at 0.23 under the
question-shaped wording and 0.55 under the declarative one.

### The binary arm's failure is structural, not marginal

Every binary run answered **`argument` AND `bug` both true** on `assertion-expected-actual` and
`undefined-property-under-edit` — two classes true at once, on classes that are mutually exclusive
by construction. Three independent yes/no questions have no way to express exclusivity, so nothing
in that call shape forbids the row. A choice question forbids it in the protocol.

Two of the `argument` scores that produced it were 0.51 and 0.53: verdicts the 0.5 threshold made,
not the model.

### The rescued wording did not fix it

The binary arm above ran the **rephrased** `argument` question from the question-shape rescue
(`Does this error tie to the invocation's own arguments, path, or command rather than the
environment?`), not the original. It still never reached 11/11. Across all seven binary runs
tonight — three in this harness, two through `measure.mjs`, two through a throwaway probe importing
the extension's own `QUESTIONS` — the case-level score was 9, 10, 9, 9, 9, 9, 9, and the *identity*
of the missed cases moved between measurement blocks (`assertion-expected-actual` and
`undefined-property-under-edit` here; `permission-denied-system-path` and `adv-econnrefused-is-a-bug`
in the probe block). **The instability was never a wording problem.** Rewording moved which cases
broke; changing the shape stopped them breaking.

That both multiclass wordings — one of them our own binary strings, verbatim — score 11/11 is the
control that says the same thing from the other side: the win does not depend on the phrasing.

## The conversion

`work/omp-jev-failure/src/index.ts` now asks one choice question. Clean cutover, no alias:

- `QUESTIONS` → `FAILURE_QUESTION` + `FAILURE_CLASSES` (declarative text, chosen for the wider
  margin on the weakest case; both wordings measured identical verdicts).
- Row `kind` `failure_scored` → `failure_classified`, `schemaVersion` 1 → 2, `scores` →
  `failureClass` + `confidence` + `probabilities`. The full distribution stays on the row: a 0.98
  argmax and a 0.34 argmax are different facts.
- `test/failure.test.mjs` asserts the row shape, asserts `scores` is *gone* rather than aliased,
  and asserts the call carries `classes` and never a question map.

Live, through the installed path with no fixture injected:

```text
com.zeststream.omp-jev-failure.decision.v1
{"schemaVersion":2,"kind":"failure_classified","toolCallId":"live-smoke-1","toolName":"read",
 "failure":"ENOENT: no such file or directory, open 'wrok/jev-client/src/index.ts'",
 "latencyMs":421,"model":"jev-1.13.0","timestamp":"2026-09-20T00:37:00.159Z",
 "failureClass":"argument","confidence":1,"probabilities":{"transient":0,"argument":1,"bug":0}}
```

Tests: `work/jev-client/test/client.test.mjs` 14 (21 with subtests), `work/omp-jev-failure/test/failure.test.mjs` 5.

## Verdict

**Converted.** The receipt's claim reproduced through our own client: 11/11 on three consecutive
runs of each of two wordings, zero drift, both adversarial arms, against a same-session binary
baseline of 9/11 that emits two structurally impossible rows per run.

## NO-CLAIM

- **These eleven cases are the cases the class descriptions were shaped against.** There is no
  hold-out here, and a good-looking number on shaped cases is precisely the failure this lane hit
  tonight: a rescued question elsewhere scored 6/7 on fresh cases while answering *no* to all
  seven. Running this multiclass question on failures nobody wrote for it is the next unit and has
  not been done. Until then the honest claim is **stability and coherence on a fixed set, not
  accuracy**.
- Eleven hand-built failures, authored by someone who knew the answers, scored against the gold
  table that defines them. Nothing here estimates accuracy on real tool traffic, and nothing rules
  out that the case text makes its own class legible.
- Mixed causes — a flaky dependency exposed by a real bug — are absent from the set, and the
  multiclass framing *forces* a single label. Where the truth is genuinely two classes, this shape
  is now structurally incapable of saying so. That is a real cost of the change, untested here.
- Three repeats bound drift at this sample size only. A label stable across three calls can move on
  the fourth; the receipt's own `adv-econnrefused-is-a-bug` sat at 0.26–0.37 confidence through its
  runs while reaching 0.82 here, which shows how much the surrounding `state` shape moves
  confidence even when the argmax holds.
- The binary arm's 9/11 is the **post-rescue** wording measured tonight. It is not the number in
  the original `measure.mjs` receipt, and it is not evidence about the pre-rescue phrasing.
- The extension emits a class. It does not act on one. Nothing here licenses retrying, suppressing,
  or routing on a failure classification.
