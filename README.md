# jev_playground

An experimental lab for [Jev](https://docs.typesafe.ai). You ask a typed question. You get a number. You decide, in code, what that number is allowed to do.

![A typed judgment, not a paragraph](visual/hero.jpg)

## The thing to run

A message guard, riffed from the official cookbook. One command. No key. A refund passes, a jailbreak blocks, a dosage request goes to review, a crisis line goes to support.

```bash
node demos/guard/demo.mjs
```

The policy is [`demos/guard/policy.mjs`](demos/guard/policy.mjs). The questions and thresholds are the ones in [`docs-mirror/typesafe/cookbooks/llm_guardrails.md`](docs-mirror/typesafe/cookbooks/llm_guardrails.md). The default lane uses recorded assessments so the routing is visible without spending. `--live` calls Jev through `askJevBundle` and needs `TYPESAFE_API_KEY`.

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

A skill suggestion, riffed from the official cookbook. One command. No key. A fixture roster stands in for the skill catalog, and recorded overlap scores stand in for the two TypeSafe calls.

```bash
node demos/skill-suggest/demo.mjs
```

The roster and scores are inline in [`demos/skill-suggest/demo.mjs`](demos/skill-suggest/demo.mjs) (the rank-then-verify shape from [`docs-mirror/typesafe/cookbooks/skill_suggestion.md`](docs-mirror/typesafe/cookbooks/skill_suggestion.md)). Nothing here calls Jev; fixture suggestions are not a live ranking.

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
