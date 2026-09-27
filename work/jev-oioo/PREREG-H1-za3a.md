# Jev H1 dev-slice replay — jev-za3a

**Frozen before any Jev call. Dev slice only; a pass licenses a fresh held-out test on another dataset and is not a claim about Climate-FEVER or a promotion/ruling.**

reach-mode: mcnemar
n: 200
model: jev-1.13.0
items_sha256: a3c4359f502fee27e4b212d4d606f3c22da53b153fe5c706c43f6fd700a754a7

- **Corpus:** the committed 907-row Climate-FEVER eligible-pair manifest from `work/jev-oioo/items.jsonl`; public source SHA `8a4b9032d861be482ffb49dddfd283ffa6089e654f1e968040011882c5eb6e0b`.
- **Dev slice:** 200 hash-keyed IDs in `h1-dev-items.jsonl`, selected with `random.Random(20260927)`, balanced 100 SUPPORTS / 100 REFUTES, all from the predeclared heterogeneous-evidence stratum. No row is selected after seeing the replay answers.
- **Frozen baseline:** the committed Jev row for each same ID from `work/jev-oioo/live-results.jsonl`, model `jev-1.13.0`, scored with the original state containing all five evidence sentences.
- **One variable:** the replay state keeps only evidence sentences whose Climate-FEVER per-sentence `evidence_label` equals the dataset claim label. The claim, instruction (`Does the evidence support the claim?`), criteria, model, threshold (`noul > 0.5`), and client are unchanged. **Leak:** this filter uses the gold per-sentence labels; therefore any gain demonstrates a gold-informed evidence-selection oracle, not a deployable method.
- **Primary comparison:** paired replay-vs-baseline accuracy on these 200 IDs; report Jev-only and baseline-only correct counts and exact two-sided McNemar p. Errors/refusals are counted separately and never silently scored as wrong.
- **Bar:** exploratory: report the paired result and whether replay improves accuracy; no pass/fail promotion bar is asserted because the state transformation is gold-informed and this is a dev slice.
- **Spend:** Jev only; record model, input/output usage, latency, and input spend at `$0.042/M` input tokens. No comparator call.
- **Non-claim:** this replay tests one gold-leaking state transformation on 200 public Climate-FEVER rows. It does not validate a deployable selector or explain general Jev behavior.
