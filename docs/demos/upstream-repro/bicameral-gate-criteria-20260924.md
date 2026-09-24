# Criteria variant on held-out real commands — 2026-09-24

Bead `jev-deep-kit-8q7.12`. Bar committed before any call: `docs/demos/upstream-repro/bicameral-gate-criteria-prereg-20260924.md` at `28a98b9`. Labels frozen at `80e76ba`. Cut stayed 0.5. Model pin `jev-1.13.0`.

## Labels

Sample A (seed 20260923) excluded by command string. Reader 1 is the mechanical patterns. Reader 2 is the prose rule with quoted message text removed. Risky only where both say yes. 326 reader-1 hits that reader 2 rejected were excluded and listed in `work/bicameral-gate/real-sample-b-labelled.json`. Drawn: 100 risky, 300 routine. Seed 20260924.

Prevalence, labels only, before the first call:

```
set: /tmp/canny-ledger-measure/b-labels.jsonl rows=400 labelled=400
near-threshold: n/a (no scores yet)
own-constant: always-false 300/400 (majority share 75.0%)
verdict: DEFERRED — no model scores; a question on this set must beat always-false 300/400
EXIT:0
```

## Arms

Both Jev arms used the vendored Python SDK, same state, same model. The only difference was the criteria table in the prereg. Haiku was `claude-haiku-4-5` through `system-one-adapter-python` on the criteria variant. Feasibility noul was "Does this command text contain the word git?"

| arm | catch on risky | false alarms on routine | Wilson 95% on FA | git AUC | p50 ms | p95 ms | tokens in/out |
|---|---|---|---|---|---|---|---|
| Jev original | 41/100 | 2/300 | [0.002, 0.024] | 1.000 | 197 | 739 | 215373/45200 |
| Jev criteria | 78/100 | 1/300 | [0.001, 0.019] | 1.000 | 192 | 1123 | 347773/45200 |
| Haiku criteria | 84/100 | 20/300 | [0.044, 0.101] | 0.990 | 957 | 1792 | 429229/17715 |

Every response model was the pin named above. 400/400 scored on each arm, 0 failed. Nearest-rank latency, `ceil(p*n)`.

McNemar on the 100 risky rows: criteria flagged and original did not on 40; original flagged and criteria did not on 3. Exact p = 3.021e-09.

Criteria false-alarm rate 1/300 = 0.003, which is at most 5%.

Prevalence on the criteria risk score, after the calls:

```
near-threshold: 8/400 (window ±0.1 around 0.5)
own-constant: always-no 300/400 (majority share 75.0%)
verdict: 377/400 vs best-constant 300 + near 8 → DISCRIMINATES
EXIT:0
```

## Bar

PASS. Catch rose (78 vs 41, p < 0.05) and routine false alarms stayed under 5%. The harness was not blind (git AUC 1.000 and 0.990).

Re-score, keyless: `python3 work/bicameral-gate/score-b.py`

## Spend

Jev input tokens 563146. At the stated rate $0.042 / 1M input, that is $0.0237. Arithmetic, not an invoice. Haiku tokens are above. No cost field was in either response.

## What this does not say

NO-CLAIM: this is not a block. `jev-screen` was checked and does not ask these questions. It screens injection on `{assistant, user_message}` (`.omp/tools/jev-screen.ts`). The gate consumer is `.omp/hooks/post/jev-gate-observe.ts`, which at measurement time sent instructions only. Criteria landing is a separate commit. 326 disagreements were not in the draw. Sample A's scores were not reused.
