# Jev Score confirmation retry: Shopee Reviews TL Stars

Status: PREREGISTERED BEFORE LIVE CALLS
Bead: jev-545t
Date: 2026-09-27
Launch gate: no live row before 2026-09-29T00:00:00Z; 2026-09-28 is reserved for OrangeFrog's jev-oioo comparator run after the 2026-09-28T00:00Z free-tier reset.

reach-mode: mcnemar

## Question

Does the fixed five-level Score design from `kit/src/score.ts` retain the Amazon/SST-5 behavior on a fresh public five-class sentiment corpus, and does Jev beat the required free comparator on the same rows?

## Corpus

- Dataset: `scaredmeow/shopee-reviews-tl-stars`, public Hugging Face dataset, MPL-2.0.
- Dataset revision: `d096f402fdc76886458c0cfb5dedc829bea2b935`.
- Language: Tagalog (`tl`).
- Source file: pinned public `test.csv`.
- Source file SHA-256: `d851b139250932165b1cd26b42e50ac69bd9033dae3c2bcf58091d5d069bc0ba`.
- Source file bytes: `334754`.
- Exact corpus: `work/score-shopee/corpus.jsonl`, 350 rows, 70 per label, corpus SHA-256 `e8799a4c8dcfb769ad51f5ce04fa28260814485a7e005c942ddac4cde005d663`.
- Selection: first 70 rows per label from the pinned public test split, preserving each source row index and review text; no text or label was authored or rewritten.
- Labels `0..4` map directly to the dataset's documented 1-star through 5-star ordered levels.
- Workspace novelty check: no prior committed Jev/comparator rows or source mention for this dataset before this preregistration.

## Fixed design

State for every row: `{ "text": row.text }`.

Instruction: `How positive is this review?`

Ordered levels, score indices 0 through 4:

1. `Very negative: strongly critical, scathing, or contemptuous`
2. `Negative: somewhat critical or unfavorable`
3. `Neutral: neither positive nor negative, or evenly mixed`
4. `Positive: somewhat favorable or approving`
5. `Very positive: strongly enthusiastic, glowing, or full of praise`

Jev model: `jev-1.13.0`, through the official TypeSafe client path used by the kit. Comparator: OpenRouter free model `dots-studio/dots-3-note-preview:free` through the existing free-comparator adapter. No paid comparator is permitted.

Every request must pass keyless size preflight before a live request. The raw Score value, full probabilities, confidence, model, and normalized level are stored per arm and per row. Normalization is the measured SST-5 rule from `work/score-sst5/score.py`: `floor(raw_score + 0.5)`, clamped to `0..4` (round half up for these nonnegative scores). Jev and comparator use the same normalization rule. Invalid, missing, unparsed, or out-of-range answers are recorded as invalid and excluded from the paired valid denominator, with counts reported separately. No row is silently dropped.

## Preregistered metrics and numeric pass bar

Primary metric: MAE against the dataset's own integer label using each arm's normalized level, separately for Jev and the comparator, on the paired valid intersection. Raw Score values and probabilities remain in every row for audit.

Primary comparison: paired per-row absolute-error difference `Jev AE - comparator AE`; report the mean difference and a two-sided paired sign-flip permutation test with 10,000 flips, seed `20260927`.

**Confirmation pass bar, fixed before calls:** at least 278 paired valid rows; Jev MAE is strictly lower than comparator MAE; and the two-sided seeded permutation p-value is `< 0.05`. No bar changes after answers are observed.

Secondary metrics: exact five-class accuracy, adjacent accuracy (`abs(normalized_level-label) <= 1`), raw-score MAE, valid count, invalid count, mean confidence, per-class counts, latency, tokens, and spend.

## Power and invalid-rate sizing

The Amazon retry observed comparator invalids of `26/300 = 8.6667%`, rounded up to the preregistered conservative planning rate `q = 0.087`. With `n = 350` and independent invalid probability `q`, expected paired coverage is `350 * (1 - 0.087) = 319.55`, standard deviation `sqrt(n*p*q) = 5.272651`, and the exact binomial probability of at least 278 paired rows is `0.999999999998`. The corpus has 350 rows, 70 per class, so the count bar has margin rather than relying on another 300-row run.

The reach receipt is `work/score-shopee/reach-receipt.json`. The shared runner must check receipt `status == REACHABLE`, exact `items_sha256`, receipt `mode ==` this preregistration's `reach-mode`, exact preregistration SHA, and a repo-relative `prereg_path` before any live request. The primary outcome test remains the preregistered paired MAE sign-flip test above.

## Spend and execution bounds

- Maximum calls: 350 Jev requests and 350 comparator requests, one each per row; no unbounded retry loop.
- Jev spend: record input/output tokens and billed usage from every returned row; report total and per-valid-row cost at `$0.042/M` billed input tokens, output free. The key is loaded outside the tree.
- Comparator spend: record OpenRouter usage before and after. Expected comparator spend is `$0` because the model id is `:free`; any nonzero charge or paid model response invalidates the run.
- Run detached only through `work/score-shopee/run.py` and `kit/experiment/run.py`, with checkpointed JSONL rows, PID, heartbeat, and the matching reach receipt.
- The runner must stop cleanly on HTTP 429, record `stop_reason: comparator HTTP 429`, classify the run `NOT_RUN` rather than `LIVE_COMPLETE`, and never label the remaining rows as model errors or silently resume within the same free-tier day. It must also stop on 401/402/403.
- Live launch is prohibited before `2026-09-29T00:00:00Z` so OrangeFrog's approximately 821 comparator calls can use the `2026-09-28` free-tier allocation first.

## Decision rule

The result is `CONFIRMATION` only if both arms are present, at least 278 paired valid rows exist, corpus/preregistration hashes match, spend readings are present, no hard-stop status occurred, and every primary pass-bar condition holds. Otherwise report `UNDERPOWERED`, `INVALID`, `NO_CONFIRMATION`, `NOT_RUN`, or `RATE_LIMIT_STOP`; never change the bar after observing answers.

## Boundary

This preregistration authorizes a future live run only. It makes no claim about Jev or comparator performance and contains no live answers. The launch date is deliberately deferred until after OrangeFrog's free-tier use; no live call is permitted before the stated UTC gate.
