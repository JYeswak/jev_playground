# What we mined tonight, and what to do differently `[receipt]`

Three corpora, three completeness levels, one night. Every count as-of
2026-09-20 — all three grow while you read.

| corpus | size | mined | what it told us |
|---|---|---:|---|
| this repo's commits | ~1,067 | 100% | the verification level is decorative — `oracle` never touched a test file ([mine](./commit-mine-result-20260920.md)) |
| agent-mail | 6,510 messages | 100% | **58 of 3,135 ack-required messages were ever acked (1.85%)** ([mine](./mail-mine-result-20260920.md)) |
| CASS sessions | 5,181,931 messages | 2.32% window + n=1,000-conversation replication | dig beats invent overall; loses badly on absence-claims ([frame](./cass-sampling-frame-20260920.md), [replication](./repsample-result-20260920.md)) |

## What to do differently

- **Stop requiring acknowledgments your agents almost never send.** A
  1.85% ack rate says the coordination protocol asks for something it
  does not get. Either enforce the ack (block the sender until it
  arrives) or drop the requirement and design for unacked mail. A flag
  that fires 1.85% of the time is not a handshake; it is a log line.
- **Never dig an absence-claim on hit-count alone.** Across two sampling
  frames, digging when hits exist doubles-to-triples the loss versus
  inventing on exactly the queries where a pane most wants to dig.
  Demand evidence in the hit that it answers, or invent.
- **Put the word `[receipt]` on result-recording commits.** The mine
  showed our strongest vocabulary word never touched a test file; the
  level now exists, and the hook suggests it on docs-only diffs.

## Limits, same breath

All three corpora are live-monotonic (commits moved 1,043 → 1,067 within
the hour; the harvest file moved 77,767 → 78,242). CASS remains 97.68%
untouched — characterised, not mined. Nothing here is promoted.
