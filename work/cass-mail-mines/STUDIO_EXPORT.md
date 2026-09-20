# Studio ExternalShell export — run on Joshs-Mac-Studio.local

Box-scoped sand subagents cannot `Shell.machineId`. Parent (or any Studio-routed
agent) must run these and drop JSONL into `work/cass-mail-mines/exports/`.

Confirm first:

```bash
hostname   # must be Joshs-Mac-Studio.local
test -f /Users/josh/.local/share/mcp-agent-mail-rust-live/storage.sqlite3 && echo MAIL_OK
test -f /Volumes/ZestData/cass-data/agent_search.db && echo CASS_OK
# Do NOT start a second cass rebuild.
```

## Mine 1 — Ack-SLA (ack_required=1 → any recipient ack_ts)

```bash
MAIL=/Users/josh/.local/share/mcp-agent-mail-rust-live/storage.sqlite3
OUT=/Users/josh/Developer/jev/work/cass-mail-mines/exports/ack-sla-rows.jsonl
mkdir -p "$(dirname "$OUT")"
sqlite3 -json "$MAIL" "
SELECT m.id AS message_id,
       m.created_ts,
       m.importance,
       m.ack_required,
       length(coalesce(m.subject,'')) AS subject_len,
       length(coalesce(m.body_md,'')) AS body_len,
       (SELECT COUNT(*) FROM message_recipients r WHERE r.message_id=m.id) AS n_recipients,
       (SELECT COUNT(*) FROM message_recipients r WHERE r.message_id=m.id AND r.ack_ts IS NOT NULL) AS n_acked,
       CASE WHEN EXISTS(
         SELECT 1 FROM message_recipients r
         WHERE r.message_id=m.id AND r.ack_ts IS NOT NULL
       ) THEN 1 ELSE 0 END AS y_acked
FROM messages m
WHERE m.ack_required = 1
ORDER BY m.id
LIMIT 2000;
" | python3 -c '
import json,sys
rows=json.load(sys.stdin)
for r in rows:
    r["y"]=int(r["y_acked"])  # 1=acked (positive), 0=still waiting
    print(json.dumps(r, separators=(",",":")))
print(f"# exported {len(rows)} ack_required rows", file=sys.stderr)
' > "$OUT"
wc -l "$OUT"
# optional: copy to sand box via CopyFromComputer → work/cass-mail-mines/exports/ack-sla-rows.jsonl
```

## Mine 2 — Importance prevalence (+ length features)

```bash
MAIL=/Users/josh/.local/share/mcp-agent-mail-rust-live/storage.sqlite3
OUT=/Users/josh/Developer/jev/work/cass-mail-mines/exports/importance-rows.jsonl
sqlite3 -json "$MAIL" "
SELECT id AS message_id,
       created_ts,
       importance,
       ack_required,
       length(coalesce(subject,'')) AS subject_len,
       length(coalesce(body_md,'')) AS body_len,
       CASE WHEN importance IN ('high','urgent') THEN 1 ELSE 0 END AS y_elevated
FROM messages
ORDER BY id
LIMIT 5000;
" | python3 -c '
import json,sys
rows=json.load(sys.stdin)
for r in rows:
    r["y"]=int(r["y_elevated"])
    print(json.dumps(r, separators=(",",":")))
print(f"# exported {len(rows)} messages", file=sys.stderr)
' > "$OUT"
wc -l "$OUT"
```

## Probe counts (already confirmed 2026-09-20)

```text
messages: 6510
importance: normal=5758 high=566 urgent=186
ack_required: 0=3375 1=3135
CASS: 59807 conversations, 5181931 messages
ack_ts lives on message_recipients, not messages
```
