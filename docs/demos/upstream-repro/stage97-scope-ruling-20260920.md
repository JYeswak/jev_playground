# Stage-97 ruling: SCOPE IT (2026-09-20)

Level: `test` (gate live + selftest, full suite both modes, all offline).

## Ruling: SCOPE IT — check numerals only for the two machine-sourced facts

WIDEN (every numeral in prose) false-positives by construction: a README
legitimately says "12" about other things. REFUSE would leave the exact escape
open: both derived facts have an exact machine source (gates.d glob,
STATUS.tsv), which is what separates them from prose — the gate's own "WHY A
GATE" criterion ("derivable in one command") already draws this line. So:

- Every `<N> gate stages` numeral must equal the gates.d count.
- Every `<N> verdict rows` numeral must equal the STATUS.tsv data-row count.
- Every `(A cleared, B held, C ruled out` parenthetical must equal the
  machine breakdown.
- Fixed-noun exact equality, never "does this number appear" — a legitimate
  "12" elsewhere cannot trip it. Free prose out of scope for ever; header
  states this.

The conductor leaned SCOPE and was right; the one thing it missed: the
breakdown parenthetical is the same fact family with the same machine source,
so it rides along rather than waiting for its own escape.

## Creation-gate paperwork (in the gate header)

Consumer: foundation/gates.sh. Gate: the three numeral patterns. Observed
defect: 2026-09-20, three stale lines through 13 green stages (numeral "12
gate stages" for 13; "25 verdict rows (7/9/8)" for 33 8/13/12, twice plus once
bare). Retirement: counts GENERATED into the README; then delete the stage.

## Verification (unpiped exits)

- `97-readme-counts.sh` live: PASS exit 0 (`13 stages stated as 'Thirteen'`).
- `--selftest`: 5 arms ok exit 0, including the new planted arm replaying the
  exact escape (`stale numerals under matching word -> RED rc=1`).
- `foundation/gates.sh` live: 13 PASS exit 0. `--selftest`: ALL GREEN exit 0.

## Ledger line

RULE stage-97 SCOPE — numerals for two machine-sourced facts, planted escape arm, 13 green both modes — NO-CLAIM: offline only; free prose explicitly out of scope.
