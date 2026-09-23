---
name: prevalence-first
description: Before writing, quoting, or spending on any Jev question, compute what always-answering-the-majority scores on the same labelled rows. Use when proposing a Jev seat, quoting a Jev accuracy, choosing a threshold, reading a benchmark, or about to make a live Jev call on a new question set.
---

# prevalence-first

A Jev number means nothing until it is set beside the score of a constant that never calls Jev.
This skill makes that comparison the first thing printed, and refuses a verdict when the comparison
cannot be made.

Why this exists, measured in this repo:

- The commit judge answered yes to `describes` on all 31 commits, which scored 30 of 31. Always
  answering yes also scores 30 of 31. The question was degenerate, and it had already been quoted as
  a result.
- Jev's tool-select routing got 192 of 400 right. Always answering `bash` got 252.
- On the real command corpus, always answering `BAD` is right on 6,181 of 7,846 rows (78.8%). Any
  question on that set must beat that number before it is worth a key.

## The rule

1. **Labels first.** No labels, no verdict. Label a sample before judging any question on it.
2. **Print the constant before the model's score.** The majority share is the bar.
3. **Count the near-threshold rows.** A verdict inside ±0.1 of the cut was made by the cut.
4. **Verdict last**, computed, never typed: `DISCRIMINATES` only if correct answers beat the
   constant plus the near-threshold count.

## Run it

```bash
C=work/jev-prevalence-first/prevalence-check.mjs
node $C rows.jsonl --score p --truth label                # binary: score >= 0.5 means yes
node $C rows.jsonl --choice choice --truth label          # multiclass: constant = majority class
node $C rows.jsonl --truth outcome                        # labels only: the bar, before any spend
node $C scores.jsonl --score p --labels labels.jsonl --id id --truth label   # labels in another file
```

Exit `0` DISCRIMINATES (or DEFERRED for labels only), `3` WEAK or DEGENERATE, `2` no labels or no
usable rows, `64` bad flags. Use the exit code in scripts; a seat whose check exits 3 is refused.
It reads JSONL, a JSON array, or a JSON object with a `records` array. It never calls Jev.

## Reading the result

- **Calibrated models pay for their uncertainty here.** On the same 662 injection rows Jev had 18
  scores within ±0.1 of the cut; Haiku and grok-4 had 0, because they answer 0 or 1. The WEAK rule
  charges Jev for those 18 rows and charges the LLMs nothing. Read a WEAK next to its near count.
- **A threshold fit on one dataset does not carry to another.** Re-run this check whenever the rows
  change.
- **The constant is a floor, not the comparison that decides a purchase.** Passing it earns the
  question a run against an LLM on the same state (AGENTS.md Rule 14).

## Where it has run

`work/jev-prevalence-first/SPEC.md` "Loop on real sets" lists nine passes: the command, the constant,
the verdict, and the gap each pass found in the checker.
