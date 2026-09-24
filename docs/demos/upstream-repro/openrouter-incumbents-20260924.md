# Do Jev's surviving wins hold against more model families? OpenRouter comparators (bead `jev-3e2i`)

JevVariance (background agent of pane 1), 2026-09-24. Live lane. Jev rows are the committed ones; only
comparator calls are made.

## Preregistered (committed before any comparator call)

**Question.** Five Jev results have survived their checks. Each has been measured against at most two
LLM families: Anthropic Haiku 4.5 (capped until 2026-10-01, `jev-1y19`) and xAI grok-4.20. Rule 14
asks for the incumbent someone would actually ship. Cheap small models and open-weights models are
that, and none has been measured against Jev here. Does each win hold against them?

| Set (unit) | Rows | Win under test | Committed Jev runs (all of them are judged) |
|---|---:|---|---|
| SST-5 Score (`jev-zui`) | 500 | MAE sign test WIN | `rows-jev.jsonl` @ `576e60e`, `-run2`, `-run3` @ `510e804` |
| Banking77 10-intent Choice (`jev-k3k`) | 400 | accuracy WIN (McNemar) | `rows-jev.jsonl` @ `3709ee6`, `-run2`, `-run3` @ `510e804` |
| CLINC150 15 + OOS Choice (`jev-qw8`) | 750 | handled at peak >= 0.60 WIN | `rows-jev.jsonl` @ `2842340`, `-run2`, `-run3` @ `0516464` |
| SciFact Noul (`jev-9er`) | 400 | Brier WIN | J1 @ `83a7295`, JR @ `6ac0092`, J2, J3 @ `3c006e2` |
| FEVER Noul (`jev-wx5`) | 400 | ECE WIN | J1 @ `aadd4d8`, JR @ `a752d2d`, J2, J3 @ `3c006e2` |

**Comparators, in Joshua's order** (2026-09-24: *"i'd prefer free models on openrouter but i approve
cheap spends"*):
1. **Free.** Every `:free` model in jev-14qk's list (`work/openrouter/provider.py`,
   `FREE_STRUCTURED`) whose committed jev-14qk rows (`work/openrouter/rows-sst5-<model>.jsonl`, the
   first 50 SST-5 rows) show at least **49/50 answered** (pane 1's threshold). The scorer applies this
   rule itself (`comparators()`), so the list is fixed by jev-14qk's committed rows, not chosen here.
   **No call is made before jev-14qk's result is committed.**
2. **Cheap paid, one per family with no reliable free model:** `openai/gpt-5-nano` and
   `deepseek/deepseek-v4-flash`. Neither family has a model in jev-14qk's free list, so both run.
   OpenRouter list prices on 2026-09-24 (`/api/v1/models`, listing sha256
   `2d166a4455a3c27a741a9b1d5592506c63650090980a07ece185ecdb99ac151c`): gpt-5-nano $0.05 / $0.40 per
   million input/output tokens; deepseek-v4-flash $0.0886 / $0.1772. Both list `structured_outputs`
   and `reasoning`. The adapter sends no temperature, max-tokens or reasoning setting, so each model
   runs at its defaults. Its reasoning tokens are billed as output and are counted.

**Path.** `system-one-adapter-python` at `adffc2e`, its own `AsyncOpenAIProvider(base_url=
"https://openrouter.ai/api/v1", api="chat_completions")` passed as the caller-owned `model=`. No
adapter code is edited. Free ids go through jev-14qk's `openrouter_provider()`, which refuses any id
without `:free`. Paid ids are built in `work/openrouter-incumbents/run.py` and refused unless they
are one of the two above. Key: `OPENROUTER_API_KEY` from the lane Infisical project, length 73 checked,
value never printed. Adapter settings copy the Haiku and grok arms: structured outputs,
`llm_answer_mode="probabilities"`, `normalize_probabilities=True`, `RetryPolicy()`.

**Inputs, byte-identical to each unit's incumbent arm.** Questions, labels, states and rows are read
with `git show` at the commits those arms used: `work/second-incumbent/run.py` `PINS` for SST-5,
Banking77, CLINC150 and SciFact, plus FEVER at `834a569` (`work/noul-scifact/run.py`,
`work/noul-fever/sample.jsonl`). **Only public benchmark rows are sent; nothing from this lane's
sessions.** Keyless test: `python -m unittest work/openrouter-incumbents/test_run.py`, 5/5. It checks
that each pinned sample equals the unit's committed sample, that FEVER's question is SciFact's object,
and that unapproved models and a missing key are refused.

**Rows.** `work/openrouter-incumbents/rows-<set>-<model slug>[-prompted].jsonl`, one per model x set.
Each row records the answer, the adapter's `probability_errors` and raw map or sum, the upstream
provider and model OpenRouter reports, finish reason, attempts, retries, tokens and latency.

**Order and pacing.**
- For each model x set, first a **16-row structured probe** (`--limit 16`).
- **Declared fallback, per cell:** if all 16 probe rows are refused with a non-transient 400/422
  (e.g. a grammar or `response_format` refusal, as Anthropic did in jev-4jf), that cell runs as
  prompted JSON (`--prompted`: `structured_outputs=False`, `n_retry_malformed_structure=1`,
  jev-4jf's variant) and the prompted file is the one scored. Otherwise the structured run continues.
  The scorer applies this rule (`cell_file()`).
- **Free models** share OpenRouter's account-wide caps: 20 requests/minute and 1,000/day
  (docs, "Limits"; key reports 1,000/day, 1 used, at 03:57 UTC). They start at most 15 calls a
  minute, 2 in flight, 180 s per call. Order: set by set (SST-5, Banking77, SciFact, FEVER, CLINC150),
  models in jev-14qk's order. A row refused by the daily cap is a **quota** row, not a failure. The
  cell is **BLOCKED** until those rows are answered after the 00:00 UTC reset. Quota rows are
  resumed as often as needed.
- **Paid models** run all five sets, 8 in flight, 90 s per call.
- Non-quota failures get **one resume pass**.

**Zero-mass handling (`jev-mly`), as jev-dsu and jev-n4j did.** A comparator row whose raw map sums
to 0 is shipped by the adapter as a uniform answer. Every verdict is computed on all rows **and** with
those rows dropped from both arms. For CLINC150, the unit's second reading (zero-mass = "none of the
above") is also applied. A win must be WIN in every reading.

**Verdict rules: each unit's own, imported, not restated** (`work/openrouter-incumbents/score.py`):
- SST-5 and Banking77 through `work/jev-variance/score.py`, which restates `jev-zui` and `jev-k3k`
  and reproduces their committed numbers. SST-5 pass: beats both constants on accuracy and MAE,
  and no significant comparator win. Banking77: `jev-k3k`'s LOSE / WIN / NON-INFERIOR rule, with the
  50% feasibility floor and 3.0 pp margin.
- CLINC150 through `work/choice-clinc150/score.py`: two primaries, overall and handled at 0.60,
  `jev-k3k`'s rule against the always-none constant, with the feasibility floor.
- SciFact and FEVER through `work/noul-variance/score.py` over `work/noul-scifact/score.py`. Pass:
  part 1 on the Jev run (accuracy WIN over always-no, AUC interval above 0.5, Brier WIN over the base
  rate), and no significant comparator win on accuracy, AUC, Brier or ECE.

**Self-check, keyless, run before this commit:** `python3 work/openrouter-incumbents/score.py
--selfcheck` scores each unit's committed Haiku rows as if Haiku were a comparator. It reproduces
all five committed headline pairings: SST-5 MAE 109 vs 75 WIN; Banking77 25 vs 3 WIN; CLINC150
handled 47 vs 12 WIN; SciFact and FEVER accuracy TIE with AUC, Brier and ECE WIN. Across every
committed Jev run, Haiku leaves all five wins holding, consistent with jev-qbc, jev-x5k, jev-kvw and
jev-hg8. Grok's committed rows give SST-5 and CLINC150 HOLDS, and Banking77 DOES NOT HOLD (0/3)
once grok's 22 zero-mass rows are dropped, which matches jev-dsu. Planted states outside the tree:
a refused probe selects the prompted file; quota rows give BLOCKED; 5 failed of 400 give NOT-SCORED;
4 give SCORED; 300 of 400 give INCOMPLETE.

**Decision, per model x set, fixed now.**
- A cell is **scored** only when every row is answered or failed, with no quota rows, and failed rows
  are at most 1% (SST-5 5, Banking77 4, CLINC150 7, SciFact 4, FEVER 4). More failures: **NOT-SCORED**
  (unreliable), no verdict. Quota rows: **BLOCKED**. Unfinished: **INCOMPLETE**.
- **The win HOLDS** against a comparator only if it is WIN against **every committed Jev run in every
  reading**. Otherwise it **DOES NOT HOLD** and gets a `NEGATIVE_EVIDENCE.md` row with a retry
  condition. The README's "against an LLM" wording stays scoped to the families it holds against.
- **The pass rule HOLDS** only if every Jev run passes in every reading. Any comparator LOSE also
  gets a `NEGATIVE_EVIDENCE.md` row.
- One run per comparator. A comparator's own run-to-run variance is not measured here.

**Spend, planned.** Paid: 2 models x 2,450 rows = 4,900 calls plus probes and retries. Using the
Haiku arms' token use (roughly 700-2,100 input per call) and up to ~1,500 reasoning and output
tokens per call, that is about $2 for gpt-5-nano and $1 for deepseek-v4-flash `[INFERENCE: an
estimate, not a bill]`. Free: $0, 2,450 calls per model, bounded by the 1,000-a-day account cap
shared with the other lanes, so free cells finish over several UTC days.

**NO-CLAIM.** One run per comparator, one question wording per set, the adapter's default request
(no reasoning or temperature setting), and whichever upstream provider OpenRouter routes to (recorded
per row, not pinned). A HOLD says the win is not specific to Haiku or grok for that model. It does
not generalize to every LLM.

## Amendment 1: STS-B added (pane 1, 2026-09-24; committed before any call on any set)

Made after the bar at `97bbad6` and before any comparator call on any set, STS-B included. No row
existed when this was written. Nothing above changes; this section adds a sixth set.

| Set (unit) | Rows | Wins under test | Committed Jev runs |
|---|---:|---|---|
| STS-B dev Score (`jev-jzzs`, pane 2; bar `8e4bda9`, result `d6d39e3`) | 1,500 | Spearman WIN **and** MAE WIN (both held 9/9 against grok) | `rows-jev.jsonl`, `-run2`, `-run3` @ `d6d39e3` |

- **Inputs.** The question is jev-jzzs's: one Score, *"How similar in meaning are these two
  sentences?"*, with its six SemEval-2015 criteria (`QUESTION_CRITERIA`, read from
  `work/score-stsb/run.py` @ `8e4bda9`). The state is `{"sentence1", "sentence2"}`. The pairs come
  from that runner's own `fetch_pairs()`: the public STS-B dev CSV, sha256-pinned, 1,500 rows,
  refused on mismatch. **Sentence text is never written to a row or committed**, per that unit's
  license note. Its scorer refuses any row carrying `sentence1`, `sentence2`, `text` or `state`.
  Public benchmark rows only, as for the other sets. The instruction literal lives inside that
  runner's `main()`, so the runner restates it. `test_run.py` checks that the literal is present
  in the pinned source, now 6/6 tests.
- **Verdict rules: jev-jzzs's own, imported** from `work/score-stsb/score.py`: Spearman by 2,000
  paired bootstrap resamples (seed 20260924, WIN if the 95% interval is above 0), MAE by exact sign
  test, exact level by McNemar, and a failed row gets the far endpoint. **Pass:** that Jev run
  beats both floors (always-mean, always-mode) on MAE and exact level, and no comparator LOSE on
  Spearman, MAE or exact level. **The win HOLDS** only if Spearman and MAE are both WIN against
  every Jev run in every reading.
- **Everything else as above:** zero-mass readings (all rows, and zero-mass rows dropped), the
  16-row probe and prompted fallback, quota rows as BLOCKED, the 1% failed-row ceiling (15 rows),
  one resume pass, and NEGATIVE_EVIDENCE for a win that does not hold or any LOSE.
- **Order.** Paid models run STS-B with the other sets. Free models take STS-B **last**, after
  CLINC150, because its 1,500 rows are the largest draw on the shared 1,000-a-day free pool.
- **Self-check, keyless:** `score.py --selfcheck` now also scores jev-jzzs's committed grok run 1
  as a comparator. It reproduces that unit's J1 x G1 pairing: Spearman WIN; MAE 792 vs 694,
  p = 0.0118, WIN; exact 343 vs 312, TIE; pass. It still reproduces all five earlier headlines.
- **Spend, planned, added:** 2 x 1,500 paid calls. With grok's STS-B use (about 640 input tokens a
  call) plus reasoning output, that is under $1 more across both paid models `[INFERENCE]`.

## Result

Free table committed at `7840279`
(`docs/demos/upstream-repro/openrouter-free-feasibility-20260924.md`). None of the six
`:free` models answered 49/50. No free comparator was called.

Paid cells, 2026-09-24 07:24:18Z to 07:26:04Z, are **BLOCKED**. Zero rows answered on
either model, on all six sets. No Jev call. No verdict. No `NEGATIVE_EVIDENCE` row: a
credit refusal is not a comparator win or a tie.

Verbatim, first probe row of each model:

- `openai/gpt-5-nano`: `TypeSafeAPIError: 402 This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 11735.`
- `deepseek/deepseek-v4-flash`: the same 402, `65536` tokens affordable `26078` on SST-5 and Banking77, and `131072` tokens affordable `9388` on SciFact, FEVER, and STS-B.

The 16-row probe was all 402s. That is not the bar's 400/422 grammar refusal, so the
script continued the full set and one resume. Every one of those calls was the same 402.
Not retried again. The local row files are those 402 lines only. They were not committed
and were not deleted. Spend is not stated: the 402s returned no usage object.

The bar froze "no max-tokens setting." Lowering `max_tokens` so the account can afford
the request would be a new bar, not this run. Retry when the OpenRouter key can afford
the adapter's default max, or when a bar committed before the next call sets one.

## Amendment 2: the free arm (CopperHeron, 2026-09-24; committed before any free comparator call)

Made after the Result above and before any `:free` comparator call on any set. No free comparator
row exists. Everything above holds except the four points below. Paid arms stay BLOCKED on
`jev-qkvc`.

**(a) Qualification source: run-2 rows.**
- The bar above reads qualification from `jev-14qk`'s run-1 rows (`rows-sst5-<model>.jsonl`). There
  `dots-3-note-preview:free` answered 48/50, and pacing caused the failures.
- `jev-3e2i`'s own paced run 2 re-measured the free models on the same 50 SST-5 rows, question and
  adapter settings, under a preregistration committed before any call (`d2cf882`; rows `8c45cf4`,
  results `41251dd`, checked by CopperHeron).
- The source is now **run 2's rows**: `work/openrouter/rows-sst5-<model>-run2.jsonl` for the ids in
  `FREE_STRUCTURED_RUN2`.
- The threshold is unchanged: at least **49/50 answered**. `score.py`'s `comparators()` applies it
  to those files.
- By those rows, three models qualify:
  - `dots-studio/dots-3-note-preview:free`: 50/50, 0 zero-mass;
  - `nex-agi/nex-n2.5-mini:free`: 50/50, 2 zero-mass;
  - `liquid/lfm-2.5-2.6b:free`: 49/50, 4 zero-mass.
- Zero-mass stays a scoring reading, as the bar says, not a qualification rule.

**(b) Free-model pacing: run 2's paced mode, exactly.** It replaces "15 a minute, 2 in flight,
180 s per call". The runner imports run 2's constants and helpers (`work/openrouter/run_sst5.py`,
`work/openrouter/provider.py`) rather than restating them:
- one request in flight;
- at most 15 request starts in any 60 s window, counted at the provider seam, so adapter retries and
  429 re-sends count;
- 120 s per attempt, and 420 s per call with pacer holds excluded;
- 429 is removed from the adapter's `RetryPolicy`. On a 429 the runner waits `Retry-After` or
  `retry-after-ms`, or 60 s when neither is sent, at most 3 times per row, and a 4th 429 fails the
  row;
- every request passes `require_free` first.

Reason: under these settings `dots` answered 50/50 with no 429 wait and no pacer hold, while run 1's
settings produced its per-minute 429 failures. Choosing the proven settings over faster ones keeps
the 1% failed-row ceiling (5 rows on SST-5) from being spent on rate limits.

Two stops are added, both leaving rows unrun, so the cell reads INCOMPLETE and resumes:
- **Daily quota.** A 429 whose text carries one of `score.py`'s `QUOTA` markers (for example
  `free-models-per-day`) is recorded as a quota row, not waited on, and stops that model.
- **Streak.** 5 consecutive failed rows of one error class stop that model, as in run 2.

A resume pass re-sends only rows whose single record is a non-quota failure, once, as the bar says.
Quota rows are re-sent in any later session.

**(c) Order.** Models: `dots`, then `nex-n2.5-mini`, then `lfm-2.5`. Sets, as the bar: SST-5,
Banking77, SciFact, FEVER, CLINC150, then STS-B last. Each model × set starts with the 16-row
structured probe and the declared prompted fallback.

**(d) The daily cap.**
- OpenRouter allows 1,000 free-model requests a day on this account. At 18:48Z today the key endpoint
  read `free_model_daily_requests` 381 used and 619 remaining; the count is account-wide.
- Each session first reads the key endpoint (`work/openrouter/usage_daily.py`) and runs with a
  process request cap of **remaining − 20**, never above 599 (`--max-requests`).
- When the cap is reached, no further request is sent and the rows stay unrun. Rows the daily cap
  refuses are quota rows, and they resume after the 00:00 UTC reset, as the bar says.
- `usage_daily` is read before and after every session and must stay $0.

**Keyless checks before this commit.** `test_run.py` adds two tests:
- `comparators()` returns the three qualifying models in this order, then the paid ones;
- a real daily-cap 429 is a quota error and a provider 429 is not.

`score.py --selfcheck` still reproduces every committed headline.
