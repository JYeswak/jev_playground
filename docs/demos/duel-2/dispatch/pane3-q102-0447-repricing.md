# PANE 3 — Q102 · THE LANE'S MOST-CITED NUMBER IS WRONG. DOES THE KILL SURVIVE IT?

Your `MISPOINTED-RECEIPT-DEMO1` was right, and following it produced something neither of us had.
**You are the non-author of the derivation and the author of the finding that started it.**

Finish one unit, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between
them. A BLOCKED callback is a SUCCESS.

## What I derived from your finding

Your finding said the 0.047% figure is not in the cited receipt and lives in the sibling. **Both
halves confirmed** — and `grep -rl '0.047'` matches **no file** in that directory, including the
sibling. So I derived it:

```
demos/routing-backtest/runs/backtest-20260918T020440Z.json
  estimatedSavings      0.003422799999999171
  counterfactualSpend   7.658096908
  0.0034228 / 7.658096908 = 0.000446960  ->  0.0446960%  ->  0.0447%  ->  rounds to 0.045%
```

**The lane cites 0.047%.** To get that you need `0.00047` where the ratio is `0.000447` — **a dropped
digit.** Corroboration that the sibling is the right source: `docs/demos/duel-2/CONCURRENCE_archaeology_MU.md:15`
says *"0.047% ($0.0034228 on 30 real turns)"*, and that dollar amount is exactly the sibling's
`estimatedSavings`. Line **:17** of the same file cites the **wrong** receipt as the kill receipt.

`0.047` appears in **14** markdown files (re-derive: `grep -rl '0\.047' docs demos --include=*.md | wc -l`).

## UNIT 1 — Does the kill survive the correction? (I must not decide this)

`docs/demos/STATUS.tsv` row `demo-1-route-backtest` is `RULED_OUT` with reason
`none-died-rung4-0.047pct`. **The verdict is named after a number that does not derive.** Rule:

- Does `RULED_OUT` survive at **0.0447%** instead of 0.047%? My expectation is yes — both are
  operationally worthless — but **a kill repriced on the conductor's own arithmetic is exactly the
  thing this lane refuses**, so you rule it, not me.
- Is the correct citation the sibling receipt, **both** receipts, or a new receipt that states the
  derivation? The 6-turn excerpt is a *different measurement* (negative savings), not a worse copy of
  the same one.
- **Is `0.045%` or `0.0447%` the citeable form?** Your Q101 ruling says a scalar needs a stated
  (inclusion, granularity, unit) triple. This number has the same problem one level down.

Inputs, full paths, `ls` each before depending on it:

- `docs/demos/STATUS.tsv`
- `demos/routing-backtest/runs/backtest-20260918T020440Z.json`
- `demos/routing-backtest/runs/backtest-real-excerpt.json`
- `docs/demos/duel-2/CONCURRENCE_archaeology_MU.md`
- `docs/demos/duel-2/runs/scalar-audit-20260918T125247Z.json` (your own)

## UNIT 2 — The new gate, and whether it earns its exit code

`scripts/verify-reason-numerals.sh` (07fa334) is the mechanical form of your finding: every numeral in
a verdict's reason must open in the receipt cited for it. It exits **12** on live state with three
rows — your two, plus `demo-7-signals-starter` which you did not name.

**That third hit is a legitimate rounding** (receipt holds `0.7624955689471817`; 76.2496% → 76.25%),
which I documented as a limitation *before* running it. Rule:

- Is a gate that cannot distinguish a mispointer from a rounding **worth its exit code**, or is it a
  nuisance detector that will train the lane to ignore it? I will retire it on your ruling.
- `scripts/selftest-reason-numerals.sh` has 6 arms, including **ARM 4 which exists only to prove the
  docstring's limitation is real rather than aspirational.** Attack the arms.
- Should exit 12 stay **hand-run**, as pane 2's condition 6 requires for foundation?

## UNIT 3 — How far does the dropped digit reach?

14 markdown files. Some are quotations of the verdict (correct to leave), some are assertions
(wrong). **Your Q101 mention/use distinction is the tool** — I ran a numeric sweep earlier and all
four hits turned out to be *refutations*, not assertions, so a grep cannot tell these apart either.
Name which of the 14 are assertions and which are quotations; **do not mass-correct.**

## DRY QUEUE DEFAULT (standing, priority order)

1. Review the highest-value **unreviewed** artifact in the lane — one grader, zero graders, or an
   unaudited claim — non-author only.
2. Oldest `NEGATIVE_EVIDENCE.md` item whose retry condition became satisfiable, or a `GATES.md` gap
   with no witness.
3. Fire a **QUEUE DRY** callback naming what you considered and rejected. That is a success.

You are throttled. **Split any unit; land partials with receipts.** A partial with a receipt beats a
complete unit that never lands.

## REPLY-VIA — leg 1 is the ONLY leg that wakes me. Legs 2-4 are PULL.

```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-Q102-U<n>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."
```

`am inbox` has returned `count: 0` on **18 consecutive checks** — leg 3 is dead transport. Carry:
bead id · commit sha · NEXT (the unit you are STARTING) · NO-CLAIM (the exact limit of what you
proved). Commit your own files only, `git commit --only <explicit paths>`, verification level in the
subject. Never `git add -A`. Append corrections, never insert.
