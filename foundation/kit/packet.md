# Planning Packet — foundation kit

Working copy of notes/foundation-packet-p5.md. Three sentences in that draft
were false when checked against the files it cites, and are not repeated here:

- CALIBRATION.md does not mention a host. Calibration receipts record
  started_at, model, and fixture sha256. They do not record host or worker.
- work/jev-client/README.md names the score-path commit as 118185e, not 118180e.
- foundation/gates.d has the executable stages on disk. The draft's "sixteen"
  does not match that directory. This packet does not restate a count.

DRAFT — this file is not an execution sign-off. The readiness checker scores
structure. It does not score truth.

## 1. Problem
<!-- CHECK: PROBLEM -->
The lane needs a falsifiable answer to whether Jev's probabilities can drive
thresholds in code, owned by one caller and guarded by gates that prove RED.
Today that answer is CALIBRATION.md v1 (ECE 0.061, Brier 0.020 on 80 rows,
model jev-1.13.0) plus gates.sh aggregating the stages in foundation/gates.d.
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
The incumbent caller is work/jev-client. Its README names the cutover commit
943158c, the score-path commit 118185e, and the rerank rewire c84d562. The
vendored SDK is upstream/typesafe-ai/typesafe-sdk-js at commit 66880cc.
The calibration fixture fixtures/calibration-v1.jsonl and the receipt
runs/20260917T224444Z.json are the pinned version-1 evidence. Append strata.
Do not edit rows in place.
A new gate earns a slot only when it names a defect the existing stages miss.
Two checkers are worth having only when they fail on different commits.

## 4. Work packets
<!-- CHECK: PACKETS -->
Packet F1 calibration-rerun: goal is reproducing the frozen runner's metrics;
anchor is foundation/run_calibration.py; target is the receipts directory;
oracle is the metrics on the pinned fixture; fixture manifest is
calibration-v1.jsonl plus the interrupt-partial edge; risk is model-version
drift behind jev-latest; acceptance is a receipt with 80 rows and no dropped
error_kind.
Packet F2 gate-thrift: goal is landing a new check inside an existing gates.d
stage; anchor is gates.sh; target is that stage; oracle is --selftest RED
plus run PASS; fixture is the stage's planted-bad input; risk is two checkers
failing on the same commits; acceptance is gate-outcomes.tsv.

## 5. Claim inventory
<!-- CHECK: CLAIM-INVENTORY -->
The registry foundation/kit/claims.tsv holds one enforced row, official-sdk,
proof work/jev-client/src/index.ts. Fixture bins are not this claim.
Every further public claim registers in claims.tsv as planned before any
demo cites it, with the proof slot naming the receipt path that will fill it.
No claim graduates past planned without its artifact on disk.

## 6. Evidence design
<!-- CHECK: EVIDENCE-DESIGN -->
Calibration receipts record started_at, model version, and fixture sha256.
They do not record host or worker. Citing a host for those receipts is a
false sentence; this packet does not do it.
gates.sh records the repo commit once per run in gate-outcomes.tsv, beside
the stage name and exit code. A receipt from a different model version is
not evidence for this release.

## 7. Honesty machinery
<!-- CHECK: HONESTY-MACHINERY -->
The negative-evidence ledger lives at the repo root as NEGATIVE_EVIDENCE.md.
Each row states the refuted hypothesis and the retry-condition predicate
under which it may be reopened.
A claim whose proof artifact is missing, or whose number was measured on an
authored corpus, is demoted to planned until re-proven. Resurrection is a
re-audit when the predicate names a new fact, not a rumor.

## 8. Proof taxonomy
<!-- CHECK: PROOF-TAXONOMY -->
Admissible: an offline proof against an injected asker, a fixture receipt
with a sha pin, a --selftest RED arm, and a non-author reading the cited file.
Explicit non-proof list: a green suite around upstream code we do not own, a
remembered number without a receipt path, two panes agreeing about our own
artifact, and any live smoke presented as a distribution.
The non-proof list grows only when a dispute forces an entry.

## 9. Release gate
<!-- CHECK: RELEASE-GATE -->
Publication is blocked while any gates.d stage is RED, while any enforced
claim lacks its proof artifact, or while a secret appears in the tree.
A waiver of a non-load-bearing clause requires owner, rationale, expiry, and
a compensating control. A waiver expires. It is not renewed by silence.
No waiver covers a RED honesty finding or an unsigned packet.

## 10. Phase exit criteria
<!-- CHECK: EXIT-CRITERIA -->
Phase A entry: this packet filled from files on disk, with the twelve markers
present. Phase A exit: check-readiness.sh green on this file, plus a
non-author note of what they opened. Structure-green is not truth-green.
Phase B entry: that note exists. Phase B exit: a calibration receipt and
gates.sh with no UNMEASURED stage, on the pinned fixture.
No phase gate may claim a result whose dependency closure contains an
unresolved OPEN item.

## 11. Independent review
<!-- CHECK: REVIEW -->
Independent review: not performed. An untracked planning draft informed this working copy; the three sentences it got wrong are recorded with their corrections in this file's header (lines 3-10), so no untracked path is cited here.
This working copy changed three sentences after that draft, because those
sentences did not match the files named. Nothing else was independently
changed. Residual risk accepted until a non-author reads this file against
CALIBRATION.md, work/jev-client/README.md, and foundation/gates.d.

## 12. Execution sign-off
<!-- CHECK: SIGN-OFF -->
DRAFT — no execution is authorized by this section. The readiness checker
scores markers and vocabulary. It does not score whether the prose is true.
Signed as draft: conductor, 2026-09-23. Not a release sign-off.
