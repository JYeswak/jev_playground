# README prose check: 3 CONFIRMED, 1 STALE-fixed (2026-09-20)

Level: `test` (offline; commands below, exits unpiped).

## "50 dead-end ledger entries each with a reopen condition" — STALE, fixed

- `grep -cE "^## R[0-9]+" NEGATIVE_EVIDENCE.md` → **50** headers, all `## `
  headers are R-entries, 44 distinct IDs (dupes R28/R32/R33/R42/R43 — the known
  collisions). README said 31: stale, fixed to 50 in three places (lines 106,
  788, 831, this commit).
- Reopen-condition half: CONFIRMED in substance. 10 sections lack the literal
  words, but sampling (R15 "two retries", R16/R17/R20 "RETRY CONDITION",
  R18/R44 "refusal with a trigger", R31) shows each carries one phrased as a
  retry, trigger, or overturn condition. The number was wrong, not the shape.

## "One promotion awarded and retracted the same day" — CONFIRMED

`docs/demos/upstream-repro/foreman-supervision-adoption-20260919.md`: verdict
PROMOTE (line 33) plus same-file appendix "PROMOTION NARROWED" (line 57,
"moved off rung 5 by its author"), one dated receipt. STATUS.tsv UP-R7 now
RULED_OUT. Awarded and retracted 2026-09-19.

## "Observer (B) mechanism MET at n=1 lab; working-profile dogfood OPEN" — CONFIRMED

Post-fix state: `safeAppend` defined (`observer.mjs:29`) — the §16 defect
(called, never defined) is closed, not merely worked around;
`emits-rows.test.mjs` 5/5 green. INTEGRATIONS.md:61 states the mechanism/dogfood
split verbatim; :122 confirms working profile OPEN. README matches the fixed
tree, not the broken one.

## Breakdown (8 cleared, 13 held, 12 ruled out) = 33 — CONFIRMED

`awk -F'\t' ... STATUS.tsv`: 8 CLEARED / 13 HELD / 12 RULED_OUT, 33 data rows;
8+13+12=33. Re-derived, not trusted.

## Ledger line

REVIEW readme-prose — 3 CONFIRMED 1 STALE-fixed (ledger 31→50) — stage 97 green after fix — NO-CLAIM: offline only; reopen-condition coverage sampled, not exhaustive.
