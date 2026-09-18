# PANE 3 — Q104 · CLOSE THE THREE OPEN NUMERAL HITS, OR RULE THEM UNCLOSEABLE

Your own ruling made these blocking: *"hits require pane rulings: an unruled hit re-fires every run.
Without prompt rulings this becomes **nagware-by-accumulation** — process requirement, recorded."*
Three are open. You wrote the process requirement; this is it firing on you.

Finish one unit, fire its callback, then start the next YOURSELF. A BLOCKED callback is a SUCCESS.

## First: the gate got one wrong, and the fix changed your inputs

Your Q102-U1 remedy was applied (`86b0a8d`): row `demo-1-route-backtest` now cites
`demos/routing-backtest/runs/backtest-20260918T020440Z.json`, reason `none-died-rung4-0.0447pct`,
digest re-pinned. **Then the hit closed for the wrong reason** — `0.0447` was matching
`0.044756498000000006`, a per-turn **dollar** amount in an unrelated field. A substring is not an
opening. Matching is now digit-bounded, which **re-opened demo-1 and exposed a fourth hit**:

```
UNOPENABLE demo-1  '0.0447'  — the percentage is DERIVED from the receipt's fields, never stated
UNOPENABLE demo-7  '3.5'     — NEW; was matching 3.53, a different number
UNOPENABLE demo-7  '76.25'   — legitimate rounding of 0.7624955689471817
UNOPENABLE MU-H1   '283'     — KLOC never stored in the census receipt
```

Re-derive, do not read that list as a result: `./scripts/verify-reason-numerals.sh`.

## UNIT 1 — demo-1: a derived number has no literal home. Rule the form.

Your MU-H1 remedy language was *"store the total in the receipt or cite the derivation."* demo-1 is
now the same shape: `0.0447pct` is arithmetic over `estimatedSavings` and `counterfactualSpend`, not
a stored field. Options, and I am not choosing:

- reason cites the **stored** quantities instead of the derived percentage;
- reason keeps the percentage and a **derivation receipt** is written that states it;
- the gate is taught that a derived value is a different category from a cited one — **which would
  weaken it**, and you already ruled its scope limits are limits, not defects to wave away.

Your Q101 ruling applies one level down: a scalar needs a stated (inclusion, granularity, unit)
triple. `0.0447pct` has an implicit denominator choice — savings over **counterfactual** spend, not
over actual. Nothing states which.

## UNIT 2 — demo-7 and MU-H1

`demo-7` has two hits now. You already ruled `76.25` a legitimate rounding **plus a unit change**
("percent cited, fraction stored") with remedy *"rewrite reason to stored form or rule-and-record —
either closes it; silence does not."* `3.5` is new and is **not** a rounding: it was a substring of
`3.53`. Rule both.

`MU-H1` `283` is your own `KLOC-NOT-STORED`. Its receipt is another pane's artifact — say whether the
remedy belongs in the receipt or in the STATUS reason, and **do not edit another pane's receipt.**

## UNIT 3 — the 13 assertion sites you named and did not touch

`docs/demos/duel-2/runs/0447-site-table-20260918T130926Z.json` (608adcd) classified 13 assertions and
3 quotations, touching none. With the number now ruled and STATUS corrected, say which of the 13 are
**safe to correct mechanically** and which need their author. Corrections append; a same-line-count
in-place replacement renumbers nothing and is permitted.

Inputs — `ls` each first:
`docs/demos/STATUS.tsv` · `scripts/verify-reason-numerals.sh` ·
`docs/demos/duel-2/runs/numerals-gate-ruling-20260918T130736Z.json` ·
`docs/demos/duel-2/runs/0447-site-table-20260918T130926Z.json` ·
`docs/demos/duel-2/RULE_demo1_repricing_MU.md` ·
`demos/routing-backtest/runs/backtest-20260918T020440Z.json`

## DRY QUEUE DEFAULT (priority order)

1. Highest-value **unreviewed** artifact — one grader, zero graders, or an unaudited claim;
   non-author only.
2. Oldest `NEGATIVE_EVIDENCE.md` item whose retry condition became satisfiable, or a `GATES.md` gap
   with no witness.
3. **QUEUE DRY** callback naming what you considered and rejected. That is a success.

Throttled: split any unit, land partials with receipts.

## REPLY-VIA — leg 1 is the ONLY leg that wakes me. Legs 2-4 are PULL.

```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-Q104-U<n>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."
```

`am inbox` = `count: 0` on **19 consecutive checks**; leg 3 is dead transport. Carry bead id · sha ·
NEXT (the unit you are STARTING) · NO-CLAIM. Commit your own files only,
`git commit --only <explicit paths>`. Never `git add -A`.
