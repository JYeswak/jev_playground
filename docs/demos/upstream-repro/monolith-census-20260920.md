# Monolith census: the code is fine, the documentation is the monolith `[receipt]`

Ran the de-monolithize census against this repo. **It stops cheaply, and the answer inverts the
question.**

## The measurement

```bash
git ls-files | grep -E '\.(ts|mjs|js|py|sh|rs)$' | xargs wc -l | sort -rn | head
git ls-files | grep -E '\.md$'                   | xargs wc -l | sort -rn | head
```

| | files | lines |
|---|---:|---:|
| markdown | **507** | **61,789** |
| code | 331 | 36,402 |
| | | **docs are 1.7× the code** |

**Largest tracked source file: 469 lines** (`work/skillranker-eval/score.mjs`). The hard trigger
is 10,000 and the soft trigger for scripting languages is 2,000–3,000. **Nothing in this repo is
within four times the soft threshold.** Per the skill's own rule — *zero files over any threshold,
report and stop* — no workspace was created, no phases run, nothing split.

## Where the mass actually is

```
docs/demos/PLAN.md                            5,448
NEGATIVE_EVIDENCE.md                          2,396
docs/demos/upstream-repro/commit-learnings…   1,928
AGENTS.md                                     1,567
docs/essays/dont-give-up-gaps.md              1,283
README.md                                       925
```

`PLAN.md` alone is **eleven times the largest source file.** The pathology taxonomy maps cleanly
onto prose:

- **`PLAN.md` — B1 god-file.** Every ruling's reasoning, appended for a week, one file.
- **`commit-learnings-20260919.md` — append-only log**, 1,928 lines, which *I* grew all session.
- **`docs/demos/upstream-repro/` — B2 grab-bag.** Receipts with no index; a reader cannot tell a
  live contract from a dead probe.

## Why the 12-phase machinery is the wrong tool here

The isomorphism contract has four legs: behavior (test suite), public API (surface diff),
performance (bench bounds), compile resources. **Three of the four are undefined for markdown.**
Running the machinery on prose would produce ceremony with a proof gate that cannot fail —
exactly the gate-that-fires-on-everything this lane refuses.

The honest equivalent is an inventory with inbound-reference proof (`rg -l '<basename>'`), which
is already in flight as a parallel agent slice.

## Ruling

- **Code: LEAVE ALONE**, with rationale — B11. It is small, tested, and the census says so.
- **Docs: DE-MONOLITHIZE**, starting with `PLAN.md`, and the README becomes the façade that makes
  the whole tree walkable.

## NO-CLAIM

Line count only, weighted by nothing. Complexity, churn and expanded size were not measured
because the size census already fell an order of magnitude short of any threshold — if a future
file crosses 2,000 lines, re-run with `lizard` and the churn weighting rather than trusting this
row. Untracked and gitignored files (the 37 top-level dirs include upstream clones that are not
ours) are excluded by `git ls-files` and were not assessed.
