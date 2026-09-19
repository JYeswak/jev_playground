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
  if [ ! -d "$dep_src" ]; then
    echo "RED: pinned fast-jev-compaction clone is missing: $dep_src" >&2
    echo "FIX: from the repository root run ./scripts/bootstrap-compaction.sh, then rerun $0 --check $target" >&2
    exit 1
  fi
  verify
  exit 0
fi


# ---- install ----
[ -d "$target" ] || fail "target is not a directory: $target"
# A FRESH CLONE OF THIS REPO CANNOT RUN THIS SCRIPT without fetching the dependency first: the
# upstream clones are gitignored. Verified 2026-09-19 from a clean clone of jev_playground --
# rc=1 with a bare "pinned clone missing", which is closed but useless. Say what to fetch.
if [ ! -d "$dep_src" ]; then
  printf '%s\n' \
    "RED: pinned clone missing: $dep_src" \
    "" \
    "This repo does not vendor fast-jev-compaction. Fetch it, from the repo root:" \
    "" \
    "    git clone https://github.com/tamaratran/fast-jev-compaction fast-jev-compaction" \
    "    (cd fast-jev-compaction && npm install && npm run build)" \
    "" \
    "The build step is NOT optional: the package exports ./dist/index.js, which is published to" \
    "npm but not committed to git, so a bare clone resolves to nothing." \
    "" \
    "then re-run this installer." >&2
  exit 1
fi
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
  || fail "installed but unresolvable -- if $dep_src is a git clone, it needs a build:
    (cd $dep_src && npm install && npm run build)
  the package exports ./dist/index.js, which npm publishes but git does not carry.
  aborting before copying sources"

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
# `cp -r "$skill_src" "$skill"` NESTS on re-install. Measured 2026-09-19: the second install
# produced .omp/skills/jev-compact/jev-compact/SKILL.md, left the original stale, and still
# printed PASS -- because the verification below looks for $skill/SKILL.md, which existed. A
# false green that survives every re-install. Copy the FILE, with the same divergence rule as
# the entry and the sources.
# `cp -r` used to create this directory as a side effect; copying a file does not. A fresh install
# failed RED on the first run after that change -- closed, not silent, but a regression I caused.
mkdir -p "$skill" || fail "could not create $skill"
if [ -f "$skill/SKILL.md" ] && ! cmp -s "$skill_src/SKILL.md" "$skill/SKILL.md"; then
  skill_backup="$skill/SKILL.md.superseded-$(date -u +%Y%m%dT%H%M%SZ)"
  cp "$skill/SKILL.md" "$skill_backup" || fail "could not back up $skill/SKILL.md"
  echo "note: existing $skill/SKILL.md differs from source; kept a copy at $skill_backup"
fi
cp "$skill_src/SKILL.md" "$skill/SKILL.md" || fail "copy of skill failed"
# A nested directory from an installer older than this fix is reported, never deleted: removing a
# user's files is not this script's call.
[ -d "$skill/jev-compact" ] && echo "note: stale nested $skill/jev-compact left by an older installer; safe to delete by hand"

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
