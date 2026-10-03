# Clef-flash + Platt (design 2) on Banking77 (bead jev-576e)

Committed before any Clef-flash call on these dev rows. Same design as BAR-vendor-platt.md so one
design is tested on two sets.

- Dev: 200 rows from the 2,480 Banking77 test rows NOT in the 600-row sample,
  `random.Random(8).sample(sorted(rest), 200)`.
- Platt map logistic(a*logit(p)+b) on the chosen-option probability vs correct/incorrect,
  fitted on dev (2,000 steps, lr 0.1, init a=1 b=0), applied unchanged to the committed 600 held
  rows `rows-clefflash.jsonl`. The chosen label does not change, so accuracy is unchanged.
- Bar: PASS if accuracy >= jev 0.7867 - 0.02 AND ECE (10 bins on the mapped probability)
  <= jev 0.1017.
- Spend: $0 (local).
