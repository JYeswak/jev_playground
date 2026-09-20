#!/usr/bin/env bash
# selftest-ttsr-rules.sh — every project TTSR rule fires on its known-bad and stays quiet on a
# near-miss known-good.
#
# WHY: rules are the SUGGEST leg of the session-hardening loop. A rule with no negative arm is
# indistinguishable from a rule that fires on everything — this lane dropped `pipe-exit` v1 for
# exactly that (55.2% fire rate, wallpaper, NEGATIVE_EVIDENCE R51). Both rules here were mined
# from the 78,242-command dcg_allow harvest and ship at ~1%; see
# docs/demos/upstream-repro/suggest-leg-mining-20260920.md and pipe-exit-v2-dcg-mine-20260920.md.
#
# The near-misses are the point: each known-good differs from its known-bad by ONE element of the
# defect (no glob / no silenced stderr; no pipe / pipefail set).
# RETIRE a rule when a 30-day harvest window shows its class below 50 occurrences.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
command -v omp >/dev/null 2>&1 || { echo "  SKIP omp not on PATH — NOT counted as agreement"; echo "scripts/selftest-ttsr-rules.sh: skipped"; exit 0; }
pass=0; fail=0
note() { printf '  %-4s %s\n' "$1" "$2"; }

fires() { # fires <rule-file> <command-string>  -> 0 if the rule triggered
  omp ttsr test --rule "$1" --source tool --tool bash "$2" 2>&1 | grep -qE '^Triggered \([1-9]'
}

arm() { # arm <rule-file> <expect fire|quiet> <label> <command>
  local f="$1" want="$2" label="$3" cmd="$4"
  if fires "$f" "$cmd"; then got=fire; else got=quiet; fi
  if [ "$got" = "$want" ]; then note ok "$label ($want)"; pass=$((pass+1))
  else note FAIL "$label — wanted $want, got $got: $cmd"; fail=$((fail+1)); fi
}

G=.omp/rules/bash-glob-silenced.md
arm "$G" fire  "glob-silenced: glob path + 2>/dev/null"      "grep -rl 'x' crates/*/Cargo.toml 2>/dev/null"
arm "$G" quiet "glob-silenced: concrete path, stderr hidden" "grep -rl 'x' crates/foo/Cargo.toml 2>/dev/null"
arm "$G" quiet "glob-silenced: glob but stderr VISIBLE"      "grep -rl 'x' crates/*/Cargo.toml"

P=.omp/rules/bash-pipe-exit.md
arm "$P" fire  "pipe-exit: rc read after the pipe"           './scripts/lane-status.sh 2>&1 | tail -16; echo "EXIT=$?"'
arm "$P" quiet "pipe-exit: rc read with NO pipe"             './scripts/lane-status.sh >/tmp/x 2>&1; echo "rc=$?"'
arm "$P" quiet "pipe-exit: piped, rc never read"             'grep -c foo bar | tail -1'

S=.omp/rules/bash-structural-def-search.md
arm "$S" fire  "structural-shape: fn keyword plus a regex hole"   "grep -rn 'fn .*pressure.*polic' . --include='*.rs'"
arm "$S" quiet "structural-shape: exact known name, no hole"     "grep -rn 'fn resolve_standing_manifest' src/"
arm "$S" quiet "structural-shape: navigation, no -r"              "grep -n 'fn resume' crates/lib.rs"

C=.omp/rules/bash-callsite-grep-exclusion.md
arm "$C" fire  "callsite-exclusion: callers piped past a fn def"      "grep -rn 'is_silent(' crates/ --include='*.rs' | grep -v 'fn is_silent'"
arm "$C" quiet "callsite-exclusion: no exclusion at all"              "grep -rn 'is_silent(' crates/ --include='*.rs'"
arm "$C" quiet "callsite-exclusion: exclusion is not a def"           "grep -rn 'is_silent(' crates/ | grep -v 'test'"

# Every project rule must own at least one arm above — a rule file with no test is a rule nobody
# has ever seen fire. An empty scan set is not a pass (RULE 1).
n_rules=$(ls -1 .omp/rules/*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$n_rules" -eq 0 ]; then
  note FAIL ".omp/rules/*.md matched nothing — an empty scan set is NOT a pass"; fail=$((fail+1))
elif [ "$n_rules" -eq 4 ]; then
  note ok "every project rule ($n_rules) has arms here"; pass=$((pass+1))
else
  note FAIL "$n_rules project rules but only 4 are tested — add arms for the new one"; fail=$((fail+1))
fi

echo "scripts/selftest-ttsr-rules.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ]
