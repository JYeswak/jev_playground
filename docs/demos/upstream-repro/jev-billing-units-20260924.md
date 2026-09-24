# What does one Jev answer bill? `usage.billing_units` per question shape (bead `jev-bmn`)

BillingUnits (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.
Descriptive measurement: there is no pass bar. This plan was committed before the first call.

## What the primary sources say (read from disk before any call)

- **Neither SDK declares `billing_units`.** The JS SDK's `Usage` is `input_tokens` and
  `output_tokens` only (`upstream/typesafe-ai/typesafe-sdk-js/src/types.ts:127-132`). The Python
  wire schema is the same two fields (`typesafe-sdk-python/src/typesafe_sdk/_schemas/models.py:151-160`),
  input tokens described as "billable", output tokens as "currently free of charge". The HTTP API
  page lists the same two (`docs-mirror/typesafe/api.md:183-191`).
- **The field appears once on disk, in an SDK test fixture:** `typesafe-sdk-python/tests/test_responses.py:143`
  sends `"billing_units": 1` in `usage`, and `:152-153` assert the Python SDK **drops** it
  (`not hasattr(result.usage, "billing_units")`). So every Python runner in this lane that read
  `resp.usage` could never have seen it; it is only reachable through `raw_http_response`.
- **The JS SDK does not drop it:** `systemOne` returns the parsed body untouched
  (`work/sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs:571-574`), so `work/jev-client` can keep it.
- **Price.** `docs-mirror/typesafe/models.md:13`: Jev 1.13 (`jev-1.13.0`) "\$42 / \$0.042" per
  Btok / per Mtok; `:16`: "Charged per input token. Output tokens are free." No price per
  billing unit is stated anywhere in `docs-mirror/typesafe` or either SDK
  (`grep -rn billing_unit docs-mirror/ upstream/typesafe-ai/` hits only the test fixture above).
- **Haiku list price.** `docs-mirror/typesafe/cookbooks/consistency_choice_cookbook.md:90`:
  `"claude-haiku-4-5": (1.00, 5.00)`, dollars per 1M input / output tokens, "prices + model ids as of
  2026-07" (`:89`). A list price, not an invoice.

## Plan

**Client.** `work/jev-client/src/index.ts` returns `usage = {input_tokens, output_tokens,
billing_units, extra}` on every answer shape (`askJev`, `askJevChoice`, `askJevScore`,
`askJevBundle`). `billing_units` is `null` when the wire usage carries no finite number under that
name; `usage` is absent when the response has no usage object. Nothing is zero-filled.

**Calls.** 50 live calls per shape, 150 in total, one attempt each (retry off), 30 s timeout, through
`askJevBundle` with the exact state and question each unit's runner sent. Question bodies were
checked byte-for-byte against the Python SDK's serialisation of the runners' own objects:

| Shape | Unit and runner | State | Question |
|---|---|---|---|
| Score | `work/score-sst5/run.py` (`jev-zui`) | the sentence, as a string | `sentiment`: 5-level Score |
| Choice | `work/choice-banking77/run.py` (`jev-k3k`) | `{customer_message}` | `intent`: 10 labels, criteria `null` |
| Noul | `work/noul-scifact/run.py` (`jev-9er`) | `{claim, title, abstract}` | `supports`: Noul with true/false criteria |

Rows: the first 50 lines (`i` 0..49) of `work/score-sst5/sample.jsonl`,
`work/choice-banking77/subset.jsonl` and `work/noul-scifact/sample.jsonl`.

**Recorded per call** (`work/jev-billing-units/rows-jev.jsonl`, every attempt including failures):
the client's `usage`, the wire `usage` as sent (tee'd from the response body), latency, resolved
model, and the answers.

**Reported per shape:** billing units per call (presence count, mean, min, max, distribution),
mean input and output tokens, latency p50 and mean, and cost per 1,000 answers. If a price per
billing unit is on disk, cost is units times that price. Since none is, cost is mean input tokens
times \$0.042 per Mtok (`models.md:13,16`), and billing units are reported as counts only. Beside
it, Haiku 4.5's list-price cost per 1,000 answers from the committed Haiku rows of the same 50
`i` values in each unit (`rows-haiku.jsonl`, adapter token totals), at \$1 / \$5 per Mtok.

**Scorer checks** (exit 1 if any fails): 50/50 answered per shape, every resolved model is
`jev-1.13.0`, the client's `billing_units` and `input_tokens` equal the wire's on every row, 50/50
Haiku rows per shape, and each cited price line still says what this plan quotes.

**Re-score, no key, no network:** `node work/jev-billing-units/measure.mjs`

## Results (live, N = 150, 2026-09-24, `jev-1.13.0`)

Run from the working tree minutes before the client landed as `b1656b3`; the usage code that ran is
the code in that commit.

**The wire carries no `billing_units`: 0 of 150 answered calls had one.** Every response's `usage`
held exactly two keys, `input_tokens` and `output_tokens`, on all three question shapes. The field
exists on disk only as the Python SDK's "unknown extra field" test fixture
(`test_responses.py:143`); nothing the API returned tonight matches it. So there is no billed unit to
record beyond the documented one: **input tokens at \$0.042 per million (`models.md:13`), output
free (`models.md:16`).** The client now keeps `billing_units` if the server ever sends it, and
reports `null` until then.

Scorer output, pasted verbatim (`node work/jev-billing-units/measure.mjs`, exit 0):

| Shape (unit) | Answered | billing_units present | billing_units per call | mean input tok | mean output tok | latency p50 / mean ms | Jev $ / 1,000 answers (input tok × $0.042/Mtok) | Haiku list $ / 1,000 answers (same 50 rows) |
|---|---:|---:|---|---:|---:|---|---:|---:|
| score (work/score-sst5) | 50/50 | 0/50 | absent on every call | 375.3 | 18.0 | 129 / 147 | $0.0158 | $0.9484 |
| choice (work/choice-banking77) | 50/50 | 0/50 | absent on every call | 385.9 | 117.8 | 127 / 134 | $0.0162 | $1.4287 |
| noul (work/noul-scifact) | 50/50 | 0/50 | absent on every call | 683.3 | 20.0 | 131 / 136 | $0.0287 | $0.9475 |

- score: wire usage keys {input_tokens, output_tokens}; failed attempts 0; total input tokens 18,765;
  input tokens identical to the committed `work/score-sst5/rows-jev.jsonl` row for 50/50 rows; Haiku
  mean 728.1 in / 44.1 out over 50 rows (adapter totals); Jev 60× cheaper at these prices.
- choice: wire usage keys {input_tokens, output_tokens}; failed attempts 0; total input tokens 19,294;
  identical to the committed `work/choice-banking77/rows-jev.jsonl` row for 50/50; Haiku mean 901.4 in
  / 105.5 out; Jev 88× cheaper.
- noul: wire usage keys {input_tokens, output_tokens}; failed attempts 0; total input tokens 34,167;
  identical to the committed `work/noul-scifact/rows-jev.jsonl` row for 50/50; Haiku mean 884.6 in /
  12.6 out; Jev 33× cheaper.
- Scorer checks passed: 50/50 answered per shape, every resolved model `jev-1.13.0`, the client's
  `billing_units` and `input_tokens` equal the wire's on all 150 rows, 50/50 committed Haiku rows per
  shape, and both cited price lines still read as quoted.

**What the numbers say, per shape.** Jev's cost per answer follows the length of the state, not the
question type. Score and Choice run on short texts (about 380 input tokens, \$0.016 per 1,000
answers) and Noul on abstracts (683 tokens, \$0.029). Choice returns the most output tokens (117.8),
but output is free, so it does not move the price. Input token counts matched the earlier committed
runs row for row on all 150 requests, so for a fixed request the count is deterministic. Every earlier
Jev row in these three units can therefore be priced from its recorded `input_tokens` without a new
call.

**Response headers carry no billing either** (one extra call outside the planned 150: SciFact row 0,
same Noul question). Header names: `content-length`, `content-type`, `date`, `server`,
`x-envoy-upstream-service-time`, `x-typesafe-request-id`. None names a bill, unit, cost, credit or
token count.

**Correction to AGENTS.md RULE 14.** `AGENTS.md:98-100` says the SDK ships `usage.billing_units`.
Neither SDK declares the field, and the API did not send it on 150 of 150 calls. What the SDK ships
is a test proving the Python client would *discard* it. That line is left for pane 1 to amend; this
receipt does not edit AGENTS.md.

**Spend.** 151 Jev calls (150 planned plus 1 header probe), 0 failures, 72,820 input tokens:
\$0.0031 at \$0.042 per million. Zero Haiku calls; the Haiku column prices rows already committed.

**Re-score:** `node work/jev-billing-units/measure.mjs` (no key, no network). It exits 1 if any check
fails or a cited price line has moved.

## NO-CLAIM

- This is not an invoice. The Jev dollar figure applies the documented rate to the reported
  `input_tokens`; no TypeSafe bill or account statement was read. The Haiku figure applies the
  cookbook's 2026-07 list price to the system-one-adapter's token totals, which include any
  corrective retries. The two models use different tokenizers.
- `billing_units` was absent on 150 calls to `jev-1.13.0`, from one key, on one night. That does not
  show it is never sent: another plan, model, endpoint or later release might send it. The client
  records it if it appears.
- Three question shapes, one wording each, 50 rows each, taken as the first 50 of each sample rather
  than a random draw. Mean tokens scale with state length, so these per-1,000 figures do not transfer
  to other states without measuring again.
- Latency is wall time from this Mac Studio at concurrency 4. It is not a service-side number.
- Not changed: the Python runners (`run.py` in each unit) still read `resp.usage` through the Python
  SDK, which would drop `billing_units` if it ever arrived. Their `raw_http_response` path would keep
  it.
