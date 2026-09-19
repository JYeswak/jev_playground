# The Jev SDK surface, read from source — stop guessing these

**Date:** 2026-09-19 · **Level:** `[oracle]` — every field below is quoted from the installed
declarations, not from memory or a README.

Joshua, this tick: *"every action should have ripwire, ast-grep, morph, ripgrep, fh backed rigor
from our dicklesworthstone-mirror. we keep making stupid mistakes because we're not regularly
asking for insight from these tools."*

He is right, and the receipts are ugly. **Five defects today, every one discoverable by reading the
installed artifact instead of guessing:**

| guess | truth | cost |
|---|---|---|
| `client.systemOne.evaluate(...)` | `client.systemOne(...)` is the method | first probe crashed |
| noul answer `.probability` | **`.noul`** | Python probe crashed |
| choice answer `.distribution` | **`.probabilities`** | **three router runs reported a bogus AUC of exactly 0.500** |
| omp results as `content[].tool_result` | whole message, `role:"toolResult"` | two dead parsers |
| grep `"role": "toolResult"` | file has **no space**; spaced form matches **0 files** | nearly published "omp does not persist tool results" |

The 0.500 one is the worst: a wrong field name yields a constant score, a constant score yields an
all-ties AUC of exactly 0.500, and that looks exactly like a real null result. **A guessed field
name does not crash — it fabricates a finding.**

## Authoritative answer shapes

Source: `work/sdk/node_modules/@typesafe-ai/sdk/dist/index.d.mts:86-116` (v0.6.0).

```ts
interface NoulResponse   { type: "noul";   noul: number }                      // :86-91
interface ChoiceResponse { type: "choice"; choice: string; confidence: number;
                           probabilities: Record<label, number> }              // :92-101
interface ScoreResponse  { type: "score";  score: number;  confidence: number;
                           legend: Record<score, string>;
                           probabilities: Record<score, number> }              // :106-116
```

- **There is no `.probability` and no `.distribution` anywhere in the SDK.**
- `noul` has **no** `confidence` field; choice and score do.
- `score` is an **expected** value and may fall between rubric levels — do not treat it as an index.
- `legend` gives the rubric back, which is how you map a score to its label without re-deriving it.

## Call shape

```ts
import { TypeSafeClient, noul, score, choice } from '@typesafe-ai/sdk';
const client = new TypeSafeClient({ apiKey: process.env.TYPESAFE_API_KEY });
const r = await client.systemOne({ state: {...}, questions: { k: noul('...') } });
r.answers.k.noul
```

**Python differs and the difference bites:** `typesafe_sdk.Noul` **requires** `instructions` or
`criteria` — a bare dict returns **400 "Noul question must have criteria or instructions"** — while
the JS `noul()` helper supplies it. The Python SDK is **not on PyPI**; use the pinned uv project at
`work/pysdk` (git rev, `uv.lock`, `.python-version` 3.12; system Python 3.9.6 cannot resolve
`msgspec>=0.21.1`).

## The rule this file exists to enforce

**Before any claim about an external API, open the installed artifact and cite `file:line`.**
`grep`/`ast-grep` over `node_modules/**/*.d.mts`, the vendored clone, or the mirror — not the
README, not recall. A README documents intent; the declarations are what ships.

And when a scorer can silently read a missing field, **make it throw**. `work/router-spec/oracle.mjs`
now raises if `probabilities` is absent, because scoring silence is how a harness fabricates a null.

## NO-CLAIM

This describes `@typesafe-ai/sdk` **v0.6.0** as installed on this machine on 2026-09-19 and
`typesafe-sdk` 0.6.0 from git rev `420ef4ff`. Wire-compatible reimplementations (`localjev`,
`jeff`) may populate these fields differently — `jeff`'s own README states its `score` uses the raw
distribution and only matches the weighted average at `JEFF_TEMPERATURE=1`. Re-read the
declarations after any upgrade.
