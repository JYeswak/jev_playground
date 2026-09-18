# preaction-abstention — thin proof (COD-H2, rung 3)

Pre-action gate with three outcomes where the incumbent has two: **pass /
withhold / escalate / block** (withhold distinct from error-block),
calibrated confidence with coverage semantics, human-routing outcome.
Scope: destructive-bash turns only (rung-3 narrowing, 907 turns).

## Install

Zero dependencies, Node 20+. No install step:

```sh
node --test test/          # offline suite, injected asker, $0
node src/run.mjs --cases fixtures/cases.jsonl --asker canned --out runs/
```

Live lane (budgeted, stated): `TYPESAFE_API_KEY` in environment, then
`--asker jev`. Records model version + call count in the receipt.

## Policy

`policy.json` is pre-registered (thresholds, block list, question text,
model pin `jev-1.13.0`) and moves only by calibration procedure with a
fresh receipt — never edited to make a run green.

## Receipt

`runs/abstention-gate-<ISO>.json`: per-case verdicts, outcome
distribution, withhold rate, Jev calls + model version (0 in offline
lane), RED-arm results, failures.
