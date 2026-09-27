# Jev Score confirmation: Amazon Reviews Multi English

Status: PREREGISTERED BEFORE LIVE CALLS
Bead: jev-dml3
Date: 2026-09-27

reach-mode: mcnemar

## Question

Does the measured five-level Score design from `kit/src/score.ts` retain its SST-5 behavior on an unseen public five-class English sentiment corpus, and does Jev beat the required free comparator on the same rows?

## Corpus

- Dataset: `SetFit/amazon_reviews_multi_en`, Apache-2.0, public `test.jsonl`.
- Dataset revision: `ec73b665e4be0f567b69d39425355401cfe0d29b`.
- Source file SHA-256: `64827868be6aeb86959e283bc9ae94f5c515ca2fa334c698c3cb5c4a36395029`.
- Exact corpus: `work/score-amazon/corpus.jsonl`, 300 rows, 60 per label, corpus SHA-256 `591ba40224ccea0c0873b7dfea64a85ec53ce16b476e71d4336115d5f7d884b7`.
- Selection: first 60 rows per label from the pinned public test file; review text and labels are copied, not authored or rewritten.
- Labels `0..4` map directly to the five ordered Score levels below.
- Workspace novelty check: no prior committed Jev/comparator rows or score receipt for this dataset/revision before this preregistration.

## Fixed design

State for every row: `{ "text": row.text }`.

Instruction: `How positive is this movie review sentence?`

Ordered levels, score indices 0 through 4:

1. `Very negative: strongly critical, scathing, or contemptuous`
2. `Negative: somewhat critical or unfavorable`
3. `Neutral: neither positive nor negative, or evenly mixed`
4. `Positive: somewhat favorable or approving`
5. `Very positive: strongly enthusiastic, glowing, or full of praise`

Jev model: `jev-1.13.0`, through the official TypeSafe client path used by the kit. Comparator: OpenRouter free model `dots-studio/dots-3-note-preview:free` through the existing free-comparator adapter. No paid comparator is permitted.

Every request must pass keyless size preflight before a live request. Invalid, missing, unparsed, or out-of-range answers are recorded as invalid and excluded from the paired valid-row denominator, with counts reported separately. No row is silently dropped.

## Preregistered metrics and numeric pass bar

Primary metric: MAE against the dataset's own integer label, separately for Jev and the comparator, on the paired valid intersection.

Primary comparison: paired per-row absolute-error difference `Jev AE - comparator AE`; report the mean difference and a two-sided paired sign-flip permutation test with 10,000 flips, seed `20260927`.

**Confirmation pass bar, fixed before calls:** at least 278 paired valid rows; Jev MAE is strictly lower than comparator MAE; and the two-sided seeded permutation p-value is `< 0.05`. No fixed `0.068` observed-gap requirement is imposed: `0.068` is used only for prospective sample sizing below, avoiding a 50%-power observed-effect gate.

Secondary metrics: exact five-class accuracy, adjacent accuracy (`abs(score-label) <= 1`), valid count, invalid count, mean confidence, and per-class counts. These do not replace the primary bar.

## Power and reach binding

The prospective sizing effect is the SST-5 Jev-versus-Haiku MAE gap `0.068`, used only as a planning effect. From 500 committed paired SST-5 rows, the paired AE-difference sample SD was `0.4040226506`; normal approximation at two-sided alpha `0.05` and power `0.80` requires `278` paired rows. The Amazon corpus has 300 rows, above that bound, with 60 examples per label.

The reach receipt is `work/score-amazon/reach-receipt.json`. The shared runner really checks: receipt `status == REACHABLE`, exact `items_sha256`, receipt `mode ==` the preregistration `reach-mode`, exact preregistration SHA, and a repo-relative `prereg_path` accepted by `kit/experiment/run.py`. This receipt's `mcnemar` mode is the runner's paired-run gate; the primary outcome test remains the preregistered paired MAE sign-flip test above.

## Spend and execution bounds

- Maximum calls: 300 Jev requests and 300 comparator requests, one each per row; no unbounded retry loop.
- Jev spend: record input/output tokens and billed usage from every returned row; report total and per-valid-row cost. The key is loaded outside the tree.
- Comparator spend: record OpenRouter usage before and after. Expected comparator spend is `$0` because the model id is `:free`; any nonzero charge or paid model response is a hard stop and invalidates the run.
- Run detached only through `kit/experiment/run.py`, with checkpointed JSONL rows, PID, heartbeat, and the matching reach receipt. Stop on 401/402/403 or provider refusal; resume only from completed row ids.

## Decision rule

The result is `CONFIRMATION` only if both arms are present, at least 278 paired valid rows exist, corpus/preregistration hashes match, spend readings are present, and every primary pass-bar condition holds. Otherwise report `UNDERPOWERED`, `INVALID`, `NO_CONFIRMATION`, or `NOT_RUN`; never change the bar after observing answers.

## Boundary

This preregistration does not claim Jev or comparator performance. It authorizes the described live run only after the matching reach receipt is committed and its SHA is sent to pane 1. No live call has been made at preregistration time.
