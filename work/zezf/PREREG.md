# PREREG — zezf long-runner Noul on relabelled corpus (jev-zezf)

Frozen 2026-10-02 before any live call. Live jev-1.13.0 only.

## Design

Single Noul per row: "Will this shell command run longer than 120 seconds?"
State: `{command: <full text>, cwd: <session cwd>}`. One question per request.
Predict LONG iff noul >= 0.50, else SHORT. Fail-safe: timeout/error/invalid/refused
-> SHORT (the current default: run in foreground), logged as exclusion.

## Population (keyless, frozen)

- Sync arm: 151,275 bash toolResults with wallTimeMs (V3 census); label pos iff >120,000ms.
- Bg arm: 380 background bash jobs, max observed hub durationMs; pos iff >120,000ms.
- Total 151,655 rows, 344 positives (base 0.00227). Censoring note: bg jobs were
  backgrounded by agents (long-expected); sync negatives dominate. The decision is
  evaluated on the mixed stream as deployed (every bash call).
- Grouped split: sync grouped by command sha, bg by session; held = sha256(group)%5==0
  -> 28,614 held groups, 30,765 held rows, 55 held positives (`held_groups.json`).
- Sample (seed 20261002, `freeze_sample.py`): ALL 55 held positives + 245 random held
  negatives = 300 rows, sha `acc2cdb9a56f` (`sample.json`).
- Baseline command-name table (train groups only, cut 0.01) on this sample:
  tp=10 fp=14, prec 0.4167 rec 0.1818.

## Bar (paired per-row vs table operating point above)

- PASS iff recall >= 0.40 AND precision >= 0.20 on the 300 sampled held-out rows.
- Report: paired 2x2 table-vs-Jev disagreement counts, Wilson 95% CIs, per-call
  model/row-hash/status/tokens/latency/spend, exclusion count. Miss analysis by
  first-token (which arg-dependent longs each side catches).
- FAIL -> NEGATIVE_EVIDENCE with rows; no held-out retest without a one-variable change.

## Caps and harm limits

300 calls (1/row), spend cap $0.02 (~$0.003 expected), stop on 401/402/403 or cap.
Runner: `work/zezf/run_long.mjs`; receipt `work/zezf/longrows.jsonl`
(sample_id, row hash, first token, noul, pred, status, tokens, latency; no raw text).
Scratch corpora uncommitted; this file + bead comments committed.
