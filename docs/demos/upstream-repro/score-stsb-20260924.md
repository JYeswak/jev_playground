# Can Jev's Score rate semantic similarity? STS-B dev, Jev vs grok (bead `jev-jzzs`)

RedMaple (pane 2), 2026-09-24. Bar committed before any model call. Live calls are not in
this section.

## Preregistered

**Question.** Score is the least-proven primitive here. SST-5's MAE win held across 3x3
pairings (`jev-qbc`, `jev-x5k`). Yelp's MAE fell to TIE (R88). STS-B is a different ordinal
task: graded meaning-similarity, not sentiment. On the public dev split, does one Score
question beat the two constant predictors, and does any win over the incumbent hold on every
pairing of three Jev runs with three incumbent runs?

**Incumbent change, fixed before any call.** The bead named Claude Haiku 4.5. Pane 1, before
this file existed: Anthropic's API key hit its account usage cap (400 `specified API usage
limits`, access returns 2026-10-01 00:00Z). Haiku calls through `system-one-adapter` fail. This
bar therefore uses `grok-4.20-0309-non-reasoning` through the same adapter, the path
`work/second-incumbent/run.py` already uses. `XAI_API_KEY` was present in the lane Infisical
project (length 84, value not printed). Haiku is not called and is not retried.

**Corpus.** STS Benchmark English dev split, 1,500 pairs, published order, no subsample. The
sample seed is unused. File `data/stsb-en-dev.csv` in `PhilipMay/stsb-multi-mt` at
`30de0dec4ee199b7f42351d3f1a0b19592955385`, raw URL under that commit, sha256
`d29586e96558c4eb52cf5ea5d14e9c24d3bf0e44f111b017caba43a5adc33226`. No header. Three CSV
fields: sentence1, sentence2, score in [0, 5]. Rebuild labels with
`python3 work/score-stsb/sample.py`. It refuses a sha256 or row-count mismatch.

**License.** Scores are CC BY-SA 4.0 (Philip May's LICENSE, quoting the STS Benchmark notes:
<https://ixa2.si.ehu.eus/stswiki/index.php/STSbenchmark>). Sentence text keeps the license of
each source. MSR paraphrase and video require Microsoft's research terms. Headlines require an
EMM acknowledgement. SNLI-derived track5 is CC BY-SA 4.0. Stack Exchange answers-forums is CC
BY-SA 3.0 and requires author names, a hyperlink to each question, a hyperlink to each profile,
and redistribution of `LICENSE.answers-forums.zip`. This mirror CSV does not carry that
attribution. **Sentence text is not committed.** `work/score-stsb/labels.jsonl` has `i` and
`label` only. The runner fetches the pinned file at start, checks the sha256, and does not
write sentences into the row file. Cite Agirre et al., SemEval-2017 Task 1, and the STS wiki.

**The question, frozen** (`work/score-stsb/run.py`). State is
`{"sentence1": ..., "sentence2": ...}`. One Score question, instructions *"How similar in
meaning are these two sentences?"*. Criteria are the SemEval-2015 Task 2 gold-standard
interpretation, read from
<https://alt.qcri.org/semeval2015/task2/index.php?id=semantic-textual-similarity-for-english>
on 2026-09-24, index 0 through 5:

0. The two sentences are on different topics.
1. The two sentences are not equivalent, but are on the same topic.
2. The two sentences are not equivalent, but share some details.
3. The two sentences are roughly equivalent, but some important information differs/missing.
4. The two sentences are mostly equivalent, but some unimportant details differ.
5. The two sentences are completely equivalent, as they mean the same thing.

**Arms.** Three runs each, sequential within an arm, the two arms side by side. At most one
resume pass per run. A row still failed is incorrect on exact-level, and its predicted score
for MAE and Spearman is the endpoint farther from the gold (`0` if gold >= 2.5, else `5`).

- **Jev:** `typesafe-sdk-python` @ `0ffd094`, `AsyncTypeSafeClient(model="jev-1.13.0", retry=RetryPolicy())`. Files `rows-jev.jsonl`, `rows-jev-run2.jsonl`, `rows-jev-run3.jsonl`.
- **Incumbent:** `system-one-adapter-python` @ `adffc2e` (v0.2.0), `AsyncOpenAIProvider("grok-4.20-0309-non-reasoning", base_url="https://api.x.ai/v1")`, which selects Chat Completions for a non-OpenAI host. `structured_outputs=True`, `llm_answer_mode="probabilities"`, `normalize_probabilities=True`, `RetryPolicy()`, concurrency 8. Files `rows-grok.jsonl`, `rows-grok-run2.jsonl`, `rows-grok-run3.jsonl`. Adapter debug (`probabilityError`, `originalProbabilities`) is recorded on grok rows.

**Predicted score.** Primary continuous value is the returned expected score. Exact-level is
`floor(score + 0.5)` clamped to 0..5, compared with the gold rounded the same way. Argmax is
not in the pass rule.

**Metrics.** Over all 1,500 rows:

- Spearman of the expected score against the gold float (average ranks, Pearson of ranks; undefined if either side has no variation).
- MAE of the expected score against the gold float.
- Exact-level accuracy, with a Wilson interval reported but not tested.

**Constants, computed from the labels before any call** (`python3 work/score-stsb/score.py --bar`
must print `floors_match: true`). A constant has no rank variation, so Spearman against a
constant is not a test.

| Constant | Exact-level | MAE |
|---|---:|---:|
| always-mean (2.363908, rounded level 2) | 266/1500 | 1.293179 |
| always-mode (rounded level 3, 353 rows) | 353/1500 | 1.339955 |

Rounded gold counts: 236 / 241 / 266 / 353 / 276 / 128.

**Paired tests** (alpha 0.05, two-sided):

- MAE: exact sign test on per-row absolute error (equal errors dropped). WIN if Jev is lower and p < 0.05. LOSE if the other side is lower and p < 0.05. Else TIE.
- Exact-level: McNemar exact on the discordant pairs. Same WIN / LOSE / TIE rule.
- Spearman: 2,000 paired bootstrap resamples, `random.Random(20260924)`, with replacement. The 95% interval is the 50th and 1950th of the 2,000 sorted differences (indices 49 and 1949). WIN if the interval is entirely above 0. LOSE if entirely below 0. Else TIE. A resample whose Spearman is undefined is dropped; if any are dropped the pairing is TIE.

**All-pairings rule** (the `jev-hg8` / `jev-x5k` rule, 3 x 3 = 9, preregistered here rather than added after). Every Jev run is paired with every grok run.

- A WIN over grok on Spearman, MAE, or exact-level **stands only if it is WIN on all 9 pairings**. Otherwise that headline is not claimed. The count of WIN and LOSE pairings is reported either way.
- **PASS** requires both: (1) each of the 3 Jev runs beats both constants on MAE and on exact-level; (2) no pairing is a grok LOSE on Spearman, MAE, or exact-level. A TIE is not a loss and is not parity.
- If (1) or (2) fails, a `NEGATIVE_EVIDENCE.md` row is written with a retry condition. No wording, rounding rule, or floor is changed after an answer is seen.

**Spend, planned.** 1,500 x 3 Jev calls and 1,500 x 3 grok calls, plus at most one resume pass per run. Latency p50/p95 and token totals are reported, not tested.

**NO-CLAIM.** One dev split, one wording, one Jev version, one grok model, one adapter version, three runs per arm in one session. This is not the STS-B test split, not a Pearson claim (the SemEval official metric), and not a claim that Score works on other similarity tasks. A TIE is a failure to separate.

## Result

Bar committed at `8e4bda9` and pushed before any model call. The first launch used system
Python and died on `ModuleNotFoundError: No module named 'typesafe_sdk'` before a request.
The calls below used `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python`. Live
window 2026-09-24 03:53:39Z to 04:02:26Z. Re-score, no key:
`python3 work/score-stsb/score.py`.

Jev: 4,500/4,500 answered, 0 failed, 0 resume passes. Every answered row reports
`jev-1.13.0`. Input tokens are 651,488 on each run, so the prompts matched. Grok: 1,499/1,500
answered on each run. Row 457, gold 0.0, was refused on the first call and on the one resume
pass, all three runs, with `TypeSafePermissionDeniedError: 403 I can't help with that request.`
It is scored by the failure rule (predicted score 5, exact-level incorrect). No third attempt.
Grok input tokens on the 1,499 answered rows are 960,828 each run. No row file contains
sentence text. Grok adapter debug: 0 `probabilityError`, 0 `originalProbabilities`.

Row sha256 prefixes: `rows-jev` `940117fe04ba5b5d`, `rows-jev-run2` `b258ca389caf1f4f`,
`rows-jev-run3` `b2e639c92eeb67c2`, `rows-grok` `8a6b93ee944eacfb`, `rows-grok-run2`
`e3d2be31f66f2905`, `rows-grok-run3` `cd12b5072c53f733`.

| Arm | Answered | Spearman | MAE | Exact-level | Wilson 95% | p50 / p95 ms | Tokens in / out |
|---|---:|---:|---:|---:|---|---|---|
| Jev run 1 | 1500/1500 | 0.9072 | 0.5135 | 786/1500 | 49.9–54.9% | 158 / 318 | 651,488 / 28,500 |
| Jev run 2 | 1500/1500 | 0.9072 | 0.5136 | 784/1500 | 49.7–54.8% | 161 / 385 | 651,488 / 28,500 |
| Jev run 3 | 1500/1500 | 0.9069 | 0.5134 | 788/1500 | 50.0–55.1% | 184 / 372 | 651,488 / 28,500 |
| grok run 1 | 1499/1500 | 0.8799 | 0.5989 | 755/1500 | 47.8–52.9% | 804 / 1150 | 960,828 / 59,735 |
| grok run 2 | 1499/1500 | 0.8845 | 0.5864 | 756/1500 | 47.9–52.9% | 796 / 1205 | 960,828 / 59,585 |
| grok run 3 | 1499/1500 | 0.8850 | 0.5975 | 748/1500 | 47.3–52.4% | 885 / 1211 | 960,828 / 59,696 |

Floors, each Jev run (sign test Jev-lower / constant-lower; McNemar Jev-only / constant-only):

| Jev run | vs always-mean MAE | vs always-mean exact | vs always-mode MAE | vs always-mode exact |
|---|---|---|---|---|
| 1 | 1192/308, p=1.1e-122 WIN | 632/112, p=8.2e-89 WIN | 1142/357, p=9.4e-96 WIN | 633/200, p=4.2e-53 WIN |
| 2 | 1185/315, p=1.3e-118 WIN | 628/110, p=6.2e-89 WIN | 1140/357, p=2.2e-95 WIN | 631/200, p=9.6e-53 WIN |
| 3 | 1187/313, p=8.9e-120 WIN | 633/111, p=1.5e-89 WIN | 1139/357, p=3.3e-95 WIN | 634/199, p=1.3e-53 WIN |

Nine pairings. Spearman interval is Jev minus grok. MAE counts are Jev-lower / grok-lower.
Exact counts are Jev-only / grok-only.

| Pairing | Spearman 95% | MAE | Exact |
|---|---|---|---|
| J1 x G1 | WIN [0.0157, 0.0391] | 792/694, p=0.0118 WIN | 343/312, p=0.241 TIE |
| J1 x G2 | WIN [0.0108, 0.0354] | 794/692, p=0.0088 WIN | 363/333, p=0.272 TIE |
| J1 x G3 | WIN [0.0116, 0.0336] | 801/689, p=0.0040 WIN | 359/321, p=0.156 TIE |
| J2 x G1 | WIN [0.0157, 0.0394] | 784/705, p=0.0432 WIN | 346/317, p=0.277 TIE |
| J2 x G2 | WIN [0.0108, 0.0356] | 790/695, p=0.0147 WIN | 363/335, p=0.307 TIE |
| J2 x G3 | WIN [0.0113, 0.0337] | 798/690, p=0.0055 WIN | 361/325, p=0.181 TIE |
| J3 x G1 | WIN [0.0152, 0.0390] | 793/696, p=0.0128 WIN | 347/314, p=0.213 TIE |
| J3 x G2 | WIN [0.0104, 0.0352] | 797/690, p=0.0060 WIN | 367/335, p=0.242 TIE |
| J3 x G3 | WIN [0.0111, 0.0332] | 803/686, p=0.0026 WIN | 365/325, p=0.138 TIE |

**Under the bar.** Part 1 holds: every Jev run beats both constants on MAE and exact-level.
Part 2 holds: 0 LOSE pairings on Spearman, MAE, and exact-level. **PASS.** Spearman WIN
stands, 9/9 (thinnest interval 0.0104 to 0.0352). MAE WIN stands, 9/9 (largest p = 0.0432).
Exact-level is TIE on 9/9, so it is not a win and not a loss. No `NEGATIVE_EVIDENCE.md` row:
the preregistered trigger did not fire.

**Spend.** 4,500 Jev calls, 1,954,464 input / 85,500 output tokens. At the documented $0.042
per million input that is about $0.082, arithmetic, not an invoice. Grok: 4,497 answered calls
plus 6 refused attempts (row 457, twice per run). Answered rows: 2,882,484 input / 179,016
output tokens. The refused attempts have no usage object. Grok's dollar cost is not stated.

**Boundary.** One dev split, one wording, one Jev version, one grok model, one adapter
(`adffc2e`), three runs per arm in one session. Not the test split. Not Pearson. The
exact-level TIE is a failure to separate, not parity. Row 457 is one refusal, not a measurement
of what the text says. Awaiting a non-author re-score from the committed rows before the bead
closes.
