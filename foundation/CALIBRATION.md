# Calibration audit — frame + v1 evidence

**Question:** are Jev's probabilities calibrated enough to drive thresholds in code?
**Answer (v1, 2026-09-17, `jev-latest` → jev-1.13.0): yes — ECE 0.061, Brier 0.020.**

## Method (frozen in `run_calibration.py`, stdlib only)

- 80-row fixture (`fixtures/calibration-v1.jsonl`, sha-pinned in each receipt):
  60 Noul (20 spam / 20 injection / 20 factuality, balanced truth) + 20 Choice intent.
- One atomic question per request, sequential, 30 s timeout, ≤2 retries, Ctrl-C
  writes a partial receipt. Failures are rows with `error_kind`, never drops.
- Metrics: 10-bin ECE, Brier, Wilson 95% CI per bin, threshold sweep
  (accuracy/coverage at 0.25/0.5/0.75/0.8/0.9), Choice top-1 accuracy.

## v1 results (`runs/20260917T224444Z.json`, 80/80, 0 errors, 55 s)

| Slice | Result |
|---|---|
| ECE / Brier | **0.061 / 0.020** |
| Noul accuracy | 58/60 = 0.967 (spam 18/20, injection 20/20, factuality 20/20) |
| Choice accuracy | 19/20 = 0.95 (one genuinely ambiguous invoice item) |
| t=0.75 / 0.8 | accuracy **1.0** at 95% coverage |
| t=0.9 | accuracy 1.0 at 90% coverage |

Reading: the hardcoded thresholds in the tested repos (0.75 block, 0.8
auto-accept) are defensible on this data — full accuracy above 0.75 with small
coverage cost. Do not generalize beyond easy items (see limits).

## Most interesting finding: instruction wording moves scores, correctly

The only 2 misses (spam-03 bank phish 0.36, spam-15 IRS threat 0.37) are
*phishing*, and the instruction asked about *bulk commercial spam*. The model
returned middling scores — uncertain, not confidently wrong. Calibration-positive
behavior, fixture-labeling lesson: ambiguous items belong in their own stratum,
not forced into binary truth.

## Limits (what v1 does NOT prove)

- Easy, hand-written items; no adversarial or near-boundary cases.
- n=60/20 → wide per-bin CIs; ECE point estimate only.
- Single model snapshot; thresholds must be re-run per model version.
- No Choice-confidence calibration (only top-1 accuracy); no latency distribution.

## Rust-port contract (the foundation ask)

Everything here ports 1:1: JSON fixtures validated by `schemas/fixture-v1.json`,
receipts by `schemas/report-v1.json` (serde-compatible shapes — structs, string
enums, numbers; no untagged unions, no maps with non-string keys); pure metric
functions over rows (no IO); errors as data (`error_kind`), never control flow;
all bounds named in one place (`TIMEOUT_S`, `MAX_RETRIES`, backoff cap, one
question per request, sequential); deterministic input order; timestamps only in
receipt metadata, never in scored data. A Rust runner reads the same fixture
files byte-for-byte. Cancel-correctness is already structural: bounded retries,
per-request timeout, partial receipt on interrupt, no shared mutable state.

## Next audits (in priority order)

1. **Ambiguous stratum**: near-boundary items (phish-vs-spam, sarcasm, vague
   tickets) to test the uncertain middle, where thresholds actually bite.
2. **Choice-confidence calibration**: top-1 accuracy conditioned on confidence bins.
3. **Adversarial**: jev-sec-bench + jev-spam-eval corpora through this same harness
   (fixture format already supports it — add rows, rerun).
4. **A/B vs chat models**: system-one-adapter-python on this fixture (accuracy/latency/cost).
5. **Scheduled re-run**: same fixture + new model versions → drift detection.
