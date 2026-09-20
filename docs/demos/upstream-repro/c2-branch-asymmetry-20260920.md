# C2 strict/lenient branch asymmetry — 2026-09-20 `[pending]`

**Answer: the asymmetry is real and runs opposite to the feared direction.**
Across all 138 locked rows, ZERO of 22 positives came from the strict
branch; all 4 strict-routed rows with hits are the zeros that make the
slice lose. But C1 human review confirms all 4 strict zeros and flips 2
lenient ones — the strict veto was human-right, the lenient bar
human-loose twice. No overturn; the inversion stands on human firmer
ground than on mechanical.

## Branches (frozen as code-read in `cass_dig_y.py`, no tuning possible)

- **Strict** (query matches `no such (field|key)|keys present|requireKey|
  \.distribution`): y=1 only if a snippet matches absence language AND
  shows requireKey/keys() evidence (or receipt-shaped + absence).
- **Lenient** (everything else): y=1 iff ANY hit has source_path + line.

## Per-slice attribution (mechanical-Y)

| slice | n | y=1 | strict-y1 | lenient-y1 | strict-y0 w/ hits |
|---|---:|---:|---:|---:|---:|
| S_wrong_selector | 16 | 4 | 0 | 4 | 4 |
| S_lexical_trap | 20 | 3 | 0 | 3 | 0 |
| S_control | 2 | 0 | 0 | 0 | 0 |
| S_pass_probes | 30 | 0 | 0 | 0 | 0 |
| S_topical | 82 | 15 | 0 | 15 | 0 |

## Counterfactual that matters

Lenient applied to the 4 empties (all receipt-shaped, score 10) → y=1 ×4:
slice becomes y_dig=8, invent 0.500, dig-iff 0.000 — digging WINS and the
inversion vanishes. **The entire published inversion hangs on the strict
branch zeroing exactly those 4 rows.** On this window the strict branch is
a pure veto: evaluated 4 times, fired y=1 zero times anywhere.

## Human cross-check (C1, `c1-human-y.jsonl`)

- 4 strict zeros: human AGREES 4/4 (topical non-answers).
- 4 slice lenient ones: human flips 2 (`missing field` ledger dump,
  `undefined is not` session_id string).
- So the feared artifact (strict fabricating the loss) is backwards: the
  loss is human-real, and lenient looseness is where the 2 errors sit.
  Human slice: invent 0.125 vs dig 0.750.

## NO-CLAIM

Branch routing re-derived from the frozen regexes, not re-run through a
new scorer (attribution script was inline; counts re-verifiable from the
locked export). C1 covers the 16 slice rows only — the 18 lenient ones
outside the slice are uncalibrated; no aggregate human recompute claimed.
Strict branch may fire elsewhere on other windows; here it is 0/4.
