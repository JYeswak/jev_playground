#!/usr/bin/env bash
# selftest-lane-status-pipe.sh — the lane's honesty signal must survive a pipe.
#
# WHY THIS EXISTS (observed, not speculative): lane-status.sh exits 3 when a STATUS row cites a
# receipt that does not exist. Harvested from 78,242 dcg-allow commands, this script was invoked
# THROUGH A PIPE 223 times, e.g. `./scripts/lane-status.sh 2>&1 | tail -16; echo "EXIT=$?"`, which
# reports tail's status. Confirmed live: `bash -c 'exit 3' | head -1; echo $?` -> 0.
#
# Arm 1 (good path): unpiped rc=0 AND the in-band verdict line says rc=0.
# Arm 2 (KNOWN-BAD): a planted missing receipt must yield unpiped rc=3, and the in-band line must
#                    still read rc=3 when the output is piped through `tail` — the exact trap.
# RETIRE when a 30-day harvest window shows no piped invocation of lane-status.sh.
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO" || exit 2
PASS=0; FAIL=0
ok(){ printf '  PASS %s\n' "$1"; PASS=$((PASS+1)); }
no(){ printf '  FAIL %s\n' "$1"; FAIL=$((FAIL+1)); }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
GOOD="docs/demos/STATUS.tsv"
BAD="$TMP/bad.tsv"

python3 - "$GOOD" "$BAD" <<'PY'
import sys
src,dst=sys.argv[1],sys.argv[2]
lines=open(src).read().split('\n'); done=False
for i,l in enumerate(lines):
    if done or l.startswith('#'): continue
    c=l.split('\t')
    for j,f in enumerate(c):
        if f.strip().startswith('docs/demos/') and f.strip().endswith('.md'):
            c[j]='docs/demos/upstream-repro/NO-SUCH-RECEIPT-PLANTED.md'
            lines[i]='\t'.join(c); done=True; break
open(dst,'w').write('\n'.join(lines))
sys.exit(0 if done else 9)
PY
[ $? -eq 0 ] || { echo "  FAIL could not plant a missing receipt (STATUS.tsv shape changed)"; exit 1; }

# --- Arm 1: good path, unpiped, in-band line agrees with the real exit code
OUT="$(./scripts/lane-status.sh 2>&1)"; RC=$?
LINE="$(printf '%s\n' "$OUT" | grep -c "^LANE-STATUS-VERDICT rc=$RC ")"
if [ "$LINE" -eq 1 ]; then ok "good path: in-band verdict matches real rc=$RC"
else no "good path: no in-band line for real rc=$RC"; fi

# --- Arm 2: KNOWN-BAD. Planted missing receipt -> rc=3, and it must survive `| tail`
OUT2="$(JEV_STATUS="$BAD" ./scripts/lane-status.sh 2>&1)"; RC2=$?
if [ "$RC2" -eq 3 ]; then ok "planted missing receipt: unpiped rc=3 (gate fires)"
else no "planted missing receipt: expected rc=3, got $RC2 — the gate did NOT fire, so arm 3 proves nothing"; fi

PIPED="$(JEV_STATUS="$BAD" ./scripts/lane-status.sh 2>&1 | tail -2)"
if printf '%s\n' "$PIPED" | grep -q '^LANE-STATUS-VERDICT rc=3 '; then
  ok "planted missing receipt: rc=3 survives \`| tail\` in-band"
else
  no "planted missing receipt: verdict LOST through the pipe — the 223-instance trap is open"
fi

printf 'selftest-lane-status-pipe: %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
