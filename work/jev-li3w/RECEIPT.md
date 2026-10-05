# jev-li3w receipt

Protocol: `PREREG.md`, frozen before pair extraction. Recompute with
`python3 work/jev-li3w/stability.py --json`.

## Keyless same-pair check

Source: `~/.local/state/jev/memory-filter.jsonl` (operator-local; hashes and
outcomes only). Include only `status=scored` rows with exact pair identity
`promptHash + memoryHash` and `drop`/`keep` decisions; exclude all other
statuses.

At freeze time: 5,763 unique scored pairs; 126 repeated pairs; 2 flipping
pairs (1.5873%, below the preregistered 5% bar). Exact sidecar payloads exist
for 97 of those pairs; their identities are in `frozen-pairs.jsonl`. The
remaining 29 identities and absence reason are in `not-run.jsonl`. Census
includes prior code eras and is descriptive, not causal for one code version.

## Live rescore

Pending. The runner joins exact text from the mode-0600
`~/.local/state/jev/memory-filter-full.jsonl`, verifies both SHA-256 hashes in
memory, and writes no prompt/memory text to the repo. Cap: 291 requests, 97
pairs x 3. Stop on HTTP 401/402/403; no retries. Spend is
`inputTokens * $0.042 / 1,000,000`; output is free. No live calls or results
yet.

## Boundary

Stability is temporal decision reproducibility only; it does not establish
memory relevance, safe-drop precision, or deployment suitability.
