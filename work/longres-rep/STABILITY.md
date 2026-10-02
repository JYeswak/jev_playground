# Stability result — frozen WindyLantern held-100

Live, 2026-10-02. `jev-1.13.0`, three calls per each of the exact 100
`work/longres/corpus.json` held rows; 300 calls, 298 scored, 2 no-answers
handled as KEEP. Any-flip rate: 9/100 rows (9%). Pairwise differing
comparisons: 18/300 (6%). Nine rows varied: h001, h002, h017, h019, h022,
h055, h064, h068, h081.

Per-run on the fixed rows (35 REFERENCED):

| Run | Reference-drop misses | Unreferenced savings (row units) |
|---|---:|---:|
| 1 | 6/35 (17.1%) | 23.576 |
| 2 | 8/35 (22.9%) | 22.594 |
| 3 | 7/35 (20.0%) | 21.627 |

Spread: misses 6–8 (2-row range); savings 21.627–23.576 (1.949 units).
Input tokens 214,906; estimated spend $0.00903 at $0.042/M input tokens;
model jev-1.13.0. Receipt: `stability-rows.jsonl`, one row per call, no text.
This is repeated measurement on one fixed sample; not three independent
populations and not a population-level accuracy estimate.
