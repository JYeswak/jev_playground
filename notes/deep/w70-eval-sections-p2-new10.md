# EVAL sections — pane 2, W7.0 new clones — 2026-09-23

`EVAL.md` was not appended. It is the highest-contention file in this tree and this session did not take a reservation. These rows are the ledger text.

Lane: live where a call was made. Model pin `jev-1.13.0` unless noted. Key via Infisical, never printed.

| clone | SHA | result class | live N | cost | receipt |
|---|---|---|---|---|---|
| Canny | `f2c5e53` | FLOOR | 24 scored stops; receipt spend 96 Jev calls, 65800 in / 2016 out. `usage.cost` absent | not invented | `docs/demos/upstream-repro/Canny-w70-20260923.md` |
| neo4jev | `d157bbe` | FLOOR | 3 goals, 2/3; instrumented 10 hops, 168124 in / 4103 out. Other calls counted in the receipt, tokens not invented | not invented | `docs/demos/upstream-repro/neo4jev-w70-20260923.md` |
| prism-liquidity-agent | `f503db1` | withheld | smoke N=1 pool, 4 calls, 2818 in / 388 out. Not re-run; `/tmp/prism-w70` absent at commit | not invented | `docs/demos/upstream-repro/prism-liquidity-agent-w70-20260923.md` |
| jev-curate | `d1a3a05` | FLOOR | binary 422s as in the receipt. This session: 32 calls (1 uncaptured parser crash, 1 shown, 30 rerun). Measured usage 18054 in / 1209 out on the 31 printed calls | $0.000758 at README input rate, arithmetic, not an invoice | `docs/demos/upstream-repro/jev-curate-w70-20260923.md` |
| agent-desktop | `a4a695f` | withheld | smoke N=4, no execute | not an accuracy | `docs/demos/upstream-repro/agent-desktop-w70-20260923.md` |
| jev-drone | `c0efd03` | FLOOR | 287 Jev calls in the receipt; prevalence exit 2; no accuracy claim | disclosed-rate arithmetic in the receipt, not an invoice | `docs/demos/upstream-repro/jev-drone-w70-20260923.md` |
| typesafe-mario | `ca22449` | UNEARNED | N=0. No ROM on disk. Not downloaded | $0 | `docs/demos/upstream-repro/typesafe-mario-w70-20260923.md` |

## W7.4 tuples, not inserted into `w74-ranking.tsv`

Written score, plan §4 W7.4: lexicographic on ground_truth (1 if the receipt names a labelled corpus), prevalence (fraction, else 0), cost (2 keyless, 1 live-key, 0 rch-worker), leverage (1 if an omp surface can block or rewrite), then result class. A FLOOR seat is refused unless the application changes the task. The shared ranking already has a top three and beads. These tuples were not inserted.

- Canny: ground_truth 1 (1132 labelled stops in the receipt's extraction). Prevalence of done on that extraction 37/1095 = 0.0338, not the stratified 12/12 sample. Cost 1 (live-key). Leverage 1 (Stop hook blocks). Class FLOOR on `claims_done`. The application that changes the task is the deterministic ledger, which does not call Jev. That does not displace `jev-review`.
- jev-drone: ground_truth 0 (prevalence exit 2, no labelled maneuver corpus). Prevalence 0. Cost 1. Leverage 0 (sim control loop, not an omp block). Class FLOOR. Does not enter the acting top three.

## Boundary

Keyless rows characterise clone code. Live rows are the calls named above, at the pins named above, on 2026-09-23. Nothing here is an omp L3 firing. Canny was not installed. prism had no wallet. mario had no ROM. jev-trader was not run.
