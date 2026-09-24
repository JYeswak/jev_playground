# Does Score's SST-5 result carry to Yelp review stars? Jev vs Haiku (bead `jev-76o`)

ConfidenceCascade (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.
Method copied from `jev-zui` (`score-sst5-20260924.md`, `work/score-sst5/`). Only the corpus and
the question wording change.

## Preregistered (committed before the first call)

**Question.** On SST-5, one Score question beat both constants and tied Haiku 4.5 on exact accuracy
(p = 0.092) with lower absolute error (sign test p = 0.015). Across three Jev runs that MAE win held
at p = 0.015 / 0.040 / 0.019 (`jev-qbc`), which is narrow. Is Score's advantage specific to SST-5,
or does it also appear on a second public ordinal set with longer text?

**Corpus.** Yelp Review Full (Zhang, Zhao and LeCun 2015), test split, as published in the Hugging
Face dataset `Yelp/yelp_review_full`, file `yelp_review_full/test-00000-of-00001.parquet` at
revision `c1f9ee939b7d05667af864ee1cb066393154bf85`. It has 50,000 rows and sha256
`bf06d5969bff93ecd4a6d4b330643761ce108b42e9b8a894cf82c9df02a08540`. Labels 0..4 are 1..5 stars,
as the reviewers gave them; they are not ours. The dataset card lists the licence as "other"
(yelp-licence), and this repository is public, so **no review text is committed**.
`work/score-yelp/sample.jsonl` holds `i`, `src` (row in the parquet), `label`, `chars` and each
text's sha256. The runner reads the text from a gitignored `texts.jsonl` and checks every sha256
before any call.

**Sample.** 500 rows drawn without replacement by `random.Random(20260924)` over the 50,000. Rebuild
and check: `uv run --no-project --python 3.12 --with pyarrow==21.0.0 python
work/score-yelp/sample.py 500 20260924 --check`. This fetches the pinned file, refuses a sha256
mismatch, and prints `check: identical`. Sample sha256
`c2b9fd852cbf91498ef83ba2874b42f9ae767f5689b304b4a352b72378971b58`. Label counts 1..5 stars:
117 / 107 / 100 / 90 / 86. Review length: median 526 characters, 95th percentile 2,228, max 4,873
(SST-5 items are single sentences). Texts are sent whole, not truncated.

**The question, frozen** (`work/score-yelp/run.py`, `QUESTION`). State is the review text as a
string. One Score question named `stars`, with instructions *"How many stars (1 to 5) did the author
of this Yelp review give the business?"* Criteria, in order:

0. 1 star: very negative; a bad experience, strongly critical, would not return
1. 2 stars: negative; mostly disappointed, with a few redeeming points
2. 3 stars: mixed or average; about as much good as bad
3. 4 stars: positive; a good experience with minor complaints
4. 5 stars: very positive; enthusiastic, would highly recommend

The wording was written once, before any call, and is not tuned after.

**Arms, unchanged from `jev-zui`.**
- **Jev:** official `typesafe_sdk` `AsyncTypeSafeClient(model="jev-1.13.0", retry=RetryPolicy())`,
  8 concurrent.
- **Incumbent:** the same `Score` object and state through `system-one-adapter-python`, using
  `anthropic/claude-haiku-4-5`, structured outputs, `llm_answer_mode="probabilities"` and
  normalized probabilities, 8 concurrent. **New for this bead:** every Haiku row records the
  adapter's `debug.probability_errors` and `debug.original_probabilities` for the question
  (`probabilityError`, `originalProbabilities`). Score is exposed to the zero-mass defect
  (`adapter-uniform-20260924.md`, `jev-mly`): an all-zero map comes back as the middle level (3
  stars) at confidence 0, with no error raised.
- **Constants,** computed before any call by `python3 work/score-yelp/score.py`:

| Constant | Exact correct | Accuracy | MAE (levels) |
|---|---:|---:|---:|
| majority class (always 0, 1 star) | 117/500 | 23.4% | 1.842 |
| middle level (always 2, 3 stars) | 100/500 | 20.0% | 1.206 |

**Predicted level, metrics and paired tests: identical to `jev-zui`.** Primary level is
`floor(score + 0.5)` clamped to 0..4; the argmax level (ties to the lower index) is reported and
not used. Measures: exact accuracy with a Wilson 95% interval, and MAE in levels, over all 500 rows.
A row still unanswered after the runner's resume pass counts as wrong with error `max(y, 4 - y)`.
Accuracy is compared with McNemar exact; per-row absolute error with an exact two-sided sign test
(ties dropped). Alpha 0.05, two-sided.

**Pass rule.**
1. Jev beats both constants: accuracy WIN **and** MAE WIN against each.
2. Jev does not lose to Haiku: neither test is a significant Haiku win. A non-significant
   difference is a TIE, not proof of parity.
3. **PASS** needs 1 and 2 on all 500 rows **and** again with every zero-mass Haiku row (raw map
   summed to 0) dropped from every arm. The scorer prints a third pass, with every row that has
   `probability_errors` set dropped; that pass is descriptive.
4. If Jev fails 1, or loses to Haiku on either metric in either required pass, a
   `NEGATIVE_EVIDENCE.md` row is written with a retry condition. No criterion, instruction or
   rounding rule is changed after an answer is seen.

**Stated before running:** 500 Jev requests and 500 Haiku requests, plus retries of failed rows
only. Spend is not capped (AGENTS.md, Live Call Budget Gate) and is reported. [INFERENCE] Haiku at
roughly 0.5M input tokens is about $0.6 at list price. Also reported: p50/p95 latency, tokens,
model strings, argmax results, MAE of the raw expected score, coverage and calibration by
returned confidence, and confusion matrices (all descriptive, as in `jev-zui`).

**Re-score, no key, no text needed:** `python3 work/score-yelp/score.py`.

**NO-CLAIM.** One more public ordinal set (Yelp business reviews), one question wording, one run per
arm, one Jev version and one Haiku version. A PASS here does not show Score works on every ordinal
task, and a TIE is not evidence of equivalence. Star labels are noisy: the same text can plausibly
carry adjacent ratings.

## Results

Pending the live run.
