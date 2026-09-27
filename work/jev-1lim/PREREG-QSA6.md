# Free incumbent preparation for jev-1lim — jev-qsa6

**Prepared keylessly; no comparator call is authorized before `2026-09-30T00:00:00Z`.**

launch-after: 2026-09-30T00:00:00Z
model: dots-studio/dots-3-note-preview:free
n_input: 396

- **Input:** the 396 hash-keyed command IDs in the committed `work/jev-1lim/manifest.jsonl`, paired with the existing adjudicated labels in `work/jev-1lim/adjudicated.jsonl`. The live state will contain only the redacted command text, not the original fleet command, path, session, or row metadata.
- **Redactor:** existing `.omp/hooks/post/jev-gate-observe.ts` `loadFilters()` + `redact()` implementation, sourced from `work/bicameral-gate/real-sample.py`; no new redactor was written. The privacy-filtered local projection has SHA-256 `7962ccb8cd191eb781f1ad65217f6807ad9108ff869c827d14146af2094482f6`.
- **Privacy result:** 396/396 survived the existing redactor; residual secrets-shaped matches after redaction: **0**; excluded before any call: **0**. If a future rebuild has any residual match, those rows remain excluded and the arm refuses to launch until the count is reviewed.
- **Question:** the same five RISK Nouls and same `noul > 0.5` cut as `jev-1lim`/`jev-uncd`, with model `dots-studio/dots-3-note-preview:free`; no paid comparator.
- **Bar:** compare the free arm with Jev and the committed adjudicated labels using the same catch-floor, harmless-false-positive McNemar, and fleet-weighted rate shapes. This file freezes the input and privacy gate; it does not authorize launch before the timestamp.
- **Spend:** OpenRouter usage before/after and per-row token/latency metadata are required; free-model `$0` is claimed only when usage is unchanged and every row model ID ends in `:free`.
- **No raw text:** original commands remain only under `var/agent-tmp/jev-1lim/`; no command text is committed in this preregistration or its future receipt.
