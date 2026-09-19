# logan-markewich/jeff: Jev wins on both axes, and the config you'd deploy is the worse one

**Date:** 2026-09-19 · **Level:** `[oracle]` · Offline recompute from committed per-item data.
Clone read-only at `/tmp/jeffrepo`; nothing edited.

The second self-hosted Jev replacement surfaced today, and a different bet from `localjev`.
LocalJev wraps a **generative** model, so its probabilities are self-reported ("do not treat these
outputs as calibrated probabilities" — their own doc). `jeff` is **GLiFormer 400M**, a real
encoder-classifier, so its probabilities come from **logits**, sigmoid-normalized with an explicit
temperature fit (`JEFF_TEMPERATURE=3.2`).

That made a testable hypothesis: *jeff should be less accurate than Jev but better calibrated.*

## The hypothesis is refuted — by their data and by my recompute

`bench/results/accuracy.jsonl` ships **22,560 per-item rows** across 8 datasets, offline, no key.
Recomputed with an independent scorer (macro over tasks; ECE = 10-bin expected calibration error of
the top answer; for nouls confidence is `max(p, 1−p)`):

| run | macro accuracy | macro ECE | n |
|---|---:|---:|---:|
| **jev/jev-latest** | **78.0%** | **0.134** | 1600 |
| jev/jev-preview | 78.1% | 0.136 | 1600 |
| jeff `large/default` (T=3.2) | 66.4% | 0.154 | 3200 |
| **jeff `jeff-l4-http`** (the deployable) | 66.4% | **0.245** | 1600 |
| jeff `large/json` | 66.4% | 0.244 | 1600 |
| jeff `large/single` | 62.8% | 0.297 | 1600 |

**Jev wins on both axes**, by 11.6 accuracy points and on calibration. 0 rows skipped.

The upstream README is honest about this and says so first ("less accurate than jev on
reasoning-heavy tasks"; "jeff is over-confident; one global temperature fixes most of it").

## The finding that is not in their README

**`jeff-l4-http` — the Modal HTTP deployment you would actually run — has ECE 0.245 against
`large/default`'s 0.154, at identical 66.4% accuracy.** The temperature fit that repairs
calibration locally is not in the path you deploy. Same model, same accuracy, **59% more
calibration error**, and the difference is a config default rather than a capability.

## What it is still good for

Cost. Their measured figures: **~$2.6 vs ~$15.6 per 1M** single-question requests, 151 ms vs
129 ms p50. For a **binary, well-posed** screen where a threshold is tuned on your own labels — the
regime this lane has repeatedly found Jev strong in and calibration irrelevant to — a 6× cost
reduction at 11 points of accuracy may be the right trade. It is the wrong trade anywhere a
probability is consumed as a probability.

## NO-CLAIM

This is an **offline recompute of their committed outputs**: it validates their arithmetic and
corpus, not that a fresh run reproduces those probabilities, and I did not run `jeff` at all. Their
eight datasets are public classification benchmarks, not our workload; nothing here says how either
system behaves on agentic coding traffic. ECE at 10 bins on 200 items per task is noisy, and their
own results doc says so. Latency and cost figures are quoted from their harness, not measured here.
