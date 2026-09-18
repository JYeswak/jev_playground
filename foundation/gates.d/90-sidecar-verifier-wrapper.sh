#!/usr/bin/env bash
# Stage 90 — run the sidecar verifier as a GATE, mapping its transient class to UNMEASURED.
#
# WHY THIS EXISTS, and it is the first instrument in this lane to earn a consumer.
#
# `verify-other-reasons.sh` was hand-run for this entire session and pane 2 refused to promote it
# FOUR times, each refusal naming a real unmet precondition. On the fifth ruling
# (docs/demos/duel-2/runs/ruling-sidecar-promotion-20260918T160000Z.json, f862ec0) it flipped:
#
#   "PROMOTE_TO_FOUNDATION_WRAPPER ... Keeping it indefinitely hand-run would make it PROCESS under
#    the new tick boundary. Promotion must be through a foundation wrapper, not direct commit wiring."
#
# The new tick's creation gate is what moved it: an instrument nothing branches on is process, however
# good its arms are. So this stage is the consumer, and the four gate fields are recorded here rather
# than asserted in prose elsewhere:
#
#   CONSUMER            foundation/gates.sh (this stage)
#   GATE                sidecar metadata integrity
#   OBSERVED DEFECTS    exact other-row coverage · digest mismatch · locator mismatch · provenance
#                       absence · short-row masking · snapshot/transient races
#   RETIREMENT          "retire or demote only after a replacement verifier consumes the same sidecar
#                       contract with equal or stronger arms and a recorded migration; NEVER delete
#                       because the current run is green"
#
# THE ONE HARD CONSTRAINT, quoted because getting it wrong is the whole risk: "foundation wrapper must
# distinguish TRANSIENT_UNSTABLE from durable RED; DIRECT AGGREGATION OF rc10 AS ORDINARY DURABLE RED
# IS NOT ACCEPTABLE." Pane 2 warned earlier in the session that foundation "would collapse rc10 to RED
# if wired" — a peer editing evidence mid-run would then RED the suite for everyone. rc10 means the
# verifier declined to issue a verdict; a gate that reports "no verdict" as "failed" manufactures
# failures out of concurrency, which in a three-pane shared worktree is a self-inflicted outage.
#
# rc13 (symlink escape) IS durable: it is a defect in the evidence, not a race.
set -euo pipefail

root="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$root"

out="$(./scripts/verify-other-reasons.sh 2>&1)" && rc=0 || rc=$?

case "$rc" in
  0)
    echo "PASS  stage 90 sidecar verifier            rc=0 coverage, bindings and locators clean"
    exit 0
    ;;
  10)
    # UNMEASURED, not PASS and not FAIL. Named explicitly so a reader cannot mistake a race for proof.
    echo "UNMEASURED  stage 90 sidecar verifier      rc=10 TRANSIENT_UNSTABLE — source moved during"
    echo "            both bounded captures; the verifier withheld its verdict, so this stage has"
    echo "            NOTHING TO REPORT. Not a pass: nothing was verified. Not a failure: nothing"
    echo "            failed. Re-run when the tree is quiet."
    echo "$out" | sed 's/^/            /'
    # EXIT 7, not 0. Exiting 0 here was MY defect: the aggregator prints PASS on 0 and discards
    # stdout, so "nothing was verified" was laundered into a green row and ALL GREEN asserted
    # something no stage had established. Pane 2 caught it (2e7bab2). 7 is nonblocking but surfaced.
    exit 7
    ;;
  13)
    echo "FAIL  stage 90 sidecar verifier            rc=13 SYMLINK ESCAPE — cited evidence resolves"
    echo "      outside the repository boundary. Durable: a defect in the evidence, not a race."
    echo "$out" | sed 's/^/      /'
    exit 1
    ;;
  2)
    echo "FAIL  stage 90 sidecar verifier            rc=2 usage/environment — STATUS or sidecar missing"
    echo "$out" | sed 's/^/      /'
    exit 1
    ;;
  *)
    echo "FAIL  stage 90 sidecar verifier            rc=$rc durable verification failure"
    echo "$out" | sed 's/^/      /'
    exit 1
    ;;
esac
