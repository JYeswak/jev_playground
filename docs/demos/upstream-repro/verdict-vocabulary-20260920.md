# Verdict vocabulary: two axes, not one — 2026-09-20 `[receipt]`

**Ruled: separate them.** Callback words (`DONE|HELD|REFUSE|BLOCKED`) and
STATUS words (`CLEARED|HELD|RULED_OUT`) are two different things wearing
one slot. Merging is refused; the closure carries both, each enforced.

## Argument

`DONE` means *the unit finished*; `CLEARED` means *the claim survived*.
Evidence from my own demo closures, which mistranslate 2 of 3:

| closure | old (one slot) | canonical (two slots) | lost in translation |
|---|---|---|---|
| a11-join | HELD | HELD / DONE | none (the overlap that hid the problem) |
| a12-refusal | REFUSE | RULED_OUT / DONE | rule-vs-approach: REFUSE could equally mean the unit failed |
| dig-repframe | DONE | CLEARED / DONE | everything: DONE says nothing about the claim |

A DONE callback routinely carries HELD and REFUSE findings (tonight:
CASSMINE-HELD, CASSMINE-REFUSE) — the callback word already modifies the
unit in practice. The STATUS slot modifies the claim. One slot cannot hold
both without the 2/3 loss above, so this is separation, not renaming.

## Measurement (tonight's callbacks, recalled session counts, flagged)

Roughly: DONE ~20 (unit finished, findings various), HELD ~4, REFUSE ~5,
BLOCKED 0–1. Every HELD/REFUSE callback was a DONE unit carrying a
finding — consistent with two axes, and with the mistranslation table.
Recalled, not mined: direction unanimous, counts approximate.

## Enforcement

`emit.mjs` accepts only `CLEARED|HELD|RULED_OUT` for `--verdict` and only
`DONE|BLOCKED` for `--outcome` (both required, both refused otherwise).
The STATUS projection renders the claim verdict; the 10-column schema is
frozen, so unit outcome lives in JSON. Selftest arms: old word in verdict
slot refuses, canonical pair passes (6/6 green).

## NO-CLAIM

Ruling about our own vocabulary, argued from 3 demo closures + recalled
counts. If a future unit's outcome needs a third word (e.g. deferred),
extend the set with a receipt, not by improvisation — that sentence is
the whole point of this ruling.
