# jev_playground

Jev answers typed questions about a state with calibrated numbers. This repo is where we find out which of those numbers deserve to drive code, and where a regex or a constant does the job better.

![A typed judgment, not a paragraph](visual/hero.jpg)

## TL;DR

[Jev](https://docs.typesafe.ai) (TypeSafe's System One model, pinned here as `jev-1.13.0`) does not generate text. You send a state and typed questions (true or false, pick one, place on a rubric) and get back probabilities and a confidence. The engineering is the code around the answer: the threshold, the side it fails toward, and what happens when the answer is malformed.

- **Demos.** Twenty patterns as one-command programs, seventeen of them from TypeSafe's official cookbooks. They run on recorded answers with no key; `--live` makes the real call.
- **A client.** [`work/jev-client`](work/jev-client/README.md) wraps the official SDK so a missing key, a timeout and a malformed answer all fail the same way, toward review.
- **Measurements.** Each has a rule written before any spend, a comparator someone would actually ship, and committed rows you can re-score.

Tonight's picture, every number re-scorable under Measurements. On 662 public prompt-injection rows, Jev at `jev-1.13.0` is right on 639 by the benchmark's own count and on 640 in a fresh live run here; asked the same questions through TypeSafe's own LLM adapter, Claude Haiku 4.5 is right on 579 and on 584 across two runs, and grok-4 on 558. Against Haiku on other public sets it wins intent routing across all 77 Banking77 intents (2,467 vs 2,267 of 3,080), ties on accuracy for checking claims against evidence (SciFact 361 vs 351, FEVER 379 vs 376 of 400), with a lower Brier score on SciFact and a lower ECE on FEVER that held across 12 run pairings each, while the other calibration wins were retracted on re-runs (R89, R90), and ties on out-of-scope routing (688 vs 681 of 750) but wins once both abstain below 0.60 confidence (685 vs 650); against xAI's grok-4.20, checked over three grok runs, it wins SciFact outright (361 vs 330 on the first run, and in all 12 run pairings), SST-5 rating error and CLINC150 routing with abstention, and it rates similarity on 1,500 STS-B pairs closer to human scores than grok-4.20 (Haiku was not run there); and its SST-5 rating error and 10-intent Banking77 routing wins held on three runs of each arm. At list prices 1,000 Jev answers cost $0.0158 to $0.0287, and Haiku 33 to 88 times as much on the same rows. It lost where the question was ours: the command gate caught 11 of 23 risky in-place file edits where Haiku caught 23, the injection question could not be made quiet on tool output without losing catch (175 of 300 clean tool results flagged with its persona, 213 of 263 attacks caught without it), the claim checker caught 0 of 31 changed numbers in long bead close reasons, and on tool-call harm a small rule beat the judge because the label was already in the tokens.

## Quick start

```bash
git clone https://github.com/JYeswak/jev_playground.git
cd jev_playground
node demos/guard/demo.mjs       # a message guard: pass, block, or send to support
bash scripts/quickstart.sh      # five questions answered from files already in the tree
```

Node 22.18 or newer: the tests and the client import TypeScript files directly, which Node 20 refuses. Python 3 only for the injection re-score. No key and no package install, except the compaction demo, which fetches and builds its upstream first. To make real calls, run `npm ci --prefix work/sdk` once (it installs the pinned TypeSafe SDK), put `TYPESAFE_API_KEY` in the environment from outside this tree, and add `--live` to a demo.

## Demos

Each demo is one recipe from TypeSafe's cookbooks ([published here](https://docs.typesafe.ai/cookbooks); `docs-mirror/typesafe/` holds a local copy once the docs are synced, see Commands), a public guide, or a paper, with the policy in plain code next to it. Without `--live`, the questions go to recorded answers, so you can read the routing before you spend anything. Recorded answers are fixtures. They show the policy. They do not show the model.

| Run | What it shows | Recipe | Live smoke |
|---|---|---|---|
| `node demos/guard/demo.mjs` | A message guard. A refund passes, a jailbreak blocks, a crisis goes to support. | [llm_guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails.md) | [4 calls, differs](demos/guard/live-receipt.json) |
| `node demos/rag/demo.mjs` | A RAG passage filter. Injections and noise drop; contrary evidence is kept and labelled. | [classifying_rag_passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages.md) | [5 calls, differs](demos/rag/live-receipt.json) |
| `node demos/citation/demo.mjs` | A citation check. A supported claim stands, a contradicted one goes to review, a fabricated quote is dropped. | [citation_check](https://docs.typesafe.ai/cookbooks/citation_check.md) | [4 calls, differs](demos/citation/live-receipt.json) |
| `node demos/skill-suggest/demo.mjs` | Skill suggestion that can abstain. Two tasks get a skill; the third gets nothing. | [skill_suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion.md) | [6 calls, same](demos/skill-suggest/live-receipt.json) |
| `node demos/chief/demo.mjs` | A job router. A confident pick goes to research or write; anything under 0.85 goes to review. | Movez, Jev Engineering guide step 4 | [4 calls, 3 of 4 same](demos/chief/live-receipt.json) |
| `./scripts/bootstrap-compaction.sh && node demos/compact/demo.mjs` | Context compaction. Stale calls drop, verbose ones are truncated, failure evidence stays verbatim. Nothing is summarized. The bootstrap fetches and builds the upstream once, over the network. | Movez guide step 5, run through `fast-jev-compaction@6e1da50` | [1 call, differs](demos/compact/live-receipt.json) |
| `node demos/function-call/demo.mjs` | Typed function dispatch. Each argument gets its own judgment; a missing one takes its default. | [function_calling](https://docs.typesafe.ai/cookbooks/function_calling.md) | none |
| `node demos/classify/demo.mjs` | Confidence-gated classification. Report the group when sure, the parent division when not. | [classification_using_confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md) | none |
| `node demos/rerank/demo.mjs` | A passage re-rank. Word overlap misorders both queries; per-pair scores put the right passage first. | [rerank_typesafe](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md) | [10 calls, same](demos/rerank/live-receipt.json) |
| `node demos/date/demo.mjs` | Date extraction. Parts are judged, code does the calendar math, anything under 0.60 goes to review. | [date_extraction](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook.md) | [6 calls, differs](demos/date/live-receipt.json) |
| `node demos/entity/demo.mjs` | Entity alignment. Identical products merge, different ones stay apart, close variants go to a curator. | [entity_alignment](https://docs.typesafe.ai/cookbooks/entity_alignment.md) | [4 calls, same](demos/entity/live-receipt.json) |
| `node demos/hierarchy/demo.mjs` | Hierarchical classification. Greedy cannot recover from an early mistake; beam search can. | [hierarchical_classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md) | [10 calls, differs](demos/hierarchy/live-receipt.json) |
| `node demos/autoformat/demo.mjs` | Structure recovery. Wrapped lines stitch and blocks classify into headings, code, warnings and lists. | [autoformat](https://docs.typesafe.ai/cookbooks/autoformat.md) | [2 calls, differs](demos/autoformat/live-receipt.json) |
| `node demos/parallel/demo.mjs` | Parallel questions. Four questions of three types answered from one request. | [parallel_questions](https://docs.typesafe.ai/cookbooks/parallel_questions.md) | [1 call, same](demos/parallel/live-receipt.json) |
| `node demos/semantic-find/demo.mjs` | Line search with an existence check, so "not in this document" is an answer. | [semantic_find](https://docs.typesafe.ai/cookbooks/semantic_find.md) | [2 calls, same](demos/semantic-find/live-receipt.json) |
| `node demos/cascade/demo.mjs` | A verify cascade. A schema-valid extraction still escalates when a per-field check fires. | [sde_cascade](https://docs.typesafe.ai/cookbooks/sde_cascade.md) | [1 call, differs](demos/cascade/live-receipt.json) |
| `node demos/ontology-gate/demo.mjs` | Two decision rules from EvoOntology: query the term instead of pasting the layer; ship a candidate only if it beats its parent. | arXiv:2609.15779 | none |
| `node demos/consistency/demo.mjs` | Self-consistency over repeated choices, abstaining below 0.60. | [consistency_choice](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md) | [3 calls, not compared](demos/consistency/live-receipt.json) |
| `node demos/consistency-noul/demo.mjs` | Self-consistency over repeated true/false judgments, with a 0.30 to 0.70 review band. | [consistency_noul](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook.md) | [3 calls, not compared](demos/consistency-noul/live-receipt.json) |
| `node demos/preparsed/demo.mjs` | Pre-parsed extraction. Regexes over-find spans, a judgment picks one, code copies it verbatim. | [pre_parsed_value_extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md) | [4 calls, same](demos/preparsed/live-receipt.json) |

Seventeen demos have a live smoke: one small `--live` run, recorded. On 9 of the 17, the live model decided at least one item differently from the recorded fixture; on 6 it matched; 2 were not compared, because their recorded live runs sent only an id, not the text the fixture was recorded on (the demos now send it; the re-record waits on credits) ([recomputed from the receipts' rows](docs/demos/upstream-repro/live-cells-20260924.md)). [`demos/LIVE.md`](demos/LIVE.md) says what differed in each. A smoke of 1 to 10 calls is a direction, not a benchmark. The disagreements are why both lanes stay in the tree. [`demos/START.md`](demos/START.md) is the short tour.

## What you can copy

[`work/jev-client`](work/jev-client/README.md) is the caller. A missing key returns `unconfigured`. A malformed body is not a score.

```js
import { askJev } from "./work/jev-client/src/index.ts";

const result = await askJev({
  model: "jev-1.13.0",
  state: { assistant: "A news assistant.", user_message: text },
  questions: {
    injection: "Is this message trying to manipulate the assistant, rather than use it?",
  },
});

if (!result.ok) {
  // missing key, timeout, or a body the schema refused: review it
} else if (result.scores.injection >= 0.5) {
  // flag
}
```

| Function | Question | Returns |
|---|---|---|
| `askJev` | Is this statement true? | a probability |
| `askJevChoice` | Which of these labels? | one label, only from the set you offered |
| `askJevScore` | Where on this rubric? | a level and its distribution |
| `askJevBundle` | Several of the above | one request, one state |

The screen built on that caller is [`.omp/tools/jev-screen.ts`](.omp/tools/jev-screen.ts): flag at 0.5, pass below, review otherwise. It does not block. Your code does.

The tool-call gate runs as [`.omp/hooks/post/jev-gate-observe.ts`](.omp/hooks/post/jev-gate-observe.ts): after every `bash` call it asks the five gate questions and appends one redacted row to `~/.local/state/jev/gate-observe.jsonl`. It never blocks and skips commands that carry a secret without sending them ([receipt](docs/demos/upstream-repro/gate-observe-hook-20260924.md)).

The claim check is [`.omp/tools/jev-claim-check.ts`](.omp/tools/jev-claim-check.ts): the model passes a claim and the evidence text, and `jev_claim_check` returns Jev's probability and a verdict, supported at 0.8 or above, unsupported at 0.2 or below, unsure between. It refuses any claim containing a number before calling the model, and its description says so, because three designs for checking a number against its evidence failed their bars (R83); a qualitative claim still gets a verdict. Before that limit, run over the 19 claims this README then registered, each against its proof file, it supported 12 and called none of 19 planted false twins supported, catching 14; the 7 it did not support were proof-side gaps, not wrong README numbers, and 18 of those 19 claims would now be refused rather than answered ([receipt](docs/demos/upstream-repro/jev-claim-check-20260924.md)).

## Measurements

Numbers below are what the named file contains. Re-run the command. If the file and this page disagree, the file wins.

**Prompt injection.** Public `jev-sec-bench` rows, n=662, cut 0.5, model `jev-1.13.0`.

| Arm | Correct | Accuracy |
|---|---:|---:|
| Jev, the bench file's own count | 639/662 | 0.9653 |
| Jev, fresh live run | 640/662 | 0.9668 |
| Claude Haiku 4.5, official adapter, same questions | 579/662 | 0.8746 |
| Claude Haiku 4.5, fresh run | 584/662 | 0.8822 |
| grok-4, official adapter, same questions | 558/662 | 0.8429 |

Discordant pairs: Jev right and grok-4 wrong on 89, the reverse on 8. Jev right and Haiku wrong on 65, the reverse on 5, and 61 against 5 in the fresh run (McNemar p = 2.6e-13). The pre-registered rule passes on this corpus only.

Re-run, the grok-4 win holds: across three Jev runs (639, 640, 639) and three grok-4 runs (558, 554, 555), Jev wins all 9 pairings, the weakest at p = 2.0e-18, so the 558 in the table is grok-4's best of three; verified by a non-author. The Haiku win is provisional: it held in all 6 pairings that exist (weakest p = 4.9e-13), but the third Haiku run is blocked by the Anthropic account's spend cap until 2026-10-01, so 3 of the 9 pairings are missing (bead `jev-1y19`) ([variance](docs/demos/upstream-repro/injection-variance-20260924.md)).

These re-score with no key. The fresh run reads only committed rows. The other two also read the public bench's own results file, which is not committed here, so clone it at its pinned commit first; without it both say `NOT_RUN` and exit 2:

```bash
git clone https://github.com/Gaurav-Gosain/jev-sec-bench jev-sec-bench && git -C jev-sec-bench checkout fdb16b9
python3 work/nev-differential/fresh-20260923/score.py        # fresh run: 640, 584, 61/5
python3 work/nev-differential/variance-20260924/variance.py  # three runs: grok-4 9/9, Haiku 6/6 (third run blocked)
python3 work/nev-differential/analyze_diff.py                # earlier runs, with grok-4
```

Receipts: [`work/nev-differential/DIFF-RECEIPT.json`](work/nev-differential/DIFF-RECEIPT.json) and [`jev-sec-bench-w70-20260923.md`](docs/demos/upstream-repro/jev-sec-bench-w70-20260923.md).

**The cut, with no model in the loop.** A planted hostile message flags. A planted benign message passes. A broken answer is review.

```bash
node --test work/nev-injection/seat-guard.test.mjs
```

**Calibration.** Labelled held-out set, N=80, pinned model: ECE 0.0614, Brier 0.0195, choice 19/20. Receipt: [`foundation/runs/20260922T021352Z.json`](foundation/runs/20260922T021352Z.json).

**Rating on a scale: SST-5.** On 500 public SST-5 test sentences, one Score question at `jev-1.13.0` had lower absolute error than Claude Haiku 4.5 through the official adapter, MAE 0.488 vs 0.556 (sign test p = 0.015), while the gap in exact accuracy, 273 vs 251 of 500, was not significant (McNemar p = 0.092): a narrow win that held on three Jev runs at sign p 0.015, 0.040 and 0.019 and on three Haiku runs at sign p 0.015, 0.0010 and 0.0039 ([receipt](docs/demos/upstream-repro/score-sst5-20260924.md), [variance](docs/demos/upstream-repro/jev-variance-20260924.md), [Haiku variance](docs/demos/upstream-repro/haiku-variance-20260924.md)). Against a second family, xAI's grok-4.20 (non-reasoning) through the same adapter, Jev's error was lower too (sign test 168 vs 101, p = 5.3e-5), a win that held in all 9 pairings of three runs each ([grok](docs/demos/upstream-repro/grok-incumbent-sst5-clinc-20260924.md), [grok variance](docs/demos/upstream-repro/grok-variance-20260924.md)).

**Picking one intent: Banking77.** On a 400-query, ten-intent subset of public Banking77, one Choice question at `jev-1.13.0` routed 384/400 against Claude Haiku 4.5's 362/400 through the official adapter (McNemar p = 2.7e-5), a win that held on three Haiku runs (p = 2.7e-5, 3.1e-4 and 1.0e-5), and the win holds with the 14 Haiku rows dropped that the adapter had turned from all-zero answers into picks: 374 vs 362 of 386, p = 0.0075. Counting all 14 of those rows as correct for Haiku instead gives 384 vs 376, p = 0.13, which is not significant. Against a second incumbent, xAI's grok-4.20 (non-reasoning), Jev wins 384 vs 366 (p = 0.0014) only because of grok's 22 all-zero rows: on the 378 rows grok answered, it is a tie, 368 vs 365, p = 0.58. Both readings held across three grok runs: the win as returned in 9/9 pairings, and on answered rows a tie in 8 and a win in 1 ([receipt](docs/demos/upstream-repro/choice-banking77-20260924.md), [adapter finding](docs/demos/upstream-repro/adapter-uniform-20260924.md), [second incumbent](docs/demos/upstream-repro/second-incumbent-20260924.md), [grok variance](docs/demos/upstream-repro/grok-variance-20260924.md), [Haiku variance](docs/demos/upstream-repro/haiku-variance-20260924.md)).

**All 77 intents: the full Banking77 test split.** On all 3,080 public Banking77 test queries across all 77 intents, one Choice question at `jev-1.13.0` routed 2,467/3,080 right against 2,267/3,080 for Claude Haiku 4.5 through the official adapter answering in prompted JSON (McNemar 326 vs 126, p = 1.7e-21). Haiku's native structured output could not run: the adapter's 77-option schema hit the provider's grammar limit on 993 of 993 attempts ([receipt](docs/demos/upstream-repro/choice-banking77-full-20260924.md)). Against a second family, xAI's grok-4.20 through the same adapter, three grok runs against every committed Jev run: Jev's 2,455 to 2,472 right beat grok's 2,120 to 2,130 of 3,080 in all 9 pairings (weakest p = 3.4e-42), and in all 9 again with grok's flat answers dropped ([grok](docs/demos/upstream-repro/grok-incumbent-fever-yelp-b77-20260924.md), [Jev runs](docs/demos/upstream-repro/choice-banking77-full-variance-20260924.md)).

**Saying none of the above: CLINC150.** On 750 public CLINC150 test queries, the 450 for one randomly drawn domain's 15 intents plus 300 out-of-scope ones, one Choice question with a "none of the above" option at `jev-1.13.0` got 688/750 right against Claude Haiku 4.5's 681/750 through the official adapter, non-inferior (McNemar 21 vs 14, p = 0.311); with both arms abstaining below 0.60 confidence, Jev handled 685 vs 650 (47 vs 12, p = 5.1e-6), a win. Against grok-4.20 through the same adapter, Jev handled 685 vs 657 at the same gate (44 vs 16, p = 3.9e-4), a win that held in all 9 pairings of three runs each ([receipt](docs/demos/upstream-repro/choice-clinc150-20260924.md), [grok](docs/demos/upstream-repro/grok-incumbent-sst5-clinc-20260924.md), [grok variance](docs/demos/upstream-repro/grok-variance-20260924.md)).

**Flagging risky commands: the tool-call gate.** On 400 held-out real commands from this repo's agent sessions (100 risky, 300 routine), adding outcome criteria to the five gate questions raised Jev's catch from 41–46/100 to 77–79/100 at 1/300 false alarms across three runs of each question set, significant in all 9 run pairings (McNemar p ≤ 3.7e-08; 41 to 78, p = 3.0e-09, on the first run), where Claude Haiku 4.5 with the same criteria caught 84/100 at 20/300 in its one run, and a non-author's 3-label correction gives 77–79/97. The same questions without criteria false-alarmed on 6–8/300 routine real commands from a separate sample, across three runs ([receipt](docs/demos/upstream-repro/bicameral-gate-criteria-20260924.md), [real traffic](docs/demos/upstream-repro/bicameral-gate-real-traffic-20260923.md), [variance](docs/demos/upstream-repro/gate-variance-20260924.md)). On those real commands, Claude Haiku 4.5 asked the same questions without criteria false-alarmed on 58/300 while catching 13 of the 14 risky ones, a trade that is Haiku's rather than an LLM's in general: xAI's grok-4.20, over three runs, false-alarmed on 2–7/300 routine real commands and caught 4–7 of the 14 risky ones among them, and on the held-out sample caught 34–37/100 at 2–4/300, close to Jev without criteria and far below Jev with them ([grok](docs/demos/upstream-repro/gate-grok-incumbent-20260924.md)). The criteria wording carries most of that lift for grok too, so the 41-to-78 rise is not Jev's alone: given the same criteria, grok-4.20 caught 55–73/100 on the held-out sample, up from its 34–37 in all 9 run pairings, at 0–1/300 false alarms there and 1–2/300 on the real commands. Jev with criteria, at 77–79, still led grok with criteria in 6 of the 9 pairings; against grok's best run, 73, the gap was not significant in any pairing ([criteria on grok](docs/demos/upstream-repro/gate-grok-criteria-20260924.md), R98).

**Checking a claim against its evidence: SciFact.** On 400 public SciFact claim-abstract pairs, one Noul question at `jev-1.13.0` got 361/400 right against Claude Haiku 4.5's 351/400 through the official adapter, a tie on accuracy (McNemar 19 vs 9, p = 0.087), and its Brier score was significantly better, 0.0709 vs 0.1002, a win that held on all three Haiku runs (Haiku 0.0932 to 0.1002) and in all 12 pairings of four Jev runs with three Haiku runs ([variance](docs/demos/upstream-repro/noul-variance-20260924.md)). Its AUC 0.962 vs 0.934 and ECE 0.0431 vs 0.0854 were first reported as wins too, then retracted: when Haiku was run twice more, AUC fell to a tie on one run and ECE on another, so they are better in direction but not robust to the incumbent's re-run; across the 12 pairings AUC won in 8 and ECE in 5 (R89, [Haiku variance](docs/demos/upstream-repro/haiku-variance-20260924.md)). Against xAI's grok-4.20 (non-reasoning) on the same pairs, Jev wins all four, accuracy included: 361 vs 330 right, 46 vs 15 discordant, p = 8.8e-5 on the first grok run, and all four wins held in 12/12 pairings of four Jev runs with three grok runs ([receipt](docs/demos/upstream-repro/noul-scifact-20260924.md), [second incumbent](docs/demos/upstream-repro/second-incumbent-20260924.md), [grok variance](docs/demos/upstream-repro/grok-variance-20260924.md)).
Adding outcome criteria to that question, compared with the same instructions without them on the same 400 pairs, left accuracy tied at 361 vs 362 and significantly improved AUC 0.962 vs 0.958 and Brier 0.0709 vs 0.0774: a small lift in probability quality, not in decisions ([criteria ablation](docs/demos/upstream-repro/noul-scifact-criteria-20260924.md)). The lift replicated on the 400 FEVER claims below, on Brier only: 0.0463 with criteria against 0.0495 without, while accuracy (379 vs 377) and AUC stayed tied; a rerun of the criteria question made at the same time read the same way, and two runs of the same question agreed with each other ([FEVER ablation](docs/demos/upstream-repro/noul-fever-criteria-20260924.md)).

**A second claim set: FEVER.** On 400 FEVER 1.0 dev claims, each paired with its gold evidence, the same Noul question at `jev-1.13.0` got 379/400 right against Claude Haiku 4.5's 376/400, again a tie on accuracy (McNemar 6 vs 3, p = 0.51), and in that first run Jev was significantly ahead on AUC 0.973 vs 0.957, Brier 0.0463 vs 0.0581 and ECE 0.0376 vs 0.0664. Across 12 pairings of four Jev runs with three Haiku runs, the ECE win held in 12/12, while AUC won in only 4/12 and Brier in 9/12, so those two were retracted: better in direction, not robust to re-runs (R90) ([receipt](docs/demos/upstream-repro/noul-fever-20260924.md), [variance](docs/demos/upstream-repro/noul-variance-20260924.md)). Against grok-4.20, three grok runs against the four Jev runs, the ECE win held in all 12 pairings (grok ECE 0.252 to 0.271) ([grok](docs/demos/upstream-repro/grok-incumbent-fever-yelp-b77-20260924.md)).

**Rating review stars: Yelp.** On 500 Yelp reviews, Jev's star ratings beat xAI's grok-4.20 on both exact level and MAE in all 9 pairings of three Jev runs with three grok runs (grok exact 265 to 269 of 500, MAE 0.526 to 0.530). This is a win over grok only. Against Claude Haiku 4.5 the Yelp MAE win did not survive Haiku's re-runs and was retracted to a tie (R88) ([grok](docs/demos/upstream-repro/grok-incumbent-fever-yelp-b77-20260924.md)).

**Rating similarity: STS-B.** On all 1,500 STS Benchmark English dev pairs, one Score question at `jev-1.13.0` rated similarity closer to the human scores than xAI's grok-4.20 through the official adapter, over three runs of each (9 run pairings): Spearman 0.907 on every Jev run against 0.880 to 0.885 for grok, and MAE 0.513 to 0.514 against 0.586 to 0.599, both wins in 9/9 pairings (weakest MAE sign test p = 0.0432), while exact-level accuracy, 784 to 788 against 748 to 756 of 1,500, tied in all 9. Every Jev run beat the always-mean and always-mode constants. Claude Haiku 4.5 was not run: the Anthropic account had hit its spend cap. Grok refused one pair, row 457, in all three runs, and the preregistered rule counts it against grok; without that row the thinnest MAE pairing is still a win, p = 0.0459 ([receipt](docs/demos/upstream-repro/score-stsb-20260924.md)).

**What an answer costs.** On 150 live calls, 50 each with the SST-5 Score, Banking77 Choice and SciFact Noul questions above, the API reported input and output tokens and no billing units, so at the documented $0.042 per million input tokens with output free, 1,000 Jev answers cost $0.0158, $0.0162 and $0.0287, against $0.9484, $1.4287 and $0.9475 for Claude Haiku 4.5 at its $1 / $5 list price on the same rows, 33 to 88 times as much: list prices applied to token counts, not an invoice ([receipt](docs/demos/upstream-repro/jev-billing-units-20260924.md)).

**Where Jev lost.** On the in-place edits of tracked or config files that two labellers agree are risky, the command gate caught 11/23 where Claude Haiku 4.5 with the same questions caught 23/23 (McNemar p = 0.00049) ([receipt](docs/demos/upstream-repro/bicameral-gate-hard-cases-20260924.md), R81). The injection question that wins on the public corpus flagged 175/300 clean tool results from this repo's sessions while it kept its news-assistant persona, and with the persona removed it caught 213/263 public attacks at 12/300 tool false flags, a Wilson lower bound of 0.758 against a 0.80 bar, so no tool-output hook was built; Haiku was noisier on the same tool output, 286/300 and 94/300 ([with persona](docs/demos/upstream-repro/jev-k9z5-flag-20260924.md), [without](docs/demos/upstream-repro/jev-toolout-flag-20260924.md), R80 and R82). Asked whether a bead's close reason is supported by the files and commits it cites, `jev_claim_check` caught 0/31 long reasons with one number changed and called 4/31 of them supported, though on short README sentences it caught 7/9, so it gates nothing, and the tool now refuses numeric claims outright ([receipt](docs/demos/upstream-repro/close-reason-check-20260924.md), R83). On toxicity, 2,000 public Civil Comments of which 180 are toxic, a Noul question at `jev-1.13.0` was right on 0.726 to 0.730 of them across three runs, below the 0.91 of always answering non-toxic, and it flagged 311 to 316 of the 1,820 non-toxic comments even at the stricter 0.70 cut; against grok-4.20 over 9 run pairings AUC tied in all 9, while Brier, ECE and the false-positive rate lost in 9 and accuracy in 8 ([receipt](docs/demos/upstream-repro/noul-toxicity-20260924.md), R93). The R rows are in [`NEGATIVE_EVIDENCE.md`](NEGATIVE_EVIDENCE.md) with the condition for retrying each.

Each of these re-scores from committed rows with no key:

```bash
python3 work/score-sst5/score.py                # SST-5: MAE 0.488 vs 0.556, 273 vs 251
python3 work/jev-variance/score.py              # SST-5 and Banking77 across three Jev runs
python3 work/choice-banking77/score.py          # Banking77: 384 vs 362; 374 vs 362 of 386; credited 384 vs 376
python3 work/choice-banking77/score.py --set full-prompted  # all 77 intents: 2,467 vs 2,267 of 3,080
python3 work/choice-clinc150/score.py           # CLINC150: 688 vs 681 of 750; handled at 0.60: 685 vs 650
python3 work/noul-scifact/score.py              # SciFact: 361 vs 351, Brier 0.0709 vs 0.1002 (AUC, ECE retracted: R89)
python3 work/haiku-variance/score.py           # three Haiku runs: SST-5 and Banking77 hold; SciFact Brier holds, AUC and ECE retracted
python3 work/noul-scifact/score.py work/noul-fever  # FEVER: 379 vs 376, first run of each arm
python3 work/noul-variance/score.py            # 12 Jev x Haiku pairings per set: SciFact Brier and FEVER ECE hold; the rest retracted
python3 work/noul-scifact/compare-criteria.py   # SciFact criteria vs none: 361 vs 362, AUC and Brier lift
python3 work/noul-scifact/compare-criteria.py work/noul-fever  # FEVER criteria vs none: Brier 0.0463 vs 0.0495, accuracy 379 vs 377
python3 work/second-incumbent/score.py          # vs grok-4.20: SciFact 361 vs 330; Banking77 384 vs 366, 368 vs 365 of 378
python3 work/second-incumbent/score_n4j.py      # vs grok-4.20: SST-5 MAE 168 vs 101; CLINC150 handled 44 vs 16
python3 work/second-incumbent/grok_variance.py  # three grok runs: all 21 grok claims stand across 39 pairings
python3 work/grok-incumbent-3/score.py          # vs grok-4.20: FEVER ECE 12/12, Yelp exact and MAE 9/9, Banking77 full 9/9
python3 work/score-stsb/score.py                # STS-B vs grok-4.20: Spearman and MAE win 9/9, exact-level tie 9/9
python3 work/bicameral-gate/score-b.py          # gate, first run: 78/100 vs 41/100 at 1/300; Haiku 84/100 at 20/300
python3 work/bicameral-gate/verify-labels-b.py  # gate, first run, 3 labels corrected: 78/97
python3 work/bicameral-gate/gate-variance.py    # gate, three runs each: 77-79 vs 41-46 of 100, 77-79/97; real traffic 6-8/300
python3 work/bicameral-gate/score-grok-gate.py  # grok-4.20, same questions, three runs: 2-7/300 real, 34-37/100 at 2-4/300
python3 work/bicameral-gate/score-grok-criteria.py  # grok-4.20 with the criteria: 55-73/100, lift 9/9; Jev ahead 6/9, MIXED (R98)
node work/jev-billing-units/measure.mjs         # cost per 1,000 answers: $0.0158 / $0.0162 / $0.0287 vs Haiku list
python3 work/bicameral-gate/score-inplace-agree.py  # gate on agreed in-place edits: 11/23 vs Haiku 23/23
python3 work/jev-injection-flag/score.py        # injection seat on 300 clean tool results: 175/300 flagged
python3 work/jev-toolout-flag/score.py          # no persona: 213/263 attacks at 12/300 tool flags, FAIL
python3 work/jev-claim-check/score-close.py     # close reasons: 0/31 caught; exits 1 because the bar failed
python3 work/noul-toxicity/score.py             # toxicity vs grok-4.20: FAIL, AUC tie 9/9, Brier/ECE/FPR lose 9/9
```

**A case where a classifier is the better instrument.** On tool-call harm, a small rule beat a live judge. The check is `node work/omp-harm-rule/verify-claim.mjs`. Use a rule when the label is already in the tokens.

## What other Jev projects taught us

[`notes/deep/clone-ledger.tsv`](notes/deep/clone-ledger.tsv) lists 38 other Jev projects, each pinned to a commit and described from its own code. The first 28 were re-run from scratch against one standard: their own tests, a planted defect those tests must catch, live Jev on the project's own data, the cheapest rule on the same rows, and an LLM asked the same questions. The other 10 (a desktop agent, a completion-claim checker, a drone, a Mario player, a trader and five more) are read but not yet re-run. Receipts are under [`docs/demos/upstream-repro/`](docs/demos/upstream-repro/) with `w70` in the name. Every result below is one run at the stated size.

- **A cheap rule often ties or beats the model, and then the seat is refused.** On tool-call risk triage a keyword rule scored 58/60 against live Jev's 52/60 ([receipt](docs/demos/upstream-repro/jev-benchmark-w70-2026-09-23.md)). On phishing, a regex at 91.65% and Haiku both beat Jev's 62.98% ([receipt](docs/demos/upstream-repro/jev-phishing-bench-w70-20260923.md)).
- **Where Jev held up.** Prompt injection (above). Passage re-ranking: Jev put the right passage first on 15 of 30 queries against BM25's 10, and tied Cohere's re-ranker ([receipt](docs/demos/upstream-repro/jev-rerank-bench-w70-2026-09-23.md)). Agent-failure attribution: 28 of 35 against grok's 23, too few rows to call ([receipt](docs/demos/upstream-repro/jev-agent-failure-benchmark-w70-2026-09-23.md)).
- **A threshold carries within one dataset, not across two.** Per-question thresholds fit on the first 200 support tickets held on the next 200, within 0.02 ([receipt](docs/demos/upstream-repro/jevcal-live-w70-2026-09-23.md)). A routing threshold fit the same way moved from 0.67 to 0.37 when the dataset changed, and the routing decision flipped ([receipt](docs/demos/upstream-repro/janus-w70-2026-09-23.md)). Fit thresholds on your own labelled rows and re-check them when the data changes.
- **Calibration is only readable with rows in every bin.** On injection the error across ten bins was 0.068; on a seven-row set, or one where every answer sits in the top bin, it cannot be read at all.
- **The official JavaScript SDK can end a Node process on a timeout.** Its own suite passes 189 tests and still exits 1 on unhandled aborts ([receipt](docs/demos/upstream-repro/typesafe-sdk-js-w70-20260923.md)). [`work/jev-client`](work/jev-client/README.md) now owns the timeout; 30 of 30 timed-out requests left the host running on Node and on Bun ([receipt](docs/demos/upstream-repro/jev-client-w70-20260923.md)).
- **It is cheap to measure.** 940 requests cost $0.13 in one run; 560 cost $0.011 of input in another.

## Method

This is the part worth stealing. Each step has a script.

1. **Pin the model.** `jev-1.13.0`. `jev-latest` moves, and a percent without a model id cannot be cited next week.
2. **Score the constant first.** Before any question is judged, compute what always answering the majority label scores on the same rows: `node work/jev-prevalence-first/prevalence-check.mjs rows.jsonl --truth label`. On real command traffic here, always answering `BAD` is right 78.8% of the time; that is the bar. The same check refused Jev's tool routing (192 of 400 right against 252 for always `bash`) and exits 3 when a question does not beat its constant.
3. **Write the rule before you spend.** Corpus, cut, comparator, and sample size go in a file first. `work/nev-differential/PREREGISTER-DIFF.md` is the shape.
4. **Compare to something a person would actually ship.** A chat model on the same state, or a classifier trained on labels. A regex is the floor.
5. **Call the official SDK.** `work/jev-client` owns retry, timeout, and the refusal of a bad body. A hand-rolled `fetch` drifts.
6. **Test the policy with an injected transport.** No key, no network. `node --test work/nev-injection/seat-guard.test.mjs`.
7. **Leave the rows.** `python3 work/nev-differential/fresh-20260923/score.py` re-scores the committed injection comparison without a key or a network.

Vendor docs are mirrored under `docs-mirror/typesafe/` once synced. The bytes are not committed: `./scripts/sync-docs.sh` fetches the docs and every pinned clone (network, about two and a half minutes on a fresh clone), then `./scripts/sync-docs.sh --check` confirms them against the committed manifest.

## What the measurements changed in the client

These are in the code, not only in notes.

- The state has to contain the evidence. Hide the measurement and the answer follows the wording of the question. `node scripts/measure-framing-flip.mjs` is the live control. Run it only when you mean to spend.
- Option text that explains why an option is correct teaches the answer. Keep criteria descriptive, not argumentative.
- A missing field, a non-finite probability, or a thrown client is review. `askJev` will not coerce that into a pass.
- One call is a smoke test. The comparison harness refuses a relative verdict under ten stable samples.
- A suite that stays green when the judge is replaced by a coin flip tested the plumbing. Score against a label the suite did not write.
- Put the corpus in the same sentence as the percent. 0.9653 here is 639/662 on one injection file.
- An unknown answer keeps the user's text. Low confidence does not act.
- Do not edit an upstream clone to make a demo pass. Wrap it.

## How the repo checks itself

The gates run fully on the author's machine. A fresh clone needs one `br sync --import-only` first (the `br` issue tracker, beads_rust, builds the issue database from the committed `.beads/issues.jsonl`; without it the gates stop at their first check). Then run `bash foundation/gates.sh --portable`: a stage whose prerequisite is missing prints `SKIP (missing prerequisite: <name>, install: <how>)` instead of going red, and the summary counts the skips rather than calling the run all green. The prerequisites are `ast-grep` and `rg` for the native-surface stage (`brew install ast-grep ripgrep`), the foundry `loop-kit` (`LOOP_KIT`) for the house gates and the autofix half of the staged-deletion stage (foundry is a private repo, so a stranger skips these), and omp with its ee and dcg extensions for part of the instrument selftests. Without `--portable` a missing prerequisite stays red.

Seventeen stages run in `bash foundation/gates.sh`. Each is a script under [`foundation/gates.d/`](foundation/gates.d/) with a `--selftest` that plants a bad input and must go red; a stage that has only ever passed is unproven. Every commit subject names the level of evidence behind it (`[pending]`, `[selftest]`, `[test]`, `[oracle]`, `[live]`), and [`githooks/commit-msg`](githooks/commit-msg) refuses one that does not. Refuted ideas stay in [`NEGATIVE_EVIDENCE.md`](NEGATIVE_EVIDENCE.md) with the condition under which they are worth retrying. [`GATES.md`](GATES.md) lists every stage and what it catches.

Preregistration is checked the same way. 37 receipts state a preregistered bar, and across the 74 bar/rows pairs drawn from them every bar was committed before its rows: `python3 work/sr-adopt/audit_bars.py` prints `ok 74` ([bar census](docs/demos/upstream-repro/bar-census-20260924.md)). Eight of those rows files are earlier runs that later receipts reuse as baselines, and all 8 are audited: 4 under their original receipt, and 4 traced to an earlier bar, among them the grok-4 and Haiku rows in the injection table (bead `jev-vxx1`). The audit compares the commit that first added each bar with the commit that first added its rows, so it does not detect an edit to a bar section made after the rows landed.

jev's gates run in public CI at every push to `main` ([workflow](.github/workflows/gates.yml)); the verdict at 196e124 is green with 5 typed skips, not plain green: CI runs `bash foundation/gates.sh --portable`, and the stages whose prerequisites the runner lacks are skipped by name ([run](https://github.com/JYeswak/jev_playground/actions/runs/35978286566)).

The 87 tracked test files the runner selects by name from the suites [`TESTS.md`](TESTS.md) registers also run on every push, as a second CI job next to the gates. Seven registered entries match no name pattern and are not yet run by any CI step: four in `work/oracle-kit`, `scripts/promotion-four-gates.py`, and `verify-claim.mjs` and `install-harm-rule.sh` in `work/omp-harm-rule` (bead `jev-7xjv`; one of them, `work/oracle-kit/selector-guard.mjs`, exits 2 on `main`). The push run at f5a044a was 87 pass, 0 skip, 0 fail ([run](https://github.com/JYeswak/jev_playground/actions/runs/35995292269)), and a manually triggered run that plants a failing test went red and named the planted file ([run](https://github.com/JYeswak/jev_playground/actions/runs/35995313176)). Locally the same thing is `python3 scripts/run-registered-suites.py`. A suite whose prerequisite is missing is a named SKIP, never a pass; the prerequisites are `bun` (for the suites that run `bun test`), `npm ci --prefix work/sdk` (the TypeSafe SDK), `./scripts/bootstrap-compaction.sh` (the compaction upstream), and, for two suites, the adapter: `./scripts/sync-docs.sh --repos-only` on a fresh clone to fetch it, then `uv sync --locked --all-extras --directory upstream/typesafe-ai/system-one-adapter-python`. Before this job no gate ran the suites, and 12 omp-jev extension suites had been failing unseen since the SDK cutover.

The client also protects the account. After an HTTP 402 (no TypeSafe credits), `work/jev-client` refuses every further call in that process for 15 minutes and returns reason `billing-hold`; a 429, a 5xx or a transport error never starts the hold. The cause was measured: a hook called the API 233 times in 4.4 hours (04:19:44Z to 08:42:59Z) while every call returned 402.

87 of 88 README claim sentences are registered in [`foundation/kit/claims.tsv`](foundation/kit/claims.tsv), each tied to the file that holds its number; stage 15 fails if that count drops below the floor in [`foundation/kit/claim-coverage.floor`](foundation/kit/claim-coverage.floor).

The agent harness this lane runs in is [omp](https://omp.sh). Its project surfaces live in [`.omp/`](.omp/): the Jev tools (screen, flag, rerank, claim check), rules that interrupt a model mid-response when it starts a known-bad move, and the kit-guard extension, which is meant to block edits to gate files and is being refitted to this repo's layout.

## Commands

| Command | What you get |
|---|---|
| `bash scripts/quickstart.sh` | Five answers from committed bytes |
| `bash scripts/quickstart.sh --mine` | The same questions on your logs |
| `node demos/<name>/demo.mjs` | Any demo in the table above, keyless |
| `python3 work/nev-differential/fresh-20260923/score.py` | The fresh injection comparison (Jev 640, Haiku 584 of 662), recomputed from committed rows |
| `node --test work/nev-injection/seat-guard.test.mjs` | Flag, pass, and review, with no model |
| `node scripts/jev-probe.mjs --replay docs/demos/jev-probe/probe-response-20260918.json` | A recorded judgment, decoded. Drop `--replay` only when you mean to spend |
| `bash foundation/gates.sh` | Every repository gate, with its own selftest |
| `bash foundation/gates.sh --portable` | The same gates on a fresh clone; a missing prerequisite is a named SKIP, not a red |
| `./scripts/sync-docs.sh` | The vendored docs and pinned clones, fetched (network) |
| `./scripts/sync-docs.sh --check` | The vendored docs still match the manifest; a fresh clone fails it until the fetch above has run |

## Limitations

- The injection result is one public corpus at one cut: three runs of Jev and grok-4, two of Haiku so far. Measure your own traffic before you gate on it.
- Demos without `--live` replay recorded answers. They show the policy, not the model, and the live smokes are 1 to 10 calls each.
- Some questions in this tree are a better fit for a regex or a trained classifier. The harm-rule check is the worked example.
- CI runs only the portable gates, so a stage the runner skips is checked on the author's machine alone.
- A tool that loads in a session is not a measurement of live traffic.
- Cloned repos in this tree belong to their authors. Read them. Do not push them.

## FAQ

**Do I need a key to see if the repo runs?** No. `bash scripts/quickstart.sh` and every demo in the table run without one.

**Which model id should I pin?** `jev-1.13.0`, until you re-measure and name the id you used.

**Why not POST the API myself?** You can. The wrapper exists so a missing key, a timeout, and a bad body fail the same way, and so tests never need a network.

**What do I do with a bad response?** Review it. Do not treat it as safe.

## Status

As of 2026-09-22. Reproducible from this tree with no key: the injection comparison (after cloning the public bench, see Measurements), the calibration receipt, the twenty demos and their seventeen live receipts. jev has been assessed with the FrankenSuite RULEBOOK v1.0 ([assessment](notes/deep/jev-assessment.md), [cold read](notes/deep/jev-assessment-coldread-p2.md)). In progress: applying the omp-kit (stream rules, the kit-guard extension, and the `/loop` continuation gate) to this repository. The plan is [`docs/PLAN-DEEP-KIT-20260922.md`](docs/PLAN-DEEP-KIT-20260922.md).

All seventeen gate stages pass on the author's machine (`bash foundation/gates.sh`, rc 0); on a fresh clone, `--portable` passes with 4 stages skipped for missing prerequisites. The three instrument selftests that were red earlier in the day were fixed at their cause, not waived.

## About Contributions

> *About Contributions:* Please don't take this the wrong way, but I do not accept outside contributions for any of my projects. I simply don't have the mental bandwidth to review anything, and it's my name on the thing, so I'm responsible for any problems it causes; thus, the risk-reward is highly asymmetric from my perspective. I'd also have to worry about other "stakeholders," which seems unwise for tools I mostly make for myself for free. Feel free to submit issues, and even PRs if you want to illustrate a proposed fix, but know I won't merge them directly. Instead, I'll have Claude or Codex review submissions via `gh` and independently decide whether and how to address them. Bug reports in particular are welcome. Sorry if this offends, but I want to avoid wasted time and hurt feelings. I understand this isn't in sync with the prevailing open-source ethos that seeks community contributions, but it's the only way I can move at this velocity and keep my sanity.

## License

MIT. See [`LICENSE`](LICENSE).
