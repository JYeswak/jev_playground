# Planning Packet — foundation kit (jev calibration + gates + caller)

DRAFT ONLY — check-readiness.sh has not been run on this file. Nothing here
is an execution sign-off and no readiness is asserted. Filled by pane 5 on
2026-09-23 from files on disk: foundation/CALIBRATION.md,
foundation/gates.sh, foundation/kit/claims.tsv, work/jev-client/README.md.

## 1. Problem
<!-- CHECK: PROBLEM -->
The lane needs a falsifiable answer to whether Jev's probabilities can drive
thresholds in code, owned by one caller and guarded by gates that prove RED.
Today that answer is CALIBRATION.md v1 (ECE 0.061, Brier 0.020 on 80 rows,
model jev-1.13.0) plus gates.sh aggregating sixteen gates.d stages.
Success means a fresh agent can rerun the calibration, the gates, and the
sanctioned caller offline and get the same verdicts without asking anyone.

## 2. Non-goals — what this is NOT
<!-- CHECK: NON-GOALS -->
This packet does not certify any Jev seat for production use; a wrapper with
passing tests proves the failure taxonomy, not that any judgment is correct.
It will not re-tune the 0.75/0.8 thresholds on new data — that is a future
audit with its own preregistered bar, out of scope here.
It never invents corpus rows to make a gate pass; authored evidence inflates,
so ground truth must already exist on disk or the packet stays unfilled.

## 3. State-of-the-art survey
<!-- CHECK: SOTA -->
The incumbent caller is work/jev-client at the commits named in its README
(943158c cutover, 118180e score path, c84d562 rerank rewire), built on the
vendored first-party SDK upstream/typesafe-ai/typesafe-sdk-js pinned at
commit 66880cc — adopt as-is, since hand-rolled POST clients are gone.
The calibration fixture (fixtures/calibration-v1.jsonl, 80 rows) and receipt
runs/20260917T224444Z.json are the pinned version-1 evidence: adapt by
appending strata, never by editing rows in place.
The sixteen gates.d stages (10-fixture-integrity through 97-readme-counts)
are the survey's gate corpus; reject any proposal to add a seventeenth
before it names the defect class the existing sixteen miss, retry only when
two stages demonstrably fail on different things per gate-outcomes.tsv.

## 4. Work packets
<!-- CHECK: PACKETS -->
Packet F1 calibration-rerun: goal is reproducing ECE 0.061 / Brier 0.020 from
the frozen runner; anchor is foundation/run_calibration.py; target is the
receipts directory; oracle is byte-identical metrics on the pinned fixture;
fixture manifest is calibration-v1.jsonl happy path plus interrupt-partial
edge; risk is model-version drift behind jev-latest; acceptance is exit 0
with 80/80 rows and no error_kind surprises.
Packet F2 gate-thrift: goal is landing any new check inside an existing
gates.d stage; anchor is gates.sh stage loop; target is the matching stage
script; oracle is --selftest RED plus run PASS; fixture is the stage's own
planted-bad input; risk is two checkers failing on the same commits;
acceptance is gate-outcomes.tsv showing decorrelated failures.

## 5. Claim inventory
<!-- CHECK: CLAIM-INVENTORY -->
The registry foundation/kit/claims.tsv currently holds one planned row:
official-sdk, enforced yes, proof work/jev-client/src/index.ts, with the
explicit boundary that fixture bins are not this claim.
Every further public claim (ECE holds on stratum X, gate Y fires on known-bad
Z) registers in claims.tsv as planned before any demo cites it, with the
proof slot naming the receipt path that will fill it.
No claim graduates past planned without its artifact on disk and a reviewer
initial beside the row.

## 6. Evidence design
<!-- CHECK: EVIDENCE-DESIGN -->
Every receipt records the repo commit (gates.sh resolves HEAD once per run),
the model version (jev-1.13.0 pinned, never the moving alias), and the host
it ran on, following the CALIBRATION.md lane table (lane, N, date, version).
Calibration receipts carry fixture SHA, per-row error_kind, and metric
outputs; gate runs append one TSV line per stage per run to
gate-outcomes.tsv for later decorrelation analysis.
A receipt generated on a different fixture generation or model version is
not evidence for this release — it is a new measurement needing its own row.

## 7. Honesty machinery
<!-- CHECK: HONESTY-MACHINERY -->
The negative-evidence ledger lives at the repo root as NEGATIVE_EVIDENCE.md;
each row states the refuted hypothesis, the measurement that killed it, and
the retry-condition predicate under which it may be reopened.
Demotion rules: any claim whose proof artifact is missing, stale-pinned, or
measured against an authored corpus is demoted to planned until re-proven.
Ledger preflight blocks rows without a falsifying observation or without a
predicate; resurrection cadence is one re-audit per planning cycle, and only
for rows whose predicate names a genuinely new fact.

## 8. Proof taxonomy [PROVISIONAL]
<!-- CHECK: PROOF-TAXONOMY -->
Admissible: offline unit proof against an injected asker, fixture receipt
with SHA pinning, --selftest RED-arm demonstration, differential run against
the incumbent SDK path, and independent-reviewer confirmation.
Explicit non-proof list: a green suite around upstream code we do not own, a
remembered number without a receipt path, two panes agreeing about our own
artifact, and any live smoke presented as a distribution.
The non-proof list grows only when a dispute forces an entry; keep it short.

## 9. Release gate
<!-- CHECK: RELEASE-GATE -->
Publication is blocked while any gates.d stage is RED, while any cited
claim lacks its proof artifact, or while a secret appears anywhere in the
tree including fixtures and recorded responses.
A waiver of a non-load-bearing clause requires a public recorded entry with
owner, rationale, expiry date, and compensating controls; waivers expire and
must be re-argued, never silently renewed.
No waiver can cover a RED honesty-machinery finding or an unsigned packet —
those clauses are not waivable under any owner.

## 10. Phase exit criteria
<!-- CHECK: EXIT-CRITERIA -->
Phase A entry: this packet filled from files on disk with all twelve markers
present. Phase A exit: check-readiness.sh green on the working copy plus an
independent-review attestation, however honest about its limits.
Phase B entry: Phase A exit proof recorded. Phase B exit: calibration
rerun receipt plus full gates.sh PASS with zero UNMEASURED on the pinned
fixture, committed beside the packet.
No phase gate may claim a result whose dependency closure contains an
unresolved OPEN item from the beads graph.

## 11. Independent review
<!-- CHECK: REVIEW -->
Independent review: not performed (solo) — nothing was independently
changed. This draft was assembled by one pane from four source files with
no fresh-eyes pass and no second model; residual risk accepted by pane-5
pending reviewer assignment.
What changed as a result of review: nothing yet, since no review has
occurred; the review packet for the assigned reviewer is this file plus
the four sources named in the header.

## 12. Execution sign-off
<!-- CHECK: SIGN-OFF -->
DRAFT — no execution is authorized by this section. check-readiness.sh has
not been run on this draft and §11 records no independent review; the
plan as written is unreviewed and unsigned for execution purposes.
Recorded for attribution only. Signed as draft: pane-5, 2026-09-23.
