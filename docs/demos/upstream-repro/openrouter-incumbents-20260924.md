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

## Result

NOT_RUN: waiting on jev-14qk's committed table.
