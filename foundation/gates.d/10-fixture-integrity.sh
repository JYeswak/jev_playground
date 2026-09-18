#!/bin/sh
# 10-fixture-integrity: the calibration fixture parses, holds 80 rows with the
# expected kind/domain mix and balanced labels, and every row carries the fields
# the runner needs. A rotten fixture emits green-looking garbage downstream, so
# this refuses it here. --selftest feeds a truncated copy and requires RED.
set -uo pipefail
# `pipefail` added 2026-09-18 on pane 3's hardening plan (db97021), which graded all six of
# these SAFE-TO-HARDEN and behaviour-neutral TODAY. Its qualifier is the load-bearing half and
# is reproduced here rather than left in a receipt: neutrality holds ONLY because this file does
# not `set -e`. IF `set -e` IS EVER ADDED, RE-AUDIT — pipefail+errexit aborts on a middle-stage
# failure, and every pipe then existing needs explicit handling (see 30-no-secrets.sh:21, whose
# `grep … | head` is the feared shape and is already neutralised with `|| true`).
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
fixture=${JEV_FIXTURE:-$here/fixtures/calibration-v1.jsonl}
if [ "${1:-}" = "--selftest" ]; then
    bad=$(mktemp "${TMPDIR:-/tmp}/jev-fixture-bad.XXXXXX")
    head -c 200 "$fixture" >"$bad"
    if FH_FIXTURE_SELFTEST=1 JEV_FIXTURE="$bad" "$0" >/dev/null 2>&1; then
        echo "SELFTEST_FAIL: truncated fixture was accepted"; rm -f "$bad"; exit 1
    fi
    rm -f "$bad"
    echo "SELFTEST_PASS: truncated fixture refused"
    exit 0
fi
[ -f "$fixture" ] || { echo "RED: missing fixture: $fixture"; exit 1; }
python3 - "$fixture" <<'EOF'
import json,sys
from collections import Counter
rows = []
for i, line in enumerate(open(sys.argv[1])):
    if not line.strip(): continue
    try: rows.append(json.loads(line))
    except Exception as e: print(f"RED: line {i+1} is not JSON: {e}"); sys.exit(1)
need = {"id","kind","domain","instructions","state","expected"}
for i, r in enumerate(rows):
    missing = need - set(r)
    if missing: print(f"RED: row {i} missing {sorted(missing)}"); sys.exit(1)
    if r["kind"] == "noul" and r["expected"].get("p") not in (0, 1):
        print(f"RED: row {i} noul truth not binary"); sys.exit(1)
    if r["kind"] == "choice" and (not r["expected"].get("choice") or not r["expected"].get("options")):
        print(f"RED: row {i} choice missing choice/options"); sys.exit(1)
mix = Counter((r["kind"], r["domain"]) for r in rows)
noul = Counter(r["expected"]["p"] for r in rows if r["kind"] == "noul")
ok = (len(rows) == 80 and noul.get(0) == noul.get(1) == 30
      and mix.get(("noul","spam")) == 20 and mix.get(("noul","injection")) == 20
      and mix.get(("noul","factuality")) == 20 and mix.get(("choice","intent")) == 20)
if not ok:
    print(f"RED: expected 80 rows (20/20/20/20, balanced), got {len(rows)} {dict(mix)} noul={dict(noul)}")
    sys.exit(1)
print(f"PASS: {len(rows)} rows, balanced {dict(noul)}, mix {dict(mix)}")
EOF
