# Jev Score confirmation: Yelp Review Full

Status: PREREGISTERED BEFORE LIVE CALLS
Bead: jev-dml3
Date: 2026-09-27

reach-mode: rate

## Question

Does the measured five-level Score design from `kit/src/score.ts` retain its SST-5 result on a public five-class sentiment corpus not previously scored in this workspace, and does it beat the required free comparator on the same rows?

## Corpus

- Dataset: `Yelp/yelp_review_full`, owner `Yelp`, public `test` split.
- Dataset revision: `c1f9ee939b7d05667af864ee1cb066393154bf85`.
- Source endpoint: Hugging Face Datasets Server rows API, with the repository's required downloader user agent.
- Selection: lowest source `row_idx` 40 examples from each of the five public labels, selected from the test split without authoring or rewriting text.
- Exact corpus: `work/score-yelp/corpus.jsonl`, 200 rows, 40 per label, SHA-256 `10d6775919c2353c34d6f73a3408036fad392a72daef9538e29f238cd71b3336`.
- Labels: Yelp `0..4` map directly to the five ordered sentiment levels below.
- No row from this corpus has a committed Jev or comparator score before this preregistration.

## Fixed design

State for every row: `{ "text": row.text }`.

Instruction: `How positive is this movie review sentence?`

Ordered levels, score indices 0 through 4:

1. `Very negative: strongly critical, scathing, or contemptuous`
2. `Negative: somewhat critical or unfavorable`
3. `Neutral: neither positive nor negative, or evenly mixed`
4. `Positive: somewhat favorable or approving`
5. `Very positive: strongly enthusiastic, glowing, or full of praise`

Jev model: `jev-1.13.0`, via the official TypeSafe SDK/client path used by the kit. Comparator: OpenRouter free model `dots-studio/dots-3-note-preview:free` through the existing free-comparator adapter. No paid comparator is permitted.

Every request must pass keyless size preflight before a live request. Invalid, missing, unparsed, or out-of-range answers are not coerced: they are recorded as invalid and excluded from the primary valid-row MAE denominator, with counts reported separately. A row is not silently dropped.

## Preregistered metrics and bars

Primary metric: mean absolute error (MAE) against the dataset's own integer label, separately for Jev and the free comparator, on the paired valid intersection.

Primary comparison: paired per-row absolute-error difference `Jev AE - comparator AE`; report the mean difference and a paired permutation/significance test with 10,000 seeded sign flips, seed `20260927`. The comparison is descriptive if either arm has fewer than 100 paired valid rows; no win claim is allowed below that count.

Secondary metrics: exact five-class accuracy, adjacent accuracy (`abs(score-label) <= 1`), valid count, invalid count, mean confidence, and per-class counts. These do not replace MAE.

The fixed data-admissibility reach bar is in `work/score-yelp/reach-receipt.json`: 200 trials, minimum class count 40, `rate` reach mode, threshold 0.80. The run is refused unless that receipt matches this preregistration and the exact corpus hash.

## Spend and execution bounds

- Maximum calls: 200 Jev requests and 200 comparator requests, one each per row; no unbounded retry loop.
- Jev spend: record input/output tokens and billed usage from every returned row; report total and per-valid-row cost. The API key is loaded outside the tree.
- Comparator spend: record OpenRouter usage before and after. The expected comparator spend is `$0` because the model id is `:free`; any nonzero charge or paid model response is a hard stop and invalidates the run.
- Run detached only through `kit/experiment/run.py`, with checkpointed JSONL rows, PID, heartbeat, and the matching reach receipt. Stop on 401/402/403 or provider refusal; resume only from completed row ids.

## Decision rule

The result is a confirmation only if the receipt contains both arms, at least 100 paired valid rows, exact corpus and preregistration hashes, spend readings, and the primary MAE/permutation result. Otherwise report `UNDERPOWERED`, `INVALID`, or `NOT_RUN`; do not reinterpret the bar after seeing answers.

## Boundary

This preregistration does not claim Jev or comparator performance. It authorizes the described live run only after the reach receipt is committed and its SHA is sent to pane 1. No live call has been made at preregistration time.
