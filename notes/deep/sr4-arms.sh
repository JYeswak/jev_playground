#!/bin/sh
# Three arms from skillranker#4, verbatim shape. SR is the built binary.
set -u
SR=${1:?need sr binary}
WS=$(mktemp -d /Users/josh/Developer/sr4-dogfood-XXXX)
HH=$(mktemp -d /Users/josh/Developer/sr4-home-XXXX)
mkdir -p "$HH/.claude/skills/alpha" "$HH/.claude/skills/beta" "$HH/.claude/skills/gamma"
for s in alpha beta gamma; do
  printf -- '---\nname: %s\ndescription: Test skill %s.\n---\nBody.\n' "$s" "$s" \
    > "$HH/.claude/skills/$s/SKILL.md"
done
cat > "$WS/ctx.json" <<EOF
{"schema_version":1,"harness":"claude_code","producer_id":"repro",
"workspace_root":"$WS","session_id":"s1","agent_id":null,"branch_id":null,
"context_epoch":null,
"current_request":{"event_id":"r1","text":"Which skill helps fix a failing Rust test?",
"attachments_omitted":false,"essential_attachment_missing":false},
"events":[],"explicit_skill_references":[],"supplied_loads":[]}
EOF
cd "$WS" || exit 2
HOME="$HH" "$SR" rank --context "$WS/ctx.json" --offline --json > pass.json
echo "control_exit=$?"
mkdir -p /Users/josh/Developer/sr4-realdir && ln -s /Users/josh/Developer/sr4-realdir "$HH/.claude/skills/linked"
HOME="$HH" "$SR" rank --context "$WS/ctx.json" --offline --json > fail.json
echo "onelink_exit=$?"
rm "$HH/.claude/skills/linked"
HOME="$HH" "$SR" rank --context "$WS/ctx.json" --offline --json > restored.json
echo "restored_exit=$?"
echo "WS=$WS"
echo "HH=$HH"
python3 - << PY
import json
for name in ("pass.json","fail.json","restored.json"):
    raw=open("$WS/"+name).read()
    try:
        o=json.loads(raw)
    except Exception as e:
        print(name, "NOT_JSON", e)
        print(raw[:400])
        continue
    roster=o.get("roster") or o.get("eligibility") or {}
    print(name, "keys", sorted(o.keys())[:12])
    text=json.dumps(o)
    for needle in ("eligible", "empty-roster", "symlinked-directory-skipped", "cache-miss"):
        if needle in text:
            print(" ", needle, "present")
PY
