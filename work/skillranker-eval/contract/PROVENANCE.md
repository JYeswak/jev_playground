# Contract provenance

Pulled 2026-09-20 via `gh api` from public `Dicklesworthstone/skillranker`.
These bytes are **their evaluation contract**, not a measurement of their product.

| file | bytes | sha256 | upstream content sha |
|---|---:|---|---|
| `evaluation_policy.v1.json` | 9650 | `b0f35abdc436c6cd91358d290850d22cd2572979067821e06e3b30cf6ffed5da` | `eb60bf8e523528451ce7df70f62185f320e3347b` |
| `expected_values.v1.json` | 5212 | `a05aa971a0c99f1587c5ffcefcbc3842f0055fdbfb817b7fd694150a3ea5dda6` | `760c8edeb1ba8e7131d6d72176bfd8c70c804e34` |
| `synthetic_cases.v1.jsonl` | 11604 | `50ffd624fb6d065f8a79e672daf8d5bd305c47d8f40358ba9d7543c149085f98` | `d5a4d6c7bf5c8a6876f44888831330f690092788` |
| `README.upstream.md` | 1943 | `0236775fe98ad10395956e06d6effa4cbb7e189ed3385ed804fc11cc467d6e65` | `6ba40800f7599e3a329fd561dcb7ba91f8b0be56` |

- **Commit at fetch:** `bb52b8f256e72917b2b64963217350421c6b5bf0` (`bb52b8f25`) on `main`
- **Their status fields:** `frozen_contract_not_evidence` / `deterministic_contract_examples_not_measured_results`
- **Split on all 12 cases:** `diagnostic_synthetic` — their policy forbids promotion, calibration, or statistical quality claims on this split
- **License:** MIT (plus their OpenAI/Anthropic rider on the upstream repo). Attribution required.

Do not treat a green run of *this* harness as a SkillRanker product result.
That claim requires their `sr` binary path and their prompt construction.
