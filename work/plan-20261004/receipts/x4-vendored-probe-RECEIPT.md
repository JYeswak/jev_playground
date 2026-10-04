# x4-vendored-probe receipt

**Verdict: BEATS-BAR for the X4-specific held-AUC criterion** on this frozen 320-window sample only. This does not establish deployment or cross-repository value.

## Inputs and baselines

- `work/vendor-paste/sample.json`: 120 dev (60 pos/60 neg), 200 held (100 pos/100 neg); raw SHA256 `2a167ed69ebfa5aa41399b278c14c1dae5a40ec630f4de97cfbb7faaa39644ab`; canonical sorted-JSON SHA256 `d510050d83bfa399b9eb36252f545415bea089c03bef5ca15939f47ef858356d`.
- Source groups: 46 dev, 53 held, 0 overlap, derived from `sample.json` paths using `build-corpus.py:101-123`.
- Majority constant: dev/held accuracy .500, held AUC .500 (`sample.json`).
- Cheapest license-header rule (`lic=true`→pos): dev accuracy/AUC .5083; held accuracy/AUC .5650; only 1 dev and 13 held rows have `lic=true`, all positive (`sample.json`; regex at `work/vendor-paste/build-corpus.py:12-15`).
- Jev incumbent: .82745 held AUC; all 200 held row IDs and window hashes match `sample.json` (`work/vendor-paste/vendor-rows.jsonl`).
- Clef incumbent: .83885 held AUC; all 200 held IDs match `sample.json` (`work/local-decision-arms/vendor-rows-clefflash.jsonl`). These reproduce the cited .827/.839 baselines (`work/plan-20261004/specs/advanced-mathops.md:56`).

## Probe

Command, both runs: `nice -n 10 uv run --no-project --offline --with scikit-learn python var/agent-tmp/dogfood/x4-vendored-probe/run.py`. Cached `scikit-learn 1.9.1` / `scipy 1.18.1`; CPU-only, offline, no Jev/Clef calls, no downloads, spend $0.00. Runner: `run.py`.

Model fixed in `PREREG.md`: word TF-IDF 1–2 grams + char TF-IDF 3–5 grams (`min_df=2`, sublinear TF) + existing license-regex bit; `LogisticRegression(C=1, solver=liblinear, max_iter=1000, seed=20261004)`. Vectorizers and classifier fit only on dev. No held threshold or tuning.

## Held result

- Probe AUC .91750; accuracy at .5 = .815; 42,892 vectorizer features plus the license bit.
- Paired DeLong: probe vs Jev ΔAUC +.09005, p=.000412; probe vs Clef ΔAUC +.07865, p=.006550. Both remain below .05 under Holm correction for these two comparisons (adjusted p=.000823 and .006550). DeLong self-check Jev vs Clef: ΔAUC −.01140, p=.6740, consistent with the prior .67 comparison (`var/agent-tmp/dogfood/ecosystem/EVIDENCE-MAP.md:47`).
- Fixed X4 bar: AUC >= Jev−.02 = .80745 (`var/agent-tmp/dogfood/ecosystem/EVIDENCE-MAP.md:127`). Result passes by .11005 AUC. The broader vendor comparison contract also requires ECE <= Jev ECE (`work/local-decision-arms/BAR-vendor.md:10-11`); ECE was not measured here, so that broader contract is NOT VERIFIED.
- Two runs produced the same held AUCs, DeLong results and baseline values. Logistic-regression fit times were 30.1 ms and 32.5 ms; whole `uv run` wall times were 4.14 s and 3.72 s (includes interpreter/import, vectorizer, evaluation and DeLong). Per-window production inference latency was not measured.

This is evidence for the preregistered constructed sample, not organic prevalence, production latency, or generalization to another repository. No code outside `var/agent-tmp/dogfood/x4-vendored-probe/` changed for this experiment.
