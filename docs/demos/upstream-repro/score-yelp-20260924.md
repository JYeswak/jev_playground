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

Bar committed at `52d94c2` before either arm made a call. Run 2026-09-24 (live, `[live]`), both
arms 500/500 answered on the first pass, 0 error rows, no resume needed. Rows:
`work/score-yelp/rows-jev.jsonl` (sha256 `2921a926…343c43`) and `work/score-yelp/rows-haiku.jsonl`
(sha256 `4ab83aaf…ca76a3`). The rows hold no review text. Re-score with no key:
`python3 work/score-yelp/score.py`.

| Arm | Exact correct | Accuracy | Wilson 95% | MAE (levels) |
|---|---:|---:|---|---:|
| constant: majority (always 0, 1 star) | 117/500 | 23.4% | 19.9–27.3% | 1.842 |
| constant: middle (always 2, 3 stars) | 100/500 | 20.0% | 16.7–23.7% | 1.206 |
| **Jev `jev-1.13.0`** (rounded expected, primary) | **341/500** | **68.2%** | 64.0–72.1% | **0.348** |
| Jev (argmax, descriptive) | 338/500 | 67.6% | 63.4–71.6% | 0.360 |
| **Haiku 4.5 via adapter** (rounded expected, primary) | **323/500** | **64.6%** | 60.3–68.7% | **0.384** |
| Haiku (argmax, descriptive) | 316/500 | 63.2% | 58.9–67.3% | 0.412 |

| Arm | Answered | Model reported | p50 / p95 latency | Tokens in / out | MAE of raw expected score |
|---|---:|---|---|---|---:|
| Jev | 500/500 | `jev-1.13.0` (all rows) | 231 / 502 ms | 280,986 / 8,500 | 0.369 |
| Haiku | 500/500 | `anthropic/claude-haiku-4-5` | 932 / 1,819 ms | 465,525 / 22,783 | 0.423 |

Paired on the same 500 rows (primary levels):

| Jev vs | Jev-only correct | Other-only correct | McNemar exact p | Accuracy | Jev lower error | Other lower error | Sign test p | MAE |
|---|---:|---:|---:|---|---:|---:|---:|---|
| always 0 | 244 | 20 | 3.9e-50 | WIN | 344 | 22 | 1.7e-75 | WIN |
| always 2 | 297 | 56 | 8.9e-41 | WIN | 320 | 61 | 1.7e-43 | WIN |
| Haiku | 59 | 41 | 0.089 | TIE | 67 | 45 | 0.047 | WIN |

**Adapter zero-mass check (`jev-mly`).** `probabilityError` and `originalProbabilities` were
recorded on 500/500 Haiku rows and are `null` on all 500. The adapter always builds
`debug.probability_errors` and adds a question only when its raw map was off by more than the
tolerance (`system_one_adapter/_utils/probability_normalization.py:36-54` at `adffc2e`; wired in
`_client.py:311-313`). So no Haiku row was rescaled and none was zero-mass. The two required
passes (all rows; zero-mass rows dropped, 0 dropped) and the descriptive third pass are the same
table, and all three print PASS. One Haiku row (`i = 367`) is an exactly uniform 0.2 map at
confidence 0.0 with no `probability_errors`. That is Haiku asserting uniform, not the adapter
filling a zero map. It rounds to the middle level, which matches the label (3 stars); Jev gives
1.97 on the same row, also 3 stars.

**Pass rule applied:** (1) Jev beats both constants on accuracy and MAE: yes. (2) Jev does not lose
to Haiku on either metric: yes (accuracy TIE, MAE WIN). (3) The same holds with zero-mass rows
dropped (0 such rows). **PASS.** No `NEGATIVE_EVIDENCE.md` row: the preregistered trigger did not
fire.

**How narrow the MAE win is (descriptive).** Sign test 67 vs 45 gives p = 0.0467. Moving a single
row from "Jev lower error" to a tie gives 66 vs 45, p = 0.057, a TIE. So the MAE WIN has a
headroom of one row, narrower than SST-5's four (`jev-qbc`). Run-to-run variance on Yelp was not
measured, and on SST-5 Jev changed 6 to 8 of 500 levels between runs. A repeat run could plausibly
land on either side of 0.05.

**Descriptive, not preregistered.** Coverage by returned confidence: Jev's top 25% / 50% / 75% of
rows are 88.0% / 81.6% / 75.2% exact; Haiku's are 85.6% / 72.8% / 68.5%. Unlike SST-5, where
Haiku's confidence carried almost no ranking signal, both arms' confidence ranks here. Jev's
ranks more steeply in the top half. Confusions (`score.py` prints them): both arms err mostly by
one level. Jev reads truth 4 stars as 5 stars 40 times, and 3 stars as 4 stars 33 times. Haiku
reads 4 stars as 5 stars 40 times, and **2 stars as 1 star 48 times** (Jev: 21). That is where
most of Haiku's exact-accuracy gap comes from.

**Verdict** (`[live]`, N = 500 per arm, 2026-09-24). On 500 Yelp test reviews, one Score question
at `jev-1.13.0` beats both constants by a wide margin: 68.2% exact against 23.4% and 20.0%, MAE
0.348 against 1.842 and 1.206. It does not lose to Haiku 4.5 asked the identical question through
TypeSafe's adapter: 3.6 points higher on exact accuracy, not significant (McNemar p = 0.089), and
lower absolute error, significant by one row (sign test p = 0.047). This matches SST-5 (4.4 points,
p = 0.092; MAE p = 0.015), on a second public ordinal set with review-length text. **PASS**, with
the same shape and the same narrowness. The answer to the bead's question: the direction carries
to a second set, but the MAE margin is as thin here as on SST-5 or thinner, so neither set alone
separates Jev from Haiku with room to spare. Jev answered at 231 ms p50 against Haiku's 932 ms.

**Spend.** 1,000 live calls, 0 retries of failed rows. Jev: 500 calls, 280,986 input / 8,500 output
tokens as reported by the API. Haiku: 500 calls, 465,525 input / 22,783 output (adapter totals).
[INFERENCE] At Haiku 4.5's list price ($1 / $5 per million) the Haiku arm is about $0.58. The Jev
arm's billed units were not read and are not stated.

**Scratch left in place** (Joshua deletes): `/tmp/yelp-test.parquet` (the pinned parquet, fetched
once to take its sha256), `/tmp/yelp-smoke/` (scorer smoke copy with SST-5 rows and synthetic
debug fields), `/tmp/sst5-score-restore.py` (a byte-identical copy of the committed
`work/score-sst5/score.py`, used to undo one mistaken edit to that file before anything was
committed), `/tmp/yelp-score.txt`. `work/score-yelp/texts.jsonl` is gitignored review text that
the sampler rebuilds.

**Boundary / NO-CLAIM.** One run per arm, one question wording, one Jev version, one Haiku
configuration. Run-to-run variance on this set was not measured, and the MAE WIN has one row of
headroom. The TIE on accuracy is a failure to separate, not proof of equality. The star labels are
the reviewers' own and were not re-adjudicated. The descriptive tables were not preregistered, and
no threshold was chosen from them. No review text is published; the numbers can be re-derived
from committed rows plus the pinned public file. A non-author re-score is still pending, and the
bead stays open until it is done.

## Non-author verification — MaintFixes

MaintFixes (background agent of pane 1, not an author of this unit), 2026-09-24. Keyless, no model
call. Clean `git clone --local` in `mktemp -d` (`/tmp/maintfixes-76o.sWS4jh/jev`), checked out at `df13f17`.

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Bar before rows, text unchanged | `diff` of lines 1-91 at `52d94c2` vs `df13f17`; `git diff --stat 52d94c2 df13f17 -- work/score-yelp/{run,score,sample}.py work/score-yelp/sample.jsonl` | lines 1-91 byte-identical; the four files have no diff. Bar 21:10:39 -0600, rows first appear in `df13f17` at 21:13:52 |
| 2 | Sample rebuilds | `uv run --no-project --python 3.12 --with pyarrow==21.0.0 python work/score-yelp/sample.py 500 20260924 --check` | `check: identical`; `sample.jsonl` sha256 `c2b9fd85…971b58`. A non-check build rewrites it with no git diff, and all 500 texts match `text_sha256`. `--check` does not write `texts.jsonl` (`sample.py:80-83` returns first); only the non-check build writes it |
| 3 | Keyless re-score | `python3 work/score-yelp/score.py` | rc 0: Jev 341/500 MAE 0.348, Haiku 323/500 MAE 0.384, McNemar 59v41 p = 0.0886 TIE, sign 67v45 p = 0.0467 WIN, constants 117 (1.842) / 100 (1.206), PASS on all three passes |
| 4 | Own recompute from rows + `sample.jsonl` only | `/tmp/maintfixes-76o-recompute.py` | every number in row 3 matches. Moving one sign row to Haiku (66v46) gives p = 0.072: one row of headroom, as stated |
| 5 | Zero-mass count is real, not an empty field | adapter source at `adffc2e` | `debug.probability_errors` is always returned (`_client.py:311`, `probability_normalization.py:41`, tolerance 1e-6), so null on 500/500 means no raw map was rescaled. Haiku probabilities sum to 1.0 on 500/500. `i = 367` (uniform 0.2, confidence 0) is model-asserted, as disclosed above |
| 6 | 10 rows by hand | `random.Random(76)` over the ids: 27, 102, 152, 189, 199, 214, 237, 431, 465, 486, with texts rebuilt in scratch | star label plausible for the text 10/10; level `floor(score + 0.5)` matches 10/10; Jev exact 6/10, Haiku 7/10. Jev's worst row, `i = 214`, is a short positive review scored 1 star (p0 = 0.77) |

Also observed: on 6/500 Jev rows the returned `score` differs from E[probabilities] by more than
0.01 (the probabilities are rounded). On one of them, `i = 214`, E gives level 1 and the score gives
level 0; truth is level 4. The preregistered rule uses the score, so nothing changes.

**Verdict: CONFIRMED** at `[oracle]` level (offline re-score and recompute of committed rows, N = 500,
`jev-1.13.0` vs Haiku 4.5, 2026-09-24): PASS, accuracy TIE, MAE WIN with one row of headroom. Not
checked: no live call was repeated, so the recorded answers are taken as the API's; the latency,
token and calibration tables were not recomputed.

**Run-to-run variance, measured afterwards** (bead `jev-91u`,
[`score-yelp-variance-20260924.md`](score-yelp-variance-20260924.md)). Two more runs of each arm gave
MAE WIN in only 3 of 9 Jev x Haiku pairings, all three against this receipt's Haiku run, which was
Haiku's worst of three. Under that bar the MAE headline above is **RETRACTED to TIE**
(`NEGATIVE_EVIDENCE.md` R88). The PASS stands in all nine pairings. This section is added after the
fact; nothing above it is changed.
