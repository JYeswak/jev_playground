# Live-harvest as-of audit — 2026-09-20 `[pending]`

Regen command recovered (`python3 work/p3-calibration/mine_decisions.py`,
67s, read-only over live session logs) and run today. Artifact
`decisions_full.jsonl` (77MB, root-gitignored) derived from, then deleted.

## Re-derivation table (published 2026-09-19 → today)

| claim | published | today | status |
|---|---|---:|---|
| total dcg decisions | 216,507 | 221,873 (+2.5%) | drift demonstrated, live |
| GOOD+BAD with outcome | 78,455 (3.95%) | 82,278 (3.89%) | shape matches; conclusion unchanged (~39× kill line, NOT killed) |
| frozen sample / isError | 315/7,846 | 315/7,846 (guarded, agree) | pinned, stable |

"Joinable" reconstruction note: no saved command defines it exactly;
GOOD+BAD reproduces the shape (rate within 0.06pp) but the 3,823 gap to
78,455 is unallocated — the original corpus moved on. The as-of label on
INTEGRATIONS.md:74 now says this in the sentence.

## As-of labels placed

- INTEGRATIONS.md:74 headline: as-of 2026-09-19 + today's re-derivation +
  regen command, appended in place (numbers untouched).
- Groundtruth receipt (`toolcall-groundtruth-corpus-20260919.md`): dated
  filename is its as-of; left unedited as the historical record.

## NO-CLAIM

Re-derivation is not reproduction: today's corpus ≠ the 216,507 corpus,
so 78,455's exact method remains unrecoverable — reported, not reconciled.
Frozen counterparts are the pinned half and they agree. No rebuild, no
writes to stores; 77MB artifact removed after use.
