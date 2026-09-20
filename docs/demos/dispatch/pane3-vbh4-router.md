# P3 — `jev-vbh.4` usage-router-active: the dependency landed, so it is unblocked

`jev-eww` closed and it **overturned my prediction** — I said 30 turns would confirm the
refutation; both questions cleared their own constant at n=32 (`24 > 16+4`, `21 > 16+0`). Your
labels-before-scores discipline and the pinned turn set are what made that credible rather than
suspicious. The traps kept as named subsets are what keeps it honest: `trap-short` needs 1/6,
mech 0/6 — below a coin flip — so the aggregate is carried by clear cases.

**Do not treat route as rescued.** The correct summary is *separates easy cases, fails hard ones*.

## Why this bead is now workable

It was gated on the skillranker abstention work. **That landed**: PRs #26 and #27 are MERGED and
`work/skillranker-eval/` holds `score.mjs` plus the frozen contract
(`evaluation_policy.v1.json`, `expected_values.v1.json`). I verified by reading the tree, not the
PR titles. So the abstention mechanism exists and does not need inventing — §5's lesson.

## Unit

`usage-router-active`: shadow → active, with kill switches, and the `action` field honoured.

**Start from what is already measured, and do not re-derive any of it:**

- Route is REFUTED as a product at n=10 and **separates-easy-fails-hard** at n=32
  (`eww-32-turns-20260920.md`). An active router built on a question that fails `trap-short`
  below chance needs its abstention path to carry the hard cases, not its judge.
- The skillranker contract's own finding: **always-abstain scores 10/12 = 0.833**, and a coin
  flip does worse than abstaining. Abstention is a strong baseline — any active router must beat
  *always-abstain*, not merely beat random.
- `docs/RULES.md` rule 4: near-threshold count before prevalence.

**ACCEPTANCE:** shadow mode measured against always-abstain on the 32 pinned turns, with the
kill switch demonstrated firing, and a written ruling on whether `action` should ever be honoured
live. **REFUSE is full credit** — "an active router cannot beat always-abstain on this question"
is a defensible product ruling and, given `trap-short`, the likeliest one. I was wrong predicting
the likeliest outcome last time, so weigh that accordingly.

## Constraints

- Live calls fine; pin the turn set and record the model version.
- Nothing goes active. Shadow only; this lane's promoted count is 0 and stays there.
- Commit on create; test file + `TESTS.md` entry in the same commit; exit codes unpiped.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-VBH4-<DONE|REFUSED|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
