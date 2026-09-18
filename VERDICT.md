# Verdict: 17 ideas, 0 promotions — and why that is the honest headline

*For a reader who has never heard of this lane. Every number below traces to
`docs/demos/STATUS.tsv` (the machine-readable state of record, 17 rows) or to
the receipt file named with it. Run `./scripts/lane-status.sh` yourself: on
2026-09-18 it reported 17 candidates, 17 receipts present, 17 integrity-checked.*

A group of engineers spent days asking one question about seventeen demo ideas
built around Jev (a judgment API: your code sends state plus typed questions,
it returns constrained answers with probabilities — it never generates text).
Each idea climbed a five-step ladder — **rungs**, defined in `STATUS.tsv`:
0 unscored, 1 real demand, 2 Jev-shaped mechanism, 3 thin proof, 4 measured
lift, 5 promoted. **Nobody reached rung 5.** The highest anyone climbed is
rung 4, and two of the three ideas that got there died there.

Three verdicts exist. **CLEARED** means an idea passed its current rung (5
ideas). **HELD** means it is blocked on one named condition, with the retry
written down (8 ideas). **RULED_OUT** means it was killed, with the killer
named — kills by a *non-author* (someone other than the proposer) carry extra
weight here, marked below. Scores are 0–1000 judgments, not measurements.

## The headline first: why zero is correct, not disappointing

Two separate mechanisms produced the zero, and both are working as designed:

1. **Two ideas died at rung 4 that should have died at rung 2** — after the
   expensive work was already paid for. That waste produced the lane's
   standing rule (estimate rung 4 *before* paying for rung 3), which then
   killed the next candidate in an hour for zero dollars. The gauntlet got
   stricter because it was too loose, and the zero is partly the strictness
   working.
2. **Eight ideas are HELD, not dead** — each waits on one specific thing
   (a corpus, a measurement, a head-to-head). A promotion today would mean
   promoting past a named blocker, which is exactly what the process exists
   to refuse.

## The four kills (strongest treatment — a kill is the most defensible thing here)

**demo-1, route backtest (score 520, died rung 4).**
The flagship: replay recorded traffic through a cheap-model router and measure
the savings. It shipped — then a non-author opened the code and found it
makes **zero Jev calls**: routing is decided by a hand-written token
heuristic, and the measured lift was 0.0447% ($0.0034 on 30 real turns;
`demos/routing-backtest/runs/derivation-0447-20260918T134500Z.json`). A Jev
demo with no Jev in it. Death recorded in the cross-pane concurrence file
(`docs/demos/duel-2/CONCURRENCE_archaeology_MU.md`). Lesson, now law: price
the top rung before building the middle ones.

**MU-H1, TODO-judge (score 820, killed rung 4).**
The best idea anyone filed: judge whether a TODO comment is still *true*, in
calibrated batches with receipts. Cleared rungs 1–2, led the board — then a
one-hour census by a non-author counted the reachable world:
`docs/demos/duel-2/runs/muh1-marker-census-20260918T034820Z.json` found **17
markers in 283,786 lines across 16 repositories** (13 repos have zero; one
repo holds 70%). Batch judgment over hundreds of markers needs hundreds of
markers, and they do not exist here. Retry is deliberately narrow: show
≥5 large old repositories with marker density 17× higher, and it re-opens
(`NEGATIVE_EVIDENCE.md` R14). Refuted: *"a judgeable marker population in the
code we can reach"* — not *"nowhere."*

**COD-H3, price-drift auditor (score 890, killed rung 2).**
Real pain (a verified 262% billing excess with a repro), highest demand score
on the board — and no Jev-shaped mechanism. Decomposition showed **4 of 5
stages need no judgment model** (parse, detect, attribute, refuse); the single
Jev stage classifies what a committed capability table already answers. The
fork it could not avoid: need judgment and it becomes a router competing with
RouteLLM head-on with no wedge (the gap only it can fill — never filed), or
not, and the shipped artifact contains zero Jev calls, which is demo-1's
shape again. Killed pre-build for the cost of a table
(`docs/demos/duel-2/RUNG2_COD-H3_resolved_MU.md`, `NEGATIVE_EVIDENCE.md` R15).
Two retry tracks keep everything valuable, in two separate artifacts.

**demo-8, credential screen (score 100, killed rung 1).**
Both panes agreed: asking a remote judge whether raw credential content looks
suspicious has already crossed the security boundary — local scanners plus
demo-2 cover the safe needs. Lowest score on the board and the fastest kill
(`docs/demos/duel-2/DEMAND_SCORES_COD_ON_MU.md`). Some ideas die because the
world lacks their input; this one died because it should not exist.

## The five that passed their rung (CLEARED — alive, unpromoted)

- **demo-2, admission screen (700):** demand recovered — a named engineer
  replaced the README narrative (`docs/demos/duel-2/HELD_demo2_demand_COD.md`).
- **demo-5, fact ledger (755):** rung 3 waits on hunt scores.
- **COD-H5, compaction integrity (895):** ownership resolved (tester distinct
  from subject); queued behind COD-H2.
- **MU-H2, outbound redaction (430):** conditional pass — must beat a
  six-threshold gate (calibration ECE ≤ 0.10, Brier ≤ 0.15, +20pp recall).
- **MU-H3, runtime redaction (650):** conditional — unknown-credential cases
  only, where entropy tops out at 41.7% precision with no operating point.

## The eight on hold (HELD — each blocked on exactly one named thing)

- **demo-3, claim-check gate (430):** rung-3 head-to-head designed; ships at
  +30pt lift. **demo-4, foreman-lite (820):** withdrawn standalone, kept as a
  COD-H1 integration. **demo-6, claim-check notes (330):** incumbent search
  closed with no owner; held on demand, not structure. **demo-7, signals
  starter (560):** repriced (3.5pt method) and scope-narrowed to the top two
  signals' 76.25% weight share. **demo-9, review signal (550):** skip rung 3
  for now; priced at 1–2 engineer-days, retry at +20pp recall.
- **COD-H1, snapshot completion (885):** *unaskable* — the corpus has 2 of 30
  transcripts across 3 harnesses; retry on sourcing, not on method.
  **COD-H2, pre-action abstention (905):** rung-4-unaskable — one blocker fails
  at 25% judge agreement; phase 1 narrows to a single locally-reversible
  clause. **COD-H4, tool-result replay (900):** unaskable — corpus absent
  (4-hour build priced); the deferral is scheduling, not a blocker.

(*Unaskable* = the question cannot be fairly tested yet, usually for lack of
test material. It is a verdict on readiness, not on merit — note the 905 and
the 900, the two highest scores on the board, both sit here.)

## What would change the zero

Any one of: a legacy corpus re-opens MU-H1; a misclassification fixture
re-files COD-H3's router fork; COD-H2's agreement blocker clears; a head-to-head
lifts demo-3 thirty points. The retries are written into each row — that is
what HELD means. Until then, zero promotions is not a backlog embarrassment.
It is a gauntlet that refused four bad ships and priced eight maybes.
