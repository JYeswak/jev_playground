# Does grok-4.20 hold the FEVER, Yelp and full-Banking77 results? (bead `jev-iwhh`)

RedMaple (pane 2), 2026-09-24. Bar committed before any call. No Jev call. No OpenRouter call.

## Preregistered

**Question.** Three results are measured against Haiku only, and Haiku is capped until
2026-10-01. The only live incumbent is `grok-4.20-0309-non-reasoning` through
`system-one-adapter-python` @ `adffc2e`, `AsyncOpenAIProvider(base_url="https://api.x.ai/v1")`,
the caller used by `work/score-stsb/run.py`. Does each unit's own committed claim hold
against three grok runs, paired with every committed Jev run?

| Set | Rows | Committed Jev runs | Claim under test |
|---|---:|---|---|
| FEVER (`work/noul-fever`) | 400 | `rows-jev.jsonl`, `rows-jev-rerun.jsonl`, `rows-jev-run2.jsonl`, `rows-jev-run3.jsonl` | ECE WIN (README; held 12/12 vs Haiku) |
| Yelp (`work/score-yelp`) | 500 | `rows-jev.jsonl`, `-run2`, `-run3` | none in the README (MAE already TIE, R88) |
| Banking77 full 77 (`work/choice-banking77/full.jsonl`) | 3,080 | `rows-full-jev.jsonl`, `-run2`, `-run3` | accuracy WIN, 2,467 vs 2,267 of 3,080 (README) |

**Questions, the units' own.** FEVER: `work/noul-scifact/run.py` `QUESTION` and `state()`
(claim, title, abstract). Yelp: `work/score-yelp/run.py` `QUESTION`, review text joined by
`load_texts()` and checked against `text_sha256`. Banking77: `work/choice-banking77/run.py`
`question()` / `state()`, 77 options, criteria described by name alone. No wording is
rewritten here.

**Arms.** Three grok runs per set, sequential within a set, the three sets side by side.
Concurrency 8. At most one resume pass per run. A row still failed is scored as
`jev-jzzs` row 457: Noul on the wrong side of the label, Score at the endpoint farther
from the gold, Choice incorrect. No third attempt.

**A cell is scored only if grok answered at least 99% of its rows** (Banking77's own
ceiling: 30 of 3,080; FEVER 4 of 400; Yelp 5 of 500). More refusals, including a grammar
refusal of the 77-option schema, is **NOT-SCORED**. A NOT-SCORED cell does not retract a
README claim and does not count as grok beating or tying Jev.

**All-pairings.** Every committed Jev run x every grok run (FEVER 4x3 = 12, Yelp 3x3 = 9,
Banking77 3x3 = 9). A WIN stands only if it is WIN on every pairing. A TIE is not a win
and is not parity.

**Verdict rules, each unit's own, not restated.**

- FEVER: `work/noul-scifact/score.py` `auc`, `brier`, `ece`, `accuracy`, `boot`,
  `binom_two_sided`. Accuracy McNemar at `noul > 0.5`. AUC / Brier / ECE by the 2,000-resample
  bootstrap. README claim under test is ECE. A grok ECE TIE or LOSE on any pairing retracts
  that README WIN and gets a `NEGATIVE_EVIDENCE.md` row.
- Yelp: `work/score-yelp/score.py` exact-level McNemar and MAE sign test, levels
  `floor(score+0.5)` clamped to 0..4. No README WIN to retract.
- Banking77: `work/choice-banking77/score.py` exact McNemar on the gold intent. README claim
  under test is accuracy. A grok accuracy TIE or LOSE on any pairing retracts that README
  WIN and gets a `NEGATIVE_EVIDENCE.md` row. Zero-mass rows (flat map) are reported in both
  readings: all rows, and those rows dropped from both arms. A win must be WIN in both.

**Spend, planned.** 3 x (400 + 500 + 3,080) = 11,940 calls, plus at most one resume.
`XAI_API_KEY` length was 84. The value is not printed.

**NO-CLAIM.** One grok model, one adapter version, three runs, the units' frozen questions.
Not a new Jev measurement.

## Result

Bar committed at `6164a11` and pushed before any call. Live window 2026-09-24
07:31:59Z to 08:53:30Z. No Jev call. No OpenRouter call. Every answered row reports
`xai/grok-4.20-0309-non-reasoning`.

**Which row counted.** The bar does not say which line counts when an id appears
twice. The other units' failed-row rule counts the first attempt, so that is what
was scored. Eight of the nine files have one line per id. `rows-b77-run2.jsonl`
has 3,081 lines and 3,080 ids. `i=1294` appears twice: first
`TypeSafeInternalServerError: 502`, then an ok answer from the one resume. The
502 counted. That run is 3,079 answered and 1 failed, under the 30-row ceiling,
so the cell is scored. The later ok answer was not counted.

Grok Choice rows store the criteria key (`exchange rate`). The Jev writer maps
that key to the intent slug before storing `choice`. Scoring applied
`work/choice-banking77/run.py` `labels()` at score time. The row files were not
rewritten.

| Set | Grok answered | Point | Pairings | Verdict |
|---|---|---|---|---|
| FEVER ECE | 400/400 x 3 | grok ECE 0.267, 0.271, 0.252 | 12/12 WIN, 0 TIE, 0 LOSE | README ECE WIN **HOLDS** |
| Yelp exact / MAE | 500/500 x 3 | exact 267, 265, 269 of 500; MAE 0.530, 0.526, 0.530 | accuracy 9/9 WIN; MAE 9/9 WIN | no README WIN to retract |
| Banking77 accuracy | 3080, 3079, 3080 of 3080 | correct 2128, 2130, 2120 | 9/9 WIN all rows; 9/9 WIN with flat maps dropped (7-10 ids) | README accuracy WIN **HOLDS** |

Thinnest FEVER ECE interval is J3 x grok run 3, [-0.2561, -0.1639]. Thinnest
Banking77 all-rows pairing is J3 x grok run 1, 466/139, p=3.4e-42. No pairing
was a TIE or a LOSE. No `NEGATIVE_EVIDENCE.md` row: grok did not beat or tie a
README WIN.

Row sha256 prefixes: fever `ce7a1aa4c213c437`, `17aefa540df26fc8`,
`77b3c1621f283c6a`; yelp `38b6b831a14a37ae`, `e2794fc6afbcc863`,
`121c456b62cfa5af`; b77 `53791b8a04684a69`, `ac20d01e970b2d29`,
`c03a4506e98826f3`.

**Spend.** 11,941 grok calls (11,940 plus the one resume of `i=1294`). Input
tokens 19,745,750. Output tokens 4,941,438, almost all of it the 77-way Banking77
maps. Dollar cost is not stated. Jev spend $0.

**Boundary.** One grok model, one adapter, three runs. Yelp's 9/9 is not a README
claim. Awaiting a non-author re-score before the bead closes.
