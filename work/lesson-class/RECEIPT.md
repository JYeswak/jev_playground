# Lesson-class Clef bake-off receipt

Status: **INCOMPLETE — no model-quality verdict**.

## Frozen design

- Preregistration: `PREREG.md`, committed as `7d62611e` before any model request.
- Dataset/split: 622 reviewer-labelled rows; 312 dev and 310 held-out, stratified by source repo.
- Clef arm: `clef-flash`, local endpoint, maximum 700 requests, one per held-out row, no retries.

## Incumbents on the frozen held-out split

| Arm | N | Accuracy | Macro-F1 |
|---|---:|---:|---:|
| Keyword rule (fit on dev only) | 310 | 0.5839 | 0.1308 |
| Majority (`SCOPE_GAP`, fit on dev only) | 310 | 0.4613 | 0.0574 |
| Clef-Flash | 0 scored / 310 expected | unavailable | unavailable |

## Live attempt

The bounded run attempted one local POST, then stopped on its first `HTTPError`, as required. The ledger records the failed attempt in `rows.jsonl`; no response was scored. Local Clef spend: **$0**. The local listener's documented GET `/` probe returned `{"models":[{"id":"clef-flash"}]}`; that GET did not run inference.

The initial request used `options`; the Clef Choice wire contract requires a `criteria` map. `run.py` now constructs the documented map, and the offline suite checks it. The failed request is not retried. The frozen paired comparison is therefore **not computable**; do not treat this as evidence about Clef's classification quality, and do not assign `BEATS-BAR` or `LOSES` as a model-quality outcome.

## Boundary

No held-out Clef answers, confusion matrix, latency summary, McNemar test, or performance verdict. A complete 310-row Clef arm was not run.
