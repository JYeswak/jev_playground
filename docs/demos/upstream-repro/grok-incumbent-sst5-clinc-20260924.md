# A second LLM family on the wins that held: grok-4.20 on SST-5 and CLINC150 (bead `jev-n4j`)

ConfidenceCascade (background agent of pane 1), 2026-09-24. Live lane: grok calls only, and the Jev
rows are the committed ones.

## Preregistered (committed before any grok call)

**Question.** Two Jev results have survived their checks so far. On SST-5, Score's MAE WIN over
Haiku 4.5 held in every re-run of either arm (`jev-qbc`, `jev-x5k`). On CLINC150 15 intents plus
out-of-scope, the gated result was a WIN at peak >= 0.60 (`jev-qw8`). Both were measured against
one LLM family only. `jev-dsu` ([receipt](second-incumbent-20260924.md)) put grok against SciFact
and Banking77. Does each of the two wins hold when the incumbent is xAI's grok instead of Haiku,
asked the identical question through the identical adapter?

**Incumbent, pinned.** `grok-4.20-0309-non-reasoning` on xAI (`https://api.x.ai/v1`), behind
`system-one-adapter-python` at `adffc2e` (checkout clean) through its caller-owned
`AsyncOpenAIProvider`. This is the path `jev-dsu` used (`work/second-incumbent/run.py`, unchanged
apart from two datasets added in this commit). Adapter settings copy the Haiku arms: structured
outputs, `llm_answer_mode="probabilities"`, `normalize_probabilities=True`, `RetryPolicy()`, 8
concurrent, 90 s per call. **Key:** `XAI_API_KEY` from the lane's Infisical project, found the way
`jev-dsu` found it. Only presence and length were checked (`len=84`); the value is never printed.
No grok call, not even a smoke, is made before this commit.

**Inputs, read with `git show` from the commits the original arms used (byte-identical):**
- SST-5 (`jev-zui`): question and state from `work/score-sst5/run.py` @ `ae161b6`: one Score,
  *"How positive is this movie review sentence?"*, five level descriptions, and the sentence as a
  string. 500 rows from `sample.jsonl` @ `ae161b6`. Jev rows @ `576e60e`.
- CLINC150 (`jev-qw8`): labels, question and state from `work/choice-clinc150/run.py` @ `e0950ce`:
  one Choice, 15 intents plus `none of the above` last, state `{"user_request": ...}`. 750 rows from
  `subset.jsonl` @ `e0950ce`. Jev rows @ `2842340`.
- New row files only: `work/second-incumbent/rows-sst5-grok.jsonl` and `rows-clinc150-grok.jsonl`.
  Each row records the adapter's debug: SST-5 `probabilityError` and `originalProbabilities`;
  CLINC `probabilityError` and `rawSum`. It also records the provider's final-attempt facts
  (`modelReported`, `finishReason`, attempts). One resume pass for failed rows.

**Scorer.** `python3 work/second-incumbent/score_n4j.py` (keyless). It runs each unit's own
`score.py` at the commit its receipt scored (SST-5 @ `576e60e`, CLINC @ `2842340`). It exits 1
unless the committed Haiku results reproduce (SST-5 Jev 273 / Haiku 251, MAE sign 109 vs 75;
CLINC overall 688 vs 681, handled 685 vs 650); both do now. A planted run outside the tree
exercised the zero-mass paths: Haiku rows standing in as grok, with 3 SST-5 rows and 50 CLINC
out-of-scope rows zeroed.

**Verdict rules, copied from each unit's bar.**
- **SST-5** (`score-sst5-20260924.md`). Level = `floor(score + 0.5)`. A failed row is wrong with
  error `max(y, 4 - y)`. Accuracy is compared with McNemar exact and MAE with an exact sign test on
  per-row absolute error, alpha 0.05. **Pass rule:** Jev beats both constants (always 1, always 2)
  on accuracy and MAE, and neither test is a significant grok win. **The win under test:** the MAE
  sign test is WIN against grok.
- **CLINC150** (`choice-clinc150-20260924.md`). Primaries are overall correct (750) and handled at
  peak probability >= 0.60, each against the always-none constant (300). The rule is `jev-k3k`'s:
  LOSE if Jev is at or below the constant or more than 3.0 pp below; WIN if Jev-only > other-only
  with McNemar p < 0.05; otherwise NON-INFERIOR. Feasibility requires in-scope accuracy >= 50% per
  arm. The incumbent is read two ways, as shipped and with zero-mass rows as "none of the above",
  and each verdict is the worse of the two for Jev. **Pass rule:** both primaries WIN or
  NON-INFERIOR. **The win under test:** handled at 0.60 is WIN.

**Zero-mass handling (`jev-mly`), as `jev-dsu` did.** A zero-mass grok row has a raw map that
sums to 0 (SST-5 `originalProbabilities`, CLINC `rawSum`). The adapter ships those as a uniform
answer. Every verdict is reported on all rows **and** with zero-mass rows dropped from both arms.
For CLINC, "dropped" is a third reading beside the unit's two.

**Decision, fixed now.**
- A win **HOLDS against grok** only if it is WIN under the unit's rule **and** with zero-mass rows
  dropped.
- A win that does not hold gets a `NEGATIVE_EVIDENCE.md` row with a retry condition, and the
  README's claim that the win is "against an LLM" stays scoped to Haiku.
- A pass rule that FAILs (a LOSE, or feasibility not met) also gets a `NEGATIVE_EVIDENCE.md` row.
- A grok run with more than 1% failed rows after the resume pass (5 on SST-5, 7 on CLINC) is
  reported as failed, with no verdict for that unit.

**Spend, planned.** 500 + 750 = 1,250 grok calls, plus resume calls. xAI list prices are not read
here, so dollar spend is reported only as tokens.

**NO-CLAIM.** One grok model, non-reasoning, one run each, one adapter version. Jev rows are the
single committed run for each unit. The OpenAI lineage stays untested (its key returned 401 in
`jev-dsu`). A HOLD here says the win is not Haiku-specific for this one other family. It does not
generalize to every LLM.

## Result

Pending the live run.
