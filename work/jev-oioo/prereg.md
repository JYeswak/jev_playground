# jev-oioo unseen SciFact confirmation preregistration

**Status:** amended and committed before any Jev or comparator call.
reach-mode: mcnemar

## Frozen public corpus and sample

- Dataset: `tdiggelm/climate-fever`, release/tag `1.0.1`, official source
  `https://raw.githubusercontent.com/tdiggelm/climate-fever-dataset/1.0.1/dataset/climate-fever.jsonl`.
- Source SHA-256: `8a4b9032d861be482ffb49dddfd283ffa6089e654f1e968040011882c5eb6e0b`.
- The source has 1,535 claims and four labels. Only the dataset's own `SUPPORTS` and `REFUTES`
  labels are eligible; `NOT_ENOUGH_INFO` and `DISPUTED` are excluded before scoring.
- The confirmation corpus is all `907` eligible pairs: 654 `SUPPORTS` and 253 `REFUTES`, in
  source-row order. No sampling or post-hoc filtering is applied. The hash-only item manifest is
  `work/jev-oioo/items.jsonl` (SHA-256 `bbda30671b46678a11717d0fa89994b5226e9887ff321ec70a860e45f579032c`).
- For every state, `claim` is the dataset claim and `evidence` is the list of exactly the five
  `evidences[*].evidence` sentences in their source order. Evidence IDs, votes, entropy, and
  article metadata are not sent. The raw source/state stays local under `var/agent-tmp/jev-oioo/`.

## Jev and free comparator

- Jev: exactly `jev-1.13.0`, through the pinned kit client and `kit/experiment/run.py`.
- Jev question: exactly `kit/src/verify.ts` (`SCIFACT_INSTRUCTIONS`, `SCIFACT_CRITERIA`, support
  cut `0.5`), with state `{claim, evidence}` from the frozen item.
- Comparator: OpenRouter model `dots-studio/dots-3-note-preview:free`, the allowed free comparator.
  It receives the identical claim/evidence pair through the fixed comparator prompt in the runner and
  must return JSON `{supported: boolean, confidence: number}`; malformed output is a refusal.
- No paid comparator, no Anthropic/xAI/paid OpenRouter arm.

## Preregistered bar

Primary: paired Jev accuracy must be strictly higher than comparator accuracy on the same valid rows,
with exact two-sided McNemar p `< 0.05` (`b` Jev-only correct, `c` comparator-only correct, require
`b > c`). Secondary: Jev Brier score must be no worse than comparator Brier. Each arm's refusal rate
must be `<= 5%`; refusals are counted and excluded from valid accuracy/Brier denominators, never
coerced into an answer. Wilson 95% intervals are reported for accuracy and refusal rates.

## Reach and spend

The reach receipt is bound to this preregistration, the item-manifest hash, and `mode: mcnemar`.
The arithmetic reach bar is six Jev-only discordant wins and zero comparator-only wins: exact two-sided
McNemar p `0.03125 < 0.05`, so 907 paired rows can reach the primary test. The exact state-size check
must show all 907 requests `FITS` before the first call.

Input-token spend is computed from Jev usage at the documented `$0.042/M` input-token price; output
is free. OpenRouter spend and usage are recorded from its response metadata. The receipt records model,
rows, refusals, latency, usage, accuracy, Brier, McNemar, Wilson intervals, and total spend for both
arms. This is an unseen public sample measurement, not a fleet-wide claim or promotion decision.
