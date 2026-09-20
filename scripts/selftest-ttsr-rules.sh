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
  # Capture first, match second: `omp … | grep -q` under `set -o pipefail` reports omp's
  # exit (1 on no-trigger) instead of grep's match — the pipe-exit class inside its own guard.
  local out
  out=$(omp ttsr test --rule "$1" --source tool --tool bash "$2" 2>&1)
  grep -qE '^Triggered \([1-9]' <<<"$out"
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

arm_text() { # arm_text <rule-file> <expect fire|quiet> <label> <prose>
  local f="$1" want="$2" label="$3" txt="$4" got
  if omp ttsr test --rule "$f" --source text "$txt" 2>&1 | grep -qE '^Triggered \([1-9]'; then got=fire; else got=quiet; fi
  if [ "$got" = "$want" ]; then note ok "$label ($want)"; pass=$((pass+1))
  else note FAIL "$label — wanted $want, got $got: $txt"; fail=$((fail+1)); fi
}

K=.omp/rules/jev-key-canonical-source.md
# ROUTING rule: fires on topic contact, not on a defect. The bar is "is the injected text worth
# one paragraph", not precision. Four agents reported this key missing and all four were wrong.
arm "$K" fire  "jev-key: bash touches the key name"          'echo $TYPESAFE_API_KEY | head -c 4'
arm "$K" fire  "jev-key: bash touches the endpoint"          'curl -s https://api.typesafe.ai/v1/systemone'
arm "$K" quiet "jev-key: unrelated bash"                     'node work/jev-client/test/client.test.mjs'

A=.omp/rules/absence-from-one-probe.md
# INVARIANT rule. Measured 2026-09-20 over 45,103 assistant-text turns in 1,841 omp session
# JSONL files: shipped predicate 185 fires / 0.4102%, hand-labelled FP 0.20 (n=20, seed 20260920).
# The quiet arms below are the two tiers that were MEASURED AND REFUSED — they are not
# hypothetical near-misses, they are 379 real fires we chose not to take.
arm_text "$A" fire  "absence: capability declared not installed" 'morph is not installed on this machine'
arm_text "$A" fire  "absence: hook wired-ness denied"            'the hook is not wired the way its own author designed'
arm_text "$A" fire  "absence: capability noun + missing"         'the api key is missing from this environment'
arm_text "$A" fire  "absence: binary not available"              'nvm is not available as a shell command here'
arm_text "$A" quiet "absence: DATA missing, not a capability"    'the ranking is missing three rows from the table'
arm_text "$A" quiet "absence: REFUSED tier, path nonexistence"   'docs/plan/flow/bead-lifecycle.toml does not exist'
arm_text "$A" quiet "absence: REFUSED tier, probe-said-MISSING"  'command -v morph returned MISSING'
arm_text "$A" quiet "absence: already downgraded to UNMEASURED"  'UNMEASURED (probe: command -v morph); a second probe is required'
arm_text "$A" quiet "absence: two probes already run"            'I verified it with two probes and the binary is present'

# FILE-TYPE rule, lives ONLY in ~/.agents/rules (universal root). No drift
# pair exists on purpose: the drift guard skips basenames present in one
# root only. armf mirrors armw but varies tool+path: scope matching is on
# the tool call shape, so the arms must vary it, not the payload text.
R="$HOME/.agents/rules/ft-rs-doctrine.md"
if [ -e "$R" ]; then
  armf() { # armf <expect fire|quiet> <label> <tool> <path-or-empty> <payload>
    local want="$1" label="$2" tool="$3" path="$4" txt="$5" got out
    if [ -n "$path" ]; then
      out=$(omp ttsr test --rule "$R" --source tool --tool "$tool" --path "$path" "$txt" 2>&1)
    else
      out=$(omp ttsr test --rule "$R" --source tool --tool "$tool" "$txt" 2>&1)
    fi
    if grep -qE '^Triggered \([1-9]' <<<"$out"; then got=fire; else got=quiet; fi
    if [ "$got" = "$want" ]; then note ok "$label ($want)"; pass=$((pass+1))
    else note FAIL "$label — wanted $want, got $got"; fail=$((fail+1)); fi
  }
  armf fire  "ft-rs: fire on .rs edit"    edit  /tmp/probe.rs 'fn main() {}'
  armf fire  "ft-rs: fire on .rs write"   write /tmp/probe.rs 'fn main() {}'
  armf quiet "ft-rs: quiet on .md edit"   edit  /tmp/probe.md '# notes'
  armf quiet "ft-rs: quiet on bash cargo" bash  ''            'cargo test -p foo'
else
  note FAIL "system-wide rule missing: $R"; fail=$((fail+1))
fi
# FILETYPE-DOCTRINE rules (P2, 2026-09-20). Same fire/quiet shape as the
# ft-rs block above, separate helper and separate rule vars so neither lane
# touches the other's lines. ft-sh: single-entry scripts, wrapper-verdicts,
# capture-first. ft-md: equal-or-weaker, no-claim boundaries.
armt() { # armt <rule> <expect fire|quiet> <label> <tool> <path-or-empty> <payload>
  local rule="$1" want="$2" label="$3" tool="$4" path="$5" txt="$6" got out
  if [ -n "$path" ]; then
    out=$(omp ttsr test --rule "$rule" --source tool --tool "$tool" --path "$path" "$txt" 2>&1)
  else
    out=$(omp ttsr test --rule "$rule" --source tool --tool "$tool" "$txt" 2>&1)
  fi
  case "$out" in
    *'No rules triggered'*) got=quiet ;;
    *Triggered*) got=fire ;;
    *) got=quiet ;;
  esac
  if [ "$got" = "$want" ]; then note ok "$label ($want)"; pass=$((pass+1))
  else note FAIL "$label — wanted $want, got $got"; fail=$((fail+1)); fi
}
SH="$HOME/.agents/rules/ft-sh-doctrine.md"
MD="$HOME/.agents/rules/ft-md-doctrine.md"
if [ -e "$SH" ] && [ -e "$MD" ]; then
  armt "$SH" fire  "ft-sh: fire on .sh edit"  edit  /tmp/probe.sh 'echo hi'
  armt "$SH" quiet "ft-sh: quiet on .md edit" edit  /tmp/probe.md '# notes'
  armt "$SH" quiet "ft-sh: quiet on bash"     bash  ''            'grep -rl x probe.sh'
  armt "$MD" fire  "ft-md: fire on .md edit"  edit  /tmp/probe.md '# notes'
  armt "$MD" quiet "ft-md: quiet on .sh edit" edit  /tmp/probe.sh 'echo hi'
  armt "$MD" quiet "ft-md: quiet on bash"     bash  ''            'cat probe.md'
else
  note FAIL "system-wide filetype rules missing: $SH $MD"; fail=$((fail+1))
fi
PY="$HOME/.agents/rules/ft-py-doctrine.md"
if [ -e "$PY" ]; then
  armt "$PY" fire  "ft-py: fire on .py edit"   edit  /tmp/probe.py 'x = 1'
  armt "$PY" fire  "ft-py: fire on .py write"  write /tmp/probe.py 'x = 1'
  armt "$PY" quiet "ft-py: quiet on .sh edit"  edit  /tmp/probe.sh 'echo hi'
  armt "$PY" quiet "ft-py: quiet on .md edit"  edit  /tmp/probe.md 'text'
  armt "$PY" quiet "ft-py: quiet on bash run"  bash  ''            'python3 probe.py'
  armt "$PY" quiet "ft-py: quiet on bash pip"  bash  ''            'pip install foo'
else
  note FAIL "system-wide filetype rule missing: $PY"; fail=$((fail+1))
fi

# COMPILE GUARD. TTSR conditions are JavaScript RegExp: a PCRE inline flag like (?i) is invalid.
# omp ttsr test REPORTS that, but a live session does NOT — omp://ttsr-injection-lifecycle.md says
# an invalid condition is "logged as a warning and ignored", so the rule loads, never fires, and
# looks installed. Every arm above could pass while a sixth rule is silently dead. Measured
# 2026-09-20: the first draft of absence-from-one-probe shipped exactly this defect.
# NOTE: capture first, match second. `omp ttsr test | grep -q` is WRONG under `set -o pipefail`:
# omp exits 1 when nothing triggers, so the pipeline reports 1 even when grep DID match, and the
# check silently inverts. That is this repo's own `bash-pipe-exit` class biting the selftest that
# guards TTSR rules — measured here 2026-09-20, and it made both RED arms below read as green.

# SYSTEM-WIDE rule, lives in ~/.agents/rules so it fires in every repo. It protects the rule
# system itself: an EMBEDDED inline flag makes a rule load and never fire, and only `omp ttsr
# test` says so — a live session logs-and-ignores. The near-miss arm is load-bearing, because a
# LEADING (?i) is legal (omp lifts it to the `i` flag) and flagging it would be over-strict.
F="$HOME/.agents/rules/ttsr-embedded-inline-flag.md"
if [ -e "$F" ]; then
  armw() { # armw <expect> <label> <payload>
    local want="$1" label="$2" txt="$3" got
    if omp ttsr test --rule "$F" --source tool --tool write --path /tmp/probe.md "$txt" 2>&1 \
         | grep -qE '^Triggered \([1-9]'; then got=fire; else got=quiet; fi
    if [ "$got" = "$want" ]; then note ok "$label ($want)"; pass=$((pass+1))
    else note FAIL "$label — wanted $want, got $got"; fail=$((fail+1)); fi
  }
  armw fire  "inline-flag: EMBEDDED (?i) — the real known-bad" "condition: 'foo|(?i)bar'"
  armw quiet "inline-flag: LEADING (?i) is legal"              "condition: '(?i)leading_is_legal'"
  armw quiet "inline-flag: ordinary condition"                 "condition: 'grep[^|;&]*2>/dev/null'"
  armw quiet "inline-flag: prose mentioning (?i)"              "the docs say (?i) is invalid here"
else
  note FAIL "system-wide rule missing: $F"; fail=$((fail+1))
fi
# BOTH ROOTS. Project rules apply only in this repo; `~/.agents/rules/*.md` is the `agents`
# provider (priority 70) and is PROFILE-INDEPENDENT and PROJECT-INDEPENDENT — proven 2026-09-20
# by loading a canary from /tmp, where `omp ttsr list` showed it as `[agents]`. That root is where
# a junior-mistake rule has to live to be system-wide, so it needs the same compile guard: a
# silently-dead rule there is dead in EVERY repo on the machine, not just this one.
for rf in .omp/rules/*.md "$HOME"/.agents/rules/*.md; do
  [ -e "$rf" ] || continue
  out=$(omp ttsr test --rule "$rf" --source text 'zzzz_cannot_exist_9c42' 2>&1 || true)
  scope=project; case $rf in "$HOME"/.agents/*) scope=systemwide;; esac
  case $out in
    *'no usable TTSR condition'*)
      note FAIL "compile[$scope]: $(basename "$rf") has no usable condition — loads and NEVER fires"; fail=$((fail+1)) ;;
    *)
      note ok "compile[$scope]: $(basename "$rf") compiles"; pass=$((pass+1)) ;;
  esac
done
n_project=$(ls -1 .omp/rules/*.md 2>/dev/null | wc -l | tr -d ' ')
n_system=$(ls -1 "$HOME"/.agents/rules/*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$n_project" -eq 0 ] && [ "$n_system" -eq 0 ]; then
  note FAIL "both rule roots expanded to nothing — an empty scan set is NOT a pass"; fail=$((fail+1))
else
  note ok "rule roots scanned: project=$n_project systemwide=$n_system"; pass=$((pass+1))
fi

# DRIFT GUARD. A rule promoted to ~/.agents/rules also exists here, and name-based dedup means
# the project copy WINS (measured 2026-09-20: 35 rules in this repo, zero duplicate names, the
# five promoted all resolve to [native]). So a double-fire is impossible — but editing one copy
# and forgetting the other is not. Then this repo behaves one way and every OTHER repo on the
# machine behaves another, with nothing to say so. That silent divergence is the reason the two
# copies are tolerable at all, so it has to be RED, not a comment.
drift=0
for pf in .omp/rules/*.md; do
  [ -e "$pf" ] || continue
  sf="$HOME/.agents/rules/$(basename "$pf")"
  [ -e "$sf" ] || continue
  if cmp -s "$pf" "$sf"; then
    note ok "no drift: $(basename "$pf") identical in both roots"; pass=$((pass+1))
  else
    note FAIL "DRIFT: $(basename "$pf") differs between project and ~/.agents — this repo and every other disagree"; fail=$((fail+1)); drift=$((drift+1))
  fi
done
[ "$drift" -eq 0 ] || note FAIL "$drift rule(s) drifted across roots"

# The guard's own RED arm, assembled at runtime, because a guard that has only ever gone green is
# indistinguishable from a guard that cannot fire. Two genuine known-bads, both measured against
# omp 2026-09-20. NOTE the near-miss: a LEADING (?i) is ACCEPTED (omp lifts it to the `i` flag) —
# only an EMBEDDED inline flag breaks. The first plant tried here was a leading (?i) and it was
# legal, which is why this arm names the exact shapes instead of "any (?i)".
red_dir=/tmp/ttsr-redarm; mkdir -p "$red_dir"
printf -- '---\ncondition: %s\nscope: text\n---\nplanted known-bad\n' "'foo|(?i)bar'"  > "$red_dir/embedded-flag.md"
printf -- '---\ncondition: %s\nscope: text\n---\nplanted known-bad\n' "'foo[unclosed'" > "$red_dir/unbalanced.md"
printf -- '---\ncondition: %s\nscope: text\n---\nplanted known-GOOD near-miss\n' "'(?i)leading_is_legal'" > "$red_dir/leading-flag.md"
for plant in embedded-flag unbalanced; do
  out=$(omp ttsr test --rule "$red_dir/$plant.md" --source text 'zzzz_cannot_exist_9c42' 2>&1 || true)
  case $out in
    *'no usable TTSR condition'*) note ok "compile RED arm: planted $plant is caught"; pass=$((pass+1)) ;;
    *) note FAIL "compile RED arm: planted $plant was NOT caught — the guard cannot fire"; fail=$((fail+1)) ;;
  esac
done
out=$(omp ttsr test --rule "$red_dir/leading-flag.md" --source text 'zzzz_cannot_exist_9c42' 2>&1 || true)
case $out in
  *'no usable TTSR condition'*) note FAIL "compile near-miss: a LEADING (?i) was rejected — guard is over-strict"; fail=$((fail+1)) ;;
  *) note ok "compile near-miss: leading (?i) accepted, not flagged"; pass=$((pass+1)) ;;
esac

# Every project rule must own at least one arm above — a rule file with no test is a rule nobody
# has ever seen fire. An empty scan set is not a pass (RULE 1).
n_rules=$(ls -1 .omp/rules/*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$n_rules" -eq 0 ]; then
  note FAIL ".omp/rules/*.md matched nothing — an empty scan set is NOT a pass"; fail=$((fail+1))
elif [ "$n_rules" -eq 6 ]; then
  note ok "every project rule ($n_rules) has arms here"; pass=$((pass+1))
else
  note FAIL "$n_rules project rules but only 6 are tested — add arms for the new one"; fail=$((fail+1))
fi

echo "scripts/selftest-ttsr-rules.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ]
