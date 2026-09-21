# Sensitivity bar — written before any call

Model pinned: `jev-1.13.0`. Not `jev-latest`.

State selection, fixed now, before opening the row: the first row in
`work/nev-injection/live-rows.jsonl` that records a numeric `noul` for a named
question. That recorded noul is the known answer. The state sent is that row's
state, unchanged.

Material: absolute noul shift greater than 0.05, or a choice label that changes.
A choice question is not used here. The known answer is a noul.

## What each outcome means, before any number

- Nothing moves (every paired delta at most 0.05, no label change): stable on
  this one state. Not a stability guarantee. Record it as stable-on-this-state.
- Batch composition moves: fan-out is unsound on this evidence. Parallel
  questions are not independent until the shift is characterized.
- Wording moves: the question text is part of the measurement. One phrasing is
  not the question.
- Both move: both constraints bind.
- An arm errors: that arm is UNMEASURED, not stable.

NO-CLAIM, written now: n is small, one model version, our states. A stable
answer here is not a stability guarantee.
