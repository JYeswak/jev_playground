# jev-spam-eval W7.0 fresh run (2026-09-23, pane 4 MistyTurtle)

- jev HEAD: `9e8199b`. Clone: `jev-spam-eval @ 76ef183` (bitnovus, MIT).
- Prior receipts are LEADS, never passes (lingspam-20260918.md,
  jev-spam-eval-ood-20260918.json, EVAL.md:277).

## T4 BAR (preregistered — predates the first live call)

Pinned model `jev-1.13.0`. Rows: the clone's shipped labelled splits
(in-dist + OOD as shipped), which we did not author. Report N and
prevalence per split, call count, cost, p50/p95 latency. Noul accuracy with
exact 95% CI per split. Floor = `tfidf_baseline.py` trained/scored on the
SAME rows per split. Seat claims Jev per split iff Jev lower-CI ≥ floor;
lead says in-dist ties and OOD Jev wins — each split ruled separately, a
split the floor wins is REFUSED for that split. No cross-split pooling.

## T1–T8 + T10

| id | status | evidence |
|---|---|---|
| T1 | TBD | |
| T2 | TBD | |
| T3 | TBD | |
| T4 | TBD | |
| T5 | TBD | |
| T6 | TBD | |
| T7 | TBD | |
| T8 | TBD | |
| T10 | TBD | |

## Boundary

TBD.
