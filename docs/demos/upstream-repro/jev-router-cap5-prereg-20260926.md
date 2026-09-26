# `typesafe/jev-router` versus one fixed free model — preregistration

Bead: `jev-38qj`
Status: **PREREGISTERED before any benchmark call**.
Model under test: `typesafe/jev-router` through OpenRouter.
Fixed comparator: `dots-studio/dots-3-note-preview:free` through OpenRouter.

## Corpus

Public Banking77 subset, exactly 400 rows:

- source file: `work/choice-banking77/subset.jsonl`
- SHA-256: `8af5785efc7c6fb12be701ee4ae16eded706e4518e06460635c5f0199c1c2479`
- majority baseline: 10% (every class contributes 40 rows)
- same pinned question, labels, and state builder for both arms; no session data

The benchmark oracle is the public row intent label. The fixed model and router receive byte-equivalent
state/question content. Each row records correctness, latency, input/output usage, OpenRouter-reported
model/provider metadata, and failure reason without storing credentials.
Both arms use the same direct OpenRouter Chat Completions request shape: a system instruction
requiring one JSON object with the `intent` label and a user message containing the public
customer state. `max_tokens=256` is fixed before the first benchmark call; it is a response-size
cap, not an after-seeing optimization. The prompt and cap are identical across arms.
## Fixed bar

The benchmark is scored only after both arms have the same answered-row denominator. A cell with
more than 1% failed rows is `NOT-SCORED`; a quota stop is `INCOMPLETE`, not a model failure.

A router PASS requires all of:

1. router accuracy exceeds the fixed comparator by at least **3 percentage points**;
2. paired McNemar exact two-sided `p < 0.05` on rows answered by both arms;
3. router accuracy beats the 10% majority baseline.

A result that fails any condition is reported descriptively, not converted into a ruling. A result
near the bar is reported with the exact paired counts and confidence interval.

## Cost and hard stop

OpenRouter usage is read from `GET https://openrouter.ai/api/v1/key` immediately before the first
benchmark request and after every router request. The key is loaded with Infisical and never printed.
The hard stop is the **incremental OpenRouter usage field increasing by $5.00** from the before snapshot.
The runner refuses to start a router request when the observed delta is at or above $4.95, and stops
without sending the next row. Fixed `:free` requests are included in the usage ledger and are not
assumed free for the hard-stop accounting.

Before-call usage snapshot recorded 2026-09-26 21:05:52Z:

- cumulative usage: `$100.176529287`
- daily usage: `$0`
- free-model daily requests: `0/1000`

The final receipt must include before/after usage, incremental spend, request counts, and any rows
left unrun. No paid comparator is allowed; the only comparator is the fixed `:free` model above.

## Execution

```bash
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  python3 scripts/jev-router-cap5.py
```

The runner pins `jev-1.13.0` only for Jev-owned calls where applicable, uses the OpenRouter endpoint
for both model ids, checks usage before and after, and writes per-row metadata to the receipt. It
must not retry past the cap. The public benchmark rows and fixed question are the only input data.

## Boundary

This preregistration does not claim that routing is better, cheaper, faster, or safer. It makes no
Jev quality claim until the receipt is complete and independently checked. The router's downstream
model/effort metadata is reported when OpenRouter returns it; missing metadata is `null`, never
inferred.
