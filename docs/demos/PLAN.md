# docs/demos/PLAN.md — the demo backlog

**WIP limit: one.** No second demo starts before the active one ships.

**A demo has shipped when all four exist:** an install script a stranger can run · tests including
at least one RED arm that fails on a planted defect · a receipt JSON with inputs, counts and a
`failures` array · an `EVAL.md` row naming its verification level and its Boundary.

---

## ACTIVE — demo-1: `jev-route-backtest`

**What.** A read-only CLI that replays our own omp session logs and reports what per-turn model
routing *would have* spent versus what we actually spent. It answers "would routing have saved us
anything on OUR turns" before anybody builds live rerouting.

**Why this one first.** Highest agreement in the duel: 4 graders, mean 853.8, range 45, and both
lineages proposed it independently (`DUELING_WIZARDS_REPORT.md` §8). CC-5 scored 14.7 higher but
carries a 410-point sibling disagreement on the same seam — an unsettled implementation is exactly
what a first demo must not be. And it is **read-only with inputs already on disk**, so it produces
its evidence with zero live calls. That matters more than it looks: the lane's one live measurement
turned out to be a coin flip (`NEGATIVE_EVIDENCE.md` R11).

**Ship criteria, beyond the four artifacts.**
- Reports **arm A absolutely**. No `verdict` string over a stochastic arm — R11 and
  `jev-demo-loop-a1q.3`.
- A missing per-model price entry is an **ERROR, never a `$0` row.** MU-1's best RED arm.
- The price table carries a dated `as_of` and a re-derivation path. Pinned dollar figures rot
  silently; our own doc review flagged that class at stale-risk 2+.
- The model that actually served each turn is a **baseline, not an oracle.** It is the incumbent
  policy's choice, not ground truth for what the turn needed.
- Receipt states its denominator: how many turns, over which sessions, and how many were skipped
  and why. An empty scan set is an ERROR, not a pass.

---

## QUEUED — 7 remaining demos, ranked

The duel produced **8 distinct demos**, not 5 — two merged pairs plus four separate
implementations of two shared seams plus two cross-shortlist demos
(`DUELING_WIZARDS_REPORT.md` §1, corrected on pane 2's audit).

| # | Demo | graders | mean | note |
|---|---|---:|---:|---|
| 2 | admission screen — **CC-5 form** (injection-only, shadow-first) | 2 | 867.5 | merge with MU-2's install rigor; **the merged form is unscored** and must be graded before it ships |
| 3 | claim-check — **CC-2 form** (commit-message gate) | 2 | 835.0 | adopt MU-4's *insufficient-context ⇒ withhold, never approve* |
| 4 | foreman-lite completion judge | 2 | 812.5 | best RED arm in the duel: empty diff ⇒ human-needed, never complete |
| 5 | fact ledger | 2 | 792.5 | premise **strengthened** by R11: arm A scored 1/3 in all three runs |
| 6 | claim-check — MU-4 form (notes vs evidence dir) | 2 | 767.5 | distinct from #3; **build one, not both** |
| 7 | signals starter | 4 | 712.5 | gate is now a **property**, not a count: pinned generator or published distribution, never "N≥50 receipts" (R11) |
| 8 | admission screen — MU-2 form (credential, fail-closed) | 2 | 545.0 | **the credential branch is deleted, not fixed.** Conceded by its author |

**Killed:** MU-2's credential question. Asking Jev whether content carries credential material
requires shipping the credential to a third-party API — the hook would leak what it exists to
protect.

**Blocked on evidence, not on effort:** every mean above rests on 18 pinned community-repo
citations that are **not vendored**, so 37 of 60 numeric claims are unverifiable in-repo
(`jev-demo-loop-a1q.2`). Ranking is usable; the absolute numbers are transcriptions.
