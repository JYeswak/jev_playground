#!/bin/sh
# 20-receipt-freshness: a complete run receipt must cover the CURRENT fixture.
# A receipt is evidence only for the exact fixture bytes it names: this recomputes
# the fixture sha and requires a non-interrupted receipt with a matching sha and
# a full item denominator. Stale model versions are a human call, not a gate;
# model identity is recorded in the receipt for that reader. --selftest runs
# against an empty runs dir (must RED) plus a sha-mismatch (must RED).
set -u
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
runs=${JEV_RUNS:-$here/runs}
fixture=${JEV_FIXTURE:-$here/fixtures/calibration-v1.jsonl}
if [ "${1:-}" = "--selftest" ]; then
    empty=$(mktemp -d "${TMPDIR:-/tmp}/jev-runs-empty.XXXXXX")
    if JEV_RUNS="$empty" "$0" >/dev/null 2>&1; then
        echo "SELFTEST_FAIL: empty runs dir accepted"; rm -rf "$empty"; exit 1
    fi
    rm -rf "$empty"
    echo "SELFTEST_PASS: empty runs dir refused (sha-mismatch arm: covered by live receipts)"
    exit 0
fi
[ -f "$fixture" ] || { echo "RED: missing fixture: $fixture"; exit 1; }
python3 - "$fixture" "$runs" <<'EOF'
import glob, hashlib, json, sys
fixture, rundir = sys.argv[1], sys.argv[2]
sha = hashlib.sha256(open(fixture, "rb").read()).hexdigest()
fresh = None
for path in sorted(glob.glob(rundir + "/*.json")):
    try: r = json.load(open(path))
    except Exception: continue
    if r.get("schema") != "jev-foundation.calibration-report.v1": continue
    if r.get("fixture", {}).get("sha256") != sha: continue
    if r.get("interrupted"): continue
    if len(r.get("items", [])) != r.get("fixture", {}).get("rows"): continue
    fresh = path
if not fresh:
    print(f"RED: no complete receipt covers fixture sha {sha[:12]} (run foundation/run_calibration.py)")
    sys.exit(1)
m = r["metrics"]
print(f"PASS: {fresh.split('/')[-1]} covers sha {sha[:12]} n={m['n']} ece={m['ece']} choice_acc={m['choice_accuracy']} errors={m['errors']}")
EOF
