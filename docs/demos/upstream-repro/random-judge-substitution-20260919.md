# If Jev were replaced by a coin flip tonight, five of six repos' CI would stay green

**Date:** 2026-09-19 · **Level:** `[oracle]` · Work in scratch copies; vendored clones unmodified.

The experiment: patch the judge seam in each repo to emit **well-formed random** answers over the
same option sets — every distribution sums to 1, every argmax is consistent, all wire plumbing
intact — then run the suite unchanged. A test that stays green cannot tell a working judge from
a coin flip.

## Test classes

- **(a) MOCK-SCRIPTED** — the test supplies the judge's answer *and* the expected outcome. Blind by construction.
- **(b) RECORDED/GOLDEN** — a committed real response replayed. Catches decoder drift, never judge drift.
- **(c) GROUND-TRUTH** — scored against a label the judge did not supply. **The only class that catches a random judge.**

## Result

| repo | tests | survives a random judge | class (c) |
|---|---|---|---|
| `AbdelStark/bicameral` | 41 | ~85% random, **90% with a judge that blocks everything** | **0** |
| `tamaratran/fast-jev-compaction` | 29 | 93% random, **97% with a judge that keeps everything** | **0** |
| `browser-use/jev-ultrafast` | 31 | **90–97%** (agent clicking random page elements) | 0 in pytest |
| `typesafe-ai/system-one-adapter-python` | 204 | 164/204 — **the only real gate** | **17** |
| `AbdelStark/s1-rs` | ~15 | wire-format pins only (build denied here) | **0** |
| `Dicklesworthstone/skillranker` | — | malformed output only, never wrong ranking | **0** |

**305 executable tests → 254 (83%) still green.** Of the 51 that broke, **35 broke trivially**:
they pinned the literal number they fed the mock (`toMatchObject({noul: 0.7})`,
`assert 'DONE' == 'TYPE_TEXT'`), so they'd fail for a *correct* substituted judge too.

**Only 17 tests (5.6%) fail a random judge on principle, and all 17 are in one file.** Sixteen
score OpenAI/Anthropic behind the adapter. **Exactly one test in six repositories scores Jev
itself against a label Jev did not supply** — proven real by mutating its cassette until it
failed and restoring it until it passed.

The pattern is structural, not sloppy: nearly every test builds the judge's answer and the
expected outcome from the same literal, so the judge is **definitionally right**.

## Total ground-truth evidence about Jev in this ecosystem

**4 labeled questions, from 2 recorded calls, on 2 synthetic toy states, plus 6 live runs of a
single browser task.** Where it is measured, it is good: 3/3 on the review probe at 0.98/1.00/1.00;
1/1 on skillranker's shape probe at p=1.00; **6/6 verified** live Google Flights runs against an
independent end-state checker it could not game (median 9.450 s → 7.092 s, 1092 → 101 CDP calls),
from a repo that publishes its failures too. Nothing measures ambiguity, adversarial input, long
context, or near-miss cases.

## Two findings worth more than the survival rates

- **skillranker's labeled corpus is never pointed at the product.** 12 cases, a frozen 0/1/2 loss
  table, a negative control, a ≥0.90 promotion gate — referenced only by its own validator; `src/`
  never reads it. Computed what it *would* show: coin-flip judge **1.011 ± 0.210** mean loss,
  **worse than always-abstain (0.833)**; uniform-pick top-1 precision **0.484** against a 0.90 gate.
  The corpus is discriminative; it is simply not wired in. That number took ten minutes.
- **`fast-jev-compaction` is the one I would not deploy.** It silently deletes agent history on
  Jev's say-so, has **zero** retention oracle, and one of its 29 tests notices a judge stuck at
  "keep everything" — for a *reduction-ratio* reason, not a correctness one.

## The fix is already demonstrated inside this set

`system-one-adapter-python`: **labeled probe + committed VCR cassette + `> 0.9` assertion** — a
judgment-quality gate that runs in CI with **no key and no network**. That is the pattern to copy.

## NO-CLAIM

This proves the **suites' blindness**, not that Jev judges badly. `random`/`calm`/`alarm` are
substitutions at each repo's judge seam, not observations of the real model. Two Rust repos were
read, not built (local Rust builds denied on this host). The 6/6 flights verdicts are read from
committed receipts — no `final_page` is committed, so they were not reproduced.
