# Does the SciFact Noul hold on FEVER? Jev vs Haiku on encyclopedic claim verification (bead `jev-wx5`)

ObserveHookL3 (background agent of pane 1, Anthropic model), 2026-09-24. Live lane, model pinned
`jev-1.13.0`.

## Preregistered (committed before the first call)

**Question.** On SciFact (`noul-scifact-20260924.md`, bead `jev-9er`), one Noul question beat both
constants and beat Claude Haiku 4.5 on AUC, Brier and ECE, with accuracy tied. That was one domain
(biomedical abstracts). FEVER has short encyclopedic evidence: Wikipedia sentences, crowd-written
claims and a different distribution. With the same question, word for word, does Jev still beat the
constants and still not lose to Haiku?

**Corpus.** FEVER 1.0 (Thorne et al., 2018), the labelled `paper_dev` split, with evidence text from
`copenlu/fever_gold_evidence` `valid.jsonl` (Hugging Face revision
`a6b8d891d393e97a4efac791afffb2d7de5e57c6`, sha256
`5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9`; Atanasova et al., EMNLP 2020).
For SUPPORTS and REFUTES that file carries FEVER's gold Wikipedia sentences. For NOT ENOUGH INFO,
where FEVER ships no evidence, it carries the sentences the Papelo system retrieved (Malon, 2018):
on-topic text that does not settle the claim, the same role NEI abstracts play in SciFact. Provenance
check, run by the sampler on every build: FEVER's own `paper_dev.jsonl` from fever.ai (sha256
`41158707810008747946bf23471e82df53e77a513524b9e3ec1c2e674ef5ef8c`, 9,999 claims) is downloaded, and
the sampler refuses to run unless every one of the 15,935 copenlu rows has the same claim text and
label as FEVER for its id. All 15,935 match. (For the record, copenlu `test.jsonl` is FEVER
`paper_test`, not used.)

**Pool and sample.** One pair per FEVER claim: the first copenlu row for the claim whose evidence has
text. 62 NEI rows carry only an empty sentence and are skipped, so 9,835 of the 9,999 dev claims are
in the pool. Truth: SUPPORTS is true; REFUTES and NOT ENOUGH INFO are false (the same collapse as
SciFact). Sample: `work/noul-fever/sample.jsonl`, 400 claims by `random.Random(20260924)`. Rebuild
with `python3 work/noul-fever/sample.py 400 20260924`; it refuses a sha256 mismatch, and two runs
were byte-identical (sha256 `7f9f03cc4049861720f20730c579329d2b8d0c794f5117af10e01f835a7734d6`). The
sample holds 146 SUPPORTS, 121 REFUTES and 133 NEI (prevalence 0.365). 377 claims have evidence
from one page, 21 from two and 2 from three.

**State.** `{"claim", "title", "abstract"}`, the same keys the SciFact runner sends, so the question
text needs no edit. `title` is the evidence page names ("; "-joined). `abstract` is the evidence
sentences joined by spaces, and each sentence is prefixed with its page name when the evidence spans
pages. FEVER's bracket tokens (`-LRB-` and the like) are restored. All other FEVER tokenization, such
as spaces before commas, is left as is (`sample.py` docstring).

**The question, frozen: the exact object that won on SciFact.** `QUESTION` in
`work/noul-scifact/run.py`, unchanged since `15b0371`. Instructions *"Does the abstract support the
claim?"*. Criteria `true`: *"The abstract states the claim or directly implies that it is true"*;
`false`: *"The abstract contradicts the claim, or does not address what the claim asserts"*. The same
runner file is used with a data directory argument (`run.py <arm> work/noul-fever`). Nothing about
the question, the client settings or the cut changes.

**Arms.**
- **Jev:** official `typesafe_sdk` `AsyncTypeSafeClient(model="jev-1.13.0", retry=RetryPolicy())`.
- **Incumbent:** the same `Noul` object and state through `system-one-adapter-python` at `adffc2e`,
  `anthropic/claude-haiku-4-5`, structured outputs, `llm_answer_mode="probabilities"`,
  `normalize_probabilities=True`.
- **Constants** (computed before any call: `python3 work/noul-scifact/score.py work/noul-fever` and
  `node work/jev-prevalence-first/prevalence-check.mjs work/noul-fever/sample.jsonl --truth truth` →
  `verdict: DEFERRED`, must beat always-false 254/400):

| Constant | Correct at >0.5 | Accuracy | AUC | Brier | ECE |
|---|---:|---:|---:|---:|---:|
| always no (0) | 254/400 | 63.5% | 0.500 | 0.3650 | 0.3650 |
| base rate (0.365 on every row) | 254/400 | 63.5% | 0.500 | 0.2318 | 0.0000 |

**Adapter zero-mass requirement (from `adapter-uniform-20260924.md`, bead `jev-mly`).** The Haiku
runner records, per row, the adapter's `debug.probability_errors` and
`debug.original_probabilities` for the question (`probabilityError`, `originalProbabilities`). The
scorer counts rows where either is set (rescaled, or zero-mass with original sum 0). If there are
any, it prints the whole comparison again with those rows dropped from both arms. What we expect,
stated from source before running: the adapter rescales only Choice and Score distributions. A Noul
is a single `[0, 1]` number, `_client.py:125-127` returns it as-is, and a missing or out-of-range
value fails schema validation (`_schema.py:25`) rather than being filled in. So the expected count is
0. A nonzero count would contradict that reading and would be reported as a finding.

**Metrics and paired tests.** Identical to the SciFact bar, from the same `score.py`. The decision
is noul > 0.5. Accuracy is reported with a Wilson 95% interval. AUC is Mann-Whitney with ties
averaged. Brier is reported as is. ECE uses 10 equal-width bins weighted by count. A row still
unanswered after the resume pass counts as incorrect and enters AUC, Brier and ECE at noul 0.5. The
paired tests run on the same 400 rows: McNemar exact on correct/incorrect, and a paired bootstrap
(2,000 resamples, `random.Random(20260924)`) giving a 95% percentile interval for the AUC, Brier and
ECE differences. Alpha is 0.05, two-sided.

**Pass rule.**
1. Jev beats the constants: accuracy WIN over always-no (McNemar p < 0.05, Jev higher), AUC 95%
   interval above 0.5, and Brier WIN over the base-rate constant.
2. Jev does not lose to Haiku: none of accuracy (McNemar), AUC, Brier or ECE is a significant Haiku
   win. A non-significant difference is a TIE, not proven parity.
3. **PASS** = 1 and 2, on all 400 rows and, if any Haiku rows are rescaled or zero-mass, also with
   them dropped. If Jev fails 1, or loses to Haiku on any of the four in either scoring, a
   `NEGATIVE_EVIDENCE.md` row is written with a retry condition. The wording, criteria and 0.5 cut
   are not retuned after seeing an answer.

**Stated before running:** 400 Jev requests and 400 Haiku requests, one question each, concurrency
8. Per-call p50/p95 latency and reported token usage per arm. Descriptive only: the calibration table
per arm, accuracy and mean noul by FEVER gold label (SUPPORTS / REFUTES / NEI), the count of distinct
noul values per arm, and the count of Haiku answers exactly 0.0 and exactly 0.5.

**NO-CLAIM.** One public English set, one question wording, one Jev version and one Haiku version.
The binary collapse of REFUTES and NEI into "false" is ours; FEVER's three-way task and its evidence
retrieval are not measured, because the evidence is given. NEI evidence is one system's retrieval,
not gold. FEVER dev is public and may be in either model's training data.

## Results

Pending: filled in after both arms run.
