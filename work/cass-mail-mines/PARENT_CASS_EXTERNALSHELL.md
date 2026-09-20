# Parent ExternalShell — cass dig-vs-invent (machineId 439e8c39-3223-4273-9ce4-4263468cbba7)

Do **not** start a cass rebuild. Muse pane 3 untouched.

```bash
hostname
command -v cass; test -f /Volumes/ZestData/cass-data/agent_search.db && echo CASS_DB_OK
cd /Users/josh/Developer/jev || cd "$(git -C ~/Developer/jev rev-parse --show-toplevel 2>/dev/null)"
git fetch origin && git checkout work/cass-dig-vs-invent 2>/dev/null || git pull
# if branch not on Studio yet, sync from playground clone path:
#   cd /path/to/jev_playground && git checkout work/cass-dig-vs-invent

CASS_TIMEOUT_SEC=60 CASS_LIMIT=10 \
  python3 work/cass-mail-mines/scripts/run_cass_dig_live.py

# paste stdout + these files back / commit on branch:
#   work/cass-mail-mines/exports/cass-dig-rows.jsonl
#   work/cass-mail-mines/exports/cass-dig-hits.jsonl
#   work/cass-mail-mines/exports/cass-dig-score.txt
#   work/cass-mail-mines/exports/cass-dig-run-meta.txt
```

If `cass search` hangs: runner auto-falls back to read-only sqlite after 3×60s timeouts.
