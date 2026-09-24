# Can Jev's Noul verify a scientific claim against its cited abstract? SciFact, Jev vs Haiku (bead `jev-9er`)

ScoreSST5 (background agent of pane 1, AmberWillow), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**Question.** Claim and citation checking is a vendor cookbook
(`docs-mirror/typesafe/cookbooks/citation_check.md`) that this lane had never measured against an
incumbent on public labels. On SciFact, expert-written scientific claims paired with the abstracts
they cite, does one Noul question ("does the abstract support the claim?") beat the constants, and
does it hold up against Claude Haiku 4.5 asked the identical question through TypeSafe's own adapter,
on ranking (AUC), on probability quality (Brier, ECE) and on accuracy?

**Corpus.** SciFact (Wadden et al., 2020), AllenAI's release tarball
<https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz> (the URL the Hugging Face
loader `allenai/scifact` @ `1fe54665deee011033b2dd98db5752e0d586fdfb` downloads; ETag
`cb7da4d8609e30f2c7483b61aa447f7e`, Last-Modified 2021-01-26), sha256
`11c621288d41ac144d29b13b0f8503b3820b7d6e8b1f6ff24dff335c196d76be`. The test split ships without
labels, so the pool is every (claim, cited abstract) pair in `claims_train.jsonl` and
`claims_dev.jsonl`: 1,259 pairs. Truth is SciFact's own rationale label for that abstract: SUPPORT is
true; CONTRADICT and no rationale (NOT ENOUGH INFO) are false. No pair carries mixed labels (the sampler
refuses one). Sample: `work/noul-scifact/sample.jsonl`, 400 pairs by `random.Random(20260924)`; rebuild
with `python3 work/noul-scifact/sample.py 400 20260924` (refuses a sha256 mismatch, byte-identical on
rerun: sample sha256 `424caf18097938cd337f04a3e784737f367302b688fa34f47c38e5244088ed33`). The sample
holds 146 SUPPORT, 93 CONTRADICT, 161 NEI (prevalence 0.365), 288 from train and 112 from dev.

**The question, frozen** (`work/noul-scifact/run.py`, `QUESTION`). State = `{"claim", "title",
"abstract"}` with the abstract's sentences joined by spaces. One Noul, wording from the vendor
cookbook: instructions *"Does the abstract support the claim?"*, criteria `true`: *"The abstract states
the claim or directly implies that it is true"*, `false`: *"The abstract contradicts the claim, or does
not address what the claim asserts"*.

**Arms.**
- **Jev:** official `typesafe_sdk` 0.7.0 (`upstream/typesafe-ai/typesafe-sdk-python` @ `0ffd094`),
  `AsyncTypeSafeClient(model="jev-1.13.0", retry=RetryPolicy())`.
- **Incumbent:** the same `Noul` object and state through `system-one-adapter-python` 0.2.0
  (@ `adffc2e`), `anthropic/claude-haiku-4-5`, structured outputs, `llm_answer_mode="probabilities"`,
  probabilities normalized.
- **Constants** (computed before any call by `python3 work/noul-scifact/score.py` and
  `node work/jev-prevalence-first/prevalence-check.mjs work/noul-scifact/sample.jsonl --truth truth`):

| Constant | Correct at >0.5 | Accuracy | AUC | Brier | ECE |
|---|---:|---:|---:|---:|---:|
| always no (0) | 254/400 | 63.5% | 0.500 | 0.3650 | 0.3650 |
| base rate (0.365 on every row) | 254/400 | 63.5% | 0.500 | 0.2318 | 0.0000 |

The base-rate constant is fitted on the sample itself, which favours it, and has ECE 0 by
construction. ECE is therefore not compared against it; Brier is.

**Metrics** (`work/noul-scifact/score.py`). Decision: noul > 0.5 means "supports". Accuracy with a
Wilson 95% interval. AUC of the noul probability (Mann-Whitney, ties averaged). Brier score. ECE over 10
equal-width bins on [0, 1], weighted by count. A row that still has no answer after the runner's
resume pass counts as incorrect and enters AUC, Brier and ECE at noul 0.5.

**Paired tests** (same 400 rows, alpha 0.05, two-sided): McNemar exact on correct/incorrect; paired
bootstrap, 2,000 resamples, `random.Random(20260924)`, 95% percentile interval of the difference for
AUC, Brier and ECE. A difference is significant when its interval excludes 0.

**Pass rule.**
1. Jev beats the constants: accuracy WIN over always-no (McNemar p < 0.05, Jev higher), AUC 95% interval
   above 0.5, and Brier WIN over the base-rate constant (interval of Jev minus constant below 0).
2. Jev does not lose to Haiku: none of accuracy (McNemar), AUC, Brier or ECE (bootstrap intervals) is a
   significant Haiku win. A non-significant difference is a TIE, not parity proven.
3. **PASS** = 1 and 2. If Jev fails 1, or loses to Haiku on any of the four, a `NEGATIVE_EVIDENCE.md`
   row is written with a retry condition. The wording, criteria and 0.5 cut are not retuned after
   seeing an answer.

**Stated before running:** 400 Jev requests and 400 Haiku requests (one question each), concurrency 8,
per-call wall-clock latency p50/p95 and reported token usage per arm. Descriptive only: the calibration
table per arm, accuracy and mean noul split by SciFact gold label (SUPPORT / CONTRADICT / NEI), and the
count of distinct noul values each arm returns.

**NO-CLAIM.** One public set of biomedical claims, one question wording, one Jev model version, one
Haiku version. The binary collapse of CONTRADICT and NEI into "false" is ours; SciFact's three-way task
is not what is measured. Train and dev pairs are public and may be in either model's training data.

## Results

Pending the live run.
