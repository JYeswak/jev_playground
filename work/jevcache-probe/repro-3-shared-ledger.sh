#!/bin/bash
# repro-3 — one global ledger, no per-process isolation: unrelated processes share a cache,
#           can read each other's raw state, and concurrent writers corrupt the log.
#
# PREREQUISITES: jevcache on PATH (curl -fsSL jevcache.sh/install | sh), python3.
#                NO API key, NO network, NO access to any repo. Everything happens under a
#                throwaway HOME so your real ~/.jevcache is never touched — HOME is
#                redirected ONLY to keep this script harmless; jevcache's default is
#                $HOME/.jevcache and nothing in the tool scopes it below that.
#
# PART 1  two unrelated processes share one ledger, and each can read the other's raw state
# PART 2  JEVCACHE_DIR does isolate — but it is opt-in env, there is no flag and no default
# PART 3  N concurrent writers on one ledger: malformed lines and permanently lost decisions
set -u

TRIALS="${1:-20}"
WRITERS="${2:-16}"
WORK=$(mktemp -d)
cd "$WORK"
cat > jevcache.schemas.json <<'EOF'
[{"id":"probe","version":1,"questions":{"q":{"instructions":"Is this destructive?","type":"noul"}}}]
EOF
export JEVCACHE_BACKEND=mock
echo "jevcache $(jevcache version)   workdir=$WORK   backend=mock"

echo
echo "=============== part 1: two processes, one ledger ==============="
export HOME="$WORK/home"; mkdir -p "$HOME"
printf '{"ticket":"agent-A private state: refund for case 4471"}\n' > s_a.json
printf '{"ticket":"agent-B private state: legal hold on case 9931"}\n' > s_b.json
echo "--- process A decides (its own pid, no shared handle with B):"
jevcache decide --schema probe --state s_a.json --json | cut -c1-120
echo "--- process B decides:"
jevcache decide --schema probe --state s_b.json --json | cut -c1-120
echo "--- both landed in ONE file:"
ls -l "$HOME/.jevcache/ledger.log"
echo "--- and B's process can read A's raw state out of it:"
grep -o 'state_preview.*' "$HOME/.jevcache/ledger.log" | sed 's/^/    /'
echo "--- B recalls a decision B never made (cross-process cache sharing):"
jevcache recall --schema probe --state s_a.json --json | cut -c1-120
echo "    recall rc=$?  (0 = HIT, 3 = miss)"

echo
echo "=============== part 2: JEVCACHE_DIR does isolate ==============="
JEVCACHE_DIR="$WORK/dirA" jevcache decide --schema probe --state s_a.json --json >/dev/null
echo "--- dirA decided it; dirB recalls the same state:"
JEVCACHE_DIR="$WORK/dirB" jevcache recall --schema probe --state s_a.json --json
echo "    recall rc=$?  (3 = miss: isolation works, but only because we opted in)"

echo
echo "=============== part 3: $TRIALS trials x $WRITERS concurrent writers, one ledger ==============="
PAD=$(printf 'x%.0s' $(seq 1 300))
mal_trials=0; loss_trials=0; lost_total=0
for trial in $(seq 1 "$TRIALS"); do
  H="$WORK/t$trial"; mkdir -p "$H"; export HOME="$H"
  for i in $(seq 1 "$WRITERS"); do
    printf '{"trial":%d,"n":%d,"pad":"%s"}\n' "$trial" "$i" "$PAD" > "$WORK/s${trial}_$i.json"
  done
  for i in $(seq 1 "$WRITERS"); do
    jevcache decide --schema probe --state "$WORK/s${trial}_$i.json" --json >/dev/null 2>&1 &
  done
  wait
  mal=$(python3 - "$H/.jevcache/ledger.log" <<'PY'
import sys, json
bad = 0
for line in open(sys.argv[1]):
    line = line.strip()
    if not line: continue
    try: json.loads(line)
    except Exception: bad += 1
print(bad)
PY
)
  miss=0
  for i in $(seq 1 "$WRITERS"); do
    jevcache recall --schema probe --state "$WORK/s${trial}_$i.json" --json >/dev/null 2>&1 || miss=$((miss+1))
  done
  [ "$mal" -gt 0 ] && mal_trials=$((mal_trials+1))
  if [ "$miss" -gt 0 ]; then loss_trials=$((loss_trials+1)); lost_total=$((lost_total+miss)); fi
  printf 'trial %2d: malformed_ledger_lines=%s  decisions_written_then_unrecallable=%s/%s\n' \
    "$trial" "$mal" "$miss" "$WRITERS"
done
echo "-----"
echo "trials with a malformed ledger line     : $mal_trials/$TRIALS"
echo "trials that permanently lost a decision : $loss_trials/$TRIALS"
echo "decisions lost in total                 : $lost_total/$((TRIALS*WRITERS))"
echo
echo "The rate is load-dependent and intermittent; the failure is that it is nonzero at all"
echo "for processes that were never told they were sharing anything."
exit 0
