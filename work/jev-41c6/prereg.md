# Climate-FEVER H2: per-sentence Noul fan-out dev replay

Status: PREREGISTERED BEFORE LIVE CALLS
Bead: jev-41c6
Date: 2026-09-27
reach-mode: mcnemar

## Question and scope

H1 used one Noul over all five evidence sentences and failed on the 200-row dev slice (147 H1 vs 148 committed baseline, exact two-sided McNemar p=1.0; `jev-za3a`). H2 tests exactly one design change: fan out to one support Noul and one contradiction Noul per evidence sentence, then aggregate in code.

This is a Jev-only development-slice replay. It is not a held-out result, a fleet claim, or a promotion decision. A preregistered H2 win at exact two-sided McNemar `p < 0.05` licenses a fresh held-out test on another claim set. Otherwise the frozen next step is H3.

## Frozen public data and same dev ids

- Dataset: `tdiggelm/climate-fever`, release/tag `1.0.1`, official source.
- Source SHA-256: `8a4b9032d861be482ffb49dddfd283ffa6089e654f1e968040011882c5eb6e0b`.
- State source: existing `var/agent-tmp/jev-oioo/states.jsonl`, SHA-256 `f463ac2bb3002ec1d0262b02f3448068e9cfead5417ea1497d1680537019acb9`.
- Dev id manifest: existing `work/jev-oioo/h1-dev-items.jsonl`, exactly 200 unique IDs, SHA-256 `a3c4359f502fee27e4b212d4d606f3c22da53b153fe5c706c43f6fd700a754a7`.
- Every manifest ID occurs exactly once in the state source and in the committed H1 baseline rows. The state contains `{claim, evidence}` only for the request; no gold label, `source_claim_id`, or stratum is sent to Jev.
- The five evidence sentences remain in the existing source order. No sentence is added, removed, rewritten, labeled, or selected using gold information.
- Baseline: the committed H1 Jev answers in `work/jev-oioo/live-results.jsonl`, restricted to the same 200 IDs. Baseline exact correctness is 148/200 (0.740), all 200 baseline rows scored.

## Jev request and per-sentence fan-out

- Model: exactly `jev-1.13.0`.
- One API request per dev row, with ten Noul questions evaluated in parallel against the identical state: `support_0` through `support_4`, and `contradict_0` through `contradict_4`.
- For sentence index `j`, the support instruction is exactly: `Does evidence sentence j support the claim?`
- For sentence index `j`, the contradiction instruction is exactly: `Does evidence sentence j contradict the claim?`
- Support criteria are exactly: true = `The sentence states the claim or directly implies that it is true`; false = `The sentence contradicts the claim or does not address what the claim asserts`.
- Contradiction criteria are exactly: true = `The sentence states information incompatible with the claim`; false = `The sentence does not state information incompatible with the claim`.
- A Noul value is valid only if finite and in `[0,1]`. The fixed threshold is strict `> 0.5`; exactly `0.5` is false. Every raw value, question name, model, latency, and usage field is stored in the committed hash-keyed row.
- If any of the ten values is missing, malformed, outside `[0,1]`, or the request is refused, the whole row is `invalid`; no partial aggregation or imputation is allowed. Invalid rows are reported and excluded from the paired accuracy denominator.
- Design citation: this is the speculative fan-out pattern described in `docs-mirror/typesafe/patterns/fan-out.md`; the Noul response contract and `[0,1]` validation follow `docs-mirror/typesafe/primitives/noul.md` and `kit/src/verify.ts`.
## Frozen aggregation and decision rule

For each valid row:

1. `support_hit = any(support_j > 0.5 for j in 0..4)`.
2. `contradict_hit = any(contradict_j > 0.5 for j in 0..4)`.
3. H2 predicts `SUPPORTS` iff `support_hit` is true **and** `contradict_hit` is false. Every other case predicts `REFUTES` (including no support and no contradiction, or support plus contradiction).
4. Compare this aggregate prediction with the dataset gold label. Gold is used only for scoring after the Jev request, never in the state or question construction.

Primary pass bar, fixed before calls: among paired rows where both H2 and baseline are valid, H2 accuracy must be strictly greater than the committed H1 baseline accuracy, with exact two-sided McNemar `p < 0.05` and `b > c`, where `b` is H2-only correct and `c` is baseline-only correct. Exact p is `min(1, 2 * BinomialCDF(min(b,c); b+c, 0.5))`. The H2 result is `CONFIRM_H2` only when the primary bar and refusal bar both pass.

Refusal bar: H2 invalid/refused rows must be `<= 5%` of the 200 requested rows. Invalid rows remain visible and do not become correct or incorrect predictions. Secondary reporting: H2 valid count, accuracy, baseline valid count and accuracy, `b`, `c`, exact p, support-hit rate, contradiction-hit rate, both-hit rate, neither-hit rate, per-question raw Noul distributions, latency, input/output tokens, and spend.

## Reach, size, and spend

- Reach receipt: `work/jev-41c6/reachability.json`, bound to this prereg SHA, the 200-ID manifest SHA, and `mode: mcnemar` before the first call.
- Reach arithmetic: with 200 paired rows, `b=6,c=0` gives exact two-sided p `0.03125 < 0.05`; therefore the primary test is reachable if at least six H2-only wins and no baseline-only wins occur. The receipt records `minimum_h2_only_wins=6` and `maximum_baseline_only_wins=0` as the reach witness, not as an observed result.
- Keyless state-size preflight uses `scripts/jev-state-size.py` against the pinned state source with the compact ten-question payload; all 907 source states were `FITS` (the 200 dev states are a subset). Maximum compact H2 request bytes were 3,129; question bytes were 921.
- Maximum live calls: 200 Jev requests, each with ten Noul questions; no comparator calls and no OpenRouter key/use.
- Jev spend is recorded from each response's input tokens at the documented `$0.042/M` input-token rate; output is free. The receipt reports total input tokens, output tokens, latency, and total spend.
- Retry policy is bounded and pinned by the runner; a Jev refusal or transport failure is recorded as invalid and never retried into an unbounded loop. No free-tier or paid comparator arm is permitted.

## Boundary

This preregistration freezes a Jev-only dev replay on the same 200 IDs used by H1. It does not claim H2 performance before live calls, does not compare against an LLM, and does not license deployment. A pass only licenses a new held-out claim set; a failure selects the frozen H3 next step.
