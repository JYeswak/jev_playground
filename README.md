# jev_playground

Jev answers typed questions about a state with calibrated numbers. This repo is where we find out which of those numbers deserve to drive code, and where a regex or a constant does the job better.

![A typed judgment, not a paragraph](visual/hero.jpg)

## TL;DR

[Jev](https://docs.typesafe.ai) (TypeSafe's System One model, pinned here as `jev-1.13.0`) does not generate text. You send a state and typed questions (true or false, pick one, place on a rubric) and get back probabilities and a confidence. The engineering is the code around the answer: the threshold, the side it fails toward, and what happens when the answer is malformed.

- **Demos.** Twenty patterns as one-command programs, seventeen of them from TypeSafe's official cookbooks. They run on recorded answers with no key; `--live` makes the real call.
- **A client.** [`work/jev-client`](work/jev-client/README.md) wraps the official SDK so a missing key, a timeout and a malformed answer all fail the same way, toward review.
- **Measurements.** Each has a rule written before any spend, a comparator someone would actually ship, and committed rows you can re-score.

The strongest result: on 662 public prompt-injection rows, Jev is right on 639 by the benchmark's own count and on 640 in a fresh live run here. Asked the same questions through TypeSafe's own LLM adapter, Claude Haiku 4.5 is right on 579 and on 584 across two runs, and grok-4 on 558. That is one public corpus at one cut. The clearest loss: on tool-call harm, a small rule beat the judge, because the label was already in the tokens.

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
| `node demos/citation/demo.mjs` | A citation check. A supported claim stands, a contradicted one goes to review, a fabricated quote is dropped. | [citation_check](https://docs.typesafe.ai/cookbooks/citation_check.md) | [4 calls, not compared](demos/citation/live-receipt.json) |
| `node demos/skill-suggest/demo.mjs` | Skill suggestion that can abstain. Two tasks get a skill; the third gets nothing. | [skill_suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion.md) | [6 calls, same](demos/skill-suggest/live-receipt.json) |
| `node demos/chief/demo.mjs` | A job router. A confident pick goes to research or write; anything under 0.85 goes to review. | Movez, Jev Engineering guide step 4 | [4 calls, 3 of 4 same](demos/chief/live-receipt.json) |
| `./scripts/bootstrap-compaction.sh && node demos/compact/demo.mjs` | Context compaction. Stale calls drop, verbose ones are truncated, failure evidence stays verbatim. Nothing is summarized. The bootstrap fetches and builds the upstream once, over the network. | Movez guide step 5, run through `fast-jev-compaction@6e1da50` | [1 call, differs](demos/compact/live-receipt.json) |
| `node demos/function-call/demo.mjs` | Typed function dispatch. Each argument gets its own judgment; a missing one takes its default. | [function_calling](https://docs.typesafe.ai/cookbooks/function_calling.md) | none |
| `node demos/classify/demo.mjs` | Confidence-gated classification. Report the group when sure, the parent division when not. | [classification_using_confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md) | none |
| `node demos/rerank/demo.mjs` | A passage re-rank. Word overlap misorders both queries; per-pair scores put the right passage first. | [rerank_typesafe](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md) | [10 calls, same](demos/rerank/live-receipt.json) |
| `node demos/date/demo.mjs` | Date extraction. Parts are judged, code does the calendar math, anything under 0.60 goes to review. | [date_extraction](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook.md) | [6 calls, differs](demos/date/live-receipt.json) |
| `node demos/entity/demo.mjs` | Entity alignment. Identical products merge, different ones stay apart, close variants go to a curator. | [entity_alignment](https://docs.typesafe.ai/cookbooks/entity_alignment.md) | [4 calls, not compared](demos/entity/live-receipt.json) |
| `node demos/hierarchy/demo.mjs` | Hierarchical classification. Greedy cannot recover from an early mistake; beam search can. | [hierarchical_classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md) | [10 calls, differs](demos/hierarchy/live-receipt.json) |
| `node demos/autoformat/demo.mjs` | Structure recovery. Wrapped lines stitch and blocks classify into headings, code, warnings and lists. | [autoformat](https://docs.typesafe.ai/cookbooks/autoformat.md) | [2 calls, differs](demos/autoformat/live-receipt.json) |
| `node demos/parallel/demo.mjs` | Parallel questions. Four questions of three types answered from one request. | [parallel_questions](https://docs.typesafe.ai/cookbooks/parallel_questions.md) | [1 call, same](demos/parallel/live-receipt.json) |
| `node demos/semantic-find/demo.mjs` | Line search with an existence check, so "not in this document" is an answer. | [semantic_find](https://docs.typesafe.ai/cookbooks/semantic_find.md) | [2 calls, same](demos/semantic-find/live-receipt.json) |
| `node demos/cascade/demo.mjs` | A verify cascade. A schema-valid extraction still escalates when a per-field check fires. | [sde_cascade](https://docs.typesafe.ai/cookbooks/sde_cascade.md) | [1 call, differs](demos/cascade/live-receipt.json) |
| `node demos/ontology-gate/demo.mjs` | Two decision rules from EvoOntology: query the term instead of pasting the layer; ship a candidate only if it beats its parent. | arXiv:2609.15779 | none |
| `node demos/consistency/demo.mjs` | Self-consistency over repeated choices, abstaining below 0.60. | [consistency_choice](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md) | [3 calls, not compared](demos/consistency/live-receipt.json) |
| `node demos/consistency-noul/demo.mjs` | Self-consistency over repeated true/false judgments, with a 0.30 to 0.70 review band. | [consistency_noul](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook.md) | [3 calls, not compared](demos/consistency-noul/live-receipt.json) |
| `node demos/preparsed/demo.mjs` | Pre-parsed extraction. Regexes over-find spans, a judgment picks one, code copies it verbatim. | [pre_parsed_value_extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md) | [4 calls, same](demos/preparsed/live-receipt.json) |

Seventeen demos have a live smoke: one small `--live` run, recorded. On 8 of the 17, the live model routed at least one item differently from the recorded fixture; on 5 it matched; 4 were not compared item by item. [`demos/LIVE.md`](demos/LIVE.md) says what differed in each. A smoke of 1 to 10 calls is a direction, not a benchmark. The disagreements are why both lanes stay in the tree. [`demos/START.md`](demos/START.md) is the short tour.

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

The claim check is [`.omp/tools/jev-claim-check.ts`](.omp/tools/jev-claim-check.ts): the model passes a claim and the evidence text, and `jev_claim_check` returns Jev's probability and a verdict, supported at 0.8 or above, unsupported at 0.2 or below, unsure between. Run over the 19 claims this README registers, each against its proof file, it supported 12 and called none of 19 planted false twins supported, catching 14. The 7 it did not support were proof-side gaps, not wrong README numbers ([receipt](docs/demos/upstream-repro/jev-claim-check-20260924.md)).

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

Discordant pairs: Jev right and grok-4 wrong on 89, the reverse on 8. Jev right and Haiku wrong on 65, the reverse on 5, and 61 against 5 in the fresh run (McNemar p = 2.6e-13). The pre-registered rule passes on this corpus only. Both comparisons re-score from committed rows with no key:

```bash
python3 work/nev-differential/analyze_diff.py                # earlier runs, with grok-4
python3 work/nev-differential/fresh-20260923/score.py        # fresh run: 640, 584, 61/5
```

Receipts: [`work/nev-differential/DIFF-RECEIPT.json`](work/nev-differential/DIFF-RECEIPT.json) and [`jev-sec-bench-w70-20260923.md`](docs/demos/upstream-repro/jev-sec-bench-w70-20260923.md).

**The cut, with no model in the loop.** A planted hostile message flags. A planted benign message passes. A broken answer is review.

```bash
node --test work/nev-injection/seat-guard.test.mjs
```

**Calibration.** Labelled held-out set, N=80, pinned model: ECE 0.0614, Brier 0.0195, choice 19/20. Receipt: [`foundation/runs/20260922T021352Z.json`](foundation/runs/20260922T021352Z.json).

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
7. **Leave the rows.** `python3 work/nev-differential/analyze_diff.py` re-scores the committed comparison without a key.

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

A fresh clone needs one `br sync --import-only` before the gates run. It takes the `br` issue tracker (beads_rust) and builds the issue database from the committed `.beads/issues.jsonl`; without it the gates stop at their first check.

Seventeen stages run in `bash foundation/gates.sh`. Each is a script under [`foundation/gates.d/`](foundation/gates.d/) with a `--selftest` that plants a bad input and must go red; a stage that has only ever passed is unproven. Every commit subject names the level of evidence behind it (`[pending]`, `[selftest]`, `[test]`, `[oracle]`, `[live]`), and [`githooks/commit-msg`](githooks/commit-msg) refuses one that does not. Refuted ideas stay in [`NEGATIVE_EVIDENCE.md`](NEGATIVE_EVIDENCE.md) with the condition under which they are worth retrying. [`GATES.md`](GATES.md) lists every stage and what it catches.

The agent harness this lane runs in is [omp](https://omp.sh). Its project surfaces live in [`.omp/`](.omp/): the Jev tools (screen, flag, rerank, claim check), rules that interrupt a model mid-response when it starts a known-bad move, and the kit-guard extension, which is meant to block edits to gate files and is being refitted to this repo's layout.

## Commands

| Command | What you get |
|---|---|
| `bash scripts/quickstart.sh` | Five answers from committed bytes |
| `bash scripts/quickstart.sh --mine` | The same questions on your logs |
| `node demos/<name>/demo.mjs` | Any demo in the table above, keyless |
| `python3 work/nev-differential/analyze_diff.py` | The injection table, recomputed |
| `node --test work/nev-injection/seat-guard.test.mjs` | Flag, pass, and review, with no model |
| `node scripts/jev-probe.mjs --replay docs/demos/jev-probe/probe-response-20260918.json` | A recorded judgment, decoded. Drop `--replay` only when you mean to spend |
| `bash foundation/gates.sh` | Every repository gate, with its own selftest |
| `./scripts/sync-docs.sh` | The vendored docs and pinned clones, fetched (network) |
| `./scripts/sync-docs.sh --check` | The vendored docs still match the manifest; a fresh clone fails it until the fetch above has run |

## Limitations

- The injection result is one public corpus, one cut, one run. Measure your own traffic before you gate on it.
- Demos without `--live` replay recorded answers. They show the policy, not the model, and the live smokes are 1 to 10 calls each.
- Some questions in this tree are a better fit for a regex or a trained classifier. The harm-rule check is the worked example.
- The gates run locally. There is no CI yet, so a commit made with `--no-verify` is caught by nothing.
- A tool that loads in a session is not a measurement of live traffic.
- Cloned repos in this tree belong to their authors. Read them. Do not push them.

## FAQ

**Do I need a key to see if the repo runs?** No. `bash scripts/quickstart.sh` and every demo in the table run without one.

**Which model id should I pin?** `jev-1.13.0`, until you re-measure and name the id you used.

**Why not POST the API myself?** You can. The wrapper exists so a missing key, a timeout, and a bad body fail the same way, and so tests never need a network.

**What do I do with a bad response?** Review it. Do not treat it as safe.

## Status

As of 2026-09-22. Reproducible from this tree with no key: the injection comparison, the calibration receipt, the twenty demos and their seventeen live receipts. In progress: applying the omp-kit (stream rules, the kit-guard extension, and the `/loop` continuation gate) and the FrankenSuite assessment protocol to this repository, including an assessment of this repo under the same rulebook. The plan is [`docs/PLAN-DEEP-KIT-20260922.md`](docs/PLAN-DEEP-KIT-20260922.md).

All seventeen gate stages pass (`bash foundation/gates.sh`, rc 0). The three instrument selftests that were red earlier in the day were fixed at their cause, not waived.

## About Contributions

> *About Contributions:* Please don't take this the wrong way, but I do not accept outside contributions for any of my projects. I simply don't have the mental bandwidth to review anything, and it's my name on the thing, so I'm responsible for any problems it causes; thus, the risk-reward is highly asymmetric from my perspective. I'd also have to worry about other "stakeholders," which seems unwise for tools I mostly make for myself for free. Feel free to submit issues, and even PRs if you want to illustrate a proposed fix, but know I won't merge them directly. Instead, I'll have Claude or Codex review submissions via `gh` and independently decide whether and how to address them. Bug reports in particular are welcome. Sorry if this offends, but I want to avoid wasted time and hurt feelings. I understand this isn't in sync with the prevailing open-source ethos that seeks community contributions, but it's the only way I can move at this velocity and keep my sanity.

## License

MIT. See [`LICENSE`](LICENSE).
