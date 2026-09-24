#!/bin/sh
# install-harm-rule.sh — install the omp harm-rule extension into an omp profile.
#
# Usage: install-harm-rule.sh [--check] [profile-name]
#        install-harm-rule.sh --selftest
#   profile-name defaults to "default". --check verifies an existing install
#   without writing anything. --selftest runs the TESTS.md arms against a
#   throwaway OMP_HOME under the temp dir; no real profile is read or written.
#
# WHAT THIS IS
#   Four regular expressions that flag destructive-shaped bash commands, logged
#   and never blocked. It contains NO model call. It was built by measuring a
#   language model on the same task and losing to it by one recall point at zero
#   cost and zero latency:
#
#     deterministic rule   12/12 recall   0/40 false positives
#     the model            11/12 recall   0/40 false positives
#     a dumb baseline       5/12 recall
#
#   Scored by a non-author on a held-out, time-ordered split of 216k real tool
#   decisions. Full method: docs/demos/upstream-repro/harm-rule-shipped-20260919.md
#
# WHAT LANDS (all profile-scoped, all reviewable, all removable)
#   <profile>/agent/extensions/harm-rule.ts     the rule
#   <profile>/agent/config.yml                  gains harm-rule in extensions:
#   <profile>/agent/extensions/INSTALL-RECEIPT.txt  what was installed, from which SHA
#
# WHAT IT VERIFIES  file present, named in config.yml, parses under node --check.
# WHAT IT NEVER CLAIMS  that it fired. Only a decision row in a session proves
#   that; this script prints the exact command to check after real work.
#
# OBSERVE-ONLY BY CONSTRUCTION  there is no block path in the source. Grep it:
#   grep -nE 'block|deny|abort|reject|exit' harm-rule.ts   -> no control flow
set -u

here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
src="$here/harm-rule.ts"

if [ "${1:-}" = "--selftest" ]; then
  t=$(mktemp -d "${TMPDIR:-/tmp}/harm-rule-selftest.XXXXXX") || { echo "RED: mktemp failed" >&2; exit 1; }
  case "$t" in ""|"$HOME"/.omp*) echo "RED: refusing OMP_HOME=$t" >&2; exit 1 ;; esac
  self="$here/install-harm-rule.sh"
  bad=0
  arms=0
  # arm <name> <want-exit> <args...>: one unpiped run of this installer under the throwaway OMP_HOME.
  arm() {
    name=$1; want=$2; shift 2
    arms=$((arms + 1))
    OMP_HOME="$t" sh "$self" "$@" > "$t/$name.log" 2>&1
    got=$?
    if [ "$got" = "$want" ]; then echo "  ok   $name (exit $got)"
    else echo "  FAIL $name: exit $got, want $want (log $t/$name.log)"; bad=$((bad + 1)); fi
  }
  expect() { # expect <name> <command...>: a check on the files the arms left behind.
    name=$1; shift
    arms=$((arms + 1))
    if "$@"; then echo "  ok   $name"; else echo "  FAIL $name"; bad=$((bad + 1)); fi
  }
  profile_with() { mkdir -p "$t/profiles/$1/agent" && printf '%b' "$2" > "$t/profiles/$1/agent/config.yml"; }
  listed_once() { [ "$(grep -cE '^[[:space:]]*-[[:space:]]*harm-rule[[:space:]]*$' "$t/profiles/$1/agent/config.yml")" = 1 ]; }

  profile_with tp 'extensions:\n  - other\n'
  arm check-before-install 1 --check tp
  arm install 0 tp
  arm check-after-install 0 --check tp
  arm reinstall-idempotent 0 tp
  expect "listed once after reinstall" listed_once tp
  profile_with empty 'extensions:\n'
  arm empty-block-list 0 empty
  arm empty-block-list-check 0 --check empty
  profile_with inline 'extensions: [other]\n'
  cp "$t/profiles/inline/agent/config.yml" "$t/inline-before.yml"
  arm inline-list-refused 1 inline
  expect "inline config unmodified" cmp -s "$t/inline-before.yml" "$t/profiles/inline/agent/config.yml"
  arm missing-profile-refused 1 nosuch

  if [ "$bad" -eq 0 ]; then echo "install-harm-rule --selftest: PASS ($arms arms, OMP_HOME=$t)"; exit 0; fi
  echo "install-harm-rule --selftest: RED ($bad of $arms arms failed, OMP_HOME=$t)"
  exit 1
fi

mode="install"
profile="default"
if [ "${1:-}" = "--check" ]; then mode="check"; shift; fi
if [ "${#}" -ge 1 ]; then profile="$1"; fi

root="${OMP_HOME:-$HOME/.omp}/profiles/$profile/agent"
ext="$root/extensions"
cfg="$root/config.yml"
dst="$ext/harm-rule.ts"
receipt="$ext/INSTALL-RECEIPT.txt"

fail() { echo "RED: $1" >&2; exit 1; }

# The loader globs *.{ts,js} only — a .mjs extension is never read. Measured, not assumed.
case "$src" in *.ts) ;; *) fail "source must be .ts; the loader ignores other extensions" ;; esac

# An inline sequence (extensions: [a, b]) cannot take an appended "  - item" line: the result is
# unparseable YAML. Detect it rather than corrupting the user's config.
# Found by pane3 grading this installer (docs/demos/upstream-repro/installer-grade-20260919.md,
# 2100286) — the THIRD defect in this file, and the first that damaged the file it edited.
is_inline_list() { grep -qE '^extensions:[[:space:]]*\[' "$1"; }

verify() {
  ok=1
  [ -f "$dst" ] || { echo "  MISSING $dst"; ok=0; }
  if [ -f "$cfg" ]; then
    # A bare `grep harm-rule` also matches a comment, a corrupted line, or an unrelated key.
    # Require the entry to be a real block-sequence item.
    grep -qE '^[[:space:]]*-[[:space:]]*harm-rule[[:space:]]*$' "$cfg" \
      || { echo "  NOT LISTED as a list item in $cfg"; ok=0; }
    if is_inline_list "$cfg"; then
      echo "  MALFORMED: $cfg has an inline extensions: [...] list"; ok=0
    fi
  else
    echo "  MISSING $cfg"; ok=0
  fi
  [ "$ok" = 1 ]
}

if [ "$mode" = "check" ]; then
  echo "checking profile '$profile' at $root"
  if verify; then
    echo "GREEN: harm-rule installed and listed"
    echo
    echo "Presence is not firing. After some real work, check for decision rows:"
    echo "  grep -rho '\"kind\":\"harm_[a-z]*\"' \"${OMP_HOME:-\$HOME/.omp}/profiles/$profile/agent/sessions/\" | sort | uniq -c"
    exit 0
  fi
  echo "RED: not installed (or not listed)"
  echo "FIX: create the profile and its agent/config.yml, then run $0 $profile to install; rerun $0 --check $profile"
  exit 1
fi

[ -f "$src" ] || fail "missing source $src"
[ -d "$root" ] || fail "no such profile: $root  (create it, or pass an existing profile name)"
[ -f "$cfg" ] || fail "no config.yml at $cfg — extensions are registered there, not by directory presence"

# Refuse BEFORE touching anything. Appending "  - harm-rule" after an inline sequence produces
# `extensions: []` followed by a list item, which no YAML parser accepts — and the old --check
# then reported GREEN on the wreckage because it only grepped for the string.
if is_inline_list "$cfg"; then
  fail "$cfg uses an inline list (extensions: [...]). This installer only edits block lists.
  Convert it by hand first:
      extensions:
        - existing-one
        - harm-rule
  Nothing has been modified."
fi

mkdir -p "$ext" || fail "cannot create $ext"

# Back out cleanly: record what was there BEFORE the first install and never overwrite it.
# Measured defect: an earlier draft re-copied the backup on every run, so a second install
# clobbered the pristine config with the already-modified one and "rollback" restored a file
# that still listed the extension. A backup that a re-run can destroy is not a backup.
if [ -f "$dst" ] && [ ! -f "$dst.bak" ]; then
  cp "$dst" "$dst.bak" || fail "cannot back up existing $dst"
fi
if [ ! -f "$cfg.bak" ]; then
  cp "$cfg" "$cfg.bak" || fail "cannot back up $cfg"
else
  echo "  keeping existing $cfg.bak (pristine pre-install copy)"
fi

cp "$src" "$dst" || fail "copy failed"

# Registration is an explicit list entry. Directory presence does NOT register an
# extension — that mistake produced a valid-syntax, never-firing module and cost
# this lane a day (NEGATIVE_EVIDENCE R29).
if grep -qE '^[[:space:]]*-[[:space:]]*harm-rule[[:space:]]*$' "$cfg"; then
  echo "  already listed in config.yml, left as-is"
else
  if grep -qE '^extensions:' "$cfg"; then
    awk '/^extensions:/ { print; print "  - harm-rule"; next } { print }' "$cfg" > "$cfg.tmp" \
      && mv "$cfg.tmp" "$cfg" || fail "could not add to extensions:"
  else
    printf 'extensions:\n  - harm-rule\n' >> "$cfg" || fail "could not append extensions:"
  fi
  echo "  added to extensions: in config.yml"
fi

sha=$(git -C "$here" rev-parse --short HEAD 2>/dev/null || echo unknown)
{
  echo "harm-rule installed $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "from      $src"
  echo "source sha $sha"
  echo "shasum     $(shasum -a 256 "$dst" | cut -d' ' -f1)"
  echo "profile    $profile"
  echo "rollback   rm '$dst' && mv '$cfg.bak' '$cfg'"
} > "$receipt"

echo "GREEN: installed into profile '$profile'"
echo "  rule     $dst"
echo "  receipt  $receipt"
echo "  rollback rm '$dst' && mv '$cfg.bak' '$cfg'"
echo
echo "INSTALLED IS NOT FIRING. Do some real work, then:"
echo "  grep -rho '\"kind\":\"harm_[a-z]*\"' \"${OMP_HOME:-\$HOME/.omp}/profiles/$profile/agent/sessions/\" | sort | uniq -c"
echo
echo "Each decision row carries the command it judged, so a fire is always quotable."
echo "It never blocks. If it annoys you, run the rollback line above."
