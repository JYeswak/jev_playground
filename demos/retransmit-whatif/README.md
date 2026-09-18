# jev-context-retransmit-backtest

Offline what-if bound for retransmitted context. It reads omp session JSONL, reports per-turn and
per-session token shares, and applies deterministic 25%, 50%, and 75% retransmit reductions.

## Run

```sh
npm run whatif -- fixtures/known-shape.jsonl --out runs/known-shape.json
```

Inputs may be `.jsonl` files or directories; directories are walked recursively. No key, model call,
or network is used.

## What the what-if assumes

For a reduction `r`, the scenario removes `cacheRead * r` tokens from each usage-bearing assistant
turn. `input`, `cacheWrite`, `output`, turn count, model behavior, answer quality, retrieval recall,
and tool-call behavior remain unchanged. This is a token upper bound, not a prediction that a real
retrieval, `top_k`, context-compaction, or turn-elimination intervention preserves quality.

The receipt prints the denominator before the levers: files, sessions, assistant turns, usage-bearing
turns, missing-usage assistant turns, and non-turn records. Source SHA-256 values, observed model
versions, the accounting unit, and the residual are preserved in the receipt. A zero-usage or
malformed corpus fails visibly; it is never a green empty run.

The synthetic fixture is a planted-positive control. It contains two assistant turns with known
`cacheRead`, `cacheWrite`, `input`, and `output` values plus one non-turn record. The test and
mutation harness must recover those values before a real-corpus figure is cited.

## Boundary

This measures token shape and scenario bounds only. It does not price a provider, prove a quality
change, or justify shipping an intervention. Any published figure must include the input lane, N,
date, and observed model versions from the receipt.
