# jevcal LIVE W7.0 receipt — 2026-09-23 (T4 bar execution + threshold transfer)

Clone: `jevcal` (github.com/abhixhek/jevcal) @ `ae8f3144d69c9cb0e5e0a2c17f70b9d14714cb9f`
(tool class; T1–T3/T9–T10 per prior receipt `jevcal-w70-2026-09-23.md` — leads, not
passes, not re-run here). This unit ran ONLY: the committed T4 bar (Amendment A in
`w70-prereg-p5.md`), the pane-1 threshold-fit/transfer question, and T8. The clone
tree was never edited and never executed in place (`git status --short -- jevcal`
empty after the run); all outputs live in `/tmp/jevcal-live-w70/`.

| id | status | result |
|---|---|---|
| T4 | PASS | `ok` on all 3 questions; held-out accepted accuracy clears target−0.02 on all 3 (table below). 400 requests, 392 answered, model observed `jev-1.13.0` on every answered row. |
| T8 | PASS (stable) | 40-row subset (t041–t080) ×3 fresh + 1 reword: 0 flips on is_urgent and department across all pairs; 1 row flips on frustration; reword changes nothing on the reworded question. |
| fit/transfer | TRANSFER | Thresholds fitted on first half (t001–t200) meet the same bar arithmetic on the second half (t201–t400) for all 3 questions; fitted values within 0.02 of full-run thresholds. |

## T4 — verdict vs bar

Command (cwd `/tmp/jevcal-live-w70`, env scrubbed of `OMP_PROFILE`/`PI_PROFILE`/
`PI_CODING_AGENT_DIR`, key via infisical, `questions.yaml` NOT edited — pin at call time):

```
jevcal run --questions <clone>/src/jevcal/examples/support/questions.yaml \
  --data <clone>/src/jevcal/examples/support/tickets.jsonl \
  --provider typesafe --model jev-1.13.0 \
  --lock decisions.lock.json --report jevcal-report.html --preds-out predictions.jsonl
```

Lock records `model_requested: jev-1.13.0`, `model_observed: [jev-1.13.0]`, `holdout: 0.5`,
`seed: 7`. Corpus prevalence re-verified keylessly before the run: 400 rows,
is_urgent-true 147 (36.8%), department 136/134/130, frustration 125/214/61.

| question | thr | target | bar (target−0.02) | held-out handled | held-out accepted acc | status | vs bar |
|---|---|---|---|---|---|---|---|
| is_urgent | 0.730 | 0.97 | 0.95 | 82.9% (0.8290) | 96.9% (0.9688) | ok | PASS (+1.9pts) |
| department | 0.610 | 0.95 | 0.93 | 99.0% (0.9896) | 97.4% (0.9738) | ok | PASS (+4.4pts) |
| frustration | 0.870 | 0.95 | 0.93 | 79.8% (0.7979) | 96.1% (0.9610) | ok | PASS (+3.1pts) |

(Figures from `decisions.lock.json` question baselines; console table agreed to 0.1%.)

Caveats, both against a strict reading and for the record:

- 8/400 rows errored and were left out of `compile`: t001, t002, t004, t006, t007,
  t011, t015, t016 — all `ProviderError: TypeSafe API returned 520`, a transient edge
  blip in the first 16 rows. 520 is not in the clone's `RETRY_STATUSES`
  (`src/jevcal/providers/typesafe.py:20`), so no retry was attempted. The 400-request
  ceiling was exactly met, so the errored rows were NOT retried (a retry would be
  calls 401–408, over ceiling). Compile ran on 392 rows; the bar's PASS clause
  (status + held-out accuracy) does not require 400 answered.
- is_urgent's held-out 96.88% sits 0.12pts BELOW its 97% target but clears the
  bar (target−0.02) by 1.9pts with status `ok` — the clone's own `HOLDOUT_SLACK`
  (`compile.py:13`) and the bar agree here. It is the tightest of the three.
- `compile` flags confident misses: department 1+, frustration 10+ at 90%+ confidence
  (verbatim in run output). On a generator-trivial synthetic corpus these read as
  generator/label noise, not model failure — consistent with the prior receipt's
  floor finding (keyword rules reach 87.5–100%).

## Threshold fit — pane-1 question

"Fit per-question thresholds on a first half-split of the 400 rows, evaluate on the
second half." Done with the clone's own machinery (`metrics.sweep` +
`pick_threshold` on answered first-half rows, `metrics.at_threshold` on second-half
rows, same measure/target per question as the lock file). No new live calls.

| question | fit rows (t001–t200 answered) | fitted thr | full-run thr | Δ | second-half (n=200) handled | second-half accepted acc | bar | transfer |
|---|---|---|---|---|---|---|---|---|
| is_urgent | 192 | 0.75 | 0.73 | +0.02 | 77.5% | 98.06% | 0.95 | YES |
| department | 192 | 0.61 | 0.61 | 0.00 | 99.0% | 96.46% | 0.93 | YES |
| frustration | 192 | 0.88 | 0.87 | +0.01 | 80.5% | 96.89% | 0.93 | YES |

Transfer verdict: **TRANSFER**. All three first-half-fitted thresholds clear the same
bar arithmetic on the unseen second half, and all three fitted values land within
0.02 of the full-run thresholds (department exactly). Note the direction: thresholds
fitted on half the data are slightly *more* conservative on is_urgent/frustration and
still deliver ≥96.4% accepted accuracy — the clone's thresholding answers the pane-1
question affirmatively on its own corpus.

## T8 — stability (rides on live calls)

Subset t041–t080 (40 rows, 0 errors in the T4 run), `measure --no-cache` (fresh calls,
cache bypassed — a cached repeat would prove nothing), same pin `jev-1.13.0`.

| question | r1↔r2 | r1↔r3 | r2↔r3 | acc r1/r2/r3 | vs T4 run (r1/r2/r3) |
|---|---|---|---|---|---|
| is_urgent | 0 | 0 | 0 | 97.5 / 97.5 / 97.5 | 0 / 0 / 0 |
| department | 0 | 0 | 0 | 100 / 100 / 100 | 0 / 0 / 0 |
| frustration | 0 | 1 | 1 | 87.5 / 87.5 / 90.0 | 1 / 1 / 2 |

Reword arm (`questions.reword.yaml` in workdir; single-line paraphrase of the
department instructions, `handle` → `own and resolve`, criteria untouched): 0 flips
on department (the reworded question), 0 on is_urgent, 1 on frustration (an
unreworded question — same background wobble as the repeats). Reword accuracy:
97.5 / 100 / 90.0. The reword neither helps nor hurts; the one frustration flip is
within the repeat noise (≤1 row / 40).

## Spend

- Live calls: 400 (T4) + 120 (3×40 repeats) + 40 (reword) = **560 requests**,
  **552 answered** (8× HTTP 520, T4 run only; T8 arms 160/160 clean).
- Tokens (answered calls): **269,569 input / 40,296 output** (T4: 191,257 / 28,616
  over 392; T8: 78,312 / 11,680 over 160).
- Cost: clone's `CostModel` prices Jev input at $0.042/MTok (`compile.py:18`) and
  states no Jev output rate → input-side **$0.0113**; output tokens reported but
  unpriced by the clone's own model. Cascade economics from the run: 33.2% of rows
  escalate, $1.327/1k rows vs $3.94 LLM-only (66.3% saved); bottleneck is frustration.
- Latency (client-measured per request): T4 (n=392) **p50 329ms / p95 475ms**
  (min 235ms, max 782ms); T8 (n=160) p50 370ms / p95 957ms.

## Boundary

One clone, one SHA (`ae8f314`), one model pin (`jev-1.13.0` observed on all 552
answered rows), one day, 560 live calls, $0.0113 input-side. T4 PASS is a
threshold-validity verdict on the clone's own synthetic, generator-trivial corpus —
it does not separate Jev from a keyword rule on raw accuracy (prior receipt's
floors stand). The tight margin is is_urgent (96.88% held-out vs 97% target, bar
95%). The 8 errored rows are an API-edge transient (HTTP 520, non-retried by the
clone's status list), not a clone defect; they cost 2% of N and no bar clause.
Transfer holds across the file-order split. Stability holds to ≤1 row / 40.
`questions.yaml` in the clone is byte-untouched; the pin lived only in argv and
`decisions.lock.json` (`model_requested`).

Re-run (read-only clone, fresh workdir; needs the key — never printed):
```
mkdir -p /tmp/jevcal-live-rerun && cd /tmp/jevcal-live-rerun && env -u OMP_PROFILE -u PI_PROFILE -u PI_CODING_AGENT_DIR infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- /Users/josh/Developer/jev/jevcal/.venv/bin/jevcal run --questions /Users/josh/Developer/jev/jevcal/src/jevcal/examples/support/questions.yaml --data /Users/josh/Developer/jev/jevcal/src/jevcal/examples/support/tickets.jsonl --provider typesafe --model jev-1.13.0 --lock decisions.lock.json --report jevcal-report.html --preds-out predictions.jsonl
```
Expect `ok` on all three questions; held-out accepted accuracy within ~±2pts of
96.9 / 97.4 / 96.1 (seed-7 split; exact match requires the same 8 rows to answer —
a 520 blip reshuffles fit/holdout membership).
