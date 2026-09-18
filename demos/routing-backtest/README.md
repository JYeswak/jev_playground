# jev-route-backtest

Answers one question: **would model routing have saved money on YOUR sessions?**

Give it your omp session logs. It replays every model turn twice — once at the price you
actually paid, once at a cheap-model counterfactual — and reports the difference. Read-only:
it never calls a model, needs no API key, and makes no network requests.

## Run it

```sh
npm run backtest -- fixtures/real-excerpt-t1-t6.jsonl --out runs/try.json
```

That runs the worked example (6 turns, finishes in under a second). For your own logs, pass
one or more omp session `.jsonl` files instead of the fixture. `--out` is required so every
run leaves a receipt. Other files in `fixtures/` are intentional failure cases (unknown models,
unclassifiable turns) — start with `real-excerpt-t1-t6.jsonl`.

## Read the receipt

`runs/try.json` carries a `denominator` and a `totals` block:

```jsonc
"denominator": {"sessions": 2, "turns": 30, "classifiableTurns": 30, "skippedTurns": 0},
"totals": {"actualSpend": 7.6615, "counterfactualSpend": 7.6581, "estimatedSavings": 0.0034228, ...}
```

- `turns` / `classifiableTurns` / `skippedTurns` — what the run actually priced. A verdict over
  skipped turns is not a verdict; if `skippedTurns` is large, your logs don't fit the priced
  shape and the numbers below mean less.
- `actualSpend` vs `counterfactualSpend` — dollars at served-model prices vs cheap-model prices.
- `estimatedSavings` — the difference. Divide by `counterfactualSpend` for the percentage.

`failures` counts internal errors (not verdicts). Anything nonzero means the run itself broke;
do not quote its numbers.

## Verdict (measured 2026-09-18, price table `as_of` 2026-09-18)

On our own 30 turns: **$0.0034228 saved, or 0.0447%** (`0.0034228/7.658096908`,
counterfactual-spend basis). Upstream reports −60% on theirs; on ours, routing barely pays.

**Do not build a router on the upstream number — run this on your logs first.** If your savings
clearly beat ours, a router may pay for you; if they look like ours, it will not. Re-derive past
the price table's `as_of` date: model prices move, and a pinned verdict rots silently.
