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

Bar at `975cf81`, committed before any grok call. Live, 2026-09-24, `[live]`. Grok made 1,250
calls, all answered, with 0 failed rows and 0 resume passes. Every row's provider-reported model is
`grok-4.20-0309-non-reasoning`, with finish reason `stop`, one attempt and 0 transient retries.
Rows: `work/second-incumbent/rows-sst5-grok.jsonl` (sha256 `287dea63…752d8b`) and
`rows-clinc150-grok.jsonl` (sha256 `a0701551…569470`). Re-score with no key:
`python3 work/second-incumbent/score_n4j.py`. Its Haiku self-checks reproduce on both units.

**Adapter zero-mass: 0 rows on both units.** `probability_errors` was set on 0 of 500 SST-5 rows
and 0 of 750 CLINC rows. No raw map summed to 0, and no SST-5 answer was a flat distribution. So
the "zero-mass dropped" and "zero-mass = none" readings are identical to the as-shipped tables
below, and the scorer prints all three.

### SST-5 Score, N = 500 (Jev rows @ `576e60e`, `jev-1.13.0`)

| Arm | Exact correct | MAE | p50 / p95 | Tokens in / out |
|---|---:|---:|---|---|
| Jev | 273/500 (54.6%) | 0.488 | (committed run) | |
| grok-4.20 via adapter | 227/500 (45.4%) | 0.624 | 750 / 994 ms | 295,333 / 17,994 |
| Haiku 4.5 via adapter, for reference (`jev-zui`) | 251/500 (50.2%) | 0.556 | 855 / 1,785 ms | 364,917 / 22,004 |

| Jev vs grok | Jev-only / grok-only | p | Verdict |
|---|---|---:|---|
| Accuracy (McNemar) | 142 / 96 | 0.0035 | **WIN** |
| MAE (sign test on per-row error) | 168 / 101 | 5.3e-5 | **WIN** |

Pass rule: Jev beats both constants (unchanged from `jev-zui`), and grok wins neither test:
**PASS**. **The MAE WIN holds against grok**, on all rows and with zero-mass rows dropped (0
dropped). Accuracy, a TIE against Haiku, is a WIN against grok.

### CLINC150 15 intents + out-of-scope, N = 750 (Jev rows @ `2842340`)

| Arm | Overall correct | In-scope | OOS recall | OOS precision | p50 / p95 | Tokens in / out |
|---|---|---:|---:|---:|---|---|
| Jev | 688/750 (91.7%) | 395/450 | 293/300 | 293/310 | (committed run) | |
| grok-4.20 via adapter | 668/750 (89.1%) | 373/450 | 295/300 | 295/327 | 1,066 / 1,467 ms | 558,472 / 79,912 |
| Haiku 4.5, for reference (`jev-qw8`) | 681/750 (90.8%) | 389/450 | 292/300 | 292/310 | 1,260 / 2,155 ms | 800,996 / 81,445 |

| Primary (constant 300) | Jev / grok | Jev-only / grok-only | McNemar p | Verdict |
|---|---|---|---:|---|
| Overall correct | 688 / 668 | 35 / 15 | 0.0066 | **WIN** |
| Handled at peak >= 0.60 | 685 / 657 | 44 / 16 | 0.00039 | **WIN** |

All three readings give the same numbers: as shipped, zero-mass = none, and zero-mass dropped.
Feasibility is met, with in-scope accuracy 87.8% for Jev and 82.9% for grok. **PASS.** **The gated
WIN holds against grok** under the unit's rule and with zero-mass rows dropped. Overall
correctness, NON-INFERIOR against Haiku, is a WIN against grok. Grok refuses a little more than
Haiku: out-of-scope recall is 295/300, but it answers "none" on 327 rows, 32 of them in-scope. It
routes 22 fewer in-scope rows correctly than Jev.

**Verdict** (`[live]`, grok N = 500 + 750, 2026-09-24, Jev rows as committed). Both wins that held
against Haiku also hold against a second LLM family: xAI's `grok-4.20-0309-non-reasoning`, asked
the identical question through the identical adapter. SST-5 MAE: WIN, p = 5.3e-5. CLINC150 handled
at 0.60: WIN, p = 0.00039. Neither verdict leans on zero-mass rows, because grok produced none on
these two sets. Against grok the margins are wider than against Haiku, and both units'
second measures (SST-5 accuracy, CLINC overall) also become WINs. No `NEGATIVE_EVIDENCE.md` row
is due. The README's "an LLM" wording for these two wins can now name two families: Haiku 4.5 and
grok-4.20.

**Spend.** 1,250 grok calls: 853,805 input / 97,906 output tokens (adapter totals). xAI's list
price is not read here, so no dollar figure is given. No Jev or Haiku calls were made.

**Boundary / NO-CLAIM.** One grok model (non-reasoning), one run per unit, one adapter version
(`adffc2e`), Jev's single committed run per unit. Grok's run-to-run variance is not measured. On
Yelp, Haiku's run-to-run variance alone was enough to flip a verdict (`jev-91u`). Here the grok
margins (sign 168 vs 101, McNemar 44 vs 16) are far wider than one row, but that is an
observation, not a variance measurement. Two families are not all LLMs. The OpenAI lineage is
untested. A non-author spot-check is still pending before close.

## Non-author verification — VerifySST5

VerifySST5 (background agent of pane 1; not the author), 2026-09-24, keyless, from a fresh full
`git clone --local` at `e8096c9`. No live call was made; spend $0.

| # | Check | Result |
|---|---|---|
| 1 | `python3 work/second-incumbent/score_n4j.py` with no key | HOLDS. Exit 0. Both Haiku self-checks reproduce (SST-5 273 / 251, sign 109 vs 75; CLINC 688 vs 681, handled 685 vs 650). SST-5 vs grok: accuracy 142 / 96, p = 0.00345, WIN; MAE sign 168 / 101, p = 5.27e-05, WIN; PASS; MAE WIN HOLDS. CLINC vs grok: overall 35 / 15, p = 0.0066, WIN; handled at 0.60 44 / 16, p = 0.000394, WIN, identical in all three readings; feasibility met; PASS; gated WIN HOLDS. Row sha256 prefixes `287dea63` and `a0701551` match the receipt. |
| 2 | Independent recompute from the rows (not through any scorer) | HOLDS. Labels, samples and Jev rows were read with `git show` from `ae161b6` / `576e60e` and `e0950ce` / `2842340`. SST-5 grok: 227/500, MAE 0.624, discordant 142 / 96 and 168 / 101, same p-values. On 500/500 rows the stored `score` equals the probability-weighted index within 0.011. CLINC grok: 668 overall, 657 handled, in-scope 373/450, 327 "none" answers, discordant 35 / 15 and 44 / 16. `choice` = argmax on 750/750, 0 flat distributions, 16 options with `oos` last. |
| 3 | Identical question and state | HOLDS. `run.py` (at `975cf81`) loads each unit's runner and sample with `git show` at the pinned commit and uses its `QUESTION` / labels as they are. The SST-5 rows' raw text answers the `sentiment` question with keys 0–4. |
| 4 | Zero-mass | HOLDS. 0 rows with `probabilityError`, 0 raw sums of 0, and 0 flat SST-5 distributions, so all readings coincide. |
| 5 | Bar before data | HOLDS. `975cf81` (21:41:41 −0600) is an ancestor of `492d8d6` (21:45:19 −0600) and has no rows. The receipt diff only replaces "Pending the live run." under Result. `run.py` and `score_n4j.py` are unchanged from `975cf81` to HEAD. |

Verdict: both HOLDs and both PASSes reproduce from committed files under an unedited bar. Re-score:
`python3 work/second-incumbent/score_n4j.py`. NO-CLAIM: this re-scores committed rows; no grok
re-run, and grok's run-to-run variance is not measured (bead `jev-wu6v` is filed for it).
