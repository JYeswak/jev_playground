# Fleet family re-rank

as_of: 2026-10-04T00:48:27Z
scan verdict: COMPLETE
command: nice -n 10 python3 work/fleet-schema/miner.py --rank --as-of 2026-10-04T00:48:27Z --json
Current counts are recomputed from the streamed miner output; plan counts are from the committed decision-point registry.
A partial or deferred scan is not a ranking and MUST NOT be treated as complete.

| Family | Current occurrences | Plan occurrences | Δ occurrences | Current labels | Plan labels | Δ labels | Re-rank |
|---|---:|---:|---:|---:|---:|---:|---|
| result | 90517 | 99680 | -9163 | 3611 | 4329 | -718 | — |
| rank | 35532 | 41059 | -5527 | 341 | 421 | -80 | — |
| reread | 34407 | 36827 | -2420 | 13611 | 20388 | -6777 | — |
| route | 44042 | 44086 | -44 | 835 | 1292 | -457 | — |
| nudge | 20758 | 22479 | -1721 | 1727 | 1533 | +194 | — |
| recover | 11524 | 11970 | -446 | 6422 | 6644 | -222 | — |
| land | 6300 | 6466 | -166 | 594 | 652 | -58 | — |
| outcome | 7297 | 7536 | -239 | 31 | 31 | +0 | — |
| pin | 1416 | 1577 | -161 | 1238 | 1385 | -147 | — |
| delegate | 4022 | 4362 | -340 | 15 | 39 | -24 | REOPEN |
| review | 186 | 220 | -34 | 0 | 0 | +0 | — |
| memory | 28635 | 41025 | -12390 | 0 | 0 | +0 | — |
| gate | 30525 | 74351 | -43826 | 0 | 0 | +0 | — |
| screen | 14101 | 19835 | -5734 | 0 | 0 | +0 | — |
| watch | 15124 | 16124 | -1000 | 0 | 0 | +0 | — |
| effort | 9979 | 10756 | -777 | 0 | 0 | +0 | — |

The `outcome` occurrence count excludes DP-48 aborts; DP-48 is a label source, not a separate decision.
Any REOPEN requires a comment on jev-b35c.5 before family bake-off scores are used.
