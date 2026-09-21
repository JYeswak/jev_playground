# PREREGISTER-U2 — jev-k9z.5 UNIT 1 retry (60 fresh rows)

Committed 2026-09-21 by P3 BEFORE any Unit-2 call. Bar UNCHANGED from
PREREGISTER.md (sha 89cd1613): (1) point accuracy ≥ 0.90, (2) paired exact
McNemar two-sided p < 0.05 vs lexical on the SAME rows, (3) framing delta
report-only. Moving the bar is forbidden (R69).

## Slice (mechanical, outcome-blind, zero overlap)

- Every 11th row of pairs.jsonl starting at offset 5: rows 5, 16, 27, …, 654
  = **60 rows**. Offset 5 chosen because no 5+11k is a multiple of 33, so
  overlap with the used 21 (multiples of 33) is EMPTY by construction.
- Outcome-blind: per-row live outcomes from Unit 1 were seen only as
  aggregates + two named rows (inj-0462 framing flip, inj-0231 FP); slice rule
  fixed before reading any row outside the used 21.

## Pre-stated discordants (systematic-underpower fix, first application)

- At the observed 7:1 split the gate needs ≥9 discordants (8-1 → p=0.0391).
- If the fresh slice yields <9 discordants, or a worse split, the gate likely
  fails and that is a MISS, not a cue to add rows.
- "If the pattern eight pairs suggested holds, 60 rows suffice" — never a
  power analysis (post-hoc-power trap); if the true ratio is 3:1 this misses,
  and nothing rules that out.

## Spend

120 requests (60 rows × 2 arms, one request per row per arm, upstream shape),
model jev-1.13.0, 20 s timeout, one retry on transport failure, >2 failures
per arm renders the run INVALID. ~$0.0056, ~16 s serial. Blanket approval.
