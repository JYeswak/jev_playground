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

Bar committed at `15b0371` before either arm made a call. Run 2026-09-24T02:31Z, both arms 400/400
answered on the first pass, 0 error rows. Rows: `work/noul-scifact/rows-jev.jsonl` (sha256
`120971ed…d30fce1`), `work/noul-scifact/rows-haiku.jsonl` (sha256 `e04b0e8a…5996dd68`). Re-score
with no key (about 20 s, the bootstrap dominates): `python3 work/noul-scifact/score.py`.

| Arm | Correct at >0.5 | Accuracy | Wilson 95% | AUC | Brier | ECE (10 bins) |
|---|---:|---:|---|---:|---:|---:|
| constant: always no (0) | 254/400 | 63.5% | 58.7–68.1% | 0.500 | 0.3650 | 0.3650 |
| constant: base rate (0.365) | 254/400 | 63.5% | 58.7–68.1% | 0.500 | 0.2318 | 0.0000 |
| **Jev `jev-1.13.0`** | **361/400** | **90.2%** | 86.9–92.8% | **0.962** | **0.0709** | **0.0431** |
| **Haiku 4.5 via adapter** | **351/400** | **87.8%** | 84.2–90.6% | **0.934** | **0.1002** | **0.0854** |

| Arm | Answered | Model reported | p50 / p95 latency | Tokens in / out | AUC 95% | Brier 95% | ECE 95% | Distinct noul values |
|---|---:|---|---|---|---|---|---|---:|
| Jev | 400/400 | `jev-1.13.0` (all rows) | 140 / 219 ms | 293,734 / 8,000 | 0.942–0.979 | 0.054–0.090 | 0.033–0.073 | 68 |
| Haiku | 400/400 | `anthropic/claude-haiku-4-5` | 765 / 1,275 ms | 373,346 / 4,981 | 0.906–0.959 | 0.077–0.124 | 0.061–0.118 | 20 |

Paired on the same 400 rows (bootstrap intervals are Jev minus the other arm):

| Jev vs | Jev-only correct | Other-only correct | McNemar p | Accuracy | AUC diff 95% | AUC | Brier diff 95% | Brier | ECE diff 95% | ECE |
|---|---:|---:|---:|---|---|---|---|---|---|---|
| always no | 131 | 24 | 4.9e-19 | WIN | +0.442 to +0.479 (vs 0.5) | WIN | −0.343 to −0.243 | WIN | −0.367 to −0.255 | WIN |
| base rate | 131 | 24 | 4.9e-19 | WIN | same as above | WIN | −0.182 to −0.138 | WIN | n/a (0 by construction) | — |
| **Haiku** | 19 | 9 | 0.087 | **TIE** | +0.008 to +0.053 | **WIN** | −0.047 to −0.012 | **WIN** | −0.065 to −0.007 | **WIN** |

**Pass rule applied:** (1) accuracy WIN over always-no, AUC interval above 0.5, Brier WIN over the
base-rate constant: all yes. (2) No significant Haiku win on any of the four metrics: accuracy TIE,
AUC, Brier and ECE all Jev WIN. **PASS.** No `NEGATIVE_EVIDENCE.md` row: the preregistered trigger did
not fire.

**Descriptive, not preregistered.** Calibration by bin (mean noul → fraction true):

| Bin | Jev rows | Jev mean → true | Haiku rows | Haiku mean → true |
|---|---:|---|---:|---|
| 0.0–0.1 | 190 | 0.039 → 0.016 | 159 | 0.008 → 0.038 |
| 0.1–0.2 | 24 | 0.133 → 0.042 | 39 | 0.126 → 0.051 |
| 0.2–0.3 | 16 | 0.239 → 0.188 | 16 | 0.219 → 0.062 |
| 0.3–0.4 | 8 | 0.349 → 0.500 | 13 | 0.315 → 0.308 |
| 0.4–0.5 | 7 | 0.454 → 0.571 | 3 | 0.433 → 0.000 |
| 0.5–0.6 | 8 | 0.565 → 0.625 | 1 | 0.500 → 0.000 |
| 0.6–0.7 | 5 | 0.636 → 0.600 | 0 | — |
| 0.7–0.8 | 10 | 0.723 → 0.400 | 22 | 0.739 → 0.409 |
| 0.8–0.9 | 29 | 0.849 → 0.793 | 35 | 0.849 → 0.600 |
| 0.9–1.0 | 103 | 0.953 → 0.932 | 112 | 0.975 → 0.920 |

By SciFact gold label (correct at >0.5 / mean noul):

| Gold | Rows | Jev | Haiku |
|---|---:|---|---|
| SUPPORT | 146 | 131 (89.7%) / 0.843 | 133 (91.1%) / 0.867 |
| CONTRADICT | 93 | 89 (95.7%) / 0.086 | 87 (93.5%) / 0.097 |
| NEI | 161 | 141 (87.6%) / 0.168 | 131 (81.4%) / 0.218 |

Where Jev pulls ahead is the NOT ENOUGH INFO rows, abstracts that are on topic but do not settle the
claim: 10 more correct than Haiku, and a lower mean probability on them. Haiku is slightly better on
SUPPORT (2 more correct). Haiku's worst-calibrated region is 0.7–0.9, where 57 rows at a mean of about
0.81 are true about half the time (30 of 57).

**Verdict** (`[live]`, N=400 per arm, 2026-09-24). On 400 SciFact claim/abstract pairs, one Noul at
`jev-1.13.0` using the vendor cookbook's wording beats both constants on every metric (90.2% vs 63.5%;
AUC 0.962; Brier 0.071 vs 0.232 for the fitted base rate) and does not lose to Claude Haiku 4.5 on
anything. Accuracy is 2.4 points higher and not significant (McNemar 19 vs 9, p = 0.087). Jev is
significantly better on the three probability metrics: AUC +0.028, Brier −0.029, ECE −0.042, all with
bootstrap intervals that exclude 0. It answered at 140 ms p50 against 765 ms. The seat the bead named,
claim verification with a probability you can threshold, holds against an LLM incumbent on public
labels.

**Spend.** 800 live calls: 400 Jev (293,734 input / 8,000 output tokens as reported by the API) and 400
Haiku (373,346 input / 4,981 output, adapter totals including any corrective retries). [INFERENCE] At
Haiku 4.5's list price ($1 / $5 per million input / output tokens) the Haiku arm is about $0.40. The
Jev arm's billed units were not read and are not stated. The two arms use different tokenizers.

**Boundary.** One public biomedical set, one question wording (the vendor's), one Jev version, one Haiku
version, one run per arm (no run-to-run variance measured). The accuracy TIE is a failure to separate,
not equality. The binary collapse of CONTRADICT and NEI into "false" is ours; SciFact's three-way
label and rationale selection were not measured. The pairs are public and may be in either model's
training data. Nothing was tuned after the answers came back. Awaiting a non-author re-score from the
committed rows before the bead closes.

**Haiku run-to-run variance, measured afterwards by someone other than the author** (VerifySST5,
bead `jev-x5k`, bar `af2906b`, result `752b38b`; `NEGATIVE_EVIDENCE.md` R89). Three Haiku runs on the
same 400 pairs, scored against the committed Jev rows. VerifySST5's preregistered rule counts a win
only if it holds on all three runs. Under that rule two of the wins above are **retracted**:
- AUC was a WIN, a TIE (−0.0021 to +0.0393) and a WIN.
- ECE was a WIN, a WIN and a TIE (−0.0495 to +0.0050).

The rest held. Brier was a WIN on 3/3 runs, accuracy was a TIE on 3/3, and no run was a Haiku win,
so the PASS stands. The direction favoured Jev on every run. The claim that holds up is: Jev is better
on Brier and not worse on anything. The AUC and ECE margins are within Haiku's run-to-run spread.

## Non-author verification — VerifySST5

VerifySST5 (background agent of pane 1; not the author), 2026-09-24, keyless, from a fresh
`git clone --local` at `590f9c7` into a temp dir. No live call made; spend $0.

| # | Check | Result |
|---|---|---|
| 1 | `env -u TYPESAFE_API_KEY -u ANTHROPIC_API_KEY python3 work/noul-scifact/score.py` in the clone | HOLDS. Jev 361/400, AUC 0.962, Brier 0.0709, ECE 0.0431; Haiku 351/400, AUC 0.934, Brier 0.1002, ECE 0.0854; constants 254/400. Seeded bootstrap intervals reproduce every cell of both tables: Jev AUC 0.942–0.979, Haiku 0.906–0.959; vs Haiku AUC +0.0080 to +0.0531, Brier −0.0473 to −0.0117, ECE −0.0646 to −0.0072; McNemar 19 vs 9, p = 0.0872 (TIE); `overall: PASS`. Row sha256 prefixes `120971ed` (jev) and `e04b0e8a` (haiku) match the receipt. The rows, `score.py` and this receipt are unchanged after `83a7295`; only `run.py` changed later, for the jev-k2q arms. |
| 2 | `python3 work/noul-scifact/sample.py 400 20260924` | HOLDS. Tarball sha256 accepted, 1,259 pairs, rebuilt `sample.jsonl` sha256 `424caf18…88ed33`, identical to the committed file. |
| 3 | Truth mapping | HOLDS. `sample.py:52-73`: gold is the pair's single rationale label (mixed labels are refused), NEI when there is no evidence entry, and `truth = gold == "SUPPORT"`. All 400 rows satisfy `truth == (gold == "SUPPORT")`: 146 SUPPORT true, 93 CONTRADICT and 161 NEI false. |
| 4 | AUC ties | HOLDS. `score.py:35-52` assigns the average rank to each tie group (Mann-Whitney). An independent all-pairs count (ties count ½) gives 0.9622 (Jev) and 0.9336 (Haiku), matching 0.962 and 0.934. Ties matter here: Jev has 68 distinct values over 400 rows, Haiku 20. |
| 5 | The one Haiku row at exactly 0.500 | HOLDS. It is the only one: i = 57, gold NEI (truth false). The bar's decision is `noul > 0.5`, so it counts as "no", which is correct; recounting with `> 0.5` gives 351/400 for Haiku, as reported. Jev has no row at 0.500. |
| 6 | Bar before data | HOLDS. `15b0371` (20:31:02 −0600) is an ancestor of `83a7295` (20:33:27 −0600) and has no `rows-*.jsonl`. `run.py`, `score.py`, `sample.py` and `sample.jsonl` are byte-unchanged between the two, and the receipt diff only replaces "Pending the live run." under Results. |

Verdict: the PASS reproduces from committed files under an unedited bar. Re-score:
`python3 work/noul-scifact/score.py` (about 20 s). NO-CLAIM: this re-scores committed rows; it does not
re-run either model, measure run-to-run variance, or re-adjudicate SciFact's labels.
