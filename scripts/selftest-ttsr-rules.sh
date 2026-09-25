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
# omp absent: under `gates.sh --portable` a named SKIP, exit 8 (jev-fmy).
# Default mode is RED. Exit 0 here was an empty scan set wearing a PASS (jev-80lj).
if ! command -v omp >/dev/null 2>&1; then
  if [ -n "${JEV_GATES_PORTABLE:-}" ]; then
    echo "SKIP (missing prerequisite: omp, install: bun add -g @oh-my-pi/pi-coding-agent@18.3.0)"
    exit 8
  fi
  echo "RED: omp not on PATH — empty scan set is not a pass (selftest-ttsr-rules.sh)"
  exit 1
fi
pass=0; fail=0; na=0
note() { printf '  %-4s %s\n' "$1" "$2"; }

# CI SCOPE (jev-hjzz). The system-wide root is per machine. A CI runner or a stranger's clone has no
# ~/.agents/rules, so the arms for rules that live only there have nothing to test. They are stated
# and counted as n/a, never as ok. A machine that HAS the root but lost one of those rules is RED.
SYS_ROOT="$HOME/.agents/rules"
sys_rule_state() { # sys_rule_state <root> <file> -> present | missing | out-of-scope
  if [ ! -d "$1" ]; then echo out-of-scope
  elif [ -e "$1/$2" ]; then echo present
  else echo missing; fi
}
na_note() { note n/a "$1 (no $SYS_ROOT on this machine: system-wide rules are out of scope here)"; na=$((na+1)); }
scope_dir=$(mktemp -d "${TMPDIR:-/tmp}/ttsr-scope.XXXXXX")
mkdir -p "$scope_dir/root"
for want in "out-of-scope:$scope_dir/absent" "missing:$scope_dir/root"; do
  got=$(sys_rule_state "${want#*:}" planted.md)
  if [ "$got" = "${want%%:*}" ]; then note ok "scope classifier: ${want%%:*} root reads $got"; pass=$((pass+1))
  else note FAIL "scope classifier: wanted ${want%%:*}, got $got"; fail=$((fail+1)); fi
done
: > "$scope_dir/root/planted.md"
if [ "$(sys_rule_state "$scope_dir/root" planted.md)" = present ]; then note ok "scope classifier: present rule reads present"; pass=$((pass+1))
else note FAIL "scope classifier: present rule not read as present"; fail=$((fail+1)); fi

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

# RETIRED FILE-TYPE DOCTRINE PACK. The five ft-*-doctrine rules used to live in ~/.agents/rules and
# this block demanded they exist. They were retired on this lane's own evidence: NEGATIVE_EVIDENCE.md
# R64 (line 2896) measured the pack binding 1 time in 75 real edits against a preregistered 20% bar
# (ft-md 0/25, ft-rs 0/25, ft-sh 1/25); ft-py and ft-json went with the pack for the same refuted
# mechanism (fires on file type, not on the gap). Source of record for the global root:
# ~/Developer/omp-kit/retired/REASONS.tsv. So the arm is inverted: a retired rule REAPPEARING in the
# global root is the defect, because it would fire in every repo on the machine with a bind rate
# already measured at ~1%.
if [ "$(sys_rule_state "$SYS_ROOT" ft-rs-doctrine.md)" = out-of-scope ]; then
  na_note "retired ft-*-doctrine pack absence"
else
  for ft in ft-rs-doctrine ft-sh-doctrine ft-md-doctrine ft-py-doctrine ft-json-doctrine; do
    if [ -e "$SYS_ROOT/$ft.md" ]; then
      note FAIL "retired rule is back in ~/.agents/rules: $ft.md (R64; omp-kit retired/REASONS.tsv)"; fail=$((fail+1))
    else
      note ok "retired rule absent from ~/.agents/rules: $ft.md"; pass=$((pass+1))
    fi
  done
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
F="$SYS_ROOT/ttsr-embedded-inline-flag.md"
case $(sys_rule_state "$SYS_ROOT" ttsr-embedded-inline-flag.md) in
present)
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
  ;;
missing) note FAIL "system-wide rule missing: $F"; fail=$((fail+1)) ;;
*) na_note "ttsr-embedded-inline-flag arms" ;;
esac
# GAP-CONDITIONED ROUTER (P4, 2026-09-20). Survives R64 because the trigger IS the gap:
# `unsafe` inside a .rs edit/write. Injection is skill names + a working jsm query, not
# doctrine. jsm search hit rate on 15 natural queries was 6/15; the 5-term UB query is 0.
U="$SYS_ROOT/rs-unsafe-added-router.md"
case $(sys_rule_state "$SYS_ROOT" rs-unsafe-added-router.md) in
present)
  armu() { # armu <expect fire|quiet> <label> <tool> <path> <payload>
    local want="$1" label="$2" tool="$3" path="$4" txt="$5" got out
    out=$(omp ttsr test --rule "$U" --source tool --tool "$tool" --path "$path" "$txt" 2>&1 || true)
    case "$out" in
      *'No rules triggered'*) got=quiet ;;
      *Triggered*) got=fire ;;
      *) got=quiet ;;
    esac
    if [ "$got" = "$want" ]; then note ok "$label ($want)"; pass=$((pass+1))
    else note FAIL "$label — wanted $want, got $got"; fail=$((fail+1)); fi
  }
  armu fire  "unsafe-router: fire on .rs edit adding unsafe"  edit  /tmp/probe.rs 'unsafe fn f() {}'
  armu fire  "unsafe-router: fire on .rs write adding unsafe" write /tmp/lib.rs   'let x = unsafe { 1 };'
  armu quiet "unsafe-router: quiet on .rs without unsafe"     edit  /tmp/probe.rs 'fn main() {}'
  armu quiet "unsafe-router: quiet on .md containing unsafe"  edit  /tmp/probe.md 'unsafe fn f() {}'
  armu quiet "unsafe-router: quiet on bash even with .rs path" bash  /tmp/probe.rs 'unsafe fn f() {}'
  ;;
missing) note FAIL "system-wide rule missing: $U"; fail=$((fail+1)) ;;
*) na_note "rs-unsafe-added-router arms" ;;
esac
# BOTH ROOTS. Project rules apply only in this repo; `~/.agents/rules/*.md` is the `agents`
# provider (priority 70) and is PROFILE-INDEPENDENT and PROJECT-INDEPENDENT — proven 2026-09-20
# by loading a canary from /tmp, where `omp ttsr list` showed it as `[agents]`. That root is where
# a junior-mistake rule has to live to be system-wide, so it needs the same compile guard: a
# silently-dead rule there is dead in EVERY repo on the machine, not just this one.
# alwaysApply rules have no stream condition by design: omp puts them in the system prompt instead
# of watching the stream (e.g. ~/.agents/rules/kit-standing-law.md, 2026-09-22). Only a rule WITHOUT
# alwaysApply and without a usable condition is dead. One classifier serves the real loop and the
# planted arms below, so the exemption cannot drift away from what the arms test.
compile_verdict() { # compile_verdict <rule.md>  ->  alwaysapply | dead | ok
  if awk 'NR==1 && $0=="---" {f=1; next} f && $0=="---" {exit} f' "$1" | grep -qE '^alwaysApply:[[:space:]]*true[[:space:]]*$'; then
    echo alwaysapply; return
  fi
  case $(omp ttsr test --rule "$1" --source text 'zzzz_cannot_exist_9c42' 2>&1 || true) in
    *'no usable TTSR condition'*) echo dead ;;
    *) echo ok ;;
  esac
}
for rf in .omp/rules/*.md "$HOME"/.agents/rules/*.md; do
  [ -e "$rf" ] || continue
  scope=project; case $rf in "$HOME"/.agents/*) scope=systemwide;; esac
  case $(compile_verdict "$rf") in
    dead)
      note FAIL "compile[$scope]: $(basename "$rf") has no usable condition — loads and NEVER fires"; fail=$((fail+1)) ;;
    alwaysapply)
      note ok "compile[$scope]: $(basename "$rf") is alwaysApply (system prompt, not a stream rule)"; pass=$((pass+1)) ;;
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
if [ "$(sys_rule_state "$SYS_ROOT" x.md)" = out-of-scope ]; then
  # No system-wide copies exist to compare, so the guard has nothing to check: say so (jev-hjzz
  # left this silent, and the SCOPE line undercounted by one group).
  na_note "drift guard (project rules vs their ~/.agents/rules copies)"
else
  for pf in .omp/rules/*.md; do
    [ -e "$pf" ] || continue
    sf="$SYS_ROOT/$(basename "$pf")"
    [ -e "$sf" ] || continue
    if cmp -s "$pf" "$sf"; then
      note ok "no drift: $(basename "$pf") identical in both roots"; pass=$((pass+1))
    else
      note FAIL "DRIFT: $(basename "$pf") differs between project and ~/.agents — this repo and every other disagree"; fail=$((fail+1)); drift=$((drift+1))
    fi
  done
fi
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
printf -- '---\ndescription: planted known-bad, no condition and no alwaysApply\n---\nplanted\n' > "$red_dir/conditionless.md"
printf -- '---\ndescription: planted known-good\nalwaysApply: true\n---\nplanted\n' > "$red_dir/always.md"
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
case $(compile_verdict "$red_dir/conditionless.md") in
  dead) note ok "compile RED arm: planted rule with no condition and no alwaysApply is dead"; pass=$((pass+1)) ;;
  *) note FAIL "compile RED arm: a conditionless non-alwaysApply rule was NOT flagged — the exemption swallows dead rules"; fail=$((fail+1)) ;;
esac
case $(compile_verdict "$red_dir/always.md") in
  alwaysapply) note ok "compile near-miss: alwaysApply rule with no condition is exempt"; pass=$((pass+1)) ;;
  *) note FAIL "compile near-miss: an alwaysApply rule was flagged — guard is over-strict"; fail=$((fail+1)) ;;
esac

# EXPOSURE RED ARM. The 818-class error counted forbid(unsafe_code) churn as
# danger: raw `unsafe` is high (60 declaration payloads), real danger is near
# zero (1 payload). A tool reporting only the raw count would verdict
# WALLPAPER here (2/2 sessions); the honest tool reports both counts and
# verdicts TOO_RARE on the real one.
exp_dir=/tmp/exposure-redarm; mkdir -p "$exp_dir"
python3 - "$exp_dir" <<'PY'
import json, os, sys
d = sys.argv[1]
rows = []
for i in range(60):
    rows.append({"type": "message", "message": {"role": "assistant", "content": [
        {"type": "toolCall", "name": "edit",
         "arguments": {"path": "src/a%d.rs" % i,
                       "content": "#![forbid(unsafe_code)]\nfn f%d() {}\n" % i}}]}})
with open(os.path.join(d, "sess-a.jsonl"), "w") as fh:
    for row in rows:
        fh.write(json.dumps(row) + "\n")
with open(os.path.join(d, "sess-b.jsonl"), "w") as fh:
    fh.write(json.dumps({"type": "message", "message": {"role": "assistant", "content": [
        {"type": "toolCall", "name": "edit",
         "arguments": {"path": "src/evil.rs",
                       "content": "fn f() { unsafe { 1 } }\n"}}]}}) + "\n")
harvest = {"records": [{"command": c} for c in
           ["cargo test", "rg unsafe src", "ls", "echo hi", "make"]]}
with open(os.path.join(d, "harvest.json"), "w") as fh:
    json.dump(harvest, fh)
PY
out=$(EXPOSURE_CORPUS_DIR="$exp_dir" EXPOSURE_HARVEST="$exp_dir/harvest.json" \
  ./scripts/exposure-check.sh --pattern 'unsafe' --not 'forbid\(unsafe_code\)' --label 'red-forbid' 2>&1 || true)
case "$out" in
  *'payloads: 1/61'*'raw 61, 60 excluded'*)
    note ok "exposure RED arm: raw-vs-real discrepancy reported (61 raw, 1 real)"; pass=$((pass+1)) ;;
  *) note FAIL "exposure RED arm: tool did not report raw-vs-real — got: $out"; fail=$((fail+1)) ;;
esac
case "$out" in
  *'VERDICT: TOO_RARE'*)
    note ok "exposure RED arm: verdicts on the real count (TOO_RARE)"; pass=$((pass+1)) ;;
  *) note FAIL "exposure RED arm: wrong verdict — a raw-only tool would say WALLPAPER"; fail=$((fail+1)) ;;
esac

# KIT RULES landed at b947da1. Same fire/quiet shape. Snippets proven with
# `omp ttsr test --json` before this edit (W1.3, jev-deep-kit-8q7.1).
arm_at() { # rule expect label source tool path snippet
  local f="$1" want="$2" label="$3" src="$4" tool="$5" pth="$6" txt="$7" got out
  if [ "$src" = text ]; then
    out=$(omp ttsr test --rule "$f" --source text "$txt" 2>&1)
  elif [ -n "$pth" ]; then
    out=$(omp ttsr test --rule "$f" --source tool --tool "$tool" --path "$pth" "$txt" 2>&1)
  else
    out=$(omp ttsr test --rule "$f" --source tool --tool "$tool" "$txt" 2>&1)
  fi
  if grep -qE '^Triggered \([1-9]' <<<"$out"; then got=fire; else got=quiet; fi
  if [ "$got" = "$want" ]; then note ok "$label ($want)"; pass=$((pass+1))
  else note FAIL "$label — wanted $want, got $got"; fail=$((fail+1)); fi
}
# The live matcher sees the command inside the tool call's JSON arguments, so the closing `"` of
# the command string is what ends a bare `br close <id>`; the CLI tester passes raw text, so the
# fire arms name a terminator explicitly. The streamed-prefix arm is QUIET since 2026-09-23: the
# old pattern fired on `br close jev-x --reason` before the reason arrived (proven by pane 2, fe819d3);
# the pattern adopted from ~/.agents waits for the command to end.
arm_at .omp/rules/kit-close-needs-evidence.md fire  "kit-close: br close without reason (JSON-quoted)" tool bash "" '{"command":"br close jev-x"}'
arm_at .omp/rules/kit-close-needs-evidence.md fire  "kit-close: br close without reason, then another command" tool bash "" "br close jev-x; br list"
arm_at .omp/rules/kit-close-needs-evidence.md quiet "kit-close: streamed prefix before --reason stays quiet" tool bash "" "br close jev-x --reason"

arm_at .omp/rules/kit-close-needs-evidence.md quiet "kit-close: br close with reason"    tool bash "" "br close jev-x --reason done"
arm_at .omp/rules/kit-no-verify.md fire  "kit-no-verify: commit --no-verify" tool bash "" "git commit --no-verify -m x"
arm_at .omp/rules/kit-no-verify.md quiet "kit-no-verify: git status"          tool bash "" "git status -sb"
# jev-sx9: the hook-pointer condition used to be the bare key, so it interrupted on READS of it
# (4 false interrupts, 0 bypasses, gate-edit session 1). The omp-kit version exempts the read forms.
# Two directions, or it is a nag or a hole: reads and searches QUIET, every write form FIRES. The
# value-set arm is JSON-quoted because the pattern waits for the value to end (live tool args).
arm_at .omp/rules/kit-no-verify.md quiet "kit-no-verify: read the hook pointer (--get)" tool bash "" "git config --get core.hooksPath"
arm_at .omp/rules/kit-no-verify.md quiet "kit-no-verify: text search for the key"      tool bash "" "rg -n core.hooksPath .omp scripts"
arm_at .omp/rules/kit-no-verify.md fire  "kit-no-verify: set the hook pointer"         tool bash "" '{"command":"git config core.hooksPath /dev/null"}'
arm_at .omp/rules/kit-no-verify.md fire  "kit-no-verify: -c override of the pointer"   tool bash "" "git -c core.hooksPath=/tmp commit -m x"
arm_at .omp/rules/kit-no-verify.md fire  "kit-no-verify: --unset the pointer"          tool bash "" '{"command":"git config --unset core.hooksPath"}'
arm_at .omp/rules/kit-no-verify.md fire  "kit-no-verify: --unset then another command" tool bash "" '{"command":"git config --unset core.hooksPath; git status"}'
arm_at .omp/rules/kit-unverified-done.md fire  "kit-unverified: should now pass" text "" "" "the tests should now pass"
arm_at .omp/rules/kit-unverified-done.md quiet "kit-unverified: a receipt sha"   text "" "" "the receipt is at cead414"
arm_at .omp/rules/kit-test-skip.md fire  "kit-skip: it.skip" tool edit t.ts "it.skip('x')"
arm_at .omp/rules/kit-test-skip.md quiet "kit-skip: it("     tool edit t.ts "it('x')"
arm_at .omp/rules/kit-jsonl-close.md fire  "kit-jsonl: closed without a long reason" tool edit .beads/issues.jsonl '{"status": "closed"}'
arm_at .omp/rules/kit-jsonl-close.md fire  "kit-jsonl: old 20-char reason is insufficient" tool edit .beads/issues.jsonl '{"status": "closed", "close_reason": "01234567890123456789"}'
arm_at .omp/rules/kit-jsonl-close.md quiet "kit-jsonl: closed with evidence reason" tool edit .beads/issues.jsonl '{"status": "closed", "close_reason": "done at commit 5c065f5, 12/12 tests pass"}'
arm_at .omp/rules/kit-weasel-retry.md fire  "kit-weasel: retry predicate later" tool edit NEGATIVE_EVIDENCE.md "retry predicate: later"
arm_at .omp/rules/kit-weasel-retry.md quiet "kit-weasel: retry predicate names a receipt" tool edit NEGATIVE_EVIDENCE.md "retry predicate: a new receipt lands"
# jev-9gtw.4.2: a second copy of a benchmark scorer (Python split() vs MiniWoB's JS split) scored
# scroll-text 20/20 where the benchmark's rule gives 18/20. Fire on scorer-copy names under work/,
# stay quiet on the resume helper `answered` and outside work/.
arm_at .omp/rules/scorer-reimplementation.md fire  "scorer-copy: derive_needed_text in work/" tool write work/miniwob-jev/x.py "def derive_needed_text(record):"
arm_at .omp/rules/scorer-reimplementation.md quiet "scorer-copy: answered() resume helper"   tool write work/miniwob-jev/x.py "def answered(path):"
arm_at .omp/rules/scorer-reimplementation.md quiet "scorer-copy: same name outside work/"    tool write scripts/x.py "def derive_needed_text(record):"


# Every project rule must own at least one arm above. Check the arm declarations
# themselves, not merely the number of rule files (RULE 1).
rules_dir=${RULES_DIR:-.omp/rules}
n_rules=$(ls -1 "$rules_dir"/*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$n_rules" -eq 0 ]; then
  note FAIL ".omp/rules/*.md matched nothing — an empty scan set is NOT a pass"; fail=$((fail+1))
else
  # An arm is an arm/arm_at/arm_text line whose rule argument is the path itself or a variable
  # assigned exactly that path. A comment or a bare VAR=path line is not an arm: keeping
  # A=.omp/rules/absence-from-one-probe.md while deleting every arm_text "$A" line used to pass.
  missing_rules=0
  for rule_path in "$rules_dir"/*.md; do
    vars=$(sed -nE "s|^([A-Za-z_][A-Za-z0-9_]*)=\"?${rule_path//./\\.}\"?[[:space:]]*$|\1|p" "$0")
    alts="${rule_path//./\\.}"
    for v in $vars; do alts="$alts|\"?\\\$\{?$v\}?\"?"; done
    if grep -Eq "^[[:space:]]*arm(_at|_text)?[[:space:]]+($alts)[[:space:]]" "$0"; then
      :
    else
      note FAIL "$rule_path has no arm (no arm/arm_at/arm_text line uses its path or a variable holding it)"; missing_rules=$((missing_rules+1)); fail=$((fail+1))
    fi
  done
  if [ "$missing_rules" -eq 0 ]; then
    note ok "every project rule ($n_rules) has an arm declaration"; pass=$((pass+1))
  fi
fi

[ "$na" -eq 0 ] || echo "SCOPE: project rules only; $na system-wide arm group(s) n/a because $SYS_ROOT does not exist here"
echo "scripts/selftest-ttsr-rules.sh: $pass ok, $fail failed, $na n/a"
[ "$fail" -eq 0 ]
