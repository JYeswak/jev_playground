# measure-kit: one verdict arithmetic, route ported with identical numbers (2026-09-19)

## Kit

`work/jev-client/measure-kit.mjs` (name kept: it lives beside the asker every measure
script already imports, and "kit" is what the unit asked for). Exports `gradeQuestion`
(pure: correct, said-yes, truth-yes, own best constant, spread, near-threshold count,
verdict) and `measure` (live driver: run-1 rows, drift with flips, standard table).
Verdict rule as settled, with the near-threshold penalty the early units lacked:
DISCRIMINATES iff correct > best_constant + near_count, else WEAK, same-verdict
DEGENERATE. A kit standardises the arithmetic, not the cases.

## Port proof (route measure.mjs, the script I know best)

Same cases, same questions, same trap, same NO-CLAIM — only the loop moved into the kit.
Before (original run): needs_heavyweight 8/9 (scores .91 .93 .91 .90 .11 .62 .23 .22
.10), mechanical 8/9 (.14 .07 .10 .13 .85 .14 .98 .96 .95), pooled 16/18, both
DISCRIMINATES. After (this run): identical score sets to two decimals (what-does 0.64 /
0.14 both times), pooled 16/18, near 0 both, both DISCRIMINATES under the stricter rule.
Same numbers; only the verdict line gained the near count.

## Tests

`work/jev-client/test/measure-kit.test.mjs` (4/4 offline): planted constant → DEGENERATE
despite 6/7; planted one-item margin with a near decider → WEAK (the 010dd96 correction
as a test); clear separator → DISCRIMINATES; fake-ask driver counts 1 flip and 3 errors.
TESTS.md entry in the same commit. `foundation/gates.sh` ALL GREEN after the edit.

## NO-CLAIM

A kit standardises the arithmetic, not the cases — the case sets remain the weak link
and this does nothing about that. Other measure scripts deliberately unported this round.
