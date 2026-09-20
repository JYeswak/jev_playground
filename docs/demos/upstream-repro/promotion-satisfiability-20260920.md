# Promotion satisfiability: SATISFIABLE (2026-09-20)

Level: `test` (offline; gate run on a /tmp TSV; real STATUS.tsv untouched).

## The conjunction, in plain words

Two layers. **PLAN.md rung 5** (substantive, judged by humans): (1) rungs 1–4
each cleared by a non-author; (2) no candidate currently promoted; (3) a named
owner who is not the conductor; (4) a stated kill criterion for the project.
**Gate 85** (mechanical, `foundation/gates.d/85-promotion-contract.sh`): (a) a
PROMOTED row names all four gate words — equivalence, capability, performance,
adversarial — somewhere in the row; (b) its receipt field points at a file that
exists.

## The synthetic candidate

A fabricated best case in `/tmp/synth-status.tsv` (never committed, never near
STATUS.tsv): rung 5, verdict PROMOTED, author pane1, receipt pointing at the
existing integrity-checked
`docs/demos/duel-2/runs/ratify-label-audit-20260918T060749Z.json`, blocked_on
naming all four gates with non-author panes, an owner, and a kill criterion.

## The gate's verdict (quoted)

```
OK  promotion-contract: synth-deserving clears 4 gates with receipt docs/demos/duel-2/runs/ratify-label-audit-20260918T060749Z.json
OK  promotion-contract: 2 row(s) scanned, 1 PROMOTED, 0 violations (promoted=0 is a valid state)
```

exit=0. **The gate fires green on a deserving candidate: it is strict but
satisfiable, not theatre.**

## The recipe (what promotion actually takes)

1. Clear rungs 1–4, each evidenced by a non-author.
2. Write the PROMOTED row with the four gate words, the non-author panes, a
   non-conductor owner, and the kill criterion in it.
3. Point the receipt at a committed file that exists.

## The honest half: closest real candidate

`UP-R12-score-register-export` (rung 4, CLEARED, author pane1) — short by four
clauses: no gate words in the row, no named non-conductor owner, no kill
criterion, no recorded per-rung non-author clearances. Clause (2) is satisfied
(promoted=0). `UP-R14-route-multiturn-labels` is further (rung 3, HELD, trap
subset below chance). So **promoted=0 is honest**: the nearest candidate is
missing nearly the whole conjunction, and the bar was cleared on demand by a
candidate that had it.

## Boundary (not a defect, but the limit of this finding)

Gate 85 is a well-formedness check: it proves the row NAMES four gates and a
real receipt, not that the gates were truly cleared — a liar could write the
words. That is by design (the creation gate targets accidental promotion, and
the substance check is the non-author rung process), so I do not weaken or
extend anything. But `promoted=0` rests on the rung process being honest, not
on this script alone.

## Ledger line

REVIEW promotion-contract — SATISFIABLE — synthetic best case promotes exit 0; nearest real (UP-R12) short four clauses — NO-CLAIM: synthetic input only, real STATUS.tsv untouched.
