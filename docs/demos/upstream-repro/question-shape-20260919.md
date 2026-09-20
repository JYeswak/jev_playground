# Question-shape: visible rephrasings rescue 3 of 7 failing questions (2026-09-19)

## Premise under test

Conductor's, from six measured sets: questions about A PROPERTY VISIBLE IN THE TEXT
survive; questions needing a RELATIVE or COUNTERFACTUAL judgement fail.

## Method

`work/jev-client/question-shape-measure.mjs` (in jev-client because wording guidance
belongs to the shared asker, and this unit changes no extension). Seven failing questions
— one more than the brief's six: the dispatch set failed as a triple (7/15, two
near-constants) and dropping one to hit six would be cherry-picking — each run original
vs rephrased against the SAME committed case arrays (rerank 4, review 7, failure 11,
dispatch 5; state shapes mirrored exactly). 27 calls/run x 3 runs = 81 calls, zero
transport errors. Verdict rule: DEGENERATE = same verdict everywhere; else must beat the
better constant to DISCRIMINATE, else WEAK. One verdict flip across all 3-run cells.

## Table (run 1; constants recomputed per label set)

| question | original | rephrased | change |
|---|---|---|---|
| noise ("more than half irrelevant") → "any entry fail to show a code line with the term?" | DEGENERATE (yes x4, 2/4, spread 0.02) | DISCRIMINATES (4/4, spread 0.71) | CONFIRMED |
| definitional ("first three contain the definition") → "any of first three show a definition signature?" | DEGENERATE (no x4, 2/4, spread 0.11) | DISCRIMINATES (4/4, spread 0.92) | CONFIRMED |
| destructive ("...WITHOUT requiring a check") → "name a check-first step?" (flip) | DEGENERATE (no x5, 4/5, spread 0.23; 0.15 on the packet that caused the deletion) | DISCRIMINATES (5/5, spread 0.88) | CONFIRMED |
| leading (yes x5, 1/5) → "assert a repo fact not shown in quoted output?" | DEGENERATE | WEAK (4/5, ties always-no 4/5, spread 0.85) | PARTIAL |
| scope → "does the subject name every file/subsystem changed?" | DEGENERATE (no x7, 6/7) | DEGENERATE (no x7, 5/7, spread 0.17) | REFUTED |
| unverifiable → "acceptance names evidence with its source?" (flip; labels T x5 by construction) | WEAK (2/5, yes x4) | DEGENERATE (no x5, 0/5) | REFUTED |
| argument (already 10/11 DISCRIMINATES here) → "tie the error to the invocation's own arguments?" | DISCRIMINATES | DISCRIMINATES (11/11; fixes adv-econnrefused 0.60→0.21) | already fine, perfected |

## Reading

The hypothesis holds where the defect is genuinely about visibility: noise, definitional,
and destructive all moved degenerate→discriminating with spreads 0.71–0.92 on identical
cases. It fails in two instructive ways. Scope's rephrase degenerates to no (the model
says every subject names everything — a second relative judgement wearing visible
clothes). Unverifiable collapses by construction: every acceptance names its evidence, so
the visible version is all-true while the real defect (the 40-case corpus is 38) is
invisible in the text — that question's failure is not a wording problem and no rewording
within the visible class can fix it. Leading sits between: the rephrase breaks the
always-yes constant but ties the always-no one.

## NO-CLAIM

Reusing our own cases cannot establish wording quality on real traffic; the noise rephrase
keys off "show a line of code", which is exactly how I built JUNK — overfit is not ruled
out; and "visible" is confounded with "shorter and more concrete". A rephrase that
discriminates here earns a re-test on fresh cases, not adoption. No extension changed.
