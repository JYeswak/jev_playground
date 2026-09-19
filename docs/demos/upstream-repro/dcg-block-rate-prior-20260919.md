# dcg blocks 0.97% of real traffic. Jev's gate fired on 15%. That is the whole argument.

**Date:** 2026-09-19 · **Level:** `[live]` · Zero API calls; counted from our own session logs.

## Measurement

Across 60 omp session files, every `com.zeststream.omp-dcg-bridge.decision.v1` row:

| verdict | count | share |
|---|---:|---:|
| `dcg_allow` | 49,661 | 99.0% |
| `dcg_block` | **488** | **0.97%** |
| `bash_failure` | 1 | — |
| (null kind) | 30 | — |

## Why this number matters

It is the first **prior** we have for how often a *deterministic* guard fires on real agent
traffic on the surface we were about to build on. Set against the held-out measurement of the
Jev gate (`bicameral-gate-adoption-20260919.md`, CORRECTION section):

| guard | fire rate on real/held-out traffic |
|---|---|
| dcg (regex, deterministic) | **0.97%** |
| Jev gate v2 (held-out corpus) | **15%** (3/20 benign) |

**Jev's gate is ~15× noisier than the regex it would supplement**, on the same surface. That is
not "Jev is bad at safety" — it is a statement about where a probabilistic judge can sit next to
a deterministic one. dcg is already catching the expressible cases at 1 in 100. Adding a judge
that fires at 15 in 100 on top of it produces a nag stream, not a safety net.

**The defensible role, and it is narrow:** the 5/20 dangerous commands the v1 two-question gate
*missed* were privilege widening, secret staging, irreversible publication and security-control
tampering — harm that is neither destruction nor exfiltration, and none of it expressible as a
regex. That is the only space where a judge adds anything here, and it is a space where dcg
returns **allow**, which is exactly the filter the observe-and-log extension applies.

## Consequence for the shipped surface

Confirms the design constraint rather than changing it: **observe and log, never block**, filtered
to dcg's allow/unknown verdicts. It also confirms the filter is *enforceable* from real data —
`dcg_block` is a genuine logged verdict, not an inferred one, so the extension can key off it
instead of guessing.

## A defective premise of mine, caught before it cost a unit

I told pane 3 these decision rows carry the command text. They do not — the payload is exactly
`{"kind": "...", "toolCallId": "..."}`. The command must be joined in from the
`message.content[]` part `{type:'toolCall', id, arguments}` via `toolCallId`, and the outcome from
the `role:'toolResult'` message with the same id. A three-way join, not a two-way read. `BLOCKED`
would have been the correct response to my packet; the correction cost one message.

## NO-CLAIM

60 session files from one machine and one operator, so 0.97% is our traffic's block rate, not a
general one. `dcg_allow` dominating does not mean those commands were safe — only that dcg did
not recognise them, which is precisely why the interesting cases live in that bucket. The 15%
comparison is against a 20-command held-out corpus authored by me (R28), so it carries that
corpus's limits; the two rates come from different denominators and are directionally
comparable, not a controlled head-to-head.
