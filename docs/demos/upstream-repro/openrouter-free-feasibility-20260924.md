# Which OpenRouter free models can carry a 500-row arm? (bead `jev-14qk`)

RedMaple (pane 2), 2026-09-24. No new calls. The six row files were written by MaintFixes after
bar `5498c91` and before scoring. This pass only ran
`python3 work/openrouter/score_feasibility.py` (no key) and saved that stdout as
`work/openrouter/score-feasibility.txt`.

## Result

None of the six models can carry a 500-row arm. The bar requires 50/50 answered and 0
zero-mass rows. The closest, dots, answered 48/50 and had 1 zero-mass row. Pane 1's
`>=49/50` gate for a free comparator (`jev-3e2i`) is also missed. Recommendation: do not
send a full arm to any of these free ids. The paid fallback named in `97bbad6` is the
next comparator.

| Model | Answered | Failed | Zero-mass | Flat | Renormalized | p50 / p95 ms | Upstream |
|---|---:|---:|---:|---:|---:|---|---|
| `dots-studio/dots-3-note-preview:free` | 48/50 | 2 | 1 | 2 | 3 | 19142 / 31853 | AtlasCloud 48 |
| `nex-agi/nex-n2.5-pro:free` | 41/50 | 9 | 1 | 2 | 3 | 64304 / 151582 | Nex AGI 41 |
| `nvidia/nemotron-3-super-120b-a12b:free` | 18/50 | 32 | 4 | 4 | 5 | 6128 / 47124 | Nvidia 18 |
| `google/gemma-4-31b-it:free` | 0/50 | 50 | 0 | 0 | 0 | none |  |
| `qwen/qwen3.8-27b:free` | 0/50 | 50 | 0 | 0 | 0 | none |  |
| `google/gemma-4-26b-a4b-it:free` | 0/50 | 50 | 0 | 0 | 0 | none |  |

Exact / MAE on the answered rows only, descriptive, not a verdict: dots 11/48, MAE 1.35;
nex 13/41, MAE 1.17; nemotron 5/18, MAE 1.22.

## Failure classes, verbatim from the scorer

- `google/gemma-4-31b-it:free`: 31 `TypeSafeRateLimitError: 429 Rate limit exceeded: free-models-per-min.`; 19 `TypeSafeRateLimitError: 429 Provider returned error`. Retries: 67 and 33 of those same two messages.
- `qwen/qwen3.8-27b:free`: 34 `TypeSafeRateLimitError: 429 Rate limit exceeded: free-models-per-min.`; 16 `TypeSafeRateLimitError: 429 Provider returned error`. Retries: 70 and 30.
- `google/gemma-4-26b-a4b-it:free`: 33 `TypeSafeRateLimitError: 429 Rate limit exceeded: free-models-per-min.`; 17 `TypeSafeRateLimitError: 429 Provider returned error`. Retries: 71 and 29.
- `nvidia/nemotron-3-super-120b-a12b:free`: 19 `TimeoutError:`; 6 `TypeSafeAPIResponseValidationError: 200 Invalid response data at 'answers'.`; 6 `TypeError: 'NoneType' object is not subscriptable`; 1 `TypeSafeError: Expecting value: line 75 column 1 (char 407)`.
- `nex-agi/nex-n2.5-pro:free`: 9 `TimeoutError:`.
- `dots-studio/dots-3-note-preview:free`: 2 `TypeSafeAPIResponseValidationError: 200 Invalid response data at 'answers'.`.

## Boundary

No model was called in this pass. Spend $0. The rows are the files MaintFixes left
untracked in `work/openrouter/`. A non-author re-score is
`python3 work/openrouter/score_feasibility.py`.
