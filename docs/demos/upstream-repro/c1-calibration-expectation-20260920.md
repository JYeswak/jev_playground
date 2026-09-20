# C1 human calibration of S_wrong_selector — pre-registered expectation `[pending]`

Committed BEFORE reading any full snippet (rule 3, `docs/RULES.md`). The
label file `work/cass-mail-mines/exports/c1-human-y.jsonl` does not exist
Labeling set: the 16 frozen-regex S_wrong_selector rows from the locked
export — 8 with hits (4 mechanical-y=0 empties, 4 mechanical-y=1) and 8
with hit_count=0 (unflippable: no snippet exists, human-Y=mechanical-Y=0).
Contamination declared: during A12 I eyeballed 8 snippet HEADS (first
~300 chars). This expectation is therefore weak; the branches below are
what bind, not my confidence.

## Expected outcome: AGREES

The 4 empties read as topically-related non-answers; the 4 y=1 read as
genuine error traces. Expect 0 flips → inversion confirmed at both cost
ratios (1:2 published 0.500 vs 0.250; 1:1 tie 0.250 vs 0.250 — direction
only, stated as tie).

## Branches (binding whichever fires)

- 0 flips → AGREES: inversion confirmed, headline strengthens.
- Exactly 1 flip → still loses (0.375 vs 0.3125 at 1:2); margin is one
  label, state it.
- ≥2 flips → digging WINS (0.250 vs 0.375): our published finding is
  WRONG — say so plainly in the receipt.
- Any top snippet unreadable/truncated-past-use → that row
  UNCALIBRATABLE, excluded with reason; if ≥3 rows uncalibratable, whole
  unit UNCALIBRATABLE. Do not guess to fill a column.

## Protocol

Reader standard: does the top snippet answer the question as a reader
would judge? Snippets from locked `cass-dig-hits.jsonl` (800-char caps
noted per row); read-only DB fallback only if a top_path is missing from
the hits file. Both cost ratios recomputed from human-Y.
