#!/usr/bin/env bash
# selftest for scripts/git-commit-serialized.sh add mode — discovered by
# foundation/gates.d/80 via the scripts/selftest-*.sh glob. Every arm plants
# a real condition and requires the stated outcome.
set -uo pipefail
# jev-n3lx: this selftest builds its own fixture repo. A caller that exported GIT_DIR / GIT_WORK_TREE /
# GIT_INDEX_FILE (to point a gate at a candidate tree) must not steer the fixture's `git config` and
# `git commit` at the caller's repository: under an inherited GIT_DIR they rewrite its .git/config.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$root" || exit 2
S="$root/scripts/git-commit-serialized.sh"
pass=0; fail=0
note() { printf '  %-4s %s\n' "$1" "$2"; }
ok() { note ok "$1"; pass=$((pass + 1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail + 1)); }

mkdir -p "$root/var/agent-tmp" || exit 1
tmp=$(mktemp -d "$root/var/agent-tmp/serialized-add.XXXXXX") || { echo "selftest-serialized-add: mktemp failed"; exit 1; }
printf 'pid=%s\nlabel=selftest-serialized-add\nrepo=%s\ncreated=%s\n' "$$" "$root" "$(date -u +%FT%TZ)" > "$tmp/.owner"
cleanup() { python3 "$root/scripts/git-commitd.py" stop --repo "$tmp" >/dev/null 2>&1 || true; }
trap cleanup EXIT
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
git -C "$tmp" init -q
git -C "$tmp" config user.email selftest@example.invalid
git -C "$tmp" config user.name serialized-add-selftest
printf 'base\n' > "$tmp/base.txt"
git -C "$tmp" add base.txt && git -C "$tmp" commit -qm "baseline [test]"
printf 'one\n' > "$tmp/a.txt"
printf 'two\n' > "$tmp/b.txt"

# Arm 1: two concurrent adds serialize; both files staged, no lock left.
# (Backgrounded subshells are children of this shell, so wait observes them.)
(cd "$tmp" && exec "$S" add -- a.txt >/dev/null 2>&1) &
(cd "$tmp" && exec "$S" add -- b.txt >/dev/null 2>&1) &
wait
staged=$(cd "$tmp" && git diff --cached --name-only | sort | tr '\n' ' ')
if [ "$staged" = "a.txt b.txt " ]; then ok "concurrent adds both staged"; else no "concurrent adds staged=[$staged]"; fi
if [ ! -e "$tmp/.git/index.lock" ]; then ok "no index.lock left"; else no "index.lock left behind"; fi

# Arm 2: add mode passes paths through (single add stages exactly its file).
printf 'three\n' > "$tmp/c.txt"
(cd "$tmp" && "$S" add -- c.txt) >/dev/null 2>&1
if [ "$(cd "$tmp" && git diff --cached --name-only)" = "a.txt
b.txt
c.txt" ]; then ok "add stages its paths"; else no "add paths wrong"; fi

# Arm 3: commit only the requested path; sibling staged paths stay staged.
if (cd "$tmp" && "$S" --only -m "selftest commit [test]" -- c.txt >/dev/null 2>&1); then ok "path-limited commit intact"; else no "path-limited commit broke"; fi
committed=$(cd "$tmp" && git diff-tree --no-commit-id --name-only -r HEAD | tr '\n' ' ')
staged=$(cd "$tmp" && git diff --cached --name-only | sort | tr '\n' ' ')
if [ "$committed" = "c.txt " ] && [ "$staged" = "a.txt b.txt " ]; then ok "commit isolated to requested path"; else no "commit paths=[$committed] staged=[$staged]"; fi

# Arm 4 (jev-n3lx.1): hostile inherited Git config cannot steer fixture writes.
# A caller exporting GIT_CONFIG (bare form steers `git -C <dir> config`, proven
# 2026-10-12: probe write landed in the pointed file, not the fixture repo)
# must not mutate an unrelated sentinel config; the fixture repo takes its own
# values. Removing the unset below must fail both assertions.
sentinel="$tmp/sentinel-config"
printf '[user]\n\tname = sentinel\n' > "$sentinel"
sentinel_before=$(shasum -a 256 "$sentinel" | cut -d' ' -f1)
(
  export GIT_CONFIG="$sentinel" GIT_DIR="$tmp/.git" GIT_WORK_TREE="$tmp"
  unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG
  git -C "$tmp" config user.email probe@example.invalid
  git -C "$tmp" config user.name probe-selftest
)
if [ "$(shasum -a 256 "$sentinel" | cut -d' ' -f1)" = "$sentinel_before" ]; then ok "hostile GIT_CONFIG leaves sentinel untouched"; else no "sentinel config mutated"; fi
fixture_email=$(cd "$tmp" && git config user.email)
if [ "$fixture_email" = "probe@example.invalid" ]; then ok "fixture repo took its own config"; else no "fixture config misdirected"; fi
if grep -q "unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE" "$0"; then ok "entry guard line present"; else no "entry guard line missing"; fi

printf 'selftest-serialized-add: pass=%d fail=%d\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
