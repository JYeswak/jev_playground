# jev-li3w receipt

Protocol: `PREREG.md`, frozen before pair extraction. Recompute with
`python3 work/jev-li3w/stability.py --json`.

## Keyless same-pair check

Source: `~/.local/state/jev/memory-filter.jsonl` (operator-local, not committed;
raw rows contain hashes and model outcomes). Estimator includes only rows with
`status=scored`, exact `promptHash` + `memoryHash` pair identity, and binary
`drop`/`keep` decision. Non-scored records are excluded.

Initial census recorded during implementation: 5,707 unique scored pairs;
126 pairs scored more than once; 2 flipping pairs; 1.59% observed flip rate.
This is below the preregistered 5% descriptive bar for this historical census.
Source includes post-cutover and prior-era rows; the pooled result is NOT a
causal estimate of a single code version. The committed runner reports the
current source contents on each invocation.

## Live rescore

NOT RUN. The local log stores only pair hashes, not original prompt/memory
payloads. The bounded protocol requires exact unchanged payloads. Reconstructing
payloads from digests is impossible; no live requests were attempted. Spend:
$0.00. No claim of a live stability pass.

## Boundary

Keyless result is descriptive stability of observed repeated calls, not memory
relevance, safe-drop precision, or a deployment claim. The live arm remains
NOT_RUN until supplied exact payloads and 60-or-fewer responses.
