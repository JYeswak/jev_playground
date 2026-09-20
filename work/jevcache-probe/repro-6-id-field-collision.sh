#!/bin/bash
# repro-6 — canonicalization drops any field whose name ends in `_id` BEFORE hashing, so two
#           materially different states collide on one fingerprint and one gets the other's
#           cached answer.
#
# PREREQUISITES: jevcache on PATH, python3. Part 1 needs NO API key and NO network (mock
#                backend). Part 2 is optional and needs a real backend to show that the two
#                states genuinely deserve different answers:
#                  JEVCACHE_BACKEND=jev JEV_API_KEY=... ./repro-6-id-field-collision.sh
#                Throwaway HOME throughout.
set -u

W=$(mktemp -d); cd "$W"; export HOME="$W/home"; mkdir -p "$HOME"
cat > jevcache.schemas.json <<'EOF'
[{"id":"harm","version":1,"questions":{"harm":{"instructions":"Is this command destructive?","type":"noul"}}}]
EOF
BACKEND="${JEVCACHE_BACKEND:-mock}"
export JEVCACHE_BACKEND="$BACKEND"
echo "jevcache $(jevcache version)   backend=$BACKEND   HOME=$HOME"

ask () {  # $1 label  $2 state  $3 ledger dir
  printf '%s' "$2" > st.json
  out=$(JEVCACHE_DIR="$W/$3" jevcache decide --schema harm --state st.json --json)
  printf '  %-32s %s\n' "$1" "$(python3 -c '
import sys, json
o = json.loads(sys.stdin.read())
print("fp=" + o["fingerprint"][:16], "cached=" + str(o["cached"]), "answer=" + json.dumps(o["answers"]))' <<<"$out")"
}

echo
echo "=== control: the differing content lives in a field named 'command', separate ledgers ==="
ask "command = rm -rf /"    '{"command":"rm -rf --no-preserve-root /"}' c1
ask "command = echo hello"  '{"command":"echo hello"}'                  c2

echo
echo "=== defect A: same content in 'command_id', ONE ledger, destructive decided first ==="
ask "command_id = rm -rf /"   '{"command_id":"rm -rf --no-preserve-root /"}' dA
ask "command_id = echo hello" '{"command_id":"echo hello"}'                  dA

echo
echo "=== defect B: same, benign decided first — the dangerous direction ==="
ask "command_id = echo hello" '{"command_id":"echo hello"}'                  dB
ask "command_id = rm -rf /"   '{"command_id":"rm -rf --no-preserve-root /"}' dB

echo
echo "=== recall (never calls a backend) agrees with the poisoned entry ==="
printf '%s' '{"command_id":"rm -rf --no-preserve-root /"}' > st.json
JEVCACHE_DIR="$W/dB" jevcache recall --schema harm --state st.json --json
echo "recall rc=$?"

echo
echo "=== the mechanism: the *_id field is gone from the stored canonical state ==="
python3 - "$W/dB/ledger.log" <<'PY'
import sys, json
for line in open(sys.argv[1]):
    o = json.loads(line)
    if o.get("t") == "put":
        print("   state_preview:", o["r"]["state_preview"])
PY
echo
echo "With mock every answer is identical, so run with JEVCACHE_BACKEND=jev to see the two"
echo "states earn genuinely different answers in the control and the same one under collision."
exit 0
