#!/bin/sh
# install-jev-compact.sh — install the jev-compact pre-compaction hook + skill into any repo.
#
# Usage: install-jev-compact.sh [--check] [target-dir]
#   target-dir defaults to the current directory. --check verifies an existing
#   install without writing anything.
#
# What lands in the target (all project-scoped, all reviewable):
#   .omp/hooks/pre/jev-compact.ts          entry (template: compaction/deploy/hook-entry.ts)
#   .omp/lib/jev-compact/*.ts              tested logic (copies of compaction/src/*)
#   .omp/lib/jev-compact/node_modules/…    fast-jev-compact, from OUR pinned clone — no registry
#   .omp/skills/jev-compact/SKILL.md       the skill
#   .omp/lib/jev-compact/INSTALL-RECEIPT.txt  what was installed, from which SHAs
#
# What this verifies: files present, dependency resolvable from the lib dir.
# What it NEVER claims: that the seam fires. Only a decision-log line after a
# real /compact proves that (skill://jev-compact, "Did it fire?").
set -u

here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
repo=$(CDPATH='' cd -- "$here/.." && pwd -P)
dep_src="$repo/fast-jev-compaction"
skill_src="$repo/.omp/skills/jev-compact"
entry_src="$here/deploy/hook-entry.ts"

mode="install"
target="."
if [ "${1:-}" = "--check" ]; then
  mode="check"
  shift
fi
if [ "${#}" -ge 1 ]; then
  target="$1"
fi

lib="$target/.omp/lib/jev-compact"
entry="$target/.omp/hooks/pre/jev-compact.ts"
skill="$target/.omp/skills/jev-compact"
receipt="$lib/INSTALL-RECEIPT.txt"

fail() { echo "RED: $1" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || fail "needs '$1' on PATH"; }

verify() {
  ok=1
  for f in "$entry" "$lib/omp-binding.ts" "$lib/omp-hook.ts" "$lib/omp-adapter.ts" "$skill/SKILL.md"; do
    if [ -f "$f" ]; then
      echo "ok: $f"
    else
      echo "RED: missing $f"
      ok=0
    fi
  done
  if (cd "$lib" && node --input-type=module -e "await import('fast-jev-compaction')" >/dev/null 2>&1); then
    echo "ok: fast-jev-compaction resolves from $lib"
  else
    echo "RED: fast-jev-compaction does not resolve from $lib"
    ok=0
  fi
  if [ "$ok" = "1" ]; then
    echo "PASS: jev-compact installed at $target (placement + dependency; firing proven only by /compact + log)"
    if [ -f "$receipt" ]; then
      cat "$receipt"
    fi
  else
    fail "install at $target is incomplete"
  fi
}

if [ "$mode" = "check" ]; then
  [ -d "$target" ] || fail "target is not a directory: $target"
  need node
  verify
  exit 0
fi

# ---- install ----
[ -d "$target" ] || fail "target is not a directory: $target"
[ -d "$dep_src" ] || fail "pinned clone missing: $dep_src"
[ -f "$entry_src" ] || fail "entry template missing: $entry_src"
[ -f "$skill_src/SKILL.md" ] || fail "skill missing: $skill_src/SKILL.md"
need node
need npm

mkdir -p "$lib" "$target/.omp/hooks/pre" "$target/.omp/skills" || fail "cannot create dirs under $target"

# The lib dir is its own ESM scope. Without this, a target repo whose root
# package.json lacks (or whose tree has no) "type": "module" makes loaders treat
# the copied .ts files as CJS, and the bare 'fast-jev-compaction' import — an
# ESM-only package with no "require" condition — fails to resolve. Measured.
printf '%s\n' '{"name":"jev-compact-lib","private":true,"type":"module"}' > "$lib/package.json" \
  || fail "cannot write $lib/package.json"

# Dependency FIRST from the pinned clone (local directory install — no network,
# no registry). Nothing else is written until this resolves.
npm --prefix "$lib" install --no-save --no-audit --no-fund "$dep_src" >/dev/null 2>&1 \
  || fail "npm could not install $dep_src into $lib (leaving target untouched apart from empty dirs)"
# The package is ESM-only ("import" condition, no "require"), so resolve it the way the hook
# loader will: a bare import from inside the lib dir.
(cd "$lib" && node --input-type=module -e "await import('fast-jev-compaction')" >/dev/null 2>&1) \
  || fail "installed but unresolvable; aborting before copying sources"

# Same rule for the vendored sources, for the same measured reason (2026-09-19): a user edit to
# .omp/lib/jev-compact/*.ts was overwritten with no warning and rc=0. Protecting only the hook
# entry fixed the case I happened to test first and left this one identical.
for src in "$repo/compaction/src/omp-binding.ts" "$repo/compaction/src/omp-hook.ts" \
           "$repo/compaction/src/omp-adapter.ts"; do
  dst="$lib/$(basename "$src")"
  if [ -f "$dst" ] && ! cmp -s "$src" "$dst"; then
    lib_backup="$dst.superseded-$(date -u +%Y%m%dT%H%M%SZ)"
    cp "$dst" "$lib_backup" || fail "could not back up $dst"
    echo "note: existing $dst differs from source; kept a copy at $lib_backup"
  fi
  cp "$src" "$dst" || fail "copy of binding source failed: $src"
done
# NEVER SILENTLY DESTROY A LOCAL EDIT. Measured 2026-09-19: re-installing over a target whose
# jev-compact.ts the user had edited overwrote it, with no warning, no backup, and rc=0. An
# installer we tell people to run against their own repos must not be a data-loss path. If the
# existing entry differs from the template, it is preserved beside the new one and the divergence
# is announced -- the install still proceeds, because refusing would strand a stale hook in place.
if [ -f "$entry" ] && ! cmp -s "$entry_src" "$entry"; then
  backup="$entry.superseded-$(date -u +%Y%m%dT%H%M%SZ)"
  cp "$entry" "$backup" || fail "could not back up the existing hook entry at $entry"
  echo "note: existing $entry differs from the template; kept a copy at $backup"
fi
cp "$entry_src" "$entry" || fail "copy of hook entry failed"
cp -r "$skill_src" "$skill" || fail "copy of skill failed"

dep_ver=$(node -p "require('$lib/node_modules/fast-jev-compaction/package.json').version" 2>/dev/null || echo unknown)
dep_sha=$(git -C "$dep_src" rev-parse HEAD 2>/dev/null || echo unknown)
inst_sha=$(git -C "$repo" rev-parse --short HEAD 2>/dev/null || echo unknown)
{
  echo "installed_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "target=$target"
  echo "fast-jev-compaction version=$dep_ver sha=$dep_sha"
  echo "jev installer sha=$inst_sha"
} > "$receipt" || fail "cannot write $receipt"

verify
echo "next: restart the session WITH TYPESAFE_API_KEY, run /compact, then: tail ~/.jev-compact.log"
