# CASS dig-vs-invent mine — 2026-09-20

Canonical product-tick receipt (also mirrored as `cass-dig-vs-invent-20260920.md`).

**Level:** `[pending]` · **promoted=0**  
**Store:** CASS `/Volumes/ZestData/cass-data/agent_search.db`  
**machineId:** `439e8c39-3223-4273-9ce4-4263468cbba7`  
**Do not** start a cass rebuild. Muse skillranker pane 3 untouched.

## Measure

Raw probes (also saved under `exports/` when runner / parent runs them):

```bash
cass search "requireKey OR wrong selector OR no such column" --robot --limit 100
cass search "invented OR reimplemented OR already exists" --robot --limit 50
```

Product tick (n≥2 timed subset OK with `--allow-small`):

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

**LIVE: parent timed subset in flight** (Studio ExternalShell). Box executor stopped ExternalShell per steering. Numbers fill here when `exports/cass-dig-score.txt` lands.

```text
(n / prevalence / always-abstain / always-open-top1 / dig-iff-path-in-query — TBD)
```

## NO-CLAIM

- Mechanical Y proxy ≠ pane edit-delta usefulness.
- No Jev call. No rebuild. Not a promotion.
