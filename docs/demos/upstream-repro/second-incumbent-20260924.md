# A second incumbent: SciFact and Banking77 re-run through the adapter with xAI Grok (bead `jev-dsu`)

AdapterUniform (background agent of pane 1), 2026-09-24. Live lane. Every Jev-vs-LLM result so far
uses one incumbent, Claude Haiku 4.5. This pass re-runs only the incumbent arm of two of them,
through the same adapter, with a model from a different lab: SciFact (`jev-9er`,
[`noul-scifact-20260924.md`](noul-scifact-20260924.md)) and Banking77 10-intent (`jev-k3k`,
[`choice-banking77-20260924.md`](choice-banking77-20260924.md)). The Jev rows are the committed ones
and are not re-run.

## Preregistered (committed before any call to the second model)

**Which key.** Infisical key names in this lane's project, checked by name only (values never
read): `ANTHROPIC_API_KEY`, `GOOGLE_MAPS_API_KEY`, `KIMI_K3_API_KEY`, `OPENAI_API_KEY`,
`OPENROUTER_API_KEY`, `TYPESAFE_API_KEY`, `XAI_API_KEY`. `OPENAI_API_KEY` is present but rejected:
`models.list()` returned HTTP 401 `invalid_api_key` on 2026-09-24. `XAI_API_KEY` works:
`models.list()` on `https://api.x.ai/v1` returned 13 ids.

**Which model, and the rule that picked it.** `grok-4.20-0309-non-reasoning`: the only chat model on
the key's list whose id says it is non-reasoning. The Haiku arms ran Haiku 4.5 without extended
thinking, and the adapter sends no reasoning setting, so a reasoning model would change the
comparison class. The other chat ids (`grok-4.3` to `grok-4.7`, `grok-4.20-0309-reasoning`,
`grok-4.20-multi-agent-0309`, `grok-build-0.1`) do not say they are non-reasoning, or say they reason.
Not chosen by any result.

**Adapter and provider.** Vendored `system-one-adapter-python` at `adffc2e` (v0.2.0), the version
both Haiku arms used. The provider is the adapter's own caller-owned
`system_one_adapter.providers.openai.AsyncOpenAIProvider("grok-4.20-0309-non-reasoning",
base_url="https://api.x.ai/v1")`, which selects `api="chat_completions"` for a non-OpenAI host.
Client settings copy the Haiku arms: `structured_outputs=True` (so `response_format` is a strict
`json_schema`), `llm_answer_mode="probabilities"`, `normalize_probabilities=True`, `RetryPolicy()`,
concurrency 8, 90 s per-call timeout. Known v0.2.0 gap: Chat Completions accepts a
`finish_reason="length"` result as success (upstream #38, fixed in v0.2.1). So every row records the
provider's `finish_reason`, and any row that is not `stop` is listed in the result. Those rows are
scored as returned.

**Inputs, byte-identical to the Haiku arms,** read with `git show` (`work/second-incumbent/run.py`):
- SciFact: `QUESTION`/`state` from `work/noul-scifact/run.py` @ `30eb285` (unchanged since the bar
  `15b0371`), 400 pairs from `sample.jsonl` @ `83a7295`.
- Banking77: `question`/`labels`/`state` from `work/choice-banking77/run.py` @ `3709ee6`, 400 rows
  from `subset.jsonl` @ `3709ee6`.

**Recorded per row.** The answer (`noul`, or `choice`/`confidence`/`probabilities`), and from the
adapter's own `debug`: `probability_errors` (Banking77: `probabilityError`), the raw map's sum when
the adapter renormalized (`rawSum`), the provider's `finish_reason`, the model id the provider
reported, the raw response text, and the attempt and retry counts. Also tokens and latency.

**Feasibility first (not scored).** `run.py smoke` makes two calls on synthetic states, one per
question shape. If either is refused (schema, auth, model), the pass stops and the refusal is the
result.

**Scoring, fixed now** (`work/second-incumbent/score.py`, keyless). It uses the original receipts'
own metric code and pass rules, read with `git show` from the commits that scored them
(`work/noul-scifact/score.py` @ `15b0371`, `work/choice-banking77/score.py` @ `3709ee6`). The
committed Jev rows are compared with the new grok rows. A row still failed after one resume pass is
scored as the originals did: wrong, and for SciFact at noul 0.5.
- **SciFact**, the jev-9er rule with grok in Haiku's place: **PASS** if none of accuracy (McNemar
  exact), AUC, Brier or ECE (paired bootstrap, 2,000 resamples, seed 20260924, 95% interval) is a
  significant grok win. Bar 1 (Jev beats the constants) uses the same Jev rows, so it is unchanged and
  not re-tested.
- **Banking77**, the jev-k3k rule with grok in Haiku's place: NOT-SCORED if an arm is below 50%;
  **LOSE** if Jev does not beat the constant or is more than 3.0 pp below grok; **WIN** if Jev has
  more Jev-only-correct rows and McNemar exact p < 0.05; **NON-INFERIOR** otherwise. PASS on WIN or
  NON-INFERIOR.
- **Zero-mass rows** (Banking77 only; a Noul answer is one probability, so it cannot have one). The
  primary score takes answers as returned, as the originals did. Two sensitivities are reported
  beside it: zero-mass rows (raw map summed to 0, per
  [`adapter-uniform-20260924.md`](adapter-uniform-20260924.md)) dropped from both arms, and scored
  wrong for grok. The primary verdict decides; the sensitivities are descriptive.
- **Descriptive:** Haiku vs grok McNemar on each set, grok's distinct noul values (SciFact), top
  confusions (Banking77), tokens, latency.

**What each outcome means, fixed now.** If Jev keeps its original outcome against grok on a set
(SciFact PASS, Banking77 WIN or NON-INFERIOR), that set's result is not specific to Haiku, for this
one extra model. If Jev fails against grok on a set, that set's win was Haiku-specific, and a
`NEGATIVE_EVIDENCE.md` row with a retry condition is written.

**Scorer check before any call.** Swapping in the committed Haiku rows as the "grok" rows reproduces
both original receipts: SciFact 361 vs 351, McNemar 19/9 p = 0.087 TIE, AUC/Brier/ECE WIN; Banking77
384 vs 362, 25/3, p = 2.74e-5 WIN.

**Re-score (keyless, from committed files):** `python3 work/second-incumbent/score.py`.

**NO-CLAIM (fixed now).** One more model, one run per set, no run-to-run variance for grok. The
OpenAI lineage is untested because its key is rejected. xAI list prices are not read here, so spend
is stated in tokens.

## Result

Bar committed at `a2a4c7a` before any call to the second model. Smoke 2/2 accepted (strict
`json_schema` on Chat Completions, `finish_reason` `stop`, the provider reported model id
`grok-4.20-0309-non-reasoning`). Run 2026-09-24, finishing 02:49Z. Both sets answered 400/400 on the
first pass: 0 error rows, 0 transient retries, 0 corrective retries, every `finish_reason` `stop`
(so the v0.2.0 #38 gap did not fire). Rows: `work/second-incumbent/rows-scifact-grok.jsonl`,
`rows-banking77-grok.jsonl`. Re-score: `python3 work/second-incumbent/score.py`.

### SciFact (`[live]`, N=400 per arm; Jev and Haiku rows are the committed jev-9er rows)

| Arm | Correct at >0.5 | Accuracy | Wilson 95% | AUC | Brier | ECE | p50 / p95 ms | Tokens in / out |
|---|---:|---:|---|---:|---:|---:|---|---|
| Jev `jev-1.13.0` | 361/400 | 90.2% | 86.9–92.8% | 0.962 | 0.0709 | 0.0431 | 140 / 219 | 293,734 / 8,000 |
| Haiku 4.5 (jev-9er) | 351/400 | 87.8% | 84.2–90.6% | 0.934 | 0.1002 | 0.0854 | 765 / 1,275 | 373,346 / 4,981 |
| **Grok 4.20 non-reasoning** | **330/400** | **82.5%** | 78.5–85.9% | **0.875** | **0.1443** | **0.1363** | 614 / 894 | 336,369 / 3,513 |

| Jev vs | Jev-only | Other-only | McNemar p | Accuracy | AUC diff 95% | AUC | Brier diff 95% | Brier | ECE diff 95% | ECE |
|---|---:|---:|---:|---|---|---|---|---|---|---|
| Haiku (as published) | 19 | 9 | 0.087 | TIE | +0.008 to +0.053 | WIN | −0.047 to −0.012 | WIN | −0.065 to −0.007 | WIN |
| **Grok** | 46 | 15 | 8.8e-5 | **WIN** | +0.054 to +0.122 | **WIN** | −0.102 to −0.046 | **WIN** | −0.122 to −0.051 | **WIN** |

**SciFact verdict: PASS**, under the preregistered rule. Grok does not significantly win on any of
the four metrics. Jev wins all four, including accuracy, which was only a TIE against Haiku. Grok's
probabilities are coarse: 9 distinct noul values, 211 of 400 exactly 0.0 and 69 exactly 1.0.

### Banking77 10-intent (`[live]`, N=400 per arm; Jev and Haiku rows are the committed jev-k3k rows)

| Arm | Correct | Accuracy | Wilson 95% | p50 / p95 ms | Tokens in / out |
|---|---:|---:|---|---|---|
| Jev `jev-1.13.0` | 384/400 | 96.0% | 93.6–97.5% | 139 / 328 | 154,744 / 47,571 |
| Haiku 4.5 (jev-k3k) | 362/400 | 90.5% | 87.2–93.0% | 1,053 / 1,972 | 360,861 / 41,400 |
| **Grok 4.20 non-reasoning** | **366/400** | **91.5%** | 88.4–93.9% | 1,127 / 1,561 | 272,639 / 33,008 |
| Constant always-`activate_my_card` | 40/400 | 10.0% | | | |

Grok's probability maps, from the adapter's `debug`: 84/400 rows had a sum error above 1e-6 and
were renormalized. **22/400 were zero-mass**: the raw map summed to 0, every value `0`, the same
text shape as Haiku's. All 22 came back as `activate_my_card` at confidence 0. One of them is truly
`activate_my_card` and scores "correct" through the tie rule, not through an answer. Jev is correct
on 16 of the 22. They cluster on `beneficiary_not_allowed` (11) and `card_about_to_expire` (5), and 8
are the same rows Haiku zeroed in jev-k3k. The other 62 flagged rows had raw sums between 0.05 and
0.99.

| Scoring (k3k rule, grok in Haiku's place) | Rows | Jev | Grok | Jev-only | Grok-only | McNemar p | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| **as returned (preregistered primary)** | 400 | 384 | 366 | 24 | 6 | 0.0014 | **WIN** (+4.5 pp) |
| zero-mass rows dropped from both arms | 378 | 368 | 365 | 8 | 5 | 0.58 | NON-INFERIOR (+0.8 pp) |
| zero-mass rows scored wrong for grok | 400 | 384 | 365 | 24 | 5 | 0.00055 | WIN (+4.8 pp) |

**Banking77 verdict: WIN**, on the preregistered primary. **Anyone citing it needs the
sensitivity.** On the 378 rows where grok returned a real distribution, Jev and grok are
statistically indistinguishable: 368 vs 365, 8 vs 5 discordant, p = 0.58. Against grok, the whole
significant margin is the 22 rows where the incumbent returned no probability mass. The same cut
against Haiku leaves a gap: with Haiku's 14 zero-mass rows dropped, Jev is 374 and Haiku 362 of 386,
15 vs 3 discordant, p ≈ 0.0075 (computed here, descriptive). Haiku vs grok on the same 400 rows:
14 vs 18 discordant, p = 0.60, no difference.

### What the pair says

- **SciFact:** not Haiku-specific. A second lab's model does worse than Haiku did, and Jev beats it
  on every metric (`[live]`, N=400, one run).
- **Banking77:** Jev still wins against grok, but the win comes from Jev answering where the LLM
  returned an all-zero map. On the rows the LLM did answer, grok is within the 3 pp margin of Jev.
  The fair one-liner: "Jev never abstains by accident; on answered rows it ties Grok". Not "Jev
  routes better than LLMs".
- No preregistered FAIL, so no `NEGATIVE_EVIDENCE.md` row is triggered.

### Spend

802 xAI calls (2 smoke + 800 scored): 609,008 input + 36,521 output tokens on the scored rows, plus
1,211 / 101 on the smoke. xAI prices were not read, so no dollar figure. 0 Jev calls, 0 Haiku calls.

### NO-CLAIM

- One extra model (`grok-4.20-0309-non-reasoning`), one run per set; grok's run-to-run variance is
  not measured.
- The OpenAI lineage is untested: its key returns 401.
- Grok ran through the Chat Completions path and Haiku through the native Anthropic path. The
  provider surface differs by construction; prompts and schema are identical.
- Jev and Haiku rows are the committed ones and were not re-run.
- A non-author re-score is still owed before the bead closes.
