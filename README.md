# jev_playground

An experimental lab for [Jev](https://docs.typesafe.ai). You ask a typed question. You get a number. You decide, in code, what that number is allowed to do.

![A typed judgment, not a paragraph](visual/hero.jpg)

## The thing to run

A message guard, riffed from the official cookbook. One command. No key. A refund passes, a jailbreak blocks, a crisis line goes to support.

```bash
node demos/guard/demo.mjs
```

The policy is [`demos/guard/policy.mjs`](demos/guard/policy.mjs). The questions and thresholds are the ones in [`docs-mirror/typesafe/cookbooks/llm_guardrails.md`](docs-mirror/typesafe/cookbooks/llm_guardrails.md). The default lane uses recorded assessments so the routing is visible without spending. `--live` calls Jev through `askJevBundle` and needs `TYPESAFE_API_KEY`. A four-message live smoke is in [`demos/guard/live-receipt.json`](demos/guard/live-receipt.json): pass, block, block, support. N=4 is not a certification.

A RAG passage filter, riffed from the official cookbook. One command. No key. An injection is dropped, a premise-denier is kept as conflicting evidence, the merely irrelevant are dropped.

```bash
node demos/rag/demo.mjs
```

The policy is inline in [`demos/rag/demo.mjs`](demos/rag/demo.mjs) (thresholds + first-match `route()`). The questions and recorded assessments are the ones in [`docs-mirror/typesafe/cookbooks/classifying_rag_passages.md`](docs-mirror/typesafe/cookbooks/classifying_rag_passages.md). The default lane uses recorded assessments so the routing is visible without spending. `--live` scores through `askJevBundle` and needs `TYPESAFE_API_KEY`.

A citation check, riffed from the official cookbook. One command. No key. A supported claim stands, a contradicted or unsupported one goes to review, a fabricated quote is dropped.

```bash
node demos/citation/demo.mjs
```

The verdicts are inline in [`demos/citation/demo.mjs`](demos/citation/demo.mjs) (string-match locate, then the Choice from [`docs-mirror/typesafe/cookbooks/citation_check.md`](docs-mirror/typesafe/cookbooks/citation_check.md) with the 0.8 stand-or-review gate). The default lane uses recorded relations so the check is visible without spending. `--live` asks through `askJevChoice` and needs `TYPESAFE_API_KEY`. Fixture labels are not a live citation score.

A skill suggestion, riffed from the official cookbook. One command. No key. Two tasks get a skill, the third gets nothing — abstention is first-class.

```bash
node demos/skill-suggest/demo.mjs
```

The two-stage suggest with its gate lives in [`demos/skill-suggest/suggest.mjs`](demos/skill-suggest/suggest.mjs), following [`docs-mirror/typesafe/cookbooks/skill_suggestion.md`](docs-mirror/typesafe/cookbooks/skill_suggestion.md) (rank the roster, verify the top three, suggest nothing below gate). The default lane uses fixture overlap scores so the shape is visible without spending. Fixture suggestions are not a live ranking.

A job router, riffed from Movez's Jev Engineering guide step 4. One command. No key. A confident pick goes to research or write; anything unsure goes to review, never to a worker.

```bash
node demos/chief/demo.mjs
```

The choice and the confidence gate live in [`demos/chief/demo.mjs`](demos/chief/demo.mjs) (research/write/review classes, 0.85 gate, review fallback). The 0.85 bar is the guide author's number, not measured here. The default lane uses recorded verdicts so the routing is visible without spending. `--live` asks through `askJevChoice` and needs `TYPESAFE_API_KEY`. Four live jobs (`jev-1.13.0`) are in [`demos/chief/live-receipt.json`](demos/chief/live-receipt.json): three agree with the fixture, vague-ask diverged (research live, review fixture), gate not retuned. A fixture route is not a live handoff.

Instant context compaction, riffed from Movez's Jev Engineering guide step 5. One command. No key. A stale Glob is dropped with its result, a verbose Read keeps its call but loses its tail, failure evidence stays verbatim — nothing is summarized.

```bash
node demos/compact/demo.mjs
```

The transcript and the recorded keep/drop probabilities live in [`demos/compact/demo.mjs`](demos/compact/demo.mjs), executed through the vendored clone's own `compact(messages, asker, options)` (`fast-jev-compaction@6e1da50`, read-only). The default lane uses a fixture asker so the compaction is visible without spending. `--live` asks through `askJevBundle` and needs `TYPESAFE_API_KEY`. A fixture keep/drop is not a live compaction.

A function dispatcher, riffed from the official cookbook. One command. No key. Three commands dispatch to typed calls, one leaving an argument out so the default applies.

```bash
node demos/function-call/demo.mjs
```

The spec and dispatcher live in [`demos/function-call/dispatch.mjs`](demos/function-call/dispatch.mjs), following [`docs-mirror/typesafe/cookbooks/function_calling.md`](docs-mirror/typesafe/cookbooks/function_calling.md) (one Choice picks the function, each argument gets a Choice plus a stated Noul, call confidence is the least-certain judgment). The default lane uses fixture overlap scores so the dispatch is visible without spending. A fixture dispatch is not a live tool call.

A confidence-gated classification, riffed from the official cookbook. One command. No key. A sure filing reports its group, two unsure ones report the parent division — nothing is dropped.

```bash
node demos/classify/demo.mjs
```

The two-level taxonomy and gate live in [`demos/classify/classify.mjs`](demos/classify/classify.mjs), following [`docs-mirror/typesafe/cookbooks/classification_using_confidence.md`](docs-mirror/typesafe/cookbooks/classification_using_confidence.md) (one Choice over groups, report the group when sure else the division). The default lane uses fixture overlap margins so the gate is visible without spending. A fixture class is not a live label.

A passage re-rank, riffed from the official cookbook. One command. No key. A word-overlap shortlist misorders both queries; recorded nouls put the right passage first.

```bash
node demos/rerank/demo.mjs
```

The shortlist and the per-pair scores are inline in [`demos/rerank/demo.mjs`](demos/rerank/demo.mjs) (the shortlist-then-Noul shape from [`docs-mirror/typesafe/cookbooks/rerank_typesafe.md`](docs-mirror/typesafe/cookbooks/rerank_typesafe.md)). The default lane uses recorded nouls so the reorder is visible without spending. `--live` scores through `askJevBundle` and needs `TYPESAFE_API_KEY`. A fixture ranking is not a live search score.

A date extraction, riffed from the official cookbook. One command. No key. Six short documents resolve to calendar dates, a missing date stays empty, and anything under confidence 0.60 goes to review.

```bash
node demos/date/demo.mjs
```

The parts and the calendar math are inline in [`demos/date/demo.mjs`](demos/date/demo.mjs) (seven Choice questions plus code assembly from [`docs-mirror/typesafe/cookbooks/date_extraction_cookbook.md`](docs-mirror/typesafe/cookbooks/date_extraction_cookbook.md), pinned TODAY so relative dates reproduce). The default lane uses recorded part answers so the assembly is visible without spending. `--live` asks through `askJevBundle` and needs `TYPESAFE_API_KEY`. A fixture date is not a live extraction.

An entity alignment, riffed from the official cookbook. One command. No key. Identical products merge, different ones stay unlinked, and close variants go to a curator.

```bash
node demos/entity/demo.mjs
```

The score plus three Nouls are inline in [`demos/entity/demo.mjs`](demos/entity/demo.mjs) (one Score with three level-descriptions plus name/maker/style questions from [`docs-mirror/typesafe/cookbooks/entity_alignment.md`](docs-mirror/typesafe/cookbooks/entity_alignment.md); the nearest level names the outcome, no threshold constant). The default lane uses recorded answers so the routing is visible without spending. `--live` asks through `askJevBundle` and needs `TYPESAFE_API_KEY`. A fixture alignment is not a live match.

A hierarchical classification, riffed from the official cookbook. One command. No key. Greedy takes the top child and cannot recover; beam search keeps two paths by geometric-mean probability and repairs the early mistake.

```bash
node demos/hierarchy/demo.mjs
```

The tree and the per-node distributions are inline in [`demos/hierarchy/demo.mjs`](demos/hierarchy/demo.mjs) (one Choice per sibling set plus greedy-and-beam traversal from [`docs-mirror/typesafe/cookbooks/hierarchical_classification.md`](docs-mirror/typesafe/cookbooks/hierarchical_classification.md)). The default lane uses recorded distributions so the recovery is visible without spending. `--live` asks through `askJevChoice` and needs `TYPESAFE_API_KEY`. A fixture class is not a live label.

A structure recovery, riffed from the official cookbook. One command. No key. Wrapped lines stitch, blocks classify to heading/code/warning/list, and the memo renders as markdown.

```bash
node demos/autoformat/demo.mjs
```

The stitch and classify rules live in [`demos/autoformat/recover.mjs`](demos/autoformat/recover.mjs), following [`docs-mirror/typesafe/cookbooks/autoformat.md`](docs-mirror/typesafe/cookbooks/autoformat.md) (per-pair mid-sentence Nouls, then per-block Choice). The default lane uses deterministic rules so the recovery is visible without spending. A fixture format is not a live rewrite.

A parallel briefing, riffed from the official cookbook. One command. No key. One document, four questions of three types, all answered from a single fixture request object.

```bash
node demos/parallel/demo.mjs
```

The briefing lives in [`demos/parallel/brief.mjs`](demos/parallel/brief.mjs), following [`docs-mirror/typesafe/cookbooks/parallel_questions.md`](docs-mirror/typesafe/cookbooks/parallel_questions.md) (batching changes cost and speed, not answers). The default lane uses recorded answers so the briefing is visible without spending. A fixture briefing is not a live judgment.

A line-by-line search, riffed from the official cookbook. One command. No key. One query points at its line, another reads as unanswered — the exists check tells them apart.

```bash
node demos/semantic-find/demo.mjs
```

The ranking plus existence check live in [`demos/semantic-find/find.mjs`](demos/semantic-find/find.mjs), following [`docs-mirror/typesafe/cookbooks/semantic_find.md`](docs-mirror/typesafe/cookbooks/semantic_find.md) (Choice over line IDs plus an independent Noul). The default lane uses fixture overlap scores so the search is visible without spending. A fixture find is not a live search.

A verify cascade, riffed from the official cookbook. One command. No key. A schema-valid extraction still gets escalated when a per-field head fires; the overall head is displayed, never gating.

```bash
node demos/cascade/demo.mjs
```

The per-field battery lives in [`demos/cascade/verify.mjs`](demos/cascade/verify.mjs), following [`docs-mirror/typesafe/cookbooks/sde_cascade.md`](docs-mirror/typesafe/cookbooks/sde_cascade.md) (cheap extract, then Noul heads where true means escalate). The default lane uses recorded Nouls so the escalation is visible without spending. A fixture cascade is not a live verification.

An ontology gate, two rules from EvoOntology (arXiv:2609.15779). One command. No key. Query the term instead of pasting the layer; ship a candidate only if it beats its parent.

```bash
node demos/ontology-gate/demo.mjs
```

The rules are inline in [`demos/ontology-gate/demo.mjs`](demos/ontology-gate/demo.mjs). The paper's numbers stay the paper's (+20 and +8.8 Traj-Wise are theirs, not ours); this file only shows the decision rules on fixtures. A fixture gate is not their benchmark.

Self-consistency over a borderline post, riffed from the official cookbook. One command. No key. Eight Choices repeat five times; the action flips twice and one repeat abstains, but every plurality holds above the gate.

```bash
node demos/consistency/demo.mjs
```

The gate is inline in [`demos/consistency/demo.mjs`](demos/consistency/demo.mjs) (argmax with abstain below 0.60 from [`docs-mirror/typesafe/cookbooks/consistency_choice_cookbook.md`](docs-mirror/typesafe/cookbooks/consistency_choice_cookbook.md)). The default lane uses recorded distributions so the wobble is visible without spending. `--live` asks through `askJevBundle` and needs `TYPESAFE_API_KEY`. A fixture consistency check is not a live agreement score.

Self-consistency over a borderline claim, riffed from the official cookbook. One command. No key. Fourteen Nouls repeat five times; `covered` crosses 0.50 yet never leaves review, while two questions each flip once at an outer edge.

```bash
node demos/consistency-noul/demo.mjs
```

The review band is inline in [`demos/consistency-noul/demo.mjs`](demos/consistency-noul/demo.mjs) (no below 0.30, uncertain 0.30-0.70 inclusive, yes above, from [`docs-mirror/typesafe/cookbooks/consistency_noul_cookbook.md`](docs-mirror/typesafe/cookbooks/consistency_noul_cookbook.md)). The default lane uses recorded nouls so the band is visible without spending. A fixture noul check is not a live probability.

Pre-parsed value extraction, riffed from the official cookbook. One command. No key. Regexes over-find the candidate spans, recorded picks choose the receipt address, the mobile, the total and the credit, and code copies each verbatim into a normalized form.

```bash
node demos/preparsed/demo.mjs
```

The find-and-take shape is inline in [`demos/preparsed/demo.mjs`](demos/preparsed/demo.mjs) (recall-tuned regex, Choice-over-spans with a `none` hatch, verbatim copy plus code-side normalization from [`docs-mirror/typesafe/cookbooks/pre_parsed_value_extraction_cookbook.md`](docs-mirror/typesafe/cookbooks/pre_parsed_value_extraction_cookbook.md)). The default lane runs the regexes for real and uses recorded picks so the shape is visible without spending. `--live` asks through `askJevBundle` and needs `TYPESAFE_API_KEY`. Fixture picks are not live extraction judgments.

## TL;DR

Jev does not write prose. It scores a state you supply and returns a probability, a choice, or a rubric level. This repo keeps the questions we have actually measured, the scripts that reproduce them, and the caller you can copy so you do not rebuild the client, the cut, or the comparison from scratch.

| If you want | Run |
|---|---|
| A tour with no key | `bash scripts/quickstart.sh` |
| The injection result, re-scored | `python3 work/nev-differential/analyze_diff.py` |
| The policy, with a fake model | `node --test work/nev-injection/seat-guard.test.mjs` |
| A caller that fails closed | [`work/jev-client`](work/jev-client/README.md) |

## Installation

```bash
git clone https://github.com/JYeswak/jev_playground.git
cd jev_playground
```

Node 20 or newer. Python 3 for `analyze_diff.py`. A live call needs `TYPESAFE_API_KEY` in the environment, loaded from outside this tree. Do not print it. Do not commit a response that contains someone else's data.

## Quick start

```bash
git clone https://github.com/JYeswak/jev_playground.git
cd jev_playground
bash scripts/quickstart.sh
```

No API key. No package install. Five questions, answered from files already in the tree. `--mine` points the same tools at your logs.

Node 20 or newer. Python 3 only for the injection re-score.

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
  // missing key, timeout, or a body the schema refused — review it
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

The screen on top of that caller is [`.omp/tools/jev-screen.ts`](.omp/tools/jev-screen.ts). Flag at 0.5, pass below, review otherwise. It does not block. Your code does.

## Measurements

Numbers below are what the named file contains. Re-run the command. If the file and this page disagree, the file wins.

**Prompt injection.** Public `jev-sec-bench` rows, n=662, cut 0.5, model `jev-1.13.0`.

| Arm | Correct | Accuracy |
|---|---:|---:|
| Jev, cited from the bench file | 639/662 | 0.9653 |
| grok-4, same questions, official adapter | 558/662 | 0.8429 |
| Claude Haiku 4.5, same questions | 579/662 | 0.8746 |

Discordant pairs: Jev right and grok-4 wrong on 89, the reverse on 8. Jev right and Haiku wrong on 65, the reverse on 5. The pre-registered rule passes on this corpus only.

```bash
python3 work/nev-differential/analyze_diff.py
```

Receipt: [`work/nev-differential/DIFF-RECEIPT.json`](work/nev-differential/DIFF-RECEIPT.json).

**The cut, with no model in the loop.** A planted hostile message flags. A planted benign message passes. A broken answer is review.

```bash
node --test work/nev-injection/seat-guard.test.mjs
```

**Calibration.** Labelled held-out set, N=80, pinned model: ECE 0.0614, Brier 0.0195, choice 19/20. Receipt: [`foundation/runs/20260922T021352Z.json`](foundation/runs/20260922T021352Z.json).

**A case where a classifier is the better instrument.** On tool-call harm, a small rule beat a live judge. The check is `node work/omp-harm-rule/verify-claim.mjs`. Use it when the label is already in the tokens.

## Method

This is the part worth stealing. Each step has a script.

1. **Pin the model.** `jev-1.13.0`. `jev-latest` moves, and a percent without a model id cannot be cited next week.
2. **Write the rule before you spend.** Corpus, cut, comparator, and sample size go in a file first. `work/nev-differential/PREREGISTER-DIFF.md` is the shape.
3. **Compare to something a person would actually ship.** A chat model on the same state, or a classifier trained on labels. A regex is the floor.
4. **Call the official SDK.** `work/jev-client` owns retry, timeout, and the refusal of a bad body. A hand-rolled `fetch` drifts.
5. **Test the policy with an injected transport.** No key, no network. `node --test work/nev-injection/seat-guard.test.mjs`.
6. **Leave the rows.** `python3 work/nev-differential/analyze_diff.py` re-scores the committed comparison without a key.

Vendor docs are mirrored under `docs-mirror/typesafe/`. `./scripts/sync-docs.sh --check` confirms the bytes.

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


## Commands

| Command | What you get |
|---|---|
| `bash scripts/quickstart.sh` | Five answers from committed bytes |
| `bash scripts/quickstart.sh --mine` | The same questions on your logs |
| `python3 work/nev-differential/analyze_diff.py` | The injection table, recomputed |
| `node --test work/nev-injection/seat-guard.test.mjs` | Flag, pass, and review, with no model |
| `node scripts/jev-probe.mjs --replay docs/demos/jev-probe/probe-response-20260918.json` | A recorded judgment, decoded. Drop `--replay` only when you mean to spend |
| `./scripts/sync-docs.sh --check` | The vendored docs still match the manifest |

## Limitations

- The injection result is one public corpus, one cut, one run. Measure your own traffic before you gate on it.
- Some questions in this tree are a better fit for a regex or a trained classifier. The harm-rule check is the worked example.
- A tool that loads in a session is not a measurement of live traffic.
- Cloned repos in this tree belong to their authors. Read them. Do not push them.

## FAQ

**Do I need a key to see if the repo runs?** No. `bash scripts/quickstart.sh` is enough.

**Which model id should I pin?** `jev-1.13.0`, until you re-measure and name the id you used.

**Why not POST the API myself?** You can. The wrapper exists so a missing key, a timeout, and a bad body fail the same way, and so tests never need a network.

**What do I do with a bad response?** Review it. Do not treat it as safe.

## About Contributions

> *About Contributions:* Please don't take this the wrong way, but I do not accept outside contributions for any of my projects. I simply don't have the mental bandwidth to review anything, and it's my name on the thing, so I'm responsible for any problems it causes; thus, the risk-reward is highly asymmetric from my perspective. I'd also have to worry about other "stakeholders," which seems unwise for tools I mostly make for myself for free. Feel free to submit issues, and even PRs if you want to illustrate a proposed fix, but know I won't merge them directly. Instead, I'll have Claude or Codex review submissions via `gh` and independently decide whether and how to address them. Bug reports in particular are welcome. Sorry if this offends, but I want to avoid wasted time and hurt feelings. I understand this isn't in sync with the prevailing open-source ethos that seeks community contributions, but it's the only way I can move at this velocity and keep my sanity.

## License

MIT. See [`LICENSE`](LICENSE).
