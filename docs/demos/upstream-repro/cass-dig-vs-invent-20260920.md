# CASS dig-vs-invent live mine — 2026-09-20

**Level:** `[pending]` · **promoted=0**  
**Store:** CASS `/Volumes/ZestData/cass-data/agent_search.db`  
**machineId:** `439e8c39-3223-4273-9ce4-4263468cbba7`  
**Do not** start a cass rebuild. Muse skillranker pane 3 untouched.

## Measure

```bash
CASS_TIMEOUT_SEC=60 CASS_LIMIT=10 \
  python3 work/cass-mail-mines/scripts/run_cass_dig_live.py
python3 work/cass-mail-mines/scripts/score_cass_dig.py \
  work/cass-mail-mines/exports/cass-dig-rows.jsonl
```

- Queries: `work/cass-mail-mines/scripts/cass_dig_queries.txt` (n≥100; dig-vs-invent + wrong-selector + lexical-trap + `zzzz_cannot_exist_9c42`)
- Export: `exports/cass-dig-rows.jsonl` (≥100 query rows) + `exports/cass-dig-hits.jsonl`
- If `cass search --robot` times out 3× (60s each) → read-only sqlite sample (schema introspected; no invented tables)

## Y / loss (mechanical)

See `scripts/cass_dig_y.py`. Receipt-shaped hit (source_path + line, not AGENTS/SKILL doctrine basename) or wrong-selector evidence. **Not** human edit-delta (A04 full Y). Independent of raw `count>0` so empty-success can RED.

| outcome | loss |
|---|---:|
| correct | 0 |
| invent when y_dig=1 | 1 |
| dig when y_dig=0 | 2 |

## Measured

**LIVE: AWAITING Studio ExternalShell** for this commit. Box-scoped sand has no `cass` / no `/Volumes/ZestData`. Parent: run `PARENT_CASS_EXTERNALSHELL.md`, then numbers land in `exports/cass-dig-score.txt` and this section is replaced.

```text
(n / prevalence / always-invent / dig-iff-count>0 / dig-iff-BM25 — TBD from Studio)
```

## NO-CLAIM

- Mechanical Y proxy ≠ pane edit-delta usefulness.
- No Jev call. No rebuild. Not a promotion.
