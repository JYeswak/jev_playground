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

Pending the live run.
