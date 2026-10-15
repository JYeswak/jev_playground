# P4 organic gate cohort — preregistration (frozen before any call)

Bead: jev-p4-gate-bar-gtok. Status: terminal NOT_REACHABLE (see verdict).

reach-mode: auc

## Frozen source

- Demand census: `work/gate-family/demand/receipt.json` (p2-census-v2).
- Window rows: `work/gate-family/demand/rows-hash-only.jsonl`
  (15,481 scored rows; window SHA-256
  `12efb85b28cbe24f505536f98fe18f588c8664305024ca08144b828a23425f66`;
  concatenated sources SHA-256
  `d0e7e1154fef9c11441657ccc836faeb0fb68a9991fb0600a0024c3efa51c89a`).
- Label sets: recount join over `work/jev-1lim/manifest.jsonl`,
  `work/jev-uncd/items.jsonl` (see `work/gate-family/demand/census.py`).

## Frozen cohort

- Eligible denominator: 15,481 scored window rows.
- Covered rows (non-null recount assignment): 45, all `no-harm`; 0
  harm-labelled, 0 same-event joins, 15,481 missing outcomes.
- All 45 covered rows share one command hash
  (`823686c7…`); the split below is by event (row index), session-disjoint.
- DEV row indices (30): 4788, 4812, 4813, 4818, 4925, 7138, 7476, 7510,
  9298, 9300, 9308, 9310, 9311, 9855, 11153, 11166, 11223, 11806, 11810,
  11821, 11823, 11837, 12199, 12223, 12327, 12332, 12344, 12465, 12494, 13131.
- HELD row indices (15): remainder of the 45 covered events (see
  `reach.json`); session-disjoint from DEV (seed 20261015).

## Verdict: terminal NOT_REACHABLE

A gate decision experiment needs labelled harmful AND clean outcomes.
Harmful count is 0, so no bar (paired accuracy, low-FPR recall, or
non-inferiority margin) can be powered or preregistered. The exact
infeasible input is **labelled harmful gate outcomes** (0 exist;
15,481 outcomes missing). No call is authorized under this preregistration.
Any future labelled harms require a new preregistration; this verdict
must not be edited into reachability.
