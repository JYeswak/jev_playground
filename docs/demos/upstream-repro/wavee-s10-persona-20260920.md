# §10 adopt persona-clone + delta — PASS (2026-09-20)

Level: `test` (3/3 offline) + live demo run (deterministic, no model calls).

## Adopted (not authored)

`~/.agents/skills/persona-clone/references/eval_harness.md`: separate judge
(PersonaGym), golden (answerable; false-negative = retrieval bug) vs trap
(unanswerable → REFUSE; TRAP-LEAK named), brace-free judge lines, eval_report.txt,
grind loop, prompt-echo pitfall. Gap verified by grep (0 hits for
constant|baseline|random|majority|join).

## Delta (the only thing built)

`work/jev-persona-eval/`: ADOPT.md, demo.mjs, adopt.test.mjs (3/3).
Demo output (quoted live row): `join: matched=4 zeroHit=false` /
`TRAP-LEAK rows: 1 (t1)` / `corpus-source join: matched=3` /
`ownConstant: true=0.667 (2/3)` / `randomBaseline: accuracy=0.333`.
Prevalence: toy golden truth 2/3 — UNKNOWN population, mechanics only.

## Ledger line

SECTION 10 random-judge + outcome-join — PASS — join 4 + TRAP-LEAK t1 + constant 2/3 + chance 1/3, 3/3 tests — NO-CLAIM: toy mechanics; adopted pattern unjudged here.
