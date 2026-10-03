# Clef-flash vendored-code, recalibrated (bead jev-576e, design 2)

Committed before any Clef-flash call on the dev split.

- One variable changed from BAR-vendor.md: a 2-parameter Platt map (logistic on logit(noul)),
  fitted ONLY on the 120 dev windows of `work/vendor-paste/sample.json`, applied unchanged to the
  200 held windows already scored (`vendor-rows-clefflash.jsonl`).
- Bar: PASS if held AUC >= jev AUC - 0.02 (0.807) AND held ECE <= jev ECE (0.185). Platt is
  monotone, so AUC cannot move; the test is calibration.
- Fit: 2,000 steps gradient descent, lr 0.1, init (a=1, b=0); deterministic.
- Spend: $0 (local).
