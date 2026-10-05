# jev-li3w receipt

Protocol: `PREREG.md`; 5% bar committed before calls. Recompute keyless and
live results with `python3 work/jev-li3w/stability.py --json`.

## Keyless same-pair check

Source: operator-local `~/.local/state/jev/memory-filter.jsonl`. Include only
`status=scored` rows, exact `promptHash + memoryHash`, binary `drop`/`keep`.
At final recomputation: 5,770 unique scored pairs; 126 repeated pairs; 2
flipping pairs (1.5873%, below the preregistered 5% bar).
Exact sidecar payloads were available for 97 pairs; their identities are in
`frozen-pairs.jsonl`. The remaining 29 identities and absence reasons are in
`not-run.jsonl`. The census includes prior code eras and is descriptive, not
causal for one code version.

Live flips: 1/97 pairs = 1.0309% (below 5%; descriptive `STABLE` for the
rescorable subset). Input tokens: 124,968. Cost at $0.042 / 1M input tokens,
output free: **$0.005248656**. Model on all responses: `jev-1.13.0`.
Mean latency 162.48 ms; p95 243 ms.

## Boundary

Not a complete estimate for all 126 repeated pairs: 29 pairs were unavailable
for live rescore. This measures temporal decision reproducibility only; it does
not establish memory relevance, safe-drop precision, or deployment suitability.
