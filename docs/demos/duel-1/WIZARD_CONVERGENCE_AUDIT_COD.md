# Duel-1 convergence audit: COD ruling on the headline claim

Bead: `jev-demo-loop-a1q`
Role: arms-length audit of the orchestrator's claim that four of five ideas converged
across lineages

## Ruling

The headline **“four of five ideas converged across lineages” is overstated if it means
that the two top-five shortlists contain four genuinely same demos**.

Only two of the four proposed pairs are the same demo at the product/scope level:
**routing backtest** and **signals-not-verdicts**. The screen hooks are adjacent but have
different safety policies and enforcement stages. The claim-check ideas are adjacent but
operate on different input surfaces and different deployment boundaries. The two alleged
singletons are not singletons in the full inventories: CC's long list contains foreman-lite
(#6), and MU's winnowed list contains the fact-ledger sidecar (R3).

A weaker statement is true: both lineages independently covered the same broad problem
families, and the full 15-item inventories contain near-matches for all six concepts. That
is concept coverage, not four-of-five top-five consensus.

## Pair classifications

| Pair | Classification | Deciding difference |
|---|---|---|
| MU-1 routing ↔ CC-3 routing | **SAME DEMO** | Both are read-only per-turn backtests over our omp/session logs that estimate counterfactual routing savings. |
| MU-2 admission ↔ CC-5 admission | **ADJACENT BUT DISTINCT** | MU adds a credential-material classifier and fail-closed block/redact policy; CC is injection-only, shadow-first, advisory/fail-open. |
| MU-4 claim-checker ↔ CC-2 claim-check lane | **ADJACENT BUT DISTINCT** | MU checks working files against an evidence directory; CC checks numeric triples in staged commit messages against cited receipts. |
| MU-5 signal-kit ↔ CC-4 signals starter | **SAME DEMO** | Both fit a small model over signal questions, retain a fixed-rule/verdict baseline, and emit calibration evidence. |
| MU-3 foreman-lite ↔ CC long-list #6 | **SAME DEMO** | CC's #6 explicitly proposes “Foreman-lite completion judge wired to our bead close path”; it is omitted from CC's top five, not absent from the file. |
| CC-1 fact ledger ↔ MU winnowed R3 | **SAME DEMO** | CC proposes a byte-exact fact ledger for dropped context; MU R3 says “Pair with fact ledger” as the same §14 follow-up, but winnows it as a non-standalone item. |

## Evidence by pair

### 1. MU-1 and CC-3 — SAME DEMO

MU defines a CLI that replays omp transcripts, asks per-turn whether frontier is needed,
and emits estimated savings, latency, served-model agreement, and spot human labels
(`WIZARD_IDEAS_MU.md:22-28`). CC defines `jev-route-backtest`, points it at omp session
JSONL, emits what routing would have spent versus actual spend, and explicitly says it is
read-only (`WIZARD_IDEAS_CC.md:166-168`).

The input path and policy details differ, but those are implementation choices around the
same product: a replay-only counterfactual routing backtest before live rerouting. This is
a real convergence.

### 2. MU-2 and CC-5 — ADJACENT BUT DISTINCT

MU's proposal asks two Noul questions per incoming result: whether it carries an injection
directive and whether it carries credential material, then returns block/redact with
injection and credential fail-closed policies (`WIZARD_IDEAS_MU.md:65-70`). CC's proposal
judges bytes before context, starts in shadow mode, logs a verdict, and “never blocks”
until false-positive rate is measured (`WIZARD_IDEAS_CC.md:236-238`); its fail-safe is
explicitly advisory/fail-open in shadow (`WIZARD_IDEAS_CC.md:248-256`).

Those differences change the security contract, outbound data boundary, and operational
state machine. Unit 1's steelman makes the distinction concrete: raw credentials cannot
be sent to Jev, so MU's credential branch requires a local detector/redaction stage that
CC's injection-only shadow proposal does not specify. They share the context-admission
seam and Usage Map §1, but they are not the same shippable demo.

### 3. MU-4 and CC-2 — ADJACENT BUT DISTINCT

MU's command is `jev-claims <notes.md> --evidence <dir>`; it extracts working points,
checks each against cited evidence, reports supported/contradicted/insufficient, and
fails on contradiction (`WIZARD_IDEAS_MU.md:143-148`). CC installs a `githooks/pre-commit`
lane that extracts number/unit/cited-artifact triples from a staged commit message and
checks those receipts (`WIZARD_IDEAS_CC.md:131-134`).

The common concept is §2 claim verification, but the trigger, parser, evidence contract,
and failure boundary differ. MU is a writer-facing evidence checker over notes; CC is a
commit-message gate. Calling them the same demo erases the integration and false-positive
work each must ship.

### 4. MU-5 and CC-4 — SAME DEMO

MU proposes K signal questions, a tiny logistic regression, calibration report, and a
fixed-rule floor (`WIZARD_IDEAS_MU.md:185-189`). CC proposes a labelled CSV, 3–7 signal
Nouls, a fitted tiny model, a no-fit fixed-rule baseline, calibration, and held-out score
(`WIZARD_IDEAS_CC.md:202-204`).

The packaging and audience differ, but the product contract is the same: replace a single
Jev verdict with signal questions plus a calibrated local head and a baseline. Both make
the same §9/§13 lesson executable and both require refusal when the evidence is too small.
This is genuine convergence.

### 5. MU-3 and CC long-list #6 — SAME DEMO, NOT TOP-FIVE CONVERGENCE

MU's top-five idea is `jev-bead-check <bead-id>`, reading WHAT/ACCEPTANCE and the diff,
then returning a typed completion/evidence checklist (`WIZARD_IDEAS_MU.md:107-119`).
Claude's full 15-item inventory contains “Foreman-lite completion judge wired to our bead
close path” as item #6 (`WIZARD_IDEAS_CC.md:38`).

Thus the orchestrator table's `MU-3 | CC — singleton` is false if “proposed” includes
the full idea files. It is only true under the narrower “top-five shortlist” definition.
That distinction matters: the idea converged, but neither lineage ranked it in both top
fives.

### 6. CC-1 and MU winnowed R3 — SAME DEMO, NOT TOP-FIVE CONVERGENCE

CC-1 proposes a byte-exact fact ledger from dropped messages, appended to pruned context,
then re-scores the same three questions (`WIZARD_IDEAS_CC.md:67-72`). MU's winnowed R3 is
“fact-ledger sidecar (§14 lesson),” explicitly saying “Pair with fact ledger” and calling
it a follow-up rather than a standalone item (`WIZARD_IDEAS_MU.md:228-230`).

The distinction is maturity and packaging, not concept: both propose preserving
answer-bearing facts outside relevance pruning. The table's CC-1 singleton label is
therefore also false for the full inventories, while remaining true for the top-five
shortlists.

## Consequence for synthesis

The sentence “the dispute is implementation, not concept” is defensible only for the two
SAME DEMO top-five pairs (routing and signals). It is too strong for screen and
claim-checking, where policy and integration scope alter the safety and operational
contract. It is also misleading for the two singleton rows, because both have counterparts
outside the other lineage's shortlist.

The honest synthesis should report:

- **2/4 top-five pairings are SAME DEMO.**
- **2/4 are ADJACENT BUT DISTINCT.**
- **2 alleged singletons have same-demo counterparts outside the top fives.**
- Full-inventory concept coverage is broader than shortlist consensus; it should not be
  used as evidence that four independent top ideas converged.

**NO-CLAIM:** I did not implement, run, or live-validate any idea. This is a source-quoted
classification of proposal scope, not a product or consensus measurement.
