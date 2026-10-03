# Vendored-code recognition: local models vs jev-1.13.0 (bead jev-576e)

Committed before the first local call on this set.

- Data: `work/vendor-paste/sample.json` held split, 200 code windows (100 pos = third-party
  vendored, 100 neg), committed for jev-30hi; windows are upstream/third-party code.
- Incumbent: committed `work/vendor-paste/vendor-rows.jsonl` (jev-1.13.0 Noul, held rows).
- Request: identical to `run_vendor.mjs`: state `{"code": window[:4000]}`, one Noul with its
  instructions.
- Metrics: ROC-AUC (threshold-free), ECE (10 bins on the Noul), median latency.
- Bar per arm: PASS if AUC >= jev AUC - 0.02 AND ECE <= jev ECE; else FAIL.
  More than 2 failed rows = FAILED-RUN.
- Spend: $0 (local servers; jev answers are committed rows).
