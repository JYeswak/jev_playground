# jev-li3w: Same-pair memory-filter stability preregistration

Status: FROZEN before pair selection and any new model calls.
Bead: `jev-li3w`

## Estimand

For one unchanged `(promptHash, memoryHash)` pair, how often does the
`jev-1.13.0` memory-filter decision differ across scored evaluations? Report
keyless historical and newly rescored arms separately. A pair is a flip if its
set of scored decisions contains both `drop` and `keep`; duplicate rows with
the same decision are not flips. Non-scored statuses (including `memo`,
`daily-cap`, and `cap3-pruned`) are excluded from the decision estimand.

## Frozen sample and bar

- Historical keyless arm: every pair in
  `~/.local/state/jev/memory-filter.jsonl` with at least two `status=scored`
  rows, grouped by exact `promptHash + memoryHash`. No sampling.
- Live arm: every repeated pair in the frozen keyless source (126 pairs in the
  census used for this preregistration). Rescore each pair three times, same
  model and unchanged payload; 378 calls maximum. The complete pair identities
  are frozen in `rows.jsonl` before the first live request.
- Frozen estimator in each arm: flipping-pair count / tested-pair count.
- Stable iff flip rate is <= 0.05 in each arm. Any arm above 0.05 MUST report
  `UNSTABLE`; never report `STABLE` on partial live coverage.
- NO-CLAIM beyond the exact observed pairs; this is temporal decision
  reproducibility, not memory relevance or safe-to-drop validation.

The 5% bar was entered in bead comment 1285 before the older run (comments
1288-1293 note that run's failure to preserve a preregistration artifact).
This file freezes the same stated estimand/bar for the current keyless census
and any subsequent live calls; it does not retroactively validate the old run.

## Bounded live protocol

The runner accepts only the frozen pair identities and payloads joined from
the mode-0600 sidecar before calls begin; it MUST NOT select or change pairs
afterward. Hard cap: 378 requests, one pass of three calls per pair, no retries.
Stop immediately on HTTP 401, 402, or 403. Pin `jev-1.13.0`; record sanitized
rows only: pair hashes, round, decision, status, input tokens, latency, and
model. Spend is `inputTokens * $0.042 / 1,000,000`; output spend is $.
Missing credentials mean `NOT_RUN`, not a fallback. Never write prompt or
memory text into the repository.

The operator-local source sidecar contains exact payloads and is mode 0600.
The repo ledger contains hashes/outcomes only.

## Verification boundary

`python3 work/jev-li3w/stability.py --json` recomputes the historical arm from
the operator-local log and reads only committed/supplied sanitized live rows.
Without live rows it reports `NOT_RUN` and makes no network calls.
The live arm is unverified until populated by a separately authorized,
bounded caller with the exact pair payloads.
