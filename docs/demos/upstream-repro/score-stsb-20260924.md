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

NOT_RUN. This section is replaced only after the bar commit, and the bar text above is not edited.
