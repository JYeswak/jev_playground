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

## Results

Pending: filled in after the live run.
