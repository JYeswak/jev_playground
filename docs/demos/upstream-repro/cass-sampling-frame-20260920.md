# CASS sampling frame: the 120k window vs the 5.18M whole — 2026-09-20 `[receipt]`

Read-only sqlite characterization. Window = message ids (max-120,000,
5,876,665–5,996,665]. Whole = 5,181,931 messages / 59,807 conversations /
780 workspaces (note: max id 5,996,665 > row count — ids have gaps).

## Dimensions (window vs whole)

| dimension | window | whole |
|---|---|---|
| conversations touched | 925 (1.5%) | 59,807 |
| workspaces touched | 168 (21.5%) | 780 |
| era (conversation start) | 2026-01-31 → 07-27 | 2026-01-30 → 07-27 |
| avg message length | **3,544 chars** | **764 chars** (4.6×) |
| conversation size med / p90 / max | 4 / 67 / 20,308 | 18 / 105 / 44,637 |
| top workspaces by volume | 790, 372, 700 | 462, 219, 221 (disjoint sets) |

## Reading: unrepresentative on three axes that plausibly matter

1. **"Recent" is a misnomer.** The id-window spans the full era — message
   ids are not time-ordered — so the window is an id-slice, not a recent
   slice. Anything time-varying (freshness, index state) is uncontrolled.
2. **Messages 4.6× longer** (3,544 vs 764, exact full-scan means).
   `count>0` behavior and hit content both plausibly shift with dump-heavy
   traffic; the dig-vs-invent numbers were measured on the long end.
3. **Partial conversations** (median 4 msgs vs 18): the id cut slices
   conversations mid-stream, so retrieved context is truncated on top of
   the 800-char export caps. Different top workspaces (disjoint top-3)
   confirm a different project population.

The caveat in `cass-mountain-findings-20260920.md` ("one recent
120k-message window") is therefore upgraded to this measurement in the
same page, not softened.

## NO-CLAIM

Cheap dimensions only; no claim about which axis moves the 0.058 number.
No rebuild, `cass search` untouched, export locked. `[receipt]` used.
