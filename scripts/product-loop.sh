#!/bin/sh
# Every 5 minutes: the guard demo must still run, and one missing cookbook
# demo gets one idle pane. Never pushes a working pane. Never spends a key.
set -eu
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$root"

if ! node demos/guard/demo.mjs >/tmp/jev-product-loop-guard.out 2>&1; then
  echo "GUARD_RED"
  exit 1
fi

missing=""
if [ ! -f demos/rag/demo.mjs ]; then missing="2 jev-bb5 demos/rag/demo.mjs docs-mirror/typesafe/cookbooks/classifying_rag_passages.md"; fi
if [ -z "$missing" ] && [ ! -f demos/citation/demo.mjs ]; then missing="4 jev-kff demos/citation/demo.mjs docs-mirror/typesafe/cookbooks/citation_check.md"; fi
if [ -z "$missing" ] && [ ! -f demos/skill-suggest/demo.mjs ]; then missing="5 jev-dft demos/skill-suggest/demo.mjs docs-mirror/typesafe/cookbooks/skill_suggestion.md"; fi
if [ -z "$missing" ]; then
  echo "all four demos present"
  exit 0
fi

set -- $missing
pane=$1
bead=$2
demo=$3
cookbook=$4

working=$(ntm --robot-agent-health=jev --panes="$pane" 2>/dev/null | python3 -c '
import json,sys
raw=sys.stdin.read()
i=raw.find("{")
if i<0:
    sys.exit(0)
d=json.loads(raw[i:])
panes=d.get("panes") or {}
for v in panes.values():
    st=v.get("local_state") or {}
    print("1" if st.get("is_working") else "0")
    break
' || true)
if [ "$working" = "1" ]; then
  echo "pane $pane already working on $bead"
  exit 0
fi

msgfile=$(mktemp)
cat > "$msgfile" <<EOF
PRODUCT-LOOP. Claim $bead. Build $demo from $cookbook. Keyless. node $demo must exit 0. Name that command in README.md in the same commit. Do not spend a key. Fixture lane is not a live score. Then br ready.
EOF
ntm send jev --pane="$pane" --file "$msgfile" --json
rm -f "$msgfile"
echo "sent pane $pane $bead"
