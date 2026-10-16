#!/usr/bin/env bash
# selftest for the fixture-isolation scrub (jev-n3lx) — discovered by foundation/gates.d/80 via the
# scripts/selftest-*.sh glob. A fixture that builds its own repo must not write through the git
# environment its CALLER exported (GIT_DIR / GIT_WORK_TREE / GIT_INDEX_FILE).
#
# WHY. 2026-10-06 a pane exported those three to point foundation/gates.d/70 at a candidate tree, then
# ran `gates.sh --selftest`. Stage 80 ran selftest-pin-liveness.sh and selftest-serialized-add.sh, stage 60
# ran its fixtures: every `git -C "$tmp" init` / `git config` / `git commit` landed in the SHARED repo. The
# checkout was left with core.hooksPath=/dev/null and the identity serialized-add-selftest (so no commit hook
# ran and 48 commits were misattributed), plus stray fixture commits in its HEAD reflog.
#
# THE SENTINEL. A decoy repo stands in for the caller's repo. Its config bytes, refs, reflog length and
# staged entries are fingerprinted before and after each subject; any change means the subject wrote through
# the inherited environment. Both directions, as everywhere in this lane:
#   - a planted unscrubbed fixture and the two real selftests with their scrub deleted MUST change the decoy;
#   - the scrubbed fixture, the two real selftests and stage 60 MUST leave it byte-identical and still run.
#
# NOT COVERED HERE (measured once, recorded in docs/evidence/jev-90id-sentinel-20261011.md, not re-run by this gate):
#   gates.d/50 (needs private loop-kit) and the python fixture tests. publish-export.sh is run in full, in a fixture repo
#   (jev-x5cy made that possible: against the real tree its scan refuses first); miniwob's check_provenance is a replay.
set -uo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$root" || exit 2
pass=0; fail=0
note() { printf '  %-4s %s\n' "$1" "$2"; }
ok() { note ok "$1"; pass=$((pass + 1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail + 1)); }

mkdir -p "$root/var/agent-tmp" || exit 1
# Short label on purpose: the serialized-add fixture needs a Unix socket path under ~103 bytes.
tmp=$(mktemp -d "$root/var/agent-tmp/fi.XXXXXX") || { echo "selftest-fixture-isolation: mktemp failed"; exit 1; }
printf 'pid=%s\nlabel=selftest-fixture-isolation\nrepo=%s\ncreated=%s\n' "$$" "$root" "$(date -u +%FT%TZ)" > "$tmp/.owner"
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null

decoy="$tmp/d"
git init -q -b main "$decoy" || { echo "selftest-fixture-isolation: decoy init failed"; exit 1; }
git -C "$decoy" -c user.name=decoy -c user.email=decoy@example.invalid commit -q --allow-empty -m 'decoy base [test]' \
  || { echo "selftest-fixture-isolation: decoy commit failed"; exit 1; }

# One line that changes if a subject wrote the decoy's config, refs, reflog or staged entries.
sentinel() {
  local g="$decoy/.git"
  {
    shasum -a 256 < "$g/config"
    git --git-dir="$g" for-each-ref
    git --git-dir="$g" reflog | wc -l | tr -d ' '
    git --git-dir="$g" --work-tree="$decoy" ls-files -s
  } | shasum -a 256 | cut -c1-16
}

# Run "$@" from the repo root with the decoy as the git context its CALLER exported (the 2026-10-06 shape).
poisoned() {
  ( cd "$root" && GIT_DIR="$decoy/.git" GIT_WORK_TREE="$decoy" GIT_INDEX_FILE="$decoy/.git/index" "$@" ) > "$tmp/out" 2>&1
}

# expect_untouched <label> <subject...>: the subject must run (rc 0, or 8 = SKIP under --portable) AND leave the decoy as it was.
expect_untouched() {
  local label="$1" before after rc; shift
  before=$(sentinel); poisoned "$@"; rc=$?; after=$(sentinel)
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 8 ]; then no "$label: subject did not run (rc=$rc): $(tail -1 "$tmp/out")"
  elif [ "$before" != "$after" ]; then no "$label: wrote through the inherited GIT_DIR (decoy $before -> $after)"
  else ok "$label: decoy untouched (rc=$rc)"; fi
}

# expect_leak <label> <subject...>: the subject must change the decoy; otherwise the sentinel cannot see this class.
expect_leak() {
  local label="$1" before after; shift
  before=$(sentinel); poisoned "$@"; after=$(sentinel)
  if [ "$before" = "$after" ]; then no "$label: decoy unchanged — the sentinel is blind to this leak"; else ok "$label: decoy changed ($before -> $after)"; fi
}

# Arm 1 + 2: the sentinel itself, on a planted fixture, both directions.
mkdir -p "$tmp/fx1" "$tmp/fx2"
# shellcheck disable=SC2016  # $1 is for the planted script, not for this shell
printf '#!/usr/bin/env bash\ngit -C "$1" init -q\ngit -C "$1" config user.name leaked\n' > "$tmp/leaky.sh"
# shellcheck disable=SC2016  # same: $1 belongs to the planted script
printf '#!/usr/bin/env bash\nunset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE\ngit -C "$1" init -q\ngit -C "$1" config user.name leaked\n' > "$tmp/scrubbed.sh"
expect_leak "planted unscrubbed fixture" bash "$tmp/leaky.sh" "$tmp/fx1"
expect_untouched "planted scrubbed fixture" bash "$tmp/scrubbed.sh" "$tmp/fx2"

# Arm 3: the real subjects, as shipped.
expect_untouched "selftest-pin-liveness" "$root/scripts/selftest-pin-liveness.sh"
expect_untouched "selftest-serialized-add" "$root/scripts/selftest-serialized-add.sh"
# JEV_GATES_PORTABLE: without private loop-kit the stage runs its deletion lane and exits 8, never a false RED.
expect_untouched "gates.d/60-staged-deletion-lane" env JEV_GATES_PORTABLE=1 "$root/foundation/gates.d/60-staged-deletion-lane.sh"

# Arm 4: the same two selftests with their scrub line deleted MUST leak. Each copy sits in its own tree with
# symlinks to what it needs, so `root=$(dirname $0)/..` resolves inside the copy and nothing real is touched.
mutant() { # mutant <name> <awk-filter> <symlink target...>: build $tmp/<name>/scripts/selftest-<name>.sh
  local name="$1" filter="$2" dir; shift 2
  dir="$tmp/$name"; mkdir -p "$dir/scripts" "$dir/docs/demos"
  awk "$filter" "$root/scripts/selftest-$name.sh" > "$dir/scripts/selftest-$name.sh"
  chmod +x "$dir/scripts/selftest-$name.sh"
  local t; for t in "$@"; do ln -s "$root/$t" "$dir/$t"; done
  if cmp -s "$root/scripts/selftest-$name.sh" "$dir/scripts/selftest-$name.sh"; then echo vacuous; else echo "$dir/scripts/selftest-$name.sh"; fi
}
m=$(mutant pin-liveness '/^unset GIT_DIR/{next} {print}' scripts/pin-liveness.sh docs/demos/STATUS.tsv)
if [ "$m" = vacuous ]; then no "mutant pin-liveness: scrub line not found, the mutant equals the original"; else expect_leak "selftest-pin-liveness without its scrub" "$m"; fi
# serialized-add stops right after its fixture config (its arms would otherwise run against the decoy for ~30s).
# The mutant removes BOTH the entry unset and the helper's explicit GIT_CONFIG binding: either layer alone
# (unset, or per-command binding) keeps the decoy clean, so only the joint removal is genuinely unsafe.
m=$(mutant serialized-add '/^unset GIT_DIR/{next} { gsub(/GIT_CONFIG="\$1\/\.git\/config" /, ""); print } /config user.name serialized-add-selftest/{print "exit 0"}' scripts/git-commit-serialized.sh scripts/git-commitd.py)
if [ "$m" = vacuous ]; then no "mutant serialized-add: scrub/binding lines not found, the mutant equals the original"; else expect_leak "selftest-serialized-add without scrub/binding" "$m"; fi
# jev-90id: the commit-msg hook's own --selftest, as shipped and with its scrub deleted (standalone copy).
expect_untouched "commit-msg hook --selftest" "$root/githooks/commit-msg-verification-level.sh" --selftest
awk '/^ *unset GIT_DIR/{next} {print}' "$root/githooks/commit-msg-verification-level.sh" > "$tmp/hook-mutant.sh"; chmod +x "$tmp/hook-mutant.sh"
if cmp -s "$root/githooks/commit-msg-verification-level.sh" "$tmp/hook-mutant.sh"; then no "mutant hook: scrub line not found"; else expect_leak "commit-msg hook --selftest without its scrub" "$tmp/hook-mutant.sh" --selftest; fi
# jev-90id: run-registered-suites.py --selftest, as shipped and from a copy whose scrub (the os.environ.pop) is turned into `pass`.
expect_untouched "run-registered-suites --selftest" python3 "$root/scripts/run-registered-suites.py" --selftest
mkdir -p "$tmp/rrs/scripts"
awk '/os\.environ\.pop\(_name, None\)/{sub(/os\.environ\.pop\(_name, None\)/, "pass")} {print}' "$root/scripts/run-registered-suites.py" > "$tmp/rrs/scripts/run-registered-suites.py"
if cmp -s "$root/scripts/run-registered-suites.py" "$tmp/rrs/scripts/run-registered-suites.py"; then no "mutant run-registered-suites: scrub line not found"; else expect_leak "run-registered-suites --selftest without its scrub" python3 "$tmp/rrs/scripts/run-registered-suites.py" --selftest; fi
# jev-90id/jev-x5cy: publish-export.sh, the FULL script (archive, transforms, scan, git init, commit), run inside a tiny
# fixture repo whose own .git is exported as the caller's GIT_DIR (the 2026-10-06 shape: caller repo == the script's repo).
# As shipped the fixture repo must be untouched; with its `unset GIT_DIR ...` line deleted it must change. A full run.
pe_root() { # pe_root <name> <script>: a tiny repo that is its own ROOT (export lands beside it, inside $tmp)
  local d="$tmp/$1/root"; mkdir -p "$d/scripts" "$d/docs" "$d/data"
  cp -p "$2" "$d/scripts/publish-export.sh"; printf '# none\n' > "$d/docs/publish-key-exceptions.txt"; printf 'x\n' > "$d/data/f.txt"
  git init -q -b main "$d" && git -C "$d" add -A \
    && git -C "$d" -c user.name=fi -c user.email=fi@example.invalid commit -q -m 'fixture [test]' && printf '%s' "$d"
}
awk '/^unset GIT_DIR/{next} {print}' "$root/scripts/publish-export.sh" > "$tmp/pe-mutant.sh"
if cmp -s "$root/scripts/publish-export.sh" "$tmp/pe-mutant.sh"; then no "mutant publish-export: the unset line was not found"
elif ! d1=$(pe_root pe1 "$root/scripts/publish-export.sh") || ! d2=$(pe_root pe2 "$tmp/pe-mutant.sh"); then no "publish-export fixture repo build failed"
else
  decoy_main=$decoy
  decoy=$d1; expect_untouched "publish-export.sh full run (fixture repo as the caller)" bash "$d1/scripts/publish-export.sh"
  decoy=$d2; expect_leak "publish-export.sh full run without its unset" bash "$d2/scripts/publish-export.sh"
  decoy=$decoy_main
fi
# jev-90id: miniwob check_provenance, replayed out of run-after-rotation.sh (the script itself needs a live run sheet).
mw_block() { awk '/^check_provenance\(\)/{on=1} on{print} on && /^\)$/{exit}' "$root/work/miniwob-jev/run-after-rotation.sh"; }
# shellcheck disable=SC2016  # $1 / $ROOT belong to the generated harness
{ printf 'ROOT=%s\nRUN_ROOT=$1\n' "$root"; mw_block; printf 'mkdir -p "$RUN_ROOT"; printf "{}\\n" > "$RUN_ROOT/rows.jsonl"\ncheck_provenance s1 "$RUN_ROOT/rows.jsonl" >/dev/null 2>&1 || true\n[ -d "$RUN_ROOT/provenance-s1/.git" ]\n'; } > "$tmp/mw-shipped.sh"
awk '/^  unset GIT_DIR/{next} {print}' "$tmp/mw-shipped.sh" > "$tmp/mw-mutant.sh"
if ! grep -q '^check_provenance' "$tmp/mw-shipped.sh" || cmp -s "$tmp/mw-shipped.sh" "$tmp/mw-mutant.sh"; then
  no "miniwob block: check_provenance or its unset line was not found"
else
  expect_untouched "miniwob check_provenance (replay)" bash "$tmp/mw-shipped.sh" "$tmp/mw1"
  expect_leak "miniwob check_provenance (replay) without its unset" bash "$tmp/mw-mutant.sh" "$tmp/mw2"
fi

printf 'selftest-fixture-isolation: pass=%d fail=%d\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
