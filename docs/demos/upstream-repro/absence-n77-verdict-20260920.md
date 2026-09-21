# absence-from-one-probe n=77 — 2026-09-21 `[receipt]`

**Lane:** offline labels on real transcripts. **Oracle:** statsmodels 0.15.0 Wilson + scipy 1.18.1 Clopper–Pearson. **Decision bar (preregistered):** Wilson two-sided 95% upper ≤ 0.30 → CERTIFIED, else RETIRED.

Sampling frame and seed were written **before** the draw: `absence-n77-preregister-20260920.md`. Seed `2026092104`, mulberry32, 77 without replacement from 188 fires / 1818 session jsonl files. Replacement sample (original n=20 identities were not persisted).

## Blinding

Frame = fires, so every row already fired. Labels are gold class, not “should it fire?”. Labeller saw match span + ≤280 chars.

## Result

| | |
|---|---|
| n | 77 |
| TP | 56 |
| FP | 21 |
| p̂ | 0.2727 |
| Wilson 95% | **[0.186, 0.381]** |
| CP 95% | [0.177, 0.386] |

**Upper 0.381 > 0.30. RETIRED.**

The n=20 estimate 0.20 was underpowered **and** optimistic relative to this draw. Paying n=77 did not certify. Do not keep it live because it is already installed.

FP ranks (21): 1, 6, 15, 17, 22, 26, 28, 29, 36, 41, 42, 43, 47, 48, 54, 57, 64, 67, 69, 72, 75. Reasons in `absence-n77-labels-20260920.jsonl`. Dominant FP classes: conditionals (`if`/`when` absent), data/files/spacing, quoting/teaching the defect.

Cost: draw 20.3 s; labelling 77 rows from match+snippet in one pass, feasible (not INFEASIBLE).

## Action

Disable `absence-from-one-probe` via `ttsr.disabledRules`. Rule files stay on disk (no deletion). Same reversible path as callsite / R64.

## NO-CLAIM

Not a relabel of bash-structural-def-search. Not a claim the original 4/20 was fraud — it was n=20. Not a new predicate.
