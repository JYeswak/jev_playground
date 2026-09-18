# Q23 COD-H2 partial-2 non-author grade

Verdict: **PARTIAL_ACCEPTED_HELD_FOR_CALL_PROVENANCE_AND_N5_LIMITS**.

## Pin and live-path audit

The source implementation is real: `jev-client.mjs` posts to `https://api.typesafe.ai/v1/systemone`, sends model `jev-1.13.0`, typed questions and bearer auth, parses the returned Noul probability, and the gate consumes it. The partial2 receipt is internally consistent and states requested/resolved model identity is identical.

The receipt itself does not carry a raw request, response model echo, request ID, or separate pin-probe artifact. Therefore pin identity is **asserted but not independently proven by this receipt**. The five probabilities are plausible and the source path prevents normal canned reuse in `--asker jev`, but per-call live provenance is likewise not independently evidenced.

## Boundary and wedge

The values map exactly to policy: `.94 → pass`, `.48 → withhold`, `.06/.02 → escalate`, `.74 → withhold` because pass begins at `.75`. The mismatch is an honest boundary outcome, not a calibration result. At N=5 no calibration, accuracy, coverage, or threshold-quality conclusion is possible.

## Decision

Accept the partial mechanism with a provenance hold. Do not reject the build: the source path is real and the outcomes are distinct. Keep live-call provenance and N=5 calibration limits explicit; a future receipt needs per-call evidence or an independently observable response/model pin.

NO-CLAIM: pane2 made no live API call, did not claim calibration/accuracy/coverage, and did not resolve the prior UBS provenance hold.
