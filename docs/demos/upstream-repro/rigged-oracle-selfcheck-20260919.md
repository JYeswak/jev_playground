# My compaction oracle was rigged, and a "perfect judge" arm proves it in one line

**Date:** 2026-09-19 · **Level:** `[live]` · Joshua: *"why do we keep using broken/bunk oracles
that keep denying any progress — that is the worst thing we can do."*

He is right, and the lane's own counter is the evidence: **21 candidates ruled, 0 promoted.**

## The defect

`work/compaction-proof/oracle.mjs` scores a dropped tool result as a mistake if **any** novel token
from it reappears later. So:

- keep-everything makes **zero** drop-mistakes *by definition*;
- its only cost, "kept but never needed", is counted **per call, not per byte**, so hoarding
  megabytes is free.

Compaction cannot win that test regardless of merit. No win condition was preregistered either, so
every measurement could only read as a kill.

## The fix, and the self-check that catches rigging

`work/compaction-proof/fair-oracle.mjs`. Two fairness changes: reuse must be **substantive**
(≥3 distinct novel tokens return, not one path or flag), and **bytes are counted** as the benefit.
Win condition declared **in the file, before running**: adopt if savings ≥ 50% **and** substantive
reuse lost ≤ 10%.

Then the arm that matters — **`perfect`**: an omniscient judge that drops exactly those results
never substantively reused. It is the best any policy could possibly do.

| policy | bytes saved | substantive reuse lost | verdict |
|---|---|---|---|
| keepAll | 0.0% | 0.0% | REJECT |
| dropAll | 100.0% | 100.0% | REJECT |
| **perfect (omniscient)** | **27.2% / 29.3%** | **0.0%** | **REJECT** |
| drop-largest 30% | 71.3% / 76.5% | 29.5% / 28.3% | REJECT |

*(two sessions, 11,824 and 14,309 tool results, 38.8 MB and 38.9 MB)*

**A perfect judge fails my bar. Therefore the bar was impossible, not the candidate.** 50% savings
at ≤10% loss lies outside the feasible frontier for these transcripts.

## The finding this produces — the first usable number, not a kill

**The entire available prize from compacting these sessions is ~27–29% of tool-result bytes, at
best, with a perfect judge.** Not "compaction is bad": compaction's ceiling is 28%, and collecting
it requires near-perfect judgement. That reframes the earlier ruling — Jev's failure to rank future
need (AUC 0.35–0.65, positive control 0.941) matters *less* than the fact that the prize is small.

## HOUSE RULE adopted from this

**Every oracle must include an arm that ought to pass.** A perfect/oracle-of-last-resort arm, or a
known-good candidate. If nothing can pass, the instrument is broken before the candidate is — and
you find that out in one run instead of after five kills.

Corollary: preregister the threshold **in the file**, and count the benefit in the unit the
product actually delivers (bytes, dollars, seconds) rather than in incidents.

## NO-CLAIM

Two sessions on one machine; "substantive" is `MIN_TOKENS=3`, a judgement call I set before running
but did not tune or validate against outcomes. The 27–29% ceiling is specific to omp agentic coding
transcripts — a chat workload with disposable tool output would have a different, likely much
higher, ceiling. This measures bytes and token recurrence, still not whether the agent's answer
would change.
