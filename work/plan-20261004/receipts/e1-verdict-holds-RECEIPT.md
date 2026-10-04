# e1-verdict-holds receipt

## Result
**LOSES.** On these 55 fixed adjudicated rows, Jev does not beat either frozen baseline on accuracy or Cohen's kappa. This is descriptive evidence on this dataset only; there is no held-out partition, so it supports no generalization claim. The frozen question, threshold, row joins, and acceptance bar are in `PREREG.md`.

## Inputs and execution
- Gold set: 55 rows from `var/agent-tmp/dogfood/deferred/review-CyanPeak.jsonl` (`verdict_held`). The 55 labels joined to both verdict and bead text; the unmatched verdict `jev-qpv2` was excluded, as frozen in `PREREG.md`.
- Model: hosted `jev-1.13.0`; 55 sequential calls, concurrency 1. Each call has one matching row in `calls.jsonl` and one prediction in `predictions.jsonl`; all calls report `status=ok`, the pinned model, and input usage.
- Total input: 42,885 tokens; spend: $0.00180117; median latency: 150 ms. Source: `calls.jsonl` (`input_tokens`, `cost_usd`, `latency_ms`).
- Spend cap: $0.05. The pre-call bound was 981,860 input tokens / $0.04123812 total and 24,492 tokens maximum per request; source: `PREREG.md` and the runner's `--preflight` output. The runner stopped on any request failure, invalid answer, missing usage, or unsafe remaining spend.
- Execution used `nice -n 10`, concurrency 1, and a one-minute load guard before the first call and every 20 calls (`run.mjs`). The guard's `PAUSED` branch did not fire; all 55 calls completed (`calls.jsonl`).

## Scores
Positive class: `verdict_held=true`; predictions use the frozen Noul cutoff `p >= 0.5` (`PREREG.md`). Confusion counts and accuracy, precision, recall, and Cohen's kappa are recomputed from `predictions.jsonl` joined to the gold labels in `review-CyanPeak.jsonl`:

| Arm | TP | FP | TN | FN | Accuracy | Precision | Recall | Cohen's kappa |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Jev | 15 | 27 | 7 | 6 | 0.4000 | 15/42 = 0.3571 | 15/21 = 0.7143 | -0.0670 |
| Constant false | 0 | 0 | 34 | 21 | 0.6182 | 0/0 = 0 | 0/21 = 0 | 0.0000 |
| Frozen keyword rule | 18 | 18 | 16 | 3 | 0.6182 | 18/36 = 0.5000 | 18/21 = 0.8571 | 0.2884 |

Sources for baseline values: `PREREG.md`; independent recomputation used the gold labels and joined verdicts. Jev values: `predictions.jsonl` joined to `review-CyanPeak.jsonl`. The primary bar requires Jev to strictly exceed both baseline accuracy and kappa (`PREREG.md`); it misses both.

## DAG consequence
No DAG change recommended. This experiment does not support a build or rollout based on Jev verdict-hold classification; it loses the frozen comparison on this fixed dataset. No bead was created, changed, or closed.
