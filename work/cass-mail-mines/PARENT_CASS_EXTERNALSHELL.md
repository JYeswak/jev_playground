# Parent ExternalShell — cass dig-vs-invent (machineId 439e8c39-3223-4273-9ce4-4263468cbba7)

Do **not** start a cass rebuild. Muse pane 3 untouched.

```bash
hostname   # Joshs-Mac-Studio.local
command -v cass; test -f /Volumes/ZestData/cass-data/agent_search.db && echo CASS_DB_OK
cd /Users/josh/Developer/jev
git fetch origin && git checkout work/cass-dig-vs-invent && git pull

# Optional raw probes (save stdout):
mkdir -p work/cass-mail-mines/exports
cass search "requireKey OR wrong selector OR no such column" --robot --limit 100 \
  > work/cass-mail-mines/exports/cass-probe-requireKey.json
cass search "invented OR reimplemented OR already exists" --robot --limit 50 \
  > work/cass-mail-mines/exports/cass-probe-invented.json

# Timed subset (recommended while index rebuilds / search degraded):
CASS_TIMEOUT_SEC=45 CASS_LIMIT=10 CASS_MAX_QUERIES=30 \
  python3 work/cass-mail-mines/scripts/run_cass_dig_live.py

# Full set when healthy:
# CASS_TIMEOUT_SEC=60 CASS_LIMIT=10 python3 work/cass-mail-mines/scripts/run_cass_dig_live.py

git add work/cass-mail-mines/exports/cass-dig-*.jsonl \
        work/cass-mail-mines/exports/cass-dig-*.txt \
        work/cass-mail-mines/exports/cass-probe-*.json \
        docs/demos/upstream-repro/cass-dig-vs-invent-mine-20260920.md
# commit + push to work/cass-dig-vs-invent (PR #35)
```
