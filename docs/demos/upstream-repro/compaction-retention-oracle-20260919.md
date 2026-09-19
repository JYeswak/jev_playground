# fast-jev-compaction, taken to completion: it is 7–23× worse than doing nothing

**Date:** 2026-09-19 · **Level:** `[live]` · Clone never edited; all work in `work/compaction-proof/`.

One repo, proven end to end, instead of another survey. `tamaratran/fast-jev-compaction` asks Jev
per tool call *"will this still be needed?"*, thresholds at **0.5**, and **physically deletes** the
content. Its 29 tests are all plumbing — it ships **no retention oracle**, so nothing anywhere
checks whether the agent could still do its job afterwards. This builds that oracle and runs it on
live decisions.

## Setup a stranger can reproduce

Native SDKs, no vendored code:
- JS: `npm i @typesafe-ai/sdk` → `client.systemOne({ state, questions })`, helpers `noul/score/choice`.
  (There is **no** `client.systemOne.evaluate`.)
- Python: **not on PyPI.** `uv run --python 3.12 --with <clone> python …` — system Python 3.9.6
  cannot resolve `msgspec>=0.21.1`.
- Live probe, labels withheld from the model: safety-incident text **p=0.980**, cold-meal text
  **p=0.020** — both correct.

**omp schema** (cost me two wrong parsers): a call is a `message.content[]` part
`{type:'toolCall', id, name, arguments}`; a result is a **whole message** with `role:'toolResult'`
and `toolCallId`. 97 sessions carry results — grep **both** JSON spacings; `"role": "toolResult"`
with a space matches **0 files**, because that spacing only exists in Python's re-serialization.

## The oracle

A tool result "was needed" if **novel** tokens it introduced reappear later in the transcript.
Linear: token → first/last occurrence row. (Suffix concatenation is quadratic and OOM-kills a
14k-line session; a per-call prefix stringify hangs it.)

**The oracle is tested, not assumed** — `oracle-selftest.mjs`, two planted negatives:

| control | result |
|---|---|
| results replaced with pure noise | **0 / 200 "needed"** |
| results scored at end-of-transcript (nothing can follow) | **0 / 200 "needed"** |
| real results | 179–185 / 200 (**89.5–92.5%**) |

So the high reuse rate is a property of agentic sessions, not a loose oracle.

## Result — 3 real sessions, live Jev, n=96 each (deterministic evenly-spaced draw)

| policy | mistakes (session A / B / C) |
|---|---|
| **Jev @ 0.5 (the product)** | **82 / 91 / 81** |
| drop everything | 84 / 92 / 83 |
| random, same budget | 81 / 91 / 80 |
| recency, same budget | 82 / 91 / 81 |
| **keep everything (do nothing)** | **12 / 4 / 13** |

Jev's drop rate: **97.9% / 99.0% / 97.9%**. It is **indistinguishable from dropping everything**,
from random, and from recency — and **keeping everything is 7×, 23× and 6× better**.

## The ruling

**Do not run this compactor on an omp session.** In agentic coding transcripts ~90% of tool
results get referenced again, so aggressive compaction is destructive by default, and the product
at its shipped threshold is a rounding error away from `rm`. Compaction remains defensible only as
a **short-session, tail-only** knob — never as a general policy — and any deployment needs a
retention oracle wired into CI, which this one lacks.

## NO-CLAIM

"Needed" is a **token-reappearance proxy**, not ground truth: a path or identifier recurring for an
unrelated reason counts as reuse, which biases *toward* keeping. It measures **recoverability of
content**, not whether the agent's final answer would have changed — the decisive experiment
(ablate the result, re-run the turn, compare outcomes) is **not done here**. n=96 per session, 3
sessions, one machine, one model version, one run. The upstream repo is not accused of a bug: it
does what it says; nobody had measured what that costs.
