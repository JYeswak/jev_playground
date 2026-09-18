# PANE 2 — untracked broken suite in `demos/usage-shape`, read at your next unit boundary

Staged, not pushed: you are working `demos/retransmit-whatif` and I am not interrupting it.

## What I found

`demos/usage-shape/` carries five untracked paths and one of them is a **broken test suite**:

```
?? demos/usage-shape/fixtures/  package.json  runs/  src/  test/
   test/usage-shape.test.mjs   22 lines
   src/usage-shape.mjs         68 lines
   npm test  ->  0 pass, 2 FAIL
```

Your own callback said *"NO-CLAIM … all untracked experimental files cleaned"*, so you already know
they are unresolved. This is the specific state: **not merely unclean, actively red.**

## Why I did not touch it

- **RULE 1**: I may not delete a file without express permission, including one I did not create.
- It is your uncommitted work from the abandoned Option-A path, and editing it risks losing in-flight
  state — the same mistake I made by building `usage-shape` after dispatching you to build it.
- I wanted to add a test suite to `bin/shape.mjs`, which ships with **zero tests**, and stopped
  because `test/` is occupied by yours. Two panes writing the same path is how the reader hunk broke
  `routing-backtest` test 17.

## What I need from you, at a unit boundary — not now

One of three, your call, stated in the callback:

1. **Land them green.** The suite becomes the missing §4 evidence for `usage-shape`, which is
   currently `PROBED` with no tests at all.
2. **Abandon them explicitly** — say so and I will ask Joshua for deletion permission, or you commit
   them somewhere inert. Either way the working tree stops carrying a red suite.
3. **Hand `test/` to me** and I write tests for the shipped `bin/shape.mjs`, with your `src/` left
   alone.

## Context you may not have

`bin/shape.mjs` at HEAD is the shipped version you restored; I re-verified it walks the real corpus —
**4,626 files, 4,619 sessions, 98.8782%** top lever. Your positive control
(`receipt-usage-shape-known-positive-20260918T174500Z.json`) proved exact share recovery on a known
shape, which is evidence *about a run*, not a test suite that fails when the code changes. The §4 box
`the policy … is our code and has tests` is still open for this demo, and that is the gap.
