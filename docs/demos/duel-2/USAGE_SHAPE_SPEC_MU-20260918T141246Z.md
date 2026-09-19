# USAGE-SHAPE SPEC (pane 3) — which lever pays most on YOUR sessions

**Status:** specification only, no implementation in this unit.
**Creation-gate four:** consumer = anyone about to spend on an agent-cost intervention without
knowing their usage shape; enforces no gate (measurement tool, backtest-sibling); observed defect
= our rung-4 under-scoping (backtest priced model substitution while ~99% of our billed input was
retransmission — levers-ruling-20260918T140638Z.json); retirement = superseded by a better census.

## What it answers

Not "would THIS intervention pay" but **"rank the levers by billed share so you know which
intervention to price first."** The backtest answers one row of this table expensively; this tool
draws the whole table for $0 before anything is priced.

## Inputs

Same reader as the backtest: one or more omp session `.jsonl` files
(`~/.omp/profiles/*/agent/sessions/*/*.jsonl`), assistant `message.usage` objects. No key, no
network, offline. CLI mirrors the sibling:

```sh
npm run shape -- <session.jsonl>... --out runs/shape.json
```

`--out` required (every run receipted, backtest convention).

## Lever table (emitted per turn, per session, and aggregate)

Levers defined operationally on observed `usage` fields — `input`, `output`, `cacheRead`,
`cacheWrite`, `cost.total` where present:

| lever | definition | intervention it prices |
|---|---|---|
| RETRANSMIT | `cacheRead` — context re-served, not re-read | turn elimination, retrieval plugins, context avoidance |
| FRESH | billed input minus retransmit (see accounting rule) | prompt compression, smaller context windows |
| OUTPUT | `output` — generated tokens | cheaper serving models, shorter completions |
| CACHEWRITE | `cacheWrite` — what was banked for reuse | cache policy tuning |
| UNRECONCILED | billed total minus the sum above, signed | nonzero means the field semantics drifted — a finding, not a plug |

**Accounting rule (anti-tautology):** the table MUST balance against the billed total with the
UNRECONCILED row shown, never absorbed. If `input` already excludes cache in some provider
schema, FRESH double-subtracts — so the tool derives the relation per schema from observed
fields and STATES which accounting it used (`input-includes-cache: true/false/unknown`).
`unknown` forces UNRECONCILED to carry the ambiguity visibly rather than guessing.

**Shares:** each lever ÷ billed total, per turn and aggregate; table emitted SORTED (deterministic
sort, not judgment). **No verdict string** (R11: a one-word verdict over a distribution is the
defect) — the ranking IS the output; the reader decides what to build.

## Denominator (required, mirrors backtest)

`sessions`, `turns` (assistant messages), `turnsWithUsage`, `turnsWithoutUsage` (no usage block —
the analogue of skippedTurns; a verdict over unmeasured turns is not a verdict), `tokensUnattributed`
share. If `turnsWithoutUsage` dominates, the ranking is UNRELIABLE and the receipt says so.

## Receipt conventions (backtest-mirror)

`{schema, generated_at, inputs: [{path, sha256}], denominator, accounting, levers, failures}`.
`failures` is a LIST (`[]` healthy). Inputs hashed so a re-run is checkable. No model calls, no
temperature, no stochastic arm anywhere in the tool — the only variance is the input logs.

## Required component, detailed next unit

Planted-positive control (adopted rule, EXT-U3): a synthetic session of KNOWN shape the tool must
recover, or a ~99% share is detector silence again. Specified in UNIT 2; implementation must ship
with it or not at all.
