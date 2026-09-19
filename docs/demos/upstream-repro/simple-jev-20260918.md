# `simple-jev`: an open-model control arm, free, and it answers our hardest question

Two links from Joshua, 2026-09-18: [`nicobailon/pi-subagents`](https://github.com/nicobailon/pi-subagents)
and [`simple-jev.featherless.ai`](https://simple-jev.featherless.ai/). This receipt covers the
second; the first is summarised at the end.

`simple-jev` (`featherless-ai/simple-jev`) is an **open-source implementation of the Jev interface**:
send shared context plus typed questions, and the server reads next-token logits for the allowed
labels and constructs the JSON itself. *"The model does not generate a JSON completion: the server
constructs the response from the scores."* Same three question types this lane uses — `choice`,
`score`, `noul`.

**Every measurement in this repo has been single-armed.** We have compared Jev against TF-IDF, against
a paper's numbers, against itself. We have never asked whether the *model* matters or whether the
*shape* does. This is that control, and it costs nothing.

## It answers the question that cost us the most today

The hardest judgment this lane made was whether `283,786` cited to a census receipt is a stored
value, a derived rollup, or absent. It took two wrong mechanisms, a retracted register class, and a
non-author pane's adjudication. Asked of an open model with no key:

```
opens (is it stored as a literal?)        noul 0.012
derivable (sum of per-repo kloc × 1000?)  noul 0.894
class                                     derived_rollup, confidence 0.989
                                          stored_literal 0.0067 · absent 0.0040
```

**1.7 seconds, 1,040 input tokens, no credential.** That is the same verdict pane 2 reached, and the
same one my register now records after I got it wrong twice.

It does **not** follow that the gate should call this model. A gate needs determinism, and these
distributions are explicitly *"not calibrated probabilities of correctness"* by upstream's own
README. What follows is narrower and more useful: **the semantic classification we treated as
expensive human judgment is cheap enough to use as a second opinion on every row.**

## Two defects found in five minutes

1. **The landing page's copy-paste example fails.** It advertises
   `featherless-ai/gemma-4-26B-A4B-classifier`; `GET /v1/models` does not list it, and a POST
   returns `model_not_available` with HTTP 400. The README gets this right — *"First, list the
   available models"* — and the marketing page does not. Served today:
   `Qwen3.6-35B-A3B-classifier`, `Qwen3.8-27B-classifier`, and three RWKV sizes.
2. **The error message misattributes the cause.** It says *"not available for this API key"* on an
   endpoint that requires no key, then blames demo overload. The actual cause is an unserved model
   id. I retried twice before reading the model list, because the message told me to wait.

## Pricing, for the comparison this lane keeps making

`simple-jev` on Featherless starts at **$0.03 per million input tokens**, beta. `jev-benchmark`
measured TypeSafe at **~$0.0000173/call at $0.042/MTok**. Same order, different vendor, and the open
implementation can be self-hosted on CPU with `Qwen3.5-0.8B`.

## `pi-subagents`, briefly

A Pi extension for subagent delegation: 3,657 stars, MIT, with builtin `scout`, `worker`,
`reviewer`, `oracle`, and — directly relevant — **`evidence-auditor`, which *"independently checks
whether important research claims are supported by their sources."*** That is this conductor's modal
failure implemented as an agent role. It also ships `examples/typed-gate`, a classifier-driven
workflow gate. Not run here; recorded as the highest-value unrun item.

## No-claim

- **One question, one model, one run.** The `283,786` result is a single call against
  `Qwen3.6-35B-A3B-classifier`; nothing here establishes agreement rates, and a question I already
  knew the answer to is the easiest possible test.
- The state I supplied **described** the receipt rather than containing it, so this tests the
  model's reasoning over a summary I wrote, not its ability to read a receipt. A fair test hands it
  the file.
- No comparison against Jev on the same question was run, so *"an open model can do this"* is not
  *"an open model does this as well as Jev."*
- `pi-subagents` is **read, not run**.
