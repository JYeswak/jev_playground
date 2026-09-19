#!/usr/bin/env bash
# 30-no-secrets: no secret VALUES live in this workspace. Names (TYPESAFE_API_KEY)
# are fine and expected; values are not. Flags `apikey_` tokens and long
# base64-ish assignments. Scoped to the workspace root only — the live key file
# (/tmp/.tskey) is deliberately outside this tree. --selftest plants a fake key
# and requires RED.
set -uo pipefail
# `pipefail` added 2026-09-18 on pane 3's hardening plan (db97021), which graded all six of
# these SAFE-TO-HARDEN and behaviour-neutral TODAY. Its qualifier is the load-bearing half and
# is reproduced here rather than left in a receipt: neutrality holds ONLY because this file does
# not `set -e`. IF `set -e` IS EVER ADDED, RE-AUDIT — pipefail+errexit aborts on a middle-stage
# failure, and every pipe then existing needs explicit handling (see 30-no-secrets.sh:21, whose
# `grep … | head` is the feared shape and is already neutralised with `|| true`).
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
if [ "${1:-}" = "--selftest" ]; then
    # The fake key is assembled at runtime so this file never contains a matchable
    # literal: a selftest that trips on its own source certifies nothing (a detector
    # it never exercised). The RED must name the plant file, not anything else.
    plant="$here/.selftest-plant.tmp"
    printf 'x = "%s%s"\n' "apikey_" "ffff0000111122223333444455556666777788889999aaaa" >"$plant"
    hit=$("$0" 2>&1) && { echo "SELFTEST_FAIL: planted key accepted"; rm -f "$plant"; exit 1; }
    case "$hit" in
        *".selftest-plant.tmp"*) rm -f "$plant"; echo "SELFTEST_PASS: planted key refused"; exit 0 ;;
        *) echo "SELFTEST_FAIL: RED fired, but not on the plant:"; printf '%s\n' "$hit" | head -3; rm -f "$plant"; exit 1 ;;
    esac
fi
hits=$(grep -rEn --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=.git --exclude='*.log' -e 'apikey_[A-Za-z0-9_.-]{20,}' -e 'TYPESAFE_API_KEY.{0,3}[=:].{0,3}["'\'']?[A-Za-z0-9_.\-]{16,}' "$here" 2>/dev/null | head -5) || true
if [ -n "$hits" ]; then echo "RED: possible secret values in tree:"; printf '%s\n' "$hits" | cut -c1-160; exit 1; fi
 echo "PASS: no secret values in workspace tree"
