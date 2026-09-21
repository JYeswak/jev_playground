# absence-from-one-probe n=77 preregistration — 2026-09-20

**Written before any draw.** If this file's mtime is after the sample jsonl, the draw is invalid.

## Why not “original 20 + 57”

The shipped n=20 used seed `20260920`. Those 20 row identities were **not persisted** (no jsonl of texts/indices in-tree). Stacking 57 new rows on an unrecovered sample is not reproducible and could silently overlap. This is a **replacement sample of 77**, not an add. The original 4/20 is a prior estimate, not a subset of this 77.

## Sampling frame

- **Population:** assistant `type=="message"` turns under `~/.omp/profiles/**/sessions/*.jsonl` (exclude `.lock`).
- **Event:** the turn’s concatenated `type=="text"` parts match the shipped predicate in `.omp/rules/absence-from-one-probe.md` (`condition:` line), compiled as a JS `RegExp`.
- **Unit:** one firing turn. Duplicate texts across files count separately (they are separate turns).
- **Not in frame:** bash harvest, authored fixtures, this repo’s `docs/`, rule-file examples, eval transcripts we write after this prereg.

## Draw

- **n = 77** without replacement.
- **RNG:** mulberry32, seed **`2026092104`** (integer; date 2026-09-21 + P4).
- **Order:** collect fires in deterministic walk order (`readdir` lexical, files sorted, lines in file order), then Fisher–Yates shuffle with that RNG, take first 77.
- If fires < 77: stop and report INFEASIBLE (frame too small). Do not pad.

## Gold rubric (locked)

Label the **claim in the match span**, using surrounding turn text only as disambiguation.

- **TP** = capability/tool/config/service/key absence asserted from a probe (the defect the rule exists for).
- **FP** = data/table/row missing; quoting another speaker’s “was missing”; conditional/future “if it is missing”; path `does not exist` class already refused; already downgraded to UNMEASURED; regex hit that is not an absence claim.

FP rate = FP / 77 among **fires**. Quiet arms are out of frame.

## Blinding

Every row is a fire (the frame is fires). Blindness to “did the rule fire?” is **impossible** by construction. Labels are gold class, not “should it fire?”. Labeller sees match span + ≤280 chars of turn text, not the rule body, not the prior 4/20 examples as a cheat sheet during labelling.

## Decision (locked)

Wilson two-sided 95% upper bound on FP/77:

- **≤ 0.30 → CERTIFIED** (keep live; write n=77 interval into the rule).
- **> 0.30 → RETIRED** (disable via `ttsr.disabledRules`, same path as callsite).

No bar move. No dropping FPs after seeing them.

## Infeasible stop

If wall time to label 10 rows exceeds 12 minutes, stop, report minutes/row and projected total, verdict **INFEASIBLE**. Do not rush 77.
