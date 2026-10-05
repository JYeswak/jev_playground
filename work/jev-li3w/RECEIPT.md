# jev-li3w receipt

Protocol: `PREREG.md`, frozen before pair extraction. Recompute with
`python3 work/jev-li3w/stability.py --json`.

## Keyless same-pair check

Source: `~/.local/state/jev/memory-filter.jsonl` (operator-local; hashes and
outcomes only). Include only `status=scored` rows with exact pair identity
`promptHash + memoryHash` and `drop`/`keep` decisions; exclude all other
statuses.

At freeze time: 5,763 unique scored pairs; 126 repeated pairs; 2 flipping
pairs (1.5873%, below the preregistered 5% bar). The complete 126 pair hashes
are in `frozen-pairs.jsonl`. Census includes prior code eras and is descriptive,
not a causal estimate of one code version. The runner recomputes and refuses
if the local source census differs from the committed pair list.

## Live rescore

Pending. Exact text comes only from the mode-0600
`~/.local/state/jev/memory-filter-full.jsonl` sidecar, joined on both hashes
and hash-verified in memory. No prompt or memory text is written to the repo.
Protocol allows 378 total calls; cap and auth-stop behavior are in
`rescore.mjs`. Spend is `$0.042 / 1,000,000` input tokens; output is free.
No live result or spend claim yet.

## Boundary

Stability is temporal decision reproducibility only; it does not establish
memory relevance, safe-drop precision, or deployment suitability.
