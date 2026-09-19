# jev-usage-shape

**Where does your agent spend actually go?** Ranks the levers by share of billed tokens, so you know
which intervention could pay *before* you build one.

Offline. No API key. No network. Read-only — it never writes to the logs it reads.

## Run it

```sh
node bin/shape.mjs ~/.claude/projects
node bin/shape.mjs ~/.claude/projects --json > shape.json
```

Point it at a directory (walked recursively for `.jsonl`) or at individual session files.

## What it found on this machine

Measured 2026-09-18 over `~/.claude/projects`, **4,619 sessions / 488,724 billed turns / 4,626
files**, models `claude-opus-5` (408,265 turns), `claude-opus-4-8` (49,842), `claude-fable-5`
(15,658) and 6 others:

| share | lever | reduce by |
|---:|---|---|
| **98.9%** | retransmitted context (cache read) | fewer turns, or less parked in context |
| 1.0% | context first-write (cache create) | read less into context at all |
| 0.1% | model output | ask for less output |
| 0.0% | fresh input (uncached) | shorter prompts |

**168,554,638,779 billed input tokens; 236,197,691 output tokens. Mean retransmitted context per
turn: 341,496.**

0 unparsable lines; 1,247,069 records carried no `usage` block and were skipped, not counted.

## Why this exists

This lane spent a day building a backtest that priced **model substitution on a fixed set of turns**,
measured 0.0447% on real logs, and correctly killed it. Then it measured the same logs for shape and
found that **~99% of billed input is context being re-sent**, a lever the pricing run never examined.

That ranking was available for **$0** from logs already on disk, before any pricing work. Getting the
order of the levers wrong is more expensive than getting any single lever's number wrong — so this
runs first, and [`../routing-backtest`](../routing-backtest) runs second, on the lever this says is
worth pricing.

## Reading the output

- **Denominator first.** `sessions / turns / files`, plus what was skipped. A share over a denominator
  you have not read is not a measurement.
- **`records_without_usage`** is large by design: most JSONL lines are not billed model turns. It is
  printed so you can see the tool is discarding them deliberately rather than silently.
- **Shares are of total tokens**, billed input plus output — one denominator, stated.

## Limits

- **Token counts only. No prices and no dollar figures anywhere.** Rates differ by model, plan and
  date; multiplying these counts by a rate is your step, not ours.
- **It does not claim the top lever is worth intervening on.** A 98.9% share says where the tokens
  are, not that a fix is cheap. An intervention that removes turns has its own cost.
- **Reads Claude Code / omp session JSONL shapes only** — specifically `message.usage` with
  `cache_read_input_tokens`, `cache_creation_input_tokens`, `input_tokens`, `output_tokens`. Other
  harnesses will report zero turns, which is a visible result, not a silent one.
- Numbers above are this machine's corpus on the stated date. **Run it on yours; that is the point.**
