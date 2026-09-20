# C1 human calibration of S_wrong_selector — 2026-09-20 `[pending]`

**Outcome: AGREES (direction), margin widened.** 2 flips, both 1→0.
Human-Y slice: invent 0.125 vs dig **0.750** at 1:2 (published 0.250 vs
0.500); 0.125 vs **0.375** at 1:1 (published tie 0.250/0.250 now breaks
toward invent). The published finding is not overturned — digging loses
worse than published.

Expectation pre-registered at `8004897`; predicted 0 flips (weak,
contamination declared). Got 2. The branches bind by arithmetic, and this
arithmetic (both flips subtract positives) is the strengthen-direction,
not the overturn-direction the ≥2-flips branch priced.

## Labels (`c1-human-y.jsonl`, same directory)

8 flippable rows (8 no-hit rows unflippable, human-Y=0). Flips:

- `missing field` 1→0: top hit is a metrics ledger dump; full read-only DB
  context (conv 67693, reservation tool outputs) holds no missing-field
  answer. Mention (ledger about schemas-adjacent work) vs use.
- `undefined is not` 1→0: `undefined` occurs only as a `session_id`
  string value; no error, no answer (conv 68798 full context confirms).

Held 1s: `field does not exist` (literal `no such column` traceback),
`Cannot read properties of undefined` (literal TypeError + stack). Held
0s: all 4 empties re-read as topical non-answers.

## Cost-ratio table (human-Y, n=16, y_dig=2)

| cost (dig-miss:invent-miss) | always-invent | dig-iff-count>0 |
|---|---:|---:|
| 1:2 (published) | 0.125 | 0.750 LOSE |
| 1:1 | 0.125 | 0.375 LOSE |

## NO-CLAIM

One reader (me), mechanical-proxy author adjacent — calibration, not
independent gold. 800-char export caps; 2 rows verified past the cap via
read-only DB (no rebuild, no writes, export locked). n=16: the margin is
two labels either way, stated plainly. Pane-3 review remains the
independent check.
