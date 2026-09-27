# jev-cqex H3 result

Status: KEYLESS REANALYSIS; no Jev or comparator call.

## Provenance

- Preregistration commit: `1e93d749`
- Preregistration SHA-256: `2f95cc5e72d2ac86337f151d415865ce81eb04e9bad908a6ee63359def6f0358`
- Climate-FEVER source SHA-256: `8a4b9032d861be482ffb49dddfd283ffa6089e654f1e968040011882c5eb6e0b`
- Existing item manifest SHA-256: `bbda30671b46678a11717d0fa89994b5226e9887ff321ec70a860e45f579032c`
- Existing committed Jev answer rows SHA-256: `dff1141f3f031efac673b02e546454f3afbf6d06c69f5e5cd9fc848260ac1de7`
- Hash-keyed strata file: `work/jev-cqex/strata.jsonl`
- Strata SHA-256: `95b827deda021ee9510ae69d15e1dd05daa6b79d85749d499a4b480ce68ff117`
- Rows: 907/907 joined and scored; prediction is strict `noul > 0.5`.

## Frozen-stratum results

Wilson intervals are two-sided 95% intervals.

| Stratum | n | Jev correct | Accuracy | Wilson 95% |
|---|---:|---:|---:|---:|
| Majority evidence label agrees with claim | 412 | 301 | 0.7305825243 | [0.6857578550, 0.7711470446] |
| Majority evidence label disagrees with claim | 495 | 291 | 0.5878787879 | [0.5440027756, 0.6304013330] |
| Ambiguous majority tie | 0 | 0 | N/A | N/A |

## Preregistered diagnostic

The `disagree` accuracy is `0.5878787879`, which lies within the preregistered near-chance band `[0.40, 0.60]`. The `agree` accuracy is `0.7305825243`.

This is the preregistered keyless diagnostic only. It does not establish a general Climate-FEVER capability, prove causality, license deployment, compare against an LLM, or constitute a ruling. No new model calls were made.

## Exact computation

```text
python3 work/jev-cqex/analyze.py
```

The computation joined source evidence labels to existing hash-keyed IDs, assigned the frozen unique-majority strata, applied strict `noul > 0.5`, and computed Wilson intervals. Raw claim/evidence text is not in the committed strata file.
