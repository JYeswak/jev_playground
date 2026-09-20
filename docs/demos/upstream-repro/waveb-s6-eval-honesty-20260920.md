# Section 6 jev-eval-honesty — PASS (P1–P12, 0 Jev calls by design) (2026-09-20)

Level: `test` + live read-only scans. The three mechanisms are Jev-free tooling; live
evidence is quoted pipeline rows over real session logs, not model calls.

## Passes

- P1 PLAN-DELTA.md (adopted sources, 3 deltas, proof commands).
- P2 outcome-join.mjs + test (6/6): selector verification, zero-hit structure.
- P3 co-presence.mjs + test (4/4 → 5/5): REFUSE wording, three presence verdicts.
- P4 shape-check.mjs: 15,499 decision rows inventoried; join matched 0 — live rows
  carry `{kind,toolCallId}`, not `{outcome/error}`. Keys printed before the claim.
- P5 random-judge.mjs + test + verdictKeys fix (18/18 across the three files).
- P6 pipeline-run.mjs: `"LIVE matched=15525 unmatched=0 ..."` (P7 quoted row).
- P8 cross-check.mjs + CROSS-CHECK.md: slice-2 row reproduced byte-identical by
  orchestrator; mechanics stable, composition diverges (ownConstant 0.5351→0.9733 —
  base rates are local, prevalence-first evidence).
- P9 NEGATIVES.md + the keyOf shape bug it proved (PRESENT unreachable; fixed with
  regression test; presence=PRESENT live after fix).
- P10 prevalence cell on the quoted row (== ownConstant numbers, named as base rate).
- P11 planted negative: REFUSE exit 2 twice live (empty dir, decision-less file),
  verified by orchestrator with exit codes.
- P12 this receipt + TESTS.md entry + ledger line.

## Ledger line

SECTION 6 jev-eval-honesty — PASS — `"LIVE matched=15557 ... presence=PRESENT prevalence=0.5351 ..."` + REFUSE exit 2 twice + 19/19 tests — NO-CLAIM: tooling only, no judge scored; baselines describe kind-label skew, not quality.

## NO-CLAIM

All offline except read-only scans; no model calls in this section by design. The
mechanisms standardise eval plumbing, not verdicts. vbh.3 ready to close.
