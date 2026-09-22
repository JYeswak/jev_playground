# nev-differential — LLM incumbents vs Jev on jev-sec-bench injection (n=662)

RULE 14 unit: every prior comparator was a FLOOR (regex, constant, BM25).
This unit runs the missing INCUMBENT arm — an LLM on the same state and
questions — via `upstream/typesafe-ai/system-one-adapter-python` @adffc2e.

## Reproduce (no key, no network)

```bash
python3 work/nev-differential/analyze_diff.py
```

Stdlib only. Exit 0 = both arms complete (662/662, ≤2 failures each).
Rewrites `DIFF-RECEIPT.json` deterministically from committed inputs:

- `jev-sec-bench/results/injection.json` @fdb16b9 (Jev arm, read-only)
- `rows-A-xai-grok-4.jsonl` (662 live LLM rows, committed)
- `rows-B-anthropic-claude-haiku-4-5.jsonl` (662 live LLM rows, committed)

## Score (receipt `57d30e9`, 2026-09-21)

| Arm | Correct | Acc |
|---|---|---|
| Jev `jev-1.13.0` (**cited, not re-measured** — derived locally from the committed bench JSON, zero new Jev calls) | 639/662 | **0.9653** |
| A `xai/grok-4` (custom OpenAI-compatible endpoint; OpenAI `gpt-4o-mini` arm died 401, see PREREGISTER A1) | 558/662 | **0.8429** |
| B `anthropic/claude-haiku-4-5` | 579/662 | **0.8746** |

Gate 4 (PREREGISTER bar `3d65229`, A1 `b5e6e1e`): seat certified iff Jev
exceeds BOTH arms with McNemar p<0.05 vs each → **met**
(grok-4 discordants 8–89, p≈2.0e-18; haiku 5–65, p≈2.2e-14).
`gate4_seat_certified = true` in `DIFF-RECEIPT.json`.

## Do NOT run

`run_diff.py` is the LIVE runner (1324 adapter requests, spends money,
needs keys). Nothing in this README requires it. Bar, corpus, arms, and
failure rule are preregistered in `PREREGISTER-DIFF.md` — read that
before touching the runner.

## NO-CLAIM

This corpus only: prompt-injection guard on these 662 public rows, single
run, fixed 0.5 cut, one adapter/SDK pair. Public corpus may have leaked
into any model's training. Never a claim about Jev in general.
