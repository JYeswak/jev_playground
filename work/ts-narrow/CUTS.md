# R148 per-family cuts: recovery status (jev-dr4p, for HazySpring)

## Original values: UNRECOVERED
Searched 2026-10-02: all of `var/agent-tmp/dr4p-feas.34880/*.py` (`widelive.py`,
`widesample.py`, `wideprep.py`, `sample*.py`, `live.py`) and every `*.json*` in that
dir. `widelive.py` applies NO cut (records raw choice/confidence only); no fitting
script exists. The R148 numbers (held interruptions=34, misses=2) cannot be exactly
recomputed from committed+v1 artifacts because v1 receipts lack probabilities.
Downgrade noted: the cut-dependent part of R148 is verifier-unreproducible as run.

## What IS recomputable
`work/ts-narrow/wide_rows.jsonl` (108 rows: h, split, idx, label, rules, family,
answer, probabilities, confidence, status, tokens, model jev-1.13.0, seed
`wide-v2-rerun`). v2 reran the identical question/state (108 fresh calls ~$0.0034,
0 transport errors); modal votes match v1 on 108/108. Join key verified: label `i`
indexes the non-censored episode list (56/56 dev ts-match).

## REFIT (labeled, NOT the original)
Rule: per covered family, smallest cut keeping all DEV v2 applicables
(`max p_inapplicable over A + 1e-6`); families without dev coverage default 0.5.
- cuts: glob 0.480001, pipe 0.470001, ts 0.0 (ts dev 29/29 inapplicable: suppress all)
- uncovered (misc, kit, shell): 0.5
- outcome on v2 votes: dev 27 interruptions / 0 misses; held 27 / 5 misses.

## Unconfirmed hypothesis (speculation, not evidence)
"0.75 on covered families + 0.5 default" (0.75 was the confirmation-phase cut)
gives held 29/3 on v2 votes vs reported 34/2 on v1. Close but not reproducing;
v1 probabilities are gone, so this cannot be settled. Do not cite as the rule.
