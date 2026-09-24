# oracle-kit select-on-A/report-on-B — use-once receipt (2026-09-23) [live]

Bead `jev-deep-kit-8q7.7`. Bar committed [pending] in `notes/deep/w74-bars.md`
before any live call; bar text unchanged. Library commit `c22673b` (pushed).

## What ran

Fresh live rows, not the clone's committed aggregates: 2000/2000 emails from
`upstream/anisselbd/jev-phishing-bench/data/emails.jsonl`, one bundled request
per row (verdict Choice + 5 signal Nouls, identical wording to the clone's
`run_jev.py:29-79`), pinned `jev-1.13.0`, key via infisical, driver
`/tmp/jev-8q77-drive.py` (clone tree untouched; rows in `/tmp/jev-8q77-rows.jsonl`).
Prevalence first: 50.0% phishing, always-1 1000/2000, verdict DEFERRED.
Lane: 2000 calls, 0 errors, p50 0.381s / p95 0.868s, 1,480,888 in / 270,000 out
tokens ≈ $0.0622, model `jev-1.13.0` on every row.

## Helper under test (`work/oracle-kit`, commit `c22673b`)

`selectSingleSignal` + `fitLogistic`/`scoreLogistic`, analysis
`/tmp/jev-8q77-analyze.mjs`. Same split discipline as
`jev-phishing-bench/bench/protocol.py`: stratified halves at seed 1, everything
chosen on A, everything published from B.

## Result vs bar

| arm | AUROC on half B | source |
|---|---|---|
| single verdict (incumbent: current single-threshold path, same half) | 0.6846 | helper `selectSingleSignal` on 1-signal input (`selected:false`) |
| best single signal (sig_free_hosting, t=0.555 fit on A) | 0.9562, acc 0.8950 | helper, same run |
| 5-signal logistic fit on A | **0.9872** | helper `fitLogistic`/`scoreLogistic` |
| clone's committed split (for comparison, not evidence) | single_rule 0.9583 / logistic 0.9825, same feature, t=0.705 | `results/metrics.json` controls |

Gain (combination − single verdict): **+30.3pts ≥ 5pts → BAR PASS.**
The helper independently reproduces the clone's split to the third decimal
(feature, accuracies, weight signs, dominant features all agree).

## Planted negative

Single-signal input returns the single with `selected:false` (test suite +
live run above: the single-verdict arm reports `selected:false`, no gain claimed).

## NO-CLAIM

One 2000-row run on a public corpus at a fixed cut; not a claim that the
combination generalizes, and not a claim about any other model version.
Per-row live rows live in `/tmp` (uncommitted scratch), not in this tree.

## Rows committed — 2026-09-24

`/tmp/jev-8q77-rows.jsonl` copied byte-identical (`cmp`) to `work/tmp-rescue/jev-8q77-rows.jsonl`, sha256 `b895bf95d1dbe735aca7dfc8c24bbd7b47e1fd2557bae66f15082de0f8b0a7f2`. The `/tmp` copy was not deleted.
