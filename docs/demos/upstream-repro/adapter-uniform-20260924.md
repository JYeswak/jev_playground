# Why 14 Haiku rows came back exactly uniform through system-one-adapter-python (bead `jev-mly`)

AdapterUniform (background agent of pane 1), 2026-09-24. Live lane. Source of the anomaly:
[`choice-banking77-20260924.md`](choice-banking77-20260924.md) (bead `jev-k3k`), where 14 of 400
`anthropic/claude-haiku-4-5` rows through `upstream/typesafe-ai/system-one-adapter-python` returned
every option at exactly 0.1, confidence 0, choice = the first criterion (`activate_my_card`).

## Pins

- Adapter as vendored: `adffc2eab300a4fa3c0e92252d4ffd6ceaa53700` (Release v0.2.0, 2026-09-18).
- Upstream `main` at the time of this pass: `e1d4cc938204b22fc5a3c3aca7044072fe3f712d` (Release
  v0.2.1, 2026-09-22), one commit ahead; not pulled. `gh api .../compare/adffc2e...e1d4cc9` lists the
  changed files: `_utils/probability_normalization.py`, `_utils/confidence_metrics.py` and the Choice
  branch of `_client.py` are **not** among them, so every line cited below is unchanged at upstream
  HEAD. v0.2.1 adds an Anthropic `stop_reason` check (`providers/anthropic.py`), which is relevant
  only if the uniform rows carry an unusual stop reason.

## Every path to a uniform Choice answer, from source (file:line at `adffc2e`)

Paths are relative to `upstream/typesafe-ai/system-one-adapter-python/src/system_one_adapter/`.

1. **Zero-total rescale.** `_utils/probability_normalization.py:100-106`: in probabilities mode the
   model's per-label values are read as-is; total 0 gives `error = 1.0 > 1e-6`, so with
   `normalize_probabilities=True` it calls `rescale_probabilities`, whose zero-total branch
   (`:69-72`) returns `1/len(labels)` for every label. With 10 labels that is exactly 0.1 each.
2. **Tie resolves to the first criterion.** `_client.py:159`, `max(answers, key=probabilities.__getitem__)`
   returns the first label on a tie, so a uniform vector always answers criterion #1.
3. **Confidence 0 on a zero or uniform vector.** `_utils/confidence_metrics.py:22-24` via `_normalize`
   (`:27-32`, zero total -> uniform): `(max - 1/n) / (1 - 1/n) = 0`.
4. **With `normalize_probabilities=False`** (`probability_normalization.py:103-104`) the all-zero
   vector is returned unchanged, and paths 2 and 3 still apply: choice = first criterion, confidence
   0, probabilities all 0.0. Normalization off does not turn it into an error.
5. **A model-asserted uniform** (the model itself returns 0.1 for every label, sum 1) passes through
   untouched (`:103-104`) and is byte-identical in `answers` to path 1.
6. **Not a path:** a parse or schema failure. `_client.py:216-225` retries or raises
   `TypeSafeAPIResponseValidationError`; it never yields an answer. Missing labels fail the strict
   per-question model (`_schema.py`), and values outside [0, 1] fail `Probability = Field(ge=0, le=1)`
   (`_schema.py:25`) on decode. No logprobs are involved anywhere: the distribution is the model's
   own JSON numbers.

The only signal separating path 1 from path 5 is in `response.debug`:
`probability_errors[<id>] == 1.0` and `original_probabilities[<id>]` all zero
(`probability_normalization.py:21-54`). The jev-k3k runner kept `answers` and discarded `debug`
(`work/choice-banking77/run.py:183-190`), so its 14 rows cannot tell path 1 from path 5.

## Keyless mechanism check (no key, no network)

`work/adapter-uniform/repro_keyless.py` injects a caller-owned fake provider (the adapter's documented
`model=<provider instance>` seam) that returns a fixed raw payload, and runs the adapter's real
decode/normalize/confidence code on it. Four cases, 4/4 expectations hold (exit 0):

| Raw model payload (4 labels) | `normalize_probabilities` | Adapter `choice` | `confidence` | `probabilities` | `debug.probability_errors` |
|---|---|---|---|---|---|
| all 0.0 | True | `alpha` (first) | 0.0 | 0.25 each | `{"q": 1.0}` + `original_probabilities` all 0 |
| all 0.0 | False | `alpha` (first) | 0.0 | 0.0 each | `{"q": 1.0}` |
| 0.25 each (model-asserted) | True | `alpha` (first) | 0.0 | 0.25 each | `{}` |
| one-hot on `gamma` | True | `gamma` | 1.0 | one-hot | `{}` |

Rows 1 and 3 have identical `answers`. That is the mechanism; it does not yet say which path the 14
live rows took.

## Preregistered live bar (committed before any live call)

**Question.** For the jev-k3k rows that came back uniform, is the raw Haiku response an all-zero
distribution (path 1, the adapter fabricating a uniform answer from a non-distribution), a
model-asserted uniform (path 5, provider behaviour), or something else?

**Inputs, byte-identical to jev-k3k.** State, question, labels and client settings are imported from
`work/choice-banking77/run.py` (`structured_outputs=True`, `llm_answer_mode="probabilities"`,
`normalize_probabilities=True`, `RetryPolicy()`), model `claude-haiku-4-5`, adapter at `adffc2e`.

**Rows.** Targets: all 14 jev-k3k Haiku rows with an exactly uniform distribution. Controls: for each
target, the next subset row by `i` with the same intent that was not uniform in jev-k3k, never
reused (14). Selection is code: `select_rows()` in `work/adapter-uniform/live.py`.

**Calls.** 5 repeats per row, 28 rows, 140 calls, 8 concurrent. The raw Anthropic response of every
provider attempt is captured by wrapping the caller-owned provider's SDK `messages.create` (the
vendored clone is not edited), and parsed independently of the adapter.

**Decision rules, fixed now.**
- **ADAPTER-FABRICATES-UNIFORM (path 1) CONFIRMED LIVE** if at least one call returns an adapter
  answer that is exactly uniform and its captured raw response parses to a Choice distribution whose
  values sum to 0. Paired with the keyless table this is the defect: a non-distribution is returned
  as a well-formed, zero-confidence answer for the first criterion, not as an error.
- **PROVIDER BEHAVIOUR (path 5)** if every uniform adapter answer has a raw distribution summing to
  a positive value (the model asserted uniform). No adapter defect claimed.
- **NOT REPRODUCED** if no call returns a uniform adapter answer. The keyless mechanism stands; the
  link from it to the 14 rows stays inferred and is recorded in `NEGATIVE_EVIDENCE.md` with a retry
  condition.
- **Recurrence** is reported as uniform calls / calls, per arm, and rows with at least one uniform /
  rows, per arm. A target-arm rate above the control-arm rate says the input, not chance, drives it.
  No threshold is attached; it is descriptive.
- **Our misuse** is assessed separately: whether any documented adapter setting would have turned
  the zero-sum case into an error (keyless row 2 says `normalize_probabilities=False` does not).

**Re-score (keyless, from committed rows):** `python3 work/adapter-uniform/live.py score`.

## Result

Pending the live run.
