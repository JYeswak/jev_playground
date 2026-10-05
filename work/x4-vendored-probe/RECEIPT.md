# X4 vendored-code TF-IDF probe: receipt (bead jev-x4-vendored-probe-closeout-82p7)

**Headline: meets the non-inferiority bar on a constructed sample.** Held AUC .91750 >= bar .80745 (Jev .82745 - .02). The probe is ahead of Jev under a source-group cluster bootstrap (95% CI excludes 0, lower end +.0014), but not ahead of Clef (CI includes 0). Under the broader vendor contract (ECE <= Jev ECE), the result depends on which Jev ECE is used: the probe passes against Jev's raw ECE (.1846) but **fails** once Jev gets the same dev-fitted Platt map (.1653 vs .0724). Organic prevalence is 0/39, so none of this is deployment value.

Lane: offline, local CPU, N = 120 dev / 200 held windows, 2026-10-05, no Jev or Clef calls, spend $0.00. Inputs are committed rows only.

## Command and reproduction

```
nice -n 10 uv run --no-project --offline --with scikit-learn python work/x4-vendored-probe/run.py
nice -n 10 uv run --no-project --offline --with scikit-learn python -m unittest work/x4-vendored-probe/test_run.py -v
```

The runner prints one JSON object. I ran it twice; the outputs were identical apart from `fit_seconds`, and each run took 6.67 s wall time, including the 2 x 2,000 bootstrap. The unit tests need scikit-learn, and the system `python3` has none, so run them through `uv` as shown. Package versions are those cached by `uv` (scikit-learn 1.9.1, scipy 1.18.1, per the 2026-10-04 run).

Inputs (all tracked):
- `work/vendor-paste/sample.json`: raw sha256 `2a167ed6…44ab`, canonical `d510050d83bf…`. The runner checks both and refuses on mismatch. Source groups: 46 dev and 53 held, with no overlap.
- Jev: `work/vendor-paste/vendor-rows.jsonl`, 320 rows (dev and held), all `scored`, with window hashes checked.
- Clef: `work/local-decision-arms/vendor-rows-clefflash.jsonl` (held) and `vendor-rows-clefflash-dev.jsonl` (dev).

## Reproduced from the 2026-10-04 receipt (`work/plan-20261004/receipts/x4-vendored-probe-RECEIPT.md`)

| Quantity | 10-04 receipt | This run |
|---|---:|---:|
| Probe held AUC | .91750 | .91750 |
| Jev / Clef held AUC | .82745 / .83885 | .82745 / .83885 |
| DeLong probe - Jev | +.09005, p .000412 | +.09005, p .000412, Holm .000823 |
| DeLong probe - Clef | +.07865, p .006550 | +.07865, p .006550, Holm .006550 |
| DeLong Jev - Clef check | -.01140, p .6740 | -.01140, p .6740 |
| Majority / license rule held AUC | .500 / .5650 | .500 / .5650 |
| Vectorizer features | 42,892 | 42,892 |

## Added: source-group cluster bootstrap

DeLong treats the 200 held windows as independent, but they come from 53 source groups. This bootstrap resamples the groups (B = 2,000, seed 20261004; 1,968 draws had both classes) and reports percentile 95% CIs.

| Difference | Point | 95% CI (group-resampled) | Excludes 0 |
|---|---:|---|---|
| probe - Jev AUC | +.09005 | [+.00138, +.17371] | yes (barely) |
| probe - Clef AUC | +.07865 | [-.02783, +.12629] | **no** |

The DeLong p-values overstate significance. Once clustering is accounted for, the probe-vs-Clef win does not hold, and the probe-vs-Jev win holds with a lower bound near zero.

## Added: ECE (10 bins, rule from `work/local-decision-arms/vendor.py:85`)

Each arm gets one 2-parameter Platt map, fit on dev only and applied unchanged to held. The fit procedure is that of `work/local-decision-arms/BAR-vendor-platt.md`. For Clef, the fit reproduces `vendor.py --platt clefflash` (a 1.239, b 2.926, ECE .0832), which is an independent check of this implementation. The ECE CI comes from the same group bootstrap. Bootstrap ECE is biased upward on resampled small bins, so read the CIs as width, not center.

| Arm | ECE raw | ECE after dev Platt | Platt 95% CI | Platt (a, b) |
|---|---:|---:|---|---|
| Probe | .2237 | .1653 | [.1011, .2947] | 1.793, 0.355 |
| Jev | .1846 (contract reference) | .0724 | [.0702, .2677] | 2.112, 1.640 |
| Clef | .3106 | .0832 | [.0575, .2537] | 1.239, 2.926 |

Deviation, stated before reading held ECE: the probe's own dev scores are in-sample, because it was fit on those rows. Its Platt map is therefore fit on out-of-fold dev scores (`GroupKFold`, 5 folds over dev source groups, same model per fold). Jev and Clef dev scores are already out-of-sample.

Contract reading (`work/local-decision-arms/BAR-vendor.md:10-11`, ECE <= Jev ECE):
- Against the raw-Jev reference .1846: probe .1653, **passes**.
- Same calibration on both sides (Platt vs Platt): probe .1653 vs Jev .0724, **fails**. Calibrated Jev and Clef are both better calibrated than the calibrated probe.

## X4b (Qwen3 embedding arm): NOT_RUN under this bead

The gate is that `work/x4-vendored-probe/x4b-PREREG.md` (committed here) exists AND `jev-mvvh` returns a vendor-shadow verdict of KEEP. `jev-mvvh` is `open` with no verdict on 2026-10-05, so X4b was not run and `scripts/local-model-guard.sh` was not called (zero model loads). A pre-gate scratch run from 2026-10-04 exists (`var/agent-tmp/dogfood/x4b-vendored-embed/RECEIPT.md`: AUC .86570, ECE .21262, LOSES). It is not counted here, and the committed PREREG says it is not blind.

## Planted negatives (`test_run.py`, 4/4 pass)

- A probe refit with held rows added to dev is refused (`fit_probe` raises).
- A bootstrap that resamples windows (one unit per row) is refused (`cluster_bootstrap` raises).
- Positive controls: a dev-only fit is accepted, and source-group resampling uses exactly 53 units.

## Boundary

Not run: X4b, any live Jev or Clef call, any second repository, organic traffic, per-window production latency. This bead does not establish deployment value.
