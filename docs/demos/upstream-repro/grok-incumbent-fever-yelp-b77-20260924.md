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

NOT_RUN.
