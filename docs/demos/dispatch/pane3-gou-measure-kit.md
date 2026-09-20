# P3 — `jev-gou`: port the remaining measure scripts to `measure-kit`

Your R44 work landed and is verified on the shipped artifact: data literal `harm_pass 0.01`,
executed literal `harm_fire 0.96`, census `--no-filter` 0 fires on 81,382, curated control still
`REPRODUCIBLE`. R44 is retired. Moving the mechanism into the rule rather than leaving it in the
census was the whole difference, and you disclosed that gap yourself last round.

## Why this bead is next

Verdict discipline was the spine of tonight's work: `DISCRIMINATES` requires
`correct > best_constant + near_threshold_count`, and §14e showed **half the verdicts in a run
were made by our 0.50 threshold rather than by Jev**. `work/jev-client/measure-kit.mjs` computes
that correctly. Any measure script that hand-rolls its own arithmetic can disagree with it
silently, and a second table is how two receipts end up quoting different verdicts for the same
scores.

## Unit

Find the measure scripts still computing verdicts or baselines themselves, and port them to
`measure-kit`'s `gradeQuestion`. Start by listing candidates rather than assuming:

```bash
ls work/*/measure*.mjs work/*/*measure*.mjs 2>/dev/null
grep -rln 'best_constant\|bestConstant\|DISCRIMINATES' work/ --include='*.mjs' | sort
```

**Grep the directory, not one canonical file** — a per-package probe that assumes one entry file
cost me a wrong census tonight.

For each script: port it, or record why it should not be ported. **"Should not be ported" is a
real outcome** — `§21`'s ceiling harness computes a margin-to-bar, not a question verdict, and
forcing it through `gradeQuestion` would be wrong.

## ACCEPTANCE

1. A list of every candidate found, each marked PORTED or NOT-PORTED-because.
2. For each ported script: its verdict output **before and after**, shown identical. If any
   verdict CHANGES, that is the finding — stop and report it, because it means a shipped receipt
   quotes a number `measure-kit` disagrees with.
3. Suites green for anything touched; `TESTS.md` entry in the same commit if a test file changes.

## Constraints

- **No new Jev calls.** Port arithmetic against RECORDED scores; re-running live would change the
  numbers you are trying to compare and cost budget for nothing.
- Commit on create. Exit codes unpiped.
- Panes 1 and 2: pane 2 still `WAIT_FOR_RESET`, pane 1 free but mid-turn. Prefer a landed partial.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-GOU-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
