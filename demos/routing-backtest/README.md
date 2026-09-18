# jev-route-backtest

Answers one question: **would model routing have saved money on YOUR sessions?**

Give it your omp session logs. It replays every model turn twice — once at the price you
actually paid, once at a cheap-model counterfactual — and reports the difference. Read-only:
it never calls a model, needs no API key, and makes no network requests.

Requires Node.js 20 or newer (`node --version`; package.json `engines`). No dependencies to install.

## Run it

```sh
npm run backtest -- fixtures/real-excerpt-t1-t6.jsonl --out /tmp/rb-try.json
```

That runs the worked example: 6 turns, 1 session, `muse-spark-1.3-contributor` only
(illustrative fixture, not a measurement — your logs are the measurement). It finishes in
under a second on the author's machine (0.2–0.4s measured). For your own logs, pass one or
more omp session `.jsonl` files instead of the fixture — they live under your omp profiles
directory (e.g. `~/.omp/profiles/*/agent/sessions/*/*.jsonl`). `--out` is required
so every run leaves a receipt. Other files in `fixtures/` are intentional failure cases
(unknown models, unclassifiable turns) — start with `real-excerpt-t1-t6.jsonl`.

## Read the receipt

`/tmp/rb-try.json` carries a `denominator` and a `totals` block. The fixture run emits
something like (yours will differ — this is 6 turns, not our 30-turn measurement below):

```jsonc
"denominator": {"sessions": 1, "turns": 6, "classifiableTurns": 6, "skippedTurns": 0},
"totals": {"actualSpend": 0.0111, "counterfactualSpend": 0.0129, "estimatedSavings": -0.0018, ...}
```

- `turns` / `classifiableTurns` / `skippedTurns` — what the run actually priced. A verdict over
  skipped turns is not a verdict; if `skippedTurns` is large, your logs don't fit the priced
  shape and the numbers below mean less.
- `actualSpend` vs `counterfactualSpend` — dollars at served-model prices vs cheap-model prices.
- `estimatedSavings` — the difference. Divide by `counterfactualSpend` for the percentage.
  (Negative here is fine — the 6-turn fixture is a shape demo, not a verdict.)

`failures` is a list of internal errors (not verdicts). A non-empty list means the run itself
broke; do not quote its numbers. `[]` is the healthy state.

Write `--out` outside the repo (`/tmp/`, a scratch dir). `demos/routing-backtest/runs/` holds
committed receipts other documents cite — do not leave trial files beside them.

## Verdict (measured 2026-09-18, price table `as_of` 2026-09-18)

On our own 30 turns (30 classifiable of 30 seen, 2 sessions; 17× `gpt-5.6-luna`,
13× `muse-spark-1.3-contributor`, per-model counts in the receipt): **$0.0034228 saved, or
0.0447%** (`0.0034228/7.658096908`, counterfactual-spend basis). Upstream reports −60% on
their 237 turns (`jev-codex-router@8292b51`); on ours, routing barely pays.
Scope: this prices the SAME turns at a cheaper model. It does not measure turn reduction —
a tool that deletes turns (fewer re-sends of the full context) plays a different lever this
does not price.

**Do not build a router on the upstream number — run this on your logs first.** If your savings
clearly beat ours, a router may pay for you; if they look like ours, it will not. Re-derive past
the price table's `as_of` date: model prices move, and a pinned verdict rots silently.
