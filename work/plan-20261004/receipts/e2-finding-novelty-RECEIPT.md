# e2-finding-novelty receipt

Run date: 2026-10-04. Model: `jev-1.13.0`. 85 sequential calls; all returned validated Noul answers. No retries or comparator calls.

## Rows and labels

85 reviewer rows from `var/agent-tmp/converge/r2/L1-GoldRiver.jsonl` (12), `L2-ResearchR2.jsonl` (64), `L5-WildCarp.jsonl` (2), and `L3-AmberWillow.jsonl` (7), after excluding bead `jev-grzn.2`. `fixcheck-*` files were excluded. `issues.jsonl` is a bead snapshot, not a reviewer-finding file, and was not scored. Frozen labels: 16 new, 69 repeat (`labels-GoldRiver.jsonl`). After freezing those labels and `PREREG.md`, the R2 boolean `new` flags were inspected: they match all 85 labels (85/85).

## Results

Classification threshold was preregistered at `p_new >= 0.5`.

| Actual label | Jev new | Jev repeat | Total |
|---|---:|---:|---:|
| New | 16 | 0 | 16 |
| Repeat | 36 | 33 | 69 |

Jev: 49/85 correct (57.65%); new precision 16/52 (30.77%); new recall 16/16 (100%). The 78/85 (91.76%) pass bar was not met. The model produced 36 false-new classifications.

Baselines on these same frozen labels: majority `repeat` 69/85 (81.18%); exact same-bead+class-in-R1 rule 77/85 (90.59%). Jev is below both baselines. Because blind labels equal reviewer flags on every row, Jev's score against reviewer flags is also 49/85 (57.65%); no independent-label vs reviewer-flag disagreements.

## Cost and latency

Usage: 50,308 input tokens across 85 calls. At the documented $0.042 / million input-token rate, spend was $0.002112936 (cap $0.05). Median latency 142 ms; p95 336 ms. All calls resolved to `jev-1.13.0`. Metadata-only per-call evidence: `calls.jsonl`; probabilities: `answers.jsonl`.

Budget note: the `PREREG.md` payload estimate used a short placeholder question rather than the final serialized question. Before the first call, the runner's dry-run computed a more conservative 959,217-token reserve ($0.040287114) using the actual question payload plus a 10,000-token overhead allowance per request, within the $0.05 cap. Actual usage is reported above.

The first runner invocation stopped after 43 successful rows because its local call-cap guard double-counted completed rows and in-process calls. The guard was corrected; the runner resumed from checkpoints, made no duplicate calls, and completed all 85 rows. The combined checkpoint and answer files each contain 85 unique keys and all requests succeeded.

## Verdict and boundary

**LOSES**: Jev did not beat the frozen rule or constant baseline and missed the preregistered bar. Do not promote this classifier or claim a benefit. `dag-input.jsonl` is empty: no DAG change is supported by this result. This is one bounded corpus result, not evidence of generalization beyond these 85 review rows.

Sources: frozen labels `labels-GoldRiver.jsonl`; baselines and bar `PREREG.md`; per-call model/usage/latency `calls.jsonl`; per-row Noul `answers.jsonl`; source rows under `var/agent-tmp/converge/r2/`; prior findings under `var/agent-tmp/converge/r1/`; input price `docs-mirror/typesafe/models.md`.
