#!/bin/sh
# install-guard-rule.sh — install the guard-rule hook into an omp profile.
#
# Usage: install-guard-rule.sh [--check] [profile-name]
#   profile-name defaults to "jev-lab". --check verifies an existing install
#   without writing anything. Dogfood order: jev-lab first, never default
#   until jev-lab shows real fires with a measured FP rate.
#
# WHAT THIS IS
#   Four regular expressions that flag epistemic-correctness mistakes in bash
#   commands (pipe-exit, stage-all, commit-backtick, grep-as-proof), logged
#   and never blocked. It contains NO model call. Axis: harm-rule asks "will
#   this break the machine?"; this asks "will this make you believe something
#   false?" — folding them would destroy the distinction
#   (measurement-premortem-20260920.md, NARROW verdict).
#
# WHERE IT LANDS, and why not extensions/. omp exposes a native pre-execution
# surface: hook factories under <agentDir>/hooks/pre/*.ts load as extension
# modules through the extension runner (omp://hooks.md). A factory placed
# directly in hooks/ WITHOUT the pre/ subdir loads silently and reports NO
# ERROR — a silent-zero trap of the class this lane hit 26 times — so this
# installer refuses any destination that is not */hooks/pre/ and --check
# asserts it. No config.yml edit: hooks/pre/ is directory-discovered;
# registration-by-config was the extensions/ surface (R29), not this one.
#
# WHAT LANDS (all profile-scoped, all reviewable, all removable)
#   <profile>/agent/hooks/pre/guard-rule.ts   the hook
#   <profile>/agent/hooks/pre/INSTALL-RECEIPT.txt  what was installed, from which SHA
#
# WHAT IT VERIFIES  file present UNDER pre/, parses under node --check.
# WHAT IT NEVER CLAIMS  that it fired. Only a decision row in a session proves
#   that; this script prints the exact command to check after real work.
#
# OBSERVE-ONLY BY CONSTRUCTION  the handler returns nothing, never
# { block: true }. Grep it:
#   grep -nE 'block|deny|abort|reject|exit' guard-rule.ts   -> no control flow
set -u

here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
src="$here/guard-rule.ts"

mode="install"
profile="jev-lab"
if [ "${1:-}" = "--check" ]; then mode="check"; shift; fi
if [ "${#}" -ge 1 ]; then profile="$1"; fi

root="${OMP_HOME:-$HOME/.omp}/profiles/$profile/agent"
destdir="$root/hooks/pre"
dst="$destdir/guard-rule.ts"
receipt="$destdir/INSTALL-RECEIPT.txt"

fail() { echo "RED: $1" >&2; exit 1; }

# The loader globs *.{ts,js} only — a .mjs file is never read. Measured, not assumed.
case "$src" in *.ts) ;; *) fail "source must be .ts; the loader ignores other extensions" ;; esac

# The silent-zero trap, enforced: without the pre/ subdir the factory loads
# nothing and reports no error. Refuse any destination that is not */hooks/pre/.
case "$dst" in */hooks/pre/guard-rule.ts) ;; *) fail "destination is not a hooks/pre/ path: $dst" ;; esac

verify() {
  ok=1
  [ -f "$dst" ] || { echo "  MISSING $dst"; ok=0; }
  case "$dst" in */hooks/pre/*) ;; *) echo "  NOT UNDER pre/ $dst"; ok=0; ;; esac
  node --check "$dst" >/dev/null 2>&1 || { echo "  NO-PARSE $dst under node --check"; ok=0; }
  [ "$ok" = 1 ]
}

if [ "$mode" = "check" ]; then
  echo "checking profile '$profile' at $root"
  if verify; then
    echo "GREEN: guard-rule installed in profile '$profile'"
    echo "  hook     $dst"
    echo "  receipt  $receipt"
    echo
    echo "INSTALLED IS NOT FIRING. Do some real work, then:"
    echo "  grep -rho '\"kind\":\"guard_[a-z]*\"' \"${OMP_HOME:-\$HOME/.omp}/profiles/$profile/agent/sessions/\" | sort | uniq -c"
    exit 0
  else
    echo "FIX: run $0 $profile to install; rerun $0 --check $profile"
    exit 1
  fi
fi

[ -d "$root" ] || fail "no such profile: $root  (create it, or pass an existing profile name)"

mkdir -p "$destdir" || fail "cannot create $destdir"

# Back out cleanly: record what was there BEFORE the first install and never overwrite it.
if [ -f "$dst" ] && [ ! -f "$dst.bak" ]; then
  cp "$dst" "$dst.bak" || fail "cannot back up existing $dst"
fi

cp "$src" "$dst" || fail "copy failed"
node --check "$dst" >/dev/null 2>&1 || fail "installed file does not parse under node --check"

sha=$(git -C "$here" rev-parse --short HEAD 2>/dev/null || echo unknown)
{
  echo "guard-rule installed $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "from      $src"
  echo "source sha $sha"
  echo "shasum     $(shasum -a 256 "$dst" | cut -d' ' -f1)"
  echo "profile    $profile"
  echo "surface    hooks/pre (directory-discovered, no config.yml edit)"
  echo "rollback   rm '$dst'"
} > "$receipt"

echo "GREEN: installed into profile '$profile'"
echo "  hook     $dst"
echo "  receipt  $receipt"
echo "  rollback rm '$dst'"
echo
echo "INSTALLED IS NOT FIRING. Do some real work, then:"
echo "  grep -rho '\"kind\":\"guard_[a-z]*\"' \"${OMP_HOME:-\$HOME/.omp}/profiles/$profile/agent/sessions/\" | sort | uniq -c"
echo
echo "Each decision row carries the command it judged, so a fire is always quotable."
echo "It never blocks. If it annoys you, run the rollback line above."
