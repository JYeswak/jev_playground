#!/bin/sh
# install-jev-flag.sh — make the jev_flag injection-flag tool loadable.
#
# Usage: install-jev-flag.sh [--check] [profile]
#   profile defaults to "muse". --check verifies and prints a plan
#   without writing anything.
#
# WHAT THIS IS
#   A flag-only prompt-injection annotator (FLAG/NOTE/SILENT), measured live:
#   58/60 paired win over a keyword baseline (McNemar p=0.0000057), framing
#   delta 0.00. Full method: docs/demos/INJECTION-FLAG-RESULT.md
#
# WHAT LANDS (project scope only, reviewable in git, removable)
#   <repo>/.omp/config.yml   gains ./.omp/extensions/jev-flag.ts in extensions:
#   work/nev-injection/INSTALL-RECEIPT.txt   what was ensured, from which SHA
#   (tool + extension already ship in the repo; nothing is copied anywhere)
#
# WHAT IT VERIFIES  files present, entry present exactly once, probe
#   xd://jev_flag_ext_probe in get_state.systemPrompt under the profile,
#   absent under --no-extensions, nonce absent.
# LIMIT  counts EXACT-line matches: a duplicate differing by whitespace or quoting is invisible.
# WHAT IT NEVER CLAIMS  that it fired usefully. L4 organic precision is
#   unmeasured; only decision rows in real sessions prove anything.
#
# PROFILE SUPPORT IS MEASURED, NOT ASSUMED. The extension resolves under muse
# and grok and NOT under codex (measured 2026-09-21, mechanism unexplained).
# Unsupported profiles are refused with exit 1, never installed-into-silence.
# NEVER writes under ~/.omp — project scope only.
set -u

here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
repo=$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || echo "")
tool="$repo/.omp/tools/jev-flag.ts"
ext="$repo/.omp/extensions/jev-flag.ts"
cfg="$repo/.omp/config.yml"
entry="  - ./.omp/extensions/jev-flag.ts"
receipt="$here/INSTALL-RECEIPT.txt"
probe="xd://jev_flag_ext_probe"
nonce="xd://zzzz_no_such_tool_9c42"

mode="install"
profile="muse"
if [ "${1:-}" = "--check" ]; then mode="check"; shift; fi
if [ "${#}" -ge 1 ]; then profile="$1"; fi

fail() { echo "RED: $1" >&2; exit 1; }
say() { echo "${1:-}"; }

[ -n "$repo" ] || fail "not inside a git repo; run from the jev checkout"
[ -f "$tool" ] || fail "missing tool $tool"
[ -f "$ext" ] || fail "missing extension $ext"
[ -f "$cfg" ] || fail "missing config $cfg"

case "$profile" in
  muse|grok) ;;
  codex) fail "profile 'codex' measured ABSENT for this extension (2026-09-21, unexplained) — refusing rather than installing silence" ;;
  *) fail "profile '$profile' never measured — supported: muse grok" ;;
esac

# Count, never test existence: grep -qFx is blind to duplicates and once
# printed "exactly once" over two lines. A count the message did not measure
# is the false-claim shape this lane refuses.
entry_count=$(grep -cFx -- "$entry" "$cfg" 2>/dev/null || true)
case "$entry_count" in
  ''|*[!0-9]*) fail "cannot count entries in $cfg" ;;
esac

# Probe listing via a throwaway rpc session. Output to a file first so the
# exit code below belongs to grep alone, never to a pipeline.
tmp_full=$(mktemp) || fail "mktemp failed"
tmp_noext=$(mktemp) || fail "mktemp failed"
trap 'rm -f "$tmp_full" "$tmp_noext"' EXIT INT TERM
printf '%s\n%s\n' '{"id":"p1","type":"negotiate_protocol","protocolVersion":2}' '{"id":"s1","type":"get_state"}' | omp --profile="$profile" --mode=rpc --max-time=25 > "$tmp_full" 2>/dev/null
printf '%s\n%s\n' '{"id":"p1","type":"negotiate_protocol","protocolVersion":2}' '{"id":"s1","type":"get_state"}' | omp --profile="$profile" --mode=rpc --max-time=25 --no-extensions > "$tmp_noext" 2>/dev/null
probe_present=0; noext_absent=1; nonce_absent=1
if grep -qF -- "$probe" "$tmp_full"; then probe_present=1; fi
if grep -qF -- "$probe" "$tmp_noext"; then noext_absent=0; fi
if grep -qF -- "$nonce" "$tmp_full"; then nonce_absent=0; fi

if [ "$mode" = "check" ]; then
  say "PLAN for profile '$profile' (nothing written):"
  if [ "$entry_count" -eq 0 ]; then say "  entry: MISSING (count 0) — install would append one line to .omp/config.yml";
  elif [ "$entry_count" -eq 1 ]; then say "  entry: present exactly once (count 1, no change)";
  else say "  entry: present $entry_count times — this installer never creates that state; refusing to bless it"; fi
  if [ "$probe_present" = "1" ]; then say "  probe: $probe PRESENT"; else say "  probe: $probe ABSENT"; fi
  if [ "$noext_absent" = "1" ]; then say "  negative arm (--no-extensions): absent, discriminates"; else say "  negative arm: PRESENT — oracle suspect, stop"; fi
  if [ "$nonce_absent" = "1" ]; then say "  nonce control: absent, matcher honest"; else say "  nonce control: PRESENT — matcher broken, stop"; fi
  say "  key: keyless returns NOT_RUN, never silently passes"
  # >1 exits non-zero by decision: --check certifies only states this installer
  # understands. An exit-0-with-report would ask strangers to interpret a state
  # we cannot explain; fail-closed puts human eyes on it instead.
  if [ "$entry_count" -eq 1 ] && [ "$probe_present" = "1" ] && [ "$noext_absent" = "1" ] && [ "$nonce_absent" = "1" ]; then
    say "GREEN: installed and listed (entry count 1)"; exit 0
  elif [ "$entry_count" -gt 1 ]; then
    say "RED: entry count $entry_count, installer creates at most one"; exit 1
  else
    say "YELLOW: not fully installed (see plan above)"; exit 1
  fi
fi

# Install mode. Append only when count is 0; never duplicate, never repair a
# hand-made duplicate (a checker that edits config is a different tool).
if [ "$entry_count" -eq 0 ]; then
  if [ ! -f "$cfg.bak" ]; then cp "$cfg" "$cfg.bak" || fail "cannot back up $cfg"; fi
  printf '%s\n' "$entry" >> "$cfg" || fail "cannot append entry"
  say "appended registration to .omp/config.yml (backup at .omp/config.yml.bak)"
elif [ "$entry_count" -eq 1 ]; then
  say "entry already present exactly once — no duplicate written"
else
  say "entry present $entry_count times (not created here) — leaving config untouched"
fi

sha=$(git -C "$repo" rev-parse --short HEAD 2>/dev/null || echo unknown)
{
  echo "jev_flag installed $(date -u +%FT%TZ) profile=$profile sha=$sha"
  echo "entry: $entry"
  echo "rollback: remove the entry line from .omp/config.yml (backup .omp/config.yml.bak)"
} > "$receipt" || fail "cannot write $receipt"

say "GREEN: installed for profile '$profile'"
say "  receipt  $receipt"
say
say "INSTALLED IS NOT USEFUL. L4 organic precision is unmeasured. Keyless returns NOT_RUN."
say "Verify listing any time: $0 --check $profile"
