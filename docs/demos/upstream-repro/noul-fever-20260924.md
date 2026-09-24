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

The bar was committed at `834a569` before either arm made a call. Both arms ran on 2026-09-24
between 02:50 and 02:52 UTC. Each answered 400/400 on the first pass with 0 error rows. Rows:
`work/noul-fever/rows-jev.jsonl` (sha256 `8de7c43a…4c706acd7`) and
`work/noul-fever/rows-haiku.jsonl` (sha256 `c6035a30…abe072bdb`). Re-score with no key (about
20 s): `python3 work/noul-scifact/score.py work/noul-fever`.

| Arm | Correct at >0.5 | Accuracy | Wilson 95% | AUC | Brier | ECE (10 bins) |
|---|---:|---:|---|---:|---:|---:|
| constant: always no (0) | 254/400 | 63.5% | 58.7–68.1% | 0.500 | 0.3650 | 0.3650 |
| constant: base rate (0.365) | 254/400 | 63.5% | 58.7–68.1% | 0.500 | 0.2318 | 0.0000 |
| **Jev `jev-1.13.0`** | **379/400** | **94.8%** | 92.1–96.5% | **0.973** | **0.0463** | **0.0376** |
| **Haiku 4.5 via adapter** | **376/400** | **94.0%** | 91.2–95.9% | **0.957** | **0.0581** | **0.0664** |

| Arm | Answered | Model reported | p50 / p95 latency | Tokens in / out | AUC 95% | Brier 95% | ECE 95% | Distinct noul values |
|---|---:|---|---|---|---|---|---|---:|
| Jev | 400/400 | `jev-1.13.0` (all rows) | 159 / 378 ms | 158,899 / 8,000 | 0.954–0.989 | 0.030–0.065 | 0.025–0.062 | 47 |
| Haiku | 400/400 | `anthropic/claude-haiku-4-5` | 678 / 1,251 ms | 231,100 / 4,771 | 0.935–0.976 | 0.038–0.080 | 0.047–0.092 | 17 |

Paired on the same 400 rows. The bootstrap intervals are Jev minus the other arm:

| Jev vs | Jev-only correct | Other-only correct | McNemar p | Accuracy | AUC diff 95% | AUC | Brier diff 95% | Brier | ECE diff 95% | ECE |
|---|---:|---:|---:|---|---|---|---|---|---|---|
| always no | 140 | 15 | 1.3e-26 | WIN | +0.454 to +0.489 (vs 0.5) | WIN | −0.371 to −0.269 | WIN | −0.376 to −0.269 | WIN |
| base rate | 140 | 15 | 1.3e-26 | WIN | same as above | WIN | −0.207 to −0.163 | WIN | n/a (0 by construction) | — |
| **Haiku** | 6 | 3 | 0.51 | **TIE** | +0.003 to +0.031 | **WIN** | −0.023 to −0.002 | **WIN** | −0.041 to −0.008 | **WIN** |

**Adapter zero-mass check (jev-mly requirement).** `debug` was recorded on 400/400 Haiku rows.
`probability_errors` was set on 0 and zero-mass (original sum 0) on 0, so the "without them" scoring
drops 0 rows and is the tables above. This matches the source reading in the bar: a Noul is not
rescaled. For the record, 205 of Haiku's 400 answers are exactly 0.0 and 5 are exactly 0.5. Those
are the model's own scalar, not an adapter fill-in, because the adapter has no fill-in path for a
Noul. Jev returned neither value on any row.

**Pass rule applied.** (1) Accuracy WIN over always-no, AUC interval above 0.5, and Brier WIN over
the base rate: all yes. (2) No significant Haiku win on any of the four: accuracy TIE, and AUC,
Brier and ECE all Jev WIN. Both scorings are identical (0 rows dropped). **PASS.** The preregistered
`NEGATIVE_EVIDENCE.md` trigger did not fire, so no row was written.

**Descriptive, not preregistered.** Calibration by bin (mean noul → fraction true):

| Bin | Jev rows | Jev mean → true | Haiku rows | Haiku mean → true |
|---|---:|---|---:|---|
| 0.0–0.1 | 218 | 0.022 → 0.018 | 210 | 0.001 → 0.019 |
| 0.1–0.2 | 16 | 0.146 → 0.000 | 16 | 0.125 → 0.000 |
| 0.2–0.3 | 6 | 0.237 → 0.167 | 5 | 0.210 → 0.000 |
| 0.3–0.4 | 2 | 0.380 → 0.000 | 5 | 0.310 → 0.400 |
| 0.4–0.5 | 3 | 0.463 → 0.333 | 1 | 0.400 → 0.000 |
| 0.5–0.6 | 3 | 0.537 → 0.333 | 5 | 0.500 → 0.000 |
| 0.6–0.7 | 3 | 0.673 → 1.000 | 2 | 0.600 → 0.000 |
| 0.7–0.8 | 3 | 0.780 → 1.000 | 3 | 0.717 → 0.667 |
| 0.8–0.9 | 13 | 0.843 → 0.615 | 3 | 0.833 → 1.000 |
| 0.9–1.0 | 133 | 0.978 → 0.940 | 150 | 0.997 → 0.900 |

By FEVER gold label (correct at >0.5 / mean noul):

| Gold | Rows | Jev | Haiku |
|---|---:|---|---|
| SUPPORTS | 146 | 140 (95.9%) / 0.924 | 140 (95.9%) / 0.954 |
| NEI | 133 | 119 (89.5%) / 0.144 | 117 (88.0%) / 0.159 |
| REFUTES | 121 | 120 (99.2%) / 0.030 | 119 (98.3%) / 0.022 |

The accuracy gap is small: the two arms disagree on 9 rows, and both miss the same 18. The
probability gap is where Jev leads. Haiku puts 150 rows at a mean of 0.997, and 90% of them are
true. Jev puts 133 rows at 0.978, and 94% are true. Jev also spreads its remaining mass over 47
distinct values against Haiku's 17. As on SciFact, NEI (on-topic evidence that does not settle the
claim) is the hardest gold label for both arms.

**Verdict** (`[live]`, N=400 per arm, 2026-09-24). On 400 FEVER `paper_dev` claims with their
evidence sentences, the SciFact Noul, unchanged, at `jev-1.13.0` beats both constants on every
metric (94.8% vs 63.5%; AUC 0.973; Brier 0.046 vs 0.232 for the fitted base rate). It does not lose
to Claude Haiku 4.5 on any metric. Accuracy is 0.8 points higher, which is not significant (McNemar
6 vs 3, p = 0.51). Jev is significantly better on the three probability metrics: AUC +0.016, Brier
−0.012 and ECE −0.029, all with bootstrap intervals that exclude 0. Jev answered at 159 ms p50,
Haiku at 678 ms. This is the second public domain (encyclopedic, after biomedical) where the same
question gives the same result shape: accuracy tied and calibration won. Both scorings, with and
without rescaled or zero-mass Haiku rows, are the same, because there were none.

**Spend.** 800 live calls. Jev: 400 calls, 158,899 input / 8,000 output tokens as the API reported;
at the $0.042 per 1M input rate the criteria receipt states, that is about $0.007. Haiku: 400 calls,
231,100 input / 4,771 output (adapter totals); [INFERENCE] about $0.25 at $1 / $5 per million
input / output tokens. Neither figure is an invoice. The two arms use different tokenizers.

**Boundary.** One public set (FEVER `paper_dev`, English Wikipedia), one question wording, one Jev
version, one Haiku version, one run per arm (no run-to-run variance measured). The accuracy TIE is a
failure to separate, not equality. The binary collapse is ours. NEI evidence comes from one retrieval
system (Papelo), not gold annotation. 164 dev claims are outside the pool because copenlu does not
carry them. Correction to the bar text: its 62 empty-evidence NEI rows cost no claim, because each
of those 62 claims also has a row with text. Checked after the run, and the sample is unaffected.
FEVER dev is public and may be in either model's training data.
Nothing was tuned after the answers came back. The bead waits for a non-author re-score from the
committed rows before it closes.

## Non-author re-check (AdapterUniform, 2026-09-24, keyless)

Done in a fresh `git clone` of `main` at `d5ef746` (`/tmp/jev-wx5-verify`), with
`TYPESAFE_API_KEY` and `ANTHROPIC_API_KEY` unset. No live call.

- **Bar before rows.** `834a569` (bar, sampler, sample, generalized runner and scorer) is an ancestor
  of `aadd4d8` (rows). `sample.jsonl`, `run.py` and `score.py` are unchanged between the two
  commits. Row files hash to the receipt's values: `rows-jev.jsonl` `8de7c43a…4c706acd7`,
  `rows-haiku.jsonl` `c6035a30…abe072bdb`.
- **FEVER table reproduces.** `python3 work/noul-scifact/score.py work/noul-fever` exits 0.
  - Jev 379/400 (94.8%), AUC 0.973, Brier 0.0463, ECE 0.0376.
  - Haiku 376/400 (94.0%), AUC 0.957, Brier 0.0581, ECE 0.0664.
  - Per-arm intervals: Jev AUC 0.954–0.989, Brier 0.0296–0.0646, ECE 0.0254–0.0619. Haiku 0.935–0.976,
    0.0381–0.0802, 0.0474–0.0920.
  - Paired vs Haiku: 6/3, p = 0.508 TIE. AUC +0.0030 to +0.0306, Brier −0.0231 to −0.0020, ECE
    −0.0413 to −0.0081: all WIN.
  - Vs constants: 140/15, p = 1.33e-26.
  - `bar 1 PASS`, `bar 2 loses to incumbent: NO`, `overall: PASS`.
  - Every number matches the receipt to its printed precision.
- **SciFact unchanged under the generalized scorer.** The `15b0371` scorer (bar commit for jev-9er)
  and the current generalized scorer, both run on `work/noul-scifact`, print identical numbers in
  every table. The diff is four text lines only: the header `true (SUPPORT)` became `true`, the two
  `By SciFact gold label` headings became `By gold label`, and a new adapter-debug line reads
  "recorded on 0/400". The old jev-9er Haiku rows predate the debug fields, so zero-mass is
  correctly reported as not ruled out.
- **QUESTION.** The `QUESTION = Noul(...)` block in `work/noul-scifact/run.py` is byte-identical to
  `15b0371`.
- **Sample rebuild (network).** `python3 work/noul-fever/sample.py 400 20260924` exits 0. It reads
  a 9,835-claim pool (62 rows skipped for empty evidence text) and writes a file with sha256
  `7f9f03cc4049861720f20730c579329d2b8d0c794f5117af10e01f835a7734d6`, byte-identical (`cmp`) to the
  committed `sample.jsonl`.
- **Spot-check, 10 rows.**
  - The five Haiku answers of exactly 0.5 are rows 29, 141, 160, 202 and 358. All five are gold NEI
    (truth false), so they score "no" at the >0.5 cut. Jev answered 0.20, 0.19, 0.06, 0.38 and 0.12
    on them.
  - Five seeded others: 7 and 327 (REFUTES), 283 and 364 (NEI), 342 (SUPPORTS). Jev 0.02, 0.02,
    0.02, 0.03, 0.97 against Haiku 0.0, 0.0, 0.0, 0.1, 1.0. All agree with gold at the cut.
  - Counts match the receipt: Haiku exactly 0.0 on 205/400; Jev 0.0 or 0.5 on 0/400.
- **Debug fields.** All 400 Haiku rows carry `probabilityError` and `originalProbabilities`, both
  `null` on all 400. The runner writes `debug.probability_errors.get("supports")`
  (`work/noul-scifact/run.py:124-126`). `null` means the adapter made no normalization entry, which
  is expected: a Noul answer never goes through normalization
  (`system_one_adapter/_client.py:125-127`). The "0 rescaled, 0 zero-mass" result is therefore true
  by construction for Noul, and the scorer's 0-row drop is correct.
- Re-check verdict: **CONFIRMED**. PASS stands as written.

Scratch left in place: `/tmp/jev-wx5-verify` (clone, including an untracked copy of the `15b0371`
scorer at `work/noul-scifact/score_old_verify.py`) and `/tmp/jev-wx5-verify-*.txt|.py|.jsonl`.
