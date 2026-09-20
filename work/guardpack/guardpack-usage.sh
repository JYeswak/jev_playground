#!/usr/bin/env bash
# guardpack-usage — is the guardpack actually being used, and on what?
#
# WHY: Joshua, 2026-09-20, on the guardpack: "how are we measuring and observing its use - how is
# it a first rate citizen of everything we do?" The honest answer at that moment was that it was
# not installed here and emitted no telemetry. A guard nobody can observe is indistinguishable
# from a guard nobody installed — this lane already shipped an observer that had NEVER emitted a
# row while 13 tests passed, so that is not a hypothetical failure mode.
#
# Reads the JSONL the advisory hook appends (class + timestamp + repo basename; never the
# command string, which can carry secrets).
#
#   exit 0  warnings exist, printed by class and repo
#   exit 3  log exists but is EMPTY — installed and never fired, which is a finding
#   exit 4  no log at all — NOT INSTALLED or never wired. The loudest outcome on purpose.
set -uo pipefail
LOG="${GUARDPACK_LOG:-$HOME/.guardpack/warnings.jsonl}"

if [ ! -f "$LOG" ]; then
  echo "guardpack-usage: NO LOG at $LOG"
  echo "  The hook has never fired in any repo, which means one of:"
  echo "    - the pack is not installed         -> work/guardpack/install-guardpack.sh <repo>"
  echo "    - it is installed but NOT WIRED     -> point the harness PreToolUse bash hook at"
  echo "                                           <repo>/.guardpack/pretooluse-advise.sh"
  echo "  Unwired is the default failure: installing copies a file, wiring is a separate act."
  exit 4
fi

n=$(grep -c . "$LOG" 2>/dev/null || echo 0)
if [ "${n:-0}" -eq 0 ]; then
  echo "guardpack-usage: log exists and is EMPTY ($LOG)"
  echo "  Installed and wired but never fired. Either the defects stopped, or the hook is not"
  echo "  receiving command strings. Check by running it directly:"
  echo "    bash .guardpack/pretooluse-advise.sh 'x | tail -1'   # must warn"
  exit 3
fi

echo "guardpack-usage: $n warning(s) in $LOG"
echo
echo "by class:"
sed -E 's/.*"class":"([^"]*)".*/\1/' "$LOG" | sort | uniq -c | sort -rn | sed 's/^/  /'
echo
echo "by repo:"
sed -E 's/.*"repo":"([^"]*)".*/\1/' "$LOG" | sort | uniq -c | sort -rn | sed 's/^/  /'
echo
echo "first: $(head -1 "$LOG" | sed -E 's/.*"ts":"([^"]*)".*/\1/')"
echo "last:  $(tail -1 "$LOG" | sed -E 's/.*"ts":"([^"]*)".*/\1/')"
echo
echo "NO-CLAIM: a warning is not a prevented defect. This counts FIRINGS, not corrections —"
echo "whether the agent heeded the warning is not observable from here."
exit 0
