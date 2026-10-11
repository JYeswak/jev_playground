#!/usr/bin/env bash
# publish-export.sh — build the jev_playground export: an allowlisted,
# content-scrubbed, single-commit orphan tree. Idempotent and re-runnable.
#
#   scripts/publish-export.sh              # build + scan ../jev_playground-export
#   scripts/publish-export.sh --check-only # scan the last-built export, no rebuild
#   scripts/publish-export.sh --scan DIR   # scan any tree, read-only (selftest, review)
#
# Contract (see docs/PUBLISH-SET.md for WHY):
#   - NEVER touches this repo's history. No checkout, no reset, no new commit
#     here. The export lives OUTSIDE this repo at ../jev_playground-export.
#   - FAIL-CLOSED. Any transform miss or unexplained key hit is an ERROR.
#   - The scan runs over the EXPORT's full history (one commit by
#     construction), never over the working tree.
#   - DIAGNOSTICS ARE COUNTS AND path:line ONLY. A hit's matched text is never printed,
#     in any mode: a hit may be a real credential, and a printed credential is rotated (jev-x5cy).
#
# Exit codes: 0 clean · 1 scan failure · 2 bad usage or missing tool · 4 scanner error
#   (a grep or git call failed for a reason other than "no match", or an exceptions row is
#   malformed: the scan did not complete, which is never a pass and never reads as a finding).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORT="$ROOT/../jev_playground-export"
BRANCH="jev-playground-export"
KEY_EXCEPTIONS="$ROOT/docs/publish-key-exceptions.txt"

need() { command -v "$1" >/dev/null 2>&1 || { echo "publish-export: required tool missing: $1" >&2; exit 2; }; }
need git; need sed; need grep; need tar; need awk; need shasum

# Scan shapes. KEYPAT is the contract in docs/PUBLISH-SET.md, unchanged. Every repeated class
# excludes what follows it, and grep -E is automaton-based, so each scan is linear in its input.
KEYPAT='AKIA[0-9A-Z]{16}|sk-live-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]{16,}|xox[baprs]-[A-Za-z0-9-]{8,}|Bearer ey[A-Za-z0-9._-]+|BEGIN [A-Z ]*PRIVATE KEY'
# A BLOB IS A LONG VALUE, NOT A LONG LINE. A 1,831-char single-line receipt whose only hit was the
# prose "thinkingSignature blobs public in history" failed an older, line-length scan on 2026-09-19;
# the assignment shape below is what is refused.
SIGPAT='"thinkingSignature"[[:space:]]*:[[:space:]]*"[A-Za-z0-9+/=_-]{100,}'
SIG_SED='s|("thinkingSignature"[[:space:]]*:[[:space:]]*")[A-Za-z0-9+/=_-]{100,}|\1THINKING_SIGNATURE_BLOB|g'
# AWS's published documentation example key, built from parts so this file does not itself match KEYPAT.
BENIGN_AWS="AKIA""IOSFODNN7""EXAMPLE"
# The redactor's own patterns live here (docs/PUBLISH-SET.md). An exact path, never a filename glob.
REDACTOR_PATH="demos/preaction-abstention/src/redact.mjs"
PRINT_CAP=25

trim() { local s=$1; s=${s#"${s%%[![:space:]]*}"}; s=${s%"${s##*[![:space:]]}"}; printf '%s' "$s"; }
count_lines() { printf '%s' "$1" | awk 'NF{n++} END{print n+0}'; }
emit_locs() { printf '%s\n' "$1" | awk -v cap="$PRINT_CAP" 'NF{n++; if(n<=cap) print "        " $0} END{if(n>cap) print "        ... and " n-cap " more"}'; }

# loc_hits <dir> <grep args...>: one "relpath:line" per matching line, never the line itself.
# grep exits 1 for "no match" (a clean result) and >=2 for an error (not a result): rc 0 = the
# scan ran, hits or none; rc 4 = it did not complete. A binary file reports "relpath:binary".
loc_hits() {
  local dir=${1%/} out rc; shift
  out=$(grep -r -n -s --exclude-dir=.git "$@" "$dir" \
        | awk -F: -v pre="$dir/" '
            { if ($0 ~ /^[^:]+:[0-9]+:/) { p=$1; l=$2 }
              else if ($0 ~ /^Binary file .* matches$/) { p=substr($0,13,length($0)-20); l="binary" }
              else { p="(unparsed grep output)"; l="0" }
              if (index(p,pre)==1) p=substr(p,length(pre)+1)
              print p ":" l }'
        printf 'RC=%s' "${PIPESTATUS[0]}")
  rc=${out##*RC=}; out=${out%RC=*}
  if [ "$rc" -ge 2 ]; then echo "SCAN ERROR  grep exited $rc while scanning (not a pass; fix the scanner or the tree)"; return 4; fi
  printf '%s' "$out"
}

# files_with <dir> <grep args...>: files containing a pattern, for a content transform. Same rc rule.
files_with() {
  local dir=$1 out rc; shift
  out=$(grep -r -l -s --exclude-dir=.git "$@" "$dir"; printf 'RC=%s' "$?")
  rc=${out##*RC=}; out=${out%RC=*}
  if [ "$rc" -ge 2 ]; then echo "publish-export: grep exited $rc while listing files for a content transform" >&2; exit 4; fi
  printf '%s' "$out"
}

# Exact exceptions for key-shaped lines proven synthetic one at a time (jev-x5cy ruling). One row each:
#   EXEMPT <export-relative path> | <sha256 of the whole line, no newline> | <key-pattern hits on it> | <reason>
# A row binds the path, the full line content and the hit count together, so it cannot cover another file,
# an edited line, or a second key added to the same line. No path-wide or pattern-wide rows.
EXC_KEYS=""; RED_ROWS=""
load_exceptions() {
  local raw f1 f2 f3 f4 kind n=0 name=${KEY_EXCEPTIONS#"$ROOT"/}
  EXC_KEYS=""; RED_ROWS=""
  [ -f "$KEY_EXCEPTIONS" ] || { echo "SCAN ERROR  exceptions file missing: $name"; return 4; }
  while IFS= read -r raw || [ -n "$raw" ]; do
    n=$((n+1))
    case $raw in ''|'#'*) continue ;; esac
    case $raw in 'EXEMPT '*) kind=EXEMPT ;; 'REDACT '*) kind=REDACT ;; *) echo "SCAN ERROR  $name:$n is not an EXEMPT or REDACT row"; return 4 ;; esac
    IFS='|' read -r f1 f2 f3 f4 <<<"${raw#"$kind" }"
    f1=$(trim "$f1"); f2=$(trim "$f2"); f3=$(trim "$f3"); f4=$(trim "${f4-}")
    if [ -z "$f1" ] || [[ $f1 == /* ]] || ! [[ $f2 =~ ^[0-9a-f]{64}$ ]] || ! [[ $f3 =~ ^[1-9][0-9]*$ ]] || [ -z "$f4" ]; then
      echo "SCAN ERROR  $name:$n is malformed (need: EXEMPT|REDACT path | 64-hex line sha256 | hit count | reason)"; return 4
    fi
    if [ "$kind" = REDACT ]; then RED_ROWS+="$f1|$f2|$f3"$'\n'; else EXC_KEYS+="$f1|$f2|$f3"$'\n'; fi
  done < "$KEY_EXCEPTIONS"
}

# redact_rows: for each REDACT row, find the exported line with that sha256 (after transforms 1-3) in that file and replace every
# key-shaped match on it with KEY_SHAPE_REDACTED. Path, whole-line hash and hit count must all match or the build stops (exit 4):
# a stale row is an error, never a silent skip. A REDACT row is NOT an exemption; the source is untouched.
redact_rows() {
  local row p sha cnt f tmp line got hits done_
  while IFS= read -r row; do
    [ -n "$row" ] || continue
    p=${row%%|*}; sha=${row#*|}; cnt=${sha#*|}; sha=${sha%%|*}; f="$EXPORT/$p"; done_=0
    [ -f "$f" ] || { echo "SCAN ERROR  REDACT row names a file absent from the export: $p"; return 4; }
    tmp="$f.redact.tmp"; : > "$tmp"
    while IFS= read -r line || [ -n "$line" ]; do
      got=$(printf '%s' "$line" | shasum -a 256 | cut -d' ' -f1)
      if [ "$got" = "$sha" ]; then
        hits=$(printf '%s' "$line" | grep -o -E -- "$KEYPAT" | awk 'END{print NR}')
        [ "$hits" = "$cnt" ] || { rm -f "$tmp"; echo "SCAN ERROR  REDACT row hit count mismatch for $p"; return 4; }
        printf '%s\n' "$(printf '%s' "$line" | sed -E "s/$KEYPAT/KEY_SHAPE_REDACTED/g")" >> "$tmp"; done_=1
      else printf '%s\n' "$line" >> "$tmp"; fi
    done < "$f"
    [ "$done_" = 1 ] || { rm -f "$tmp"; echo "SCAN ERROR  REDACT row matched no line in $p (edited or stale)"; return 4; }
    mv "$tmp" "$f"
  done <<<"$RED_ROWS"
}

# lit_check <dir> <label> <grep args...>: refuse any match; print the count and path:line only.
lit_check() {
  local dir=$1 label=$2 locs n; shift 2
  locs=$(loc_hits "$dir" "$@") || { printf '%s\n' "$locs"; return 4; }
  n=$(count_lines "$locs")
  [ "$n" -eq 0 ] && return 0
  echo "FAIL  $n $label line(s) in export (locations only; matched text is never printed):"
  emit_locs "$locs"
  return 1
}

# key_check <dir>: every key-shaped line must be explained: only the AWS documentation example, the
# redactor's own source, or an exact exception row. rc 0 clean, 1 unexplained hit(s), 4 scanner error.
key_check() {
  local dir=${1%/} locs loc rel ln line cnt rest sha rc total=0 aws=0 red=0 exc=0 bad="" nbad=0 used="" key stale="" nstale=0
  locs=$(loc_hits "$dir" -E "$KEYPAT") || { printf '%s\n' "$locs"; return 4; }
  while IFS= read -r loc; do
    [ -n "$loc" ] || continue
    total=$((total+1)); rel=${loc%:*}; ln=${loc##*:}
    if [ "$rel" = "$REDACTOR_PATH" ]; then red=$((red+1)); continue; fi
    if [ "$ln" = binary ] || [ "$ln" = 0 ]; then bad+="$loc"$'\n'; nbad=$((nbad+1)); continue; fi
    line=$(sed -n "${ln}p" < "$dir/$rel") || { echo "SCAN ERROR  cannot read a flagged file"; return 4; }
    cnt=$(printf '%s' "$line" | grep -o -E -- "$KEYPAT" | awk 'END{print NR}'; exit "${PIPESTATUS[1]}") && rc=0 || rc=$?
    if [ "$rc" -ge 2 ]; then echo "SCAN ERROR  grep exited $rc classifying a flagged line"; return 4; fi
    rest=$(printf '%s' "${line//"$BENIGN_AWS"/}" | grep -o -E -- "$KEYPAT" | awk 'END{print NR}'; exit "${PIPESTATUS[1]}") && rc=0 || rc=$?
    if [ "$rc" -ge 2 ]; then echo "SCAN ERROR  grep exited $rc classifying a flagged line"; return 4; fi
    if [ "$rest" -eq 0 ]; then aws=$((aws+1)); continue; fi
    sha=$(printf '%s' "$line" | shasum -a 256 | cut -d' ' -f1)
    key="$rel|$sha|$cnt"
    case $'\n'"$EXC_KEYS" in
      *$'\n'"$key"$'\n'*) exc=$((exc+1)); used+="$key"$'\n'; continue ;;
    esac
    bad+="$loc"$'\n'; nbad=$((nbad+1))
  done <<<"$locs"
  while IFS= read -r key; do
    [ -n "$key" ] || continue
    case $'\n'"$used" in *$'\n'"$key"$'\n'*) ;; *) nstale=$((nstale+1)); stale+="${key%%|*}"$'\n' ;; esac
  done <<<"$EXC_KEYS"
  echo "   key patterns: $total flagged line(s): $aws explained by the AWS documentation example, $red in the documented redactor source, $exc by exact exception row(s), $nbad unexplained"
  [ "$nstale" -eq 0 ] || { echo "   NOTE  $nstale exception row(s) matched no hit (edited or already fixed); paths:"; emit_locs "$stale"; }
  [ "$nbad" -eq 0 ] && return 0
  echo "FAIL  $nbad unexplained key-pattern line(s) in export (locations only; matched text is never printed):"
  emit_locs "$bad"
  return 1
}

scan_export() { # scan_export <dir> ; the acceptance probe. rc 0 clean, 1 findings, 4 scanner error
  local dir=${1%/} bad=0 rc locs n gh out
  load_exceptions || return 4
  lit_check "$dir" "/Users/josh occurrence" -F -e "/Users/josh" && rc=0 || rc=$?
  [ "$rc" -eq 4 ] && return 4; [ "$rc" -eq 0 ] || bad=1
  lit_check "$dir" "encrypted_content occurrence" -F -e "encrypted_content" && rc=0 || rc=$?
  [ "$rc" -eq 4 ] && return 4; [ "$rc" -eq 0 ] || bad=1
  key_check "$dir" && rc=0 || rc=$?
  [ "$rc" -eq 4 ] && return 4; [ "$rc" -eq 0 ] || bad=1
  # thinkingSignature prose may remain; blobs may not.
  locs=$(loc_hits "$dir" -E "$SIGPAT") || { printf '%s\n' "$locs"; return 4; }
  n=$(count_lines "$locs")
  if [ "$n" -gt 0 ]; then
    echo "FAIL  $n blob-shaped thinkingSignature line(s) in $(printf '%s\n' "$locs" | awk -F: 'NF{print $1}' | sort -u | awk 'END{print NR}') file(s) (locations only):"
    emit_locs "$locs"; bad=1
  fi
  # History leg: the committed content itself (tip == history by construction).
  if [ -d "$dir/.git" ]; then
    out=$(GIT_OPTIONAL_LOCKS=0 git -C "$dir" grep -c -F -e "/Users/josh" -e "encrypted_content" HEAD -- . 2>/dev/null \
          | awk -F: '{s+=$NF} END {print s+0}'; printf 'RC=%s' "${PIPESTATUS[0]}")
    rc=${out##*RC=}; gh=$(trim "${out%RC=*}")
    if [ "$rc" -ge 2 ]; then echo "SCAN ERROR  git grep exited $rc over the export history (not a pass)"; return 4; fi
    [ "$gh" -eq 0 ] || { echo "FAIL  $gh home/blob line(s) in export HISTORY"; bad=1; }
  fi
  return $bad
}

# scan_or_exit <dir> <label>: one scan, its report printed once; returns only on a pass.
scan_or_exit() {
  local out rc=0
  out=$(scan_export "$1") || rc=$?
  printf '%s\n' "$out"
  case $rc in
    0) return 0 ;;
    4) echo "EXPORT SCAN ERROR $2: the scanner did not complete (not a pass and not a content finding)"; exit 4 ;;
    *) echo "EXPORT SCAN FAIL $2"; exit 1 ;;
  esac
}

if [ "${1-}" = "--check-only" ]; then
  [ -d "$EXPORT/.git" ] || { echo "ERROR no export at $EXPORT — build first" >&2; exit 2; }
  scan_or_exit "$EXPORT" ""
  echo "EXPORT SCAN PASS  $EXPORT"
  exit 0
fi
if [ "${1-}" = "--scan" ]; then
  [ -n "${2-}" ] && [ -d "${2-}" ] && [ -z "${3-}" ] || { echo "usage: $0 --scan DIR" >&2; exit 2; }
  scan_or_exit "$2" "($2)"
  echo "EXPORT SCAN PASS  $2"
  exit 0
fi
[ -z "${1-}" ] || { echo "usage: $0 [--check-only | --scan DIR]" >&2; exit 2; }

# Rebuild from scratch: the export is derived, never hand-edited.
rm -rf "$EXPORT"
mkdir -p "$EXPORT"

# Allowlist: tracked tip minus the internal-operational paths (PUBLISH-SET.md).
GIT_OPTIONAL_LOCKS=0 git -C "$ROOT" archive HEAD \
  | tar -x -C "$EXPORT" \
    --exclude=".beads" \
    --exclude="docs/demos/duel-1/dispatch" \
    --exclude="docs/demos/duel-2/dispatch" \
    --exclude="docs/demos/dispatch"

# Mechanical content transforms (documented in PUBLISH-SET.md). Each lists its files first, so a grep
# error stops the build (exit 4) instead of passing as "no files"; no match is a clean, empty list.
list=$(files_with "$EXPORT" -F -e "/Users/josh")
while IFS= read -r f; do
  [ -n "$f" ] || continue
  sed -i '' 's|/Users/josh|~|g' "$f"
done <<<"$list"
list=$(files_with "$EXPORT" -F -e "encrypted_content")
while IFS= read -r f; do
  [ -n "$f" ] || continue
  sed -i '' 's|encrypted_content|ENCRYPTED_BLOB|g' "$f"
done <<<"$list"
# jev-x5cy: an opaque thinkingSignature value never leaves the private repo; the key and the prose around
# it stay. The sources are untouched (original evidence is preserved), only the export copy is redacted.
list=$(files_with "$EXPORT" -E "$SIGPAT")
while IFS= read -r f; do
  [ -n "$f" ] || continue
  sed -i '' -E "$SIG_SED" "$f"
done <<<"$list"
# REDACT rows (docs/publish-key-exceptions.txt): individual uncertain key-shaped lines, redacted the same way.
load_exceptions || { echo "EXPORT SCAN ERROR: exceptions unreadable"; exit 4; }
redact_rows || exit 4

# The lane's absolute core.hooksPath would enforce lane commit-subject discipline
# inside the export too; the export is a build artifact, not the lane, so it opts
# out locally (this config lives in the export's own .git/, never here).
# Pre-commit worktree scan: fail before minting history, not after.
scan_or_exit "$EXPORT" "(worktree)"
# One commit on an orphan branch: tip == history by construction.
# jev-90id: the export is its own repo; a caller's exported GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE must not steer it.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG
git -C "$EXPORT" init -q -b "$BRANCH"
git -C "$EXPORT" config core.hooksPath ""
git -C "$EXPORT" add -A
git -C "$EXPORT" -c user.name="jev-export" -c user.email="jev-export@local" \
  commit -qm "jev_playground export $(date -u +%Y-%m-%d): allowlisted tip, scrubbed, worktree-scanned [test]"
echo "   export history: $(git -C "$EXPORT" rev-list --count HEAD) commit(s)"

scan_or_exit "$EXPORT" "(history)"
echo "EXPORT SCAN PASS  $EXPORT  ($(git -C "$EXPORT" ls-files | wc -l | tr -d ' ') files, 1 commit)"
