# jev_playground

Measure Jev on a question you already have, with the official SDK, before you build a product on the answer.

![What a typed judgment looks like](visual/hero.jpg)

## TL;DR

Jev does not write text. It scores a state against questions you define and returns numbers your code can branch on. This repo is the harness we use to decide which of those numbers are worth wiring into a tool.

**The problem.** A chat model will answer anything. A typed judge is only useful when the question, the cut, and the comparator are fixed before you spend, and when a stranger can re-score the result with no key.

**The solution.** Official TypeSafe SDK for every live call. Injected asker for every test. A bar written before the first request. An incumbent model on the same state, not only a regex.

| Use Jev when | Use something else when |
|---|---|
| The label is not a function of the literal tokens | A regex or a trained classifier already wins on that distribution |
| You need a probability you can threshold | You need prose, a summary, or a rewrite |
| Cold start or distribution shift, where a label-trained baseline collapses | In-distribution spam or harm, where the baseline already holds |
| You can name the corpus the number applies to | You would have to say "Jev works" with no N |

## What we are testing

Three question types, one request, same state:

| Question | Returns | Branch on |
|---|---|---|
| **Noul** | probability the statement is true | a fixed cut, never a tuned one |
| **Choice** | one label plus a distribution | the label only if it is in the option set |
| **Score** | a rubric level plus a distribution | the level only if every probability is finite |

The interesting code is the policy around the answer: the cut, the fail-safe side, and what happens when the response is malformed.

## How we test

1. **Read the vendor docs from disk** before inventing a question. `./scripts/sync-docs.sh --check` proves the mirror.
2. **Call through the SDK.** `work/jev-client` is the only sanctioned caller: `TypeSafeClient.systemOne`. No hand-rolled POST.
3. **Inject the transport.** Offline tests pass a fake asker. A missing key returns `unconfigured`, never a score.
4. **Write the bar first.** Accuracy, comparator, and the certify rule go in a file before the first live call.
5. **Compare to an incumbent.** An LLM on the same state and the same questions. A regex is a floor, not the product test.
6. **Re-score offline.** The live rows stay on disk. A second person runs the analyzer with no key and gets the same verdict.

```bash
# no key, no network — the injection policy
node --test work/nev-injection/seat-guard.test.mjs

# no key — re-score the committed incumbent comparison
python3 work/nev-differential/analyze_diff.py

# no key — five questions from committed bytes
bash scripts/quickstart.sh
```

## What the measurements say

Numbers below are what the cited file contains. Re-run the command. Do not quote them from this page if the file has moved.

**Prompt injection, one corpus.** On `jev-sec-bench` injection rows (n=662, cut 0.5, model `jev-1.13.0`, cited not re-measured): Jev 639/662 (0.9653). Same questions through the official adapter: grok-4 558/662 (0.8429), Claude Haiku 4.5 579/662 (0.8746). Discordant pairs 8/89 and 5/65. The pre-registered rule certifies this seat on this corpus only.

```bash
python3 work/nev-differential/analyze_diff.py
```

Receipt: [`work/nev-differential/DIFF-RECEIPT.json`](work/nev-differential/DIFF-RECEIPT.json). Public corpus, single run, fixed cut. A win here is not a certificate for Jev in general.

**Calibration, one labelled set.** Held-out fixture, N=80, pinned model: ECE 0.0614, Brier 0.0195, choice 19/20. Receipt: [`foundation/runs/20260922T021352Z.json`](foundation/runs/20260922T021352Z.json).

**Tool-call harm is not a Jev seat.** A small classifier beats a live judge on that surface. Ship the classifier. The verify command is `node work/omp-harm-rule/verify-claim.mjs`.

## Tips

Practices that keep a measurement citeable.

- **Pin `jev-1.13.0`.** `jev-latest` moves. A number without a model id is unciteable next week.
- **Use the SDK retry, and default it off** when you need one attempt per row. A hand-rolled retry loop double-counts failures and hides `Retry-After`.
- **Give Jev the measurement.** If the state omits the usage shape, the verdict tracks the question wording instead of the evidence. Run the withheld-state control: `node scripts/measure-framing-flip.mjs` only when you mean to spend.
- **Strip rationale out of criteria.** A criterion that explains why an option is right teaches the answer.
- **Malformed means review.** A missing field, a non-finite probability, or a thrown client is `review`, never `pass` and never `verified`.
- **Ten calls, not one.** A single latency or a single probability is a smoke call. The A/B harness refuses a relative verdict under ten zero-spread samples.
- **A suite that passes a coin-flip judge tested the plumbing.** Score Jev against a label it did not supply, or you learned nothing.
- **Name the corpus in the same sentence as the accuracy.** 96.5% on this injection file is not 96.5% on your traffic.
- **Reserve the safe side.** Unknown answer keeps the message. Low confidence does not act. Insufficient context is `applicable: false`, not a fabricated score.
- **Do not patch an upstream clone to make a demo pass.** Wrap it, or drop the demo.

## Scripts you can run

No API key unless the row says otherwise.

| Command | What you get |
|---|---|
| `bash scripts/quickstart.sh` | Five answers from committed bytes. Add `--mine` to point the same tools at your logs. |
| `node --test work/nev-injection/seat-guard.test.mjs` | Planted hostile flags, planted benign passes, malformed reviews. |
| `python3 work/nev-differential/analyze_diff.py` | Re-scores the injection comparison. Exit 0 when both arms are complete. |
| `node scripts/jev-probe.mjs --replay docs/demos/jev-probe/probe-response-20260918.json` | A recorded judgment, decoded. Omit `--replay` only when you intend a live call. |
| `./scripts/sync-docs.sh --check` | Byte-identity of the vendored TypeSafe docs. |
| `bash scripts/vgrep.sh` | A grep used as proof must match at least one line. Silence is not a clean result. |
| `bash foundation/gates.sh` | The local gate ladder, including the planted-defect selftests. |

The caller to copy is [`work/jev-client`](work/jev-client/README.md): `askJev`, `askJevChoice`, `askJevScore`, `askJevBundle`. Missing key returns `unconfigured`.

The screen to copy is [`.omp/tools/jev-screen.ts`](.omp/tools/jev-screen.ts): flag at p≥0.5, pass below, review on anything else. It does not block by itself. The caller branches.

## Installation

Clone the repo. Node 20 or newer for the keyless tests. Python 3 for the injection re-score. No package install for the three commands below.

```bash
git clone https://github.com/JYeswak/jev_playground.git
cd jev_playground
```

A live call is optional. Set `TYPESAFE_API_KEY` in the environment from a file outside the tree. Do not echo it. Do not commit a response that contains someone else's state.

## Quick start

```bash
git clone https://github.com/JYeswak/jev_playground.git
cd jev_playground
bash scripts/quickstart.sh
node --test work/nev-injection/seat-guard.test.mjs
python3 work/nev-differential/analyze_diff.py
```

Node 20 or newer. Python 3 for the analyzer. No install step for those three commands.

A live call needs `TYPESAFE_API_KEY` outside the tree. Load it. Do not print it. Do not commit a response body that contains someone else's state.

## Limitations

- The injection seat is one public corpus, one cut, one run. It does not transfer to your traffic until you measure yours.
- Tool-call harm, in-distribution spam, and several cost-routing questions are not Jev seats here. A cheaper deterministic rule wins those.
- `jev_screen` listed in an omp session is not the same as organic precision on a working profile. Listing and a planted fire are proven. Fleet traffic is not.
- Vendored clones under this tree are other people's repos. Read them. Do not push them.
- A calibration number is the receipt it names. This page does not recompute it.

## FAQ

**Do I need a key to see if the harness works?** No. The three commands in Quick start are keyless.

**Which model id should I pin?** `jev-1.13.0`, until you re-measure on a newer id and say so.

**Why not call `fetch` myself?** The wire contract is small, and a hand-rolled client drifts on retry, timeout, and field names. The SDK owns the wire. Your code owns the cut and the fail-safe.

**What if the answer is malformed?** Review. Do not coerce it into a pass.

**Can I treat 0.9653 as Jev's accuracy?** No. That is 639/662 on one injection file, against two incumbents, at cut 0.5.

## About Contributions

> *About Contributions:* Please don't take this the wrong way, but I do not accept outside contributions for any of my projects. I simply don't have the mental bandwidth to review anything, and it's my name on the thing, so I'm responsible for any problems it causes; thus, the risk-reward is highly asymmetric from my perspective. I'd also have to worry about other "stakeholders," which seems unwise for tools I mostly make for myself for free. Feel free to submit issues, and even PRs if you want to illustrate a proposed fix, but know I won't merge them directly. Instead, I'll have Claude or Codex review submissions via `gh` and independently decide whether and how to address them. Bug reports in particular are welcome. Sorry if this offends, but I want to avoid wasted time and hurt feelings. I understand this isn't in sync with the prevailing open-source ethos that seeks community contributions, but it's the only way I can move at this velocity and keep my sanity.

## License

MIT. See [`LICENSE`](LICENSE).
