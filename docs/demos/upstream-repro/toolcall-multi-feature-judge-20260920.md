# Multi-feature judge on frozen toolcall corpus — BEAT 0.212

**Date:** 2026-09-20 (America/Denver) · **Level:** `[test]` · **Tag:** `[pending]` · **promoted=0**

Offline mining + judge on the locked frozen file. No invented cases. No TYPESAFE.

## Commands (repro)

```bash
git pull origin main
python3 work/jev-real-corpus-eval/jev_real_corpus_eval.py \
  work/p3-calibration/toolcall-corpus-frozen.jsonl
node work/jev-real-corpus-eval/run.mjs
python3 work/jev-real-corpus-eval/mine_features.py \
  work/p3-calibration/toolcall-corpus-frozen.jsonl
python3 work/jev-real-corpus-eval/multi_feature_judge.py \
  work/p3-calibration/toolcall-corpus-frozen.jsonl
```

## Baselines (reprinted)

| | |
|---|---|
| n | **7846** |
| GOOD / BAD | **1665** / **6181** |
| sha256 | `dc90a374bbdb11bb521244be40afdaf096e56344e1c11baffb200bab05741580` |
| always-abstain mean loss | **0.212210043** |
| isError-only mean loss | **1.495284221** (LOSE) |

**Mapping:** GOOD→allow; BAD→abstain. **Loss:** correct=0, abstain-on-GOOD=1, allow-on-BAD=2.

## Why always-abstain is hard

Allowing saves **1** on a GOOD and costs **2** on a BAD. Under prevalence
P(GOOD)=0.212, any allow set must have **P(GOOD\|allow) > 2/3** to reduce mean
loss. isError-only fails because it *allows* the large non-error BAD mass
(5866 rows).

## Ranked features (lift = P(GOOD\|f) / P(GOOD); n≥20)

Top allow-eligible (P>2/3) and other separators mined from frozen args/sess:

| feature | n | GOOD | P(G\|f) | lift | note |
|---|---:|---:|---:|---:|---|
| sess_exact_grokbot_0911 | 123 | 113 | 0.9187 | 4.329 | ALLOW-ELIGIBLE |
| sess_exact_omp_0827 | 20 | 18 | 0.9000 | 4.241 | ALLOW-ELIGIBLE |
| sess_exact_omp_0802 | 216 | 149 | 0.6898 | 3.251 | ALLOW-ELIGIBLE |
| cmd_curl | 29 | 18 | 0.6207 | 2.925 | |
| cmd_has_pipefail | 152 | 91 | 0.5987 | 2.821 | |
| cmd_has_mcp | 103 | 58 | 0.5631 | 2.654 | |
| cmd_has_skills | 97 | 51 | 0.5258 | 2.478 | |
| sess_repo_grokbot | 915 | 346 | 0.3781 | 1.782 | |
| sess_repo_control_plane | 1314 | 118 | 0.0898 | 0.423 | BAD-enriched |
| sess_repo_jev | 190 | 13 | 0.0684 | 0.322 | BAD-enriched |
| isError | 315 | 0 | 0.0000 | 0.000 | perfect BAD; rare |

Full table: run `mine_features.py`. Tool name is **not** a separator (bash=7845/7846).

## Judge results (measured)

### Full-data (fit on all rows — optimistic)

| judge | mean_loss | allows | tp | fp | vs 0.212 |
|---|---:|---:|---:|---:|---|
| always-abstain | **0.212210043** | 0 | 0 | 0 | control |
| rule-list (P>2/3 keys) | **0.196660719** | 398 | 306 | 92 | **BEAT** |
| logistic (thr≈0.60) | **0.195003824** | 372 | 293 | 79 | **BEAT** |

### 5-fold CV (fit + thr/keys on train only)

| judge | CV mean_loss | vs 0.212 |
|---|---:|---|
| rule-list | **0.199720622** | **BEAT** |
| logistic | **0.197426005** | **BEAT** |

**BEST (honest CV): logistic `mean_loss=0.197426005` — BEAT always-abstain 0.212210043 by ≈0.0148.**

Fold losses (logistic): 0.1930, 0.2001, 0.1938, 0.1880, 0.2122.

## Rule-list allow keys (full fit, n≥15 & P>2/3)

- `sess=-Developer-grokbot/2026-09-11T22-19-20-324Z_…` (P≈0.92)
- `sess=-Developer-omp-orchestrator/2026-08-31T06-02-27-553Z_…` (P≈0.69)
- `sess=-Developer-omp-orchestrator/2026-08-31T06-27-13-742Z_…` (P≈0.90)
- `repo_tok=-Developer-grokbot|mcp`, `|skills`
- `repo_tok=-Developer-omp-orchestrator|mcp`

## CASS / agent-mail secondary evidence

**Not queried this run.** This executor box has no `/Volumes/ZestData`, no `cass`
binary, and Shell `machineId` routing to Studio (`439e8c39-…`) was not available
to the subagent tool surface. Per `work/jev-real-corpus-eval/README.md`, CASS and
live agent-mail are Studio-only offline-export levers — not required for the
frozen-corpus judge. No fake labels attached.

## Files added

- `work/jev-real-corpus-eval/mine_features.py`
- `work/jev-real-corpus-eval/multi_feature_judge.py`
- this receipt

## Claim status

`[pending]` · promoted=0 · offline product tick: **runnable judge beats 0.212 on
locked n=7846 with 5-fold CV**.
