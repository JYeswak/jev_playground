# Rerank question cost: the one-passage Noul against the shipped rubric on NevIR (bead `jev-k9z.9`)

CopperHeron (pane at index 2, Anthropic model), 2026-09-24. Live lane: TypeSafe only, model
`jev-1.13.0`. **No comparator model is called.** **PREPARED-NOT-MEASURED** until the rows land.

## Why

- `jev-k9z.7` showed that on BEIR SciFact the shipped `jev_rerank` rubric and the one-passage Noul
  of `work/rerank-scifact/run.py` TIE in all 9 pairings.
- The rubric costs 10.7× the input tokens there, because each of its 20 requests carries all 20
  passages.
- The rubric was chosen on NevIR (`jev-rerank-bench@cd9a35b`, `JevScoreBatch` 0.7115 paired
  accuracy), and the Noul has never run on NevIR.
- If the Noul is not worse there, `jev_rerank` could ask it instead.

## What upstream already measured (read, keyless)

`jev-rerank-bench@cd9a35b` (anessbelbati, MIT), scored with `nevir_eval.py`, strict paired
accuracy: a pair is right only if both questions rank their own passage strictly higher, and a tie
is wrong. The per-question cache is committed under `cache/<arm>/nevir.present.jsonl.gz`, and
every call in it is `jev-1.13.0`, 2026-09-16.

| Arm | Question | Pairs right / 1,383 | Input tokens / question |
|---|---|---:|---:|
| `jev-score-batch` | the rubric `rank.ts` ships, both passages in one request with 2 questions | 984 (0.7115) | 833 |
| `jev-noul-pair` | a **different** one-passage Noul ("Does the passage contain the information needed to answer or verify the query?") | 980 (0.7086) | 1,043 |
| `bm25` | the floor | 31 (0.0224) | 0 |

`jev-noul-pair` is not this bead's question. The question here is run.py's: *"Does this passage
contain evidence relevant to the query?"*, whose true criterion reads *"… states evidence a reader
could use in assessing it, **whether or not that evidence supports the query**"*.

**Prediction, stated before any call; it doesn't enter the rule:** both passages of a NevIR pair are
on the query's subject and state evidence about it, and they differ only by a negation. So run.py's
Noul should call both relevant and score them close together. I expect it to be clearly worse than
the rubric.

## Arms (all live, `jev-1.13.0`, same 2,766 questions)

**Data.**
- Questions come from `jev-rerank-bench/candidates/nevir.jsonl`, sha256 `0c3acd0d…2e07`: 2,766
  questions over 1,383 pairs, each question with its pair's `d1` and `d2` in that fixed order.
- Passage text comes from NevIR `test.jsonl` at HF revision
  `6263585072ce3b435ed09658613553fbf4e74184`, sha256 `5eb79ec3…5d67` (MIT).
- The texts are used raw: none exceeds the bench's 2,000-character truncation (the longest is
  1,316), and all 2,766 queries match the candidates file.

**Noul arm, `noul`, `noul-run2`, `noul-run3`** (`work/rerank-nevir/nevir.py`):
- It imports run.py's `QUESTION`, `state_for`, `row_ok` and `billing_block` and restates none of
  them.
- It sends one request per (question, passage), whose state holds that passage only, in run.py's
  shape with `title: ""`.
- It uses the SDK's `AsyncTypeSafeClient` with the default `RetryPolicy`, 4 requests in flight, and
  run.py's 120 s timeout.
- That is 5,532 requests per run.

**Rubric arm, `tool`, `tool-run2`, `tool-run3`** (`work/rerank-nevir/tool.mjs`):
- It runs the shipped tool's path, `rerank()` + `liveAsker`, imported unchanged. That is one
  validated Score request per passage, each state holding both passages.
- It uses `work/rerank-tool-scifact/run.mjs`'s accounting and resume logic, imported. `run.mjs`
  was changed only to export them and to dispatch only when run as a script, and its `--selftest`
  still passes.
- 4 questions are in flight, and each question makes 2 requests in series: 5,532 requests per run.

**Committed reference:** upstream's `jev-score-batch` cache, as a third arm for every Noul run.

**Failures.**
- A Noul pair that fails gets one more attempt in the same invocation.
- A tool question left `ordered=false` gets one more attempt.
- A question still missing a score is scored wrong and counted.
- More than **27** failed questions (1%) in a run makes that run NOT-SCORED, and the unit
  outcome becomes NOT-SCORED.
- A 402 stops dispatch.

Both arms refuse before any call unless this file is committed and clean
(`work/sr-adopt/phase_gate.py` `require_bar`).

## The fixed rule

**Metric.** NevIR paired accuracy, strict, as `nevir_eval.py` defines it.

**Pairings.** Each Noul run against each tool re-run makes 9 pairings, and each Noul run against the
committed `jev-score-batch` makes 3 more.
- The difference is Noul − rubric, over the 1,383 pairs.
- The interval is a paired bootstrap: 2,000 resamples of pair indices with
  `random.Random(20260924).randrange`, reseeded per pairing, taking the 95% percentile interval
  (the sorted differences at positions 50 and 1,949).
- WIN if the lower bound > 0, LOSE if the upper bound < 0, TIE otherwise.

**Feasibility arms (both must pass, or there is NO RULING).**
- f1: `nevir.py`'s scorer, run on upstream's committed `jev-score-batch` cache, gives exactly
  984/1,383. This is checked keyless now and passes in `--selftest`.
- f2: every tool re-run scores paired accuracy ≥ 0.65. That checks the shipped path reproduces
  the rubric's NevIR level.

**Outcomes.**
- **NOT-WORSE:** no LOSE among all 12 pairings. File a separate bead to switch `jev_rerank` to the
  Noul question.
- **WORSE:** LOSE on all 9 re-run pairings. No switch, and a `NEGATIVE_EVIDENCE.md` row.
- **MIXED:** anything else. Report the numbers, with no switch.

**Reported beside the rule:** question accuracy, how often both questions got the same top pick
(the "ignored the negation" signature), failures, requests, and input tokens per question from the
server's `usage`. Prevalence is fixed by construction: each question has exactly one right passage
of two, so random picking scores 25% paired.

**NO-CLAIM.**
- One dataset (negation pairs), one model pin, 3 runs per arm.
- A WORSE says only that run.py's wording loses on negation. It says nothing about
  `jev-noul-pair`'s wording, which upstream measured at 0.7086.
- On NevIR the cost ratio is not SciFact's 10.7×, because a pair has 2 passages, not 20.

## Commands

```
PY=upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python
$PY work/rerank-nevir/nevir.py --selftest
node --experimental-strip-types work/rerank-nevir/tool.mjs --selftest
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- $PY work/rerank-nevir/nevir.py noul
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/rerank-nevir/tool.mjs tool
python3 work/rerank-nevir/nevir.py score      # keyless; refuses until all six row files exist
```


## Results (live, 2026-09-24, `jev-1.13.0`): **WORSE, no switch**

The preregistration was committed at `4cb97ed` before the first call. The runs went in this order,
one at a time, attended, 23:04:32Z to 23:26:17Z: `noul`, `tool`, `noul-run2`, `tool-run2`,
`noul-run3`, `tool-run3`.
- Each run made 5,532 requests, all HTTP 200 on `jev-1.13.0`.
- No request failed, so the resume pass had nothing to retry, and no question failed.

This is `python3 work/rerank-nevir/nevir.py score`'s output, keyless, from the committed rows:

| arm | pairs right / 1383 | paired accuracy | question accuracy | same top pick | failed questions | requests | input tokens / question |
|---|---:|---:|---:|---:|---:|---:|---:|
| noul | 927 | 0.6703 | 0.8077 | 0.2726 | 0 | 5532 | 1100 |
| noul-run2 | 929 | 0.6717 | 0.8087 | 0.2675 | 0 | 5532 | 1100 |
| noul-run3 | 918 | 0.6638 | 0.8040 | 0.2711 | 0 | 5532 | 1100 |
| tool | 968 | 0.6999 | 0.8377 | 0.2777 | 0 | 5532 | 1456 |
| tool-run2 | 984 | 0.7115 | 0.8467 | 0.2697 | 0 | 5532 | 1456 |
| tool-run3 | 989 | 0.7151 | 0.8456 | 0.2625 | 0 | 5532 | 1456 |
| committed | 984 | 0.7115 | 0.8474 | 0.2697 | 0 | - | - |

- **f1 PASS.** The scorer gives the committed `jev-score-batch` 984/1,383.
- **f2 PASS.** The tool runs score 968, 984 and 989.
- No run is over the 27-question ceiling.

| Noul run | vs | diff (Noul - rubric) | 95% interval | verdict |
|---|---|---:|---|---|
| noul | tool | -0.0296 | [-0.0521, -0.0065] | LOSE |
| noul | tool-run2 | -0.0412 | [-0.0636, -0.0202] | LOSE |
| noul | tool-run3 | -0.0448 | [-0.0665, -0.0224] | LOSE |
| noul | committed | -0.0412 | [-0.0629, -0.0195] | LOSE |
| noul-run2 | tool | -0.0282 | [-0.0513, -0.0051] | LOSE |
| noul-run2 | tool-run2 | -0.0398 | [-0.0629, -0.0188] | LOSE |
| noul-run2 | tool-run3 | -0.0434 | [-0.0658, -0.0210] | LOSE |
| noul-run2 | committed | -0.0398 | [-0.0622, -0.0174] | LOSE |
| noul-run3 | tool | -0.0362 | [-0.0600, -0.0130] | LOSE |
| noul-run3 | tool-run2 | -0.0477 | [-0.0701, -0.0253] | LOSE |
| noul-run3 | tool-run3 | -0.0513 | [-0.0752, -0.0282] | LOSE |
| noul-run3 | committed | -0.0477 | [-0.0709, -0.0246] | LOSE |

**Outcome by the fixed rule: WORSE.**
- The Noul LOSEs all 9 re-run pairings, and all 3 against the committed rubric as well.
- It is 0.028 to 0.051 below the rubric in paired accuracy, and every interval's upper bound is
  below −0.005.
- No switch bead is filed. `NEGATIVE_EVIDENCE.md` R101 records the refuted claim.

**Beside the rule.**
- **Cost.** On NevIR the Noul uses 1,100 input tokens a question against the rubric's 1,456: 0.76×,
  not SciFact's 1/10.7. A pair has 2 passages, so the rubric's all-passages state is small here.
  - Requests are equal: 2 per question in each arm.
  - Latency: Noul requests p50 126–148 ms and p95 276–326 ms. Tool questions, 2 requests in series,
    p50 249–276 ms and p95 459–538 ms.
- **My prediction was half wrong.** I expected run.py's Noul to call both negation variants relevant
  and score them close together. It still separates most pairs:
  - question accuracy 0.804–0.809, against the rubric's 0.838–0.847;
  - same top pick for both questions 0.268–0.273, against 0.263–0.278;
  - in run 1, the median |noul(d1) − noul(d2)| is 0.09, and 7.8% of questions tie exactly (a tie
    scores wrong).

  It loses, but by 3 to 5 points, not by the collapse I predicted.
- **Run-to-run spread.** The rubric scored 968 to 989 pairs right and the Noul 918 to 929. On
  identical inputs, each arm's input tokens were identical across its three runs.
- **The shipped path reproduces the published figure.** `tool-run2`'s 984/1,383 matches upstream's
  one-request, two-question `jev-score-batch` exactly. Splitting it into one request per passage,
  as `live.ts` does, cost nothing measurable on NevIR.

**Spend.**
- 33,192 Jev requests, 0 failed.
- 21,211,278 input tokens: 3 × 3,042,878 Noul and 3 × 4,027,548 rubric, read from the server's
  `usage`. That is **$0.89** at $0.042 per million, with output free.
- No comparator model, and no other provider.

**What this means for `jev_rerank`.**
- Keep the rubric.
- On SciFact the two questions tie (`jev-k9z.7`), and on negation the rubric wins. So the Noul's
  SciFact token saving would cost 3 to 5 points of NevIR paired accuracy.
- A cheaper tool would need a question that keeps the rubric's negation result: for example,
  upstream's `jev-noul-pair` wording, at 980/1,383 on 2026-09-16. That would be a new
  preregistered unit, not this one.

**Rows.** `work/rerank-nevir/rows-{noul,noul-run2,noul-run3}.jsonl` hold one row per (question,
passage): ids, the noul, tokens and latency. `rows-{tool,tool-run2,tool-run3}.jsonl` hold one row
per question: ids, scores, calls, statuses and tokens. No query or passage text is committed.

**NO-CLAIM.**
- One dataset: negation pairs.
- One model pin.
- run.py's wording only.
- It says nothing about other one-passage wordings, or about rerank quality outside NevIR and
  SciFact.
