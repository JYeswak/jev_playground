# Our oracles, audited for rigging: suspicion UPGRADED on sibling evidence

Pane 3 (muse), 2026-09-19. Read-only audit, zero live calls. Every row answers
with file:line: (1) can it return YES (constructed yes-input or proof none
exists), (2) preregistered win condition or fit-after-seeing, (3) bounded null
or universal reading, (4) positive control or only negative controls.

CORRECTION (same session): the prime-suspicion verdict below was written before
reading the sibling's parallel receipt
(`docs/demos/upstream-repro/rigged-oracle-selfcheck-20260919.md`, committed
alongside this file — see the index note at the end). The sibling is right and
this row is corrected: the waste term exists, so "keep-everything cannot lose"
is false as stated, BUT the two mistake types are incommensurate (a content loss
summed 1:1 with a per-call hoarding flag, where hoarding megabytes costs the
same as hoarding bytes) and no win condition was preregistered — so the
head-to-head total structurally favors keep-all. Verdict corrected to
RIGGED-SHAPE on commensurability grounds; the sibling's `fair-oracle.mjs`
(substantive reuse ≥3 tokens, bytes counted, preregistered adopt rule, perfect-
judge arm that CONSTRUCTS the yes-input and runs it) is the stronger instrument
and supersedes this row. My error was stopping at "both directions counted"
without asking whether the directions are commensurate.
cost — but the table decomposes both, so any reader can re-weight. [SUPERSEDED
by the CORRECTION above: decomposition is necessary but not sufficient, because
the head-to-head TOTAL is what the verdict cites, and the total sums
incommensurates 1:1 with no preregistered win condition.] A genuinely fair
variant (score agent outcomes, not token recurrence) remains the ablate-and-rerun
experiment, already NO-CLAIMed as not-done, not as a defect in this oracle.

## Rows

| Oracle | YES-input? | Preregistered? | Bounded? | Positive control? | Verdict |
|---|---|---|---|---|---|
| oracle.mjs MISTAKES | yes in principle (oracle policy scores 0) but the TOTAL cannot promote a real policy: content losses and per-call hoarding flags summed 1:1, no preregistered win rule | 0.5 = product's shipped cut; verdict fitted after seeing data | 3 sessions, n=96, jev-1.13.0, one run, stated | selftest rejects noise AND fires on real, but neither proves the TOTAL can crown a winner | RIGGED-SHAPE (commensurability; corrected on sibling evidence — fair-oracle.mjs supersedes) |
| eProcessVerdict (hindsight.ts:168-188) | yes either direction (e≥20 / e≤0.05) | thresholds + anytime-validity in code comments | bounded by input arrays | CAN return JEV-BEATS (construct: random errs more) | FAIR |
| ensemble verdict rule (decorrelation.py:48-54) | yes incl. author-surprising third outcome | 0 / 0.5 stated in code | per-pair n | planted negative (self-average buys nothing, test:45) + opposite-shapes test (:32) | FAIR |
| pos_control AUC (P3-3) | yes, observed (read 0.94) | A/B rule + >0.9 expectation pre-committed in bead text BEFORE running | n=150, 3 sessions, stated | the read line IS the positive control | FAIR |
| gates.d stages (10/20/30/40/60/70/80) | yes: green runs observed daily | pass/fail coded + --selftest RED arms (gate40 proven this session) | per-tree | green runs, not just red refusals | FAIR |
| stage 95 ratchet | yes: holds on legit prose | explicitly NOT zero-hit (wiring a RED-on-legit gate named as worse) | this repo | legit-hit cases named in header | FAIR (model citizen) |
| stage 90 wrapper | yes: clean sidecars pass | transients→UNMEASURED coded, not fitted | this lane | planted bogus row discriminates | FAIR |
| lane-status / numerals / score-lineage | yes: clean trees pass | N/A (invariant checkers, no thresholds) | this repo | missing-receipt RED, bogus-row, selftests | FAIR |
| verify-frozen.sh | yes: frozen green | consumer + retirement condition stated; deliberately UNWIRED (speed) | this repo | green runs | FAIR |
| 50-house-gates | yes: all green observed | delegates RED arms to house scripts; exit 3 = instrument error, never pass | this repo | house --selftests | FAIR |
| refused instruments (neg-evidence gate, loop-integrity) | none: unwired, never run here | N/A | N/A | none | UNKNOWN (correctly dormant, retirement named) |
| my sweep.py verdicts (P3-1/P3-2) | yes in principle (0-mistake + savings threshold) but keep-all scores 0 mistakes BY CONSTRUCTION on the counts axis | grid 0.0-1.0 obvious, "no knee" drawn AFTER seeing data | n=150, stated | planted extremes (0.0/1.0 behave) | FAIR (rates led, flatness stated) with note: counts framing structurally favors keep-all; the rates axis is the honest one |
| my 4uy gap-term hypothesis | no: needs a second pair that does not exist in-tree | post-hoc (one pair + strata) | labeled hypothesis in receipt | none possible | UNKNOWN (stated as hypothesis, not finding) |
| the 21-ruled-0-promoted count | confounded: DoD CAN promote (concrete clauses; hook met L3) BUT two documented acceptances were unmeetable (R21 pruning-L4; skillranker arms at SHA — dispatch defect, conceded) | mixed | lane session | — | UNKNOWN (bar real, denominator polluted; fix in motion: obtainability check before dispatch) |

## Required FAIR case, found several times over

pos_control (pre-committed rule, observed yes), eProcessVerdict (two-sided by
construction), stage 95 (refuses to demand what legit prose cannot satisfy).
The lane's instruments are, on the evidence, harder on themselves than on their
targets — the failure mode is unmeetable ACCEPTANCES at dispatch, not rigged
verdicts at judging.

## Ranked fix list

1. Enforce the adopted obtainability check (conductor: verify acceptance is
   obtainable BEFORE filing) — check it is written into the tick file/AGENTS,
   not just a message; re-audit in one week against new beads.
2. My sweep: preregister grids + verdict rules in bead text before running
   (P3-3's A/B is the template); lead with rates, never counts alone.
3. 4uy gap-term: mark WAITING (needs keyed rerank or themsquared), not a finding.
4. DoD audit: scan §4 for further unmeetable-on-current-seams clauses (R21-type).
5. Retire-or-wire review for dormant instruments quarterly; neg-evidence gate
   already carries its retirement condition — verify the others do.

## NO-CLAIM

Read-only; no instrument executed except the previously proven gates/suites.
Row authors' intent inferred from headers/comments where behavior was not
re-driven. The 21-0 count itself is not re-litigated case by case — confounded,
not cleared.
