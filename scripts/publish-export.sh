#!/usr/bin/env bash
# publish-export.sh — build the jev_playground export: an allowlisted,
# content-scrubbed, single-commit orphan tree. Idempotent and re-runnable.
#
#   scripts/publish-export.sh              # build + scan ../jev_playground-export
#   scripts/publish-export.sh --check-only # scan the last-built export, no rebuild
#
# Contract (see docs/PUBLISH-SET.md for WHY):
#   - NEVER touches this repo's history. No checkout, no reset, no new commit
#     here. The export lives OUTSIDE this repo at ../jev_playground-export.
#   - FAIL-CLOSED. Any transform miss or unexplained key hit is an ERROR.
#   - The scan runs over the EXPORT's full history (one commit by
#     construction), never over the working tree.
#
# Exit codes: 0 clean · 1 scan failure · 2 bad usage or missing tool.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORT="$ROOT/../jev_playground-export"
BRANCH="jev-playground-export"

need() { command -v "$1" >/dev/null 2>&1 || { echo "publish-export: required tool missing: $1" >&2; exit 2; }; }
need git; need sed; need grep; need tar

scan_export() { # scan_export <dir> ; the acceptance probe
  local dir="$1" bad=0 hits
  hits=$(grep -r -c "/Users/josh" "$dir" --exclude-dir=.git 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')
  [ "$hits" -eq 0 ] || { echo "FAIL  $hits /Users/josh occurrences in export"; bad=1; }
  hits=$(grep -r -c "encrypted_content" "$dir" --exclude-dir=.git 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')
  [ "$hits" -eq 0 ] || { echo "FAIL  $hits encrypted_content occurrences in export"; bad=1; }
  # Key patterns: every hit must be on the known-benign list, else fail.
  # Shapes, not names: bare words like `AKIA` or "ghp-like" (demo prose about the
  # credential-detection demo) must not trip the scan; real key material does.
  local kh; kh=$(grep -r -n -E "AKIA[0-9A-Z]{16}|sk-live-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]{16,}|xox[baprs]-[A-Za-z0-9-]{8,}|Bearer ey[A-Za-z0-9._-]+|BEGIN [A-Z ]*PRIVATE KEY" "$dir" --exclude-dir=.git 2>/dev/null || true)
  if [ -n "$kh" ]; then
    local unexplained; unexplained=$(printf '%s\n' "$kh" | grep -v "AKIAIOSFODNN7EXAMPLE" | grep -v "redact.mjs" || true)
    if [ -n "$unexplained" ]; then
      echo "FAIL  unexplained key-pattern hits in export:"; printf '%s\n' "$unexplained"; bad=1
    else
      echo "   key patterns: $(printf '%s\n' "$kh" | wc -l | tr -d ' ') hits, all known-benign (EXAMPLE key / redactor patterns)"
    fi
  else
    echo "   key patterns: 0 hits"
  fi
  # thinkingSignature prose may remain; blobs may not. A blob is a long line.
  # A BLOB IS A LONG VALUE, NOT A LONG LINE. The original heuristic flagged any line over 300
  # chars containing the word, which false-positives on MINIFIED JSON: a 1,831-char single-line
  # receipt whose only hit was the prose "thinkingSignature blobs public in history" failed the
  # scan on 2026-09-19 and would have blocked a clean publish. Match the assignment shape instead.
  local longsig; longsig=$(grep -r -n -E '"thinkingSignature"[[:space:]]*:[[:space:]]*"[A-Za-z0-9+/=_-]{100,}' "$dir" --exclude-dir=.git 2>/dev/null || true)
  [ -z "$longsig" ] || { echo "FAIL  long thinkingSignature lines (blob-shaped):"; printf '%s\n' "$longsig"; bad=1; }
  # History leg: the committed content itself (tip == history by construction).
  if [ -d "$dir/.git" ]; then
    local gh; gh=$(git -C "$dir" grep -c "/Users/josh\|encrypted_content" HEAD -- . 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')
    [ "$gh" -eq 0 ] || { echo "FAIL  $gh home/blob hits in export HISTORY"; bad=1; }
  fi
  return $bad
}

if [ "${1-}" = "--check-only" ]; then
  [ -d "$EXPORT/.git" ] || { echo "ERROR no export at $EXPORT — build first" >&2; exit 2; }
  if scan_export "$EXPORT"; then echo "EXPORT SCAN PASS  $EXPORT"; else echo "EXPORT SCAN FAIL"; exit 1; fi
  exit 0
fi
[ -z "${1-}" ] || { echo "usage: $0 [--check-only]" >&2; exit 2; }

# Rebuild from scratch: the export is derived, never hand-edited.
rm -rf "$EXPORT"
mkdir -p "$EXPORT"

# Allowlist: tracked tip minus the internal-operational paths (PUBLISH-SET.md).
git -C "$ROOT" archive HEAD \
  | tar -x -C "$EXPORT" \
    --exclude=".beads" \
    --exclude="docs/demos/duel-1/dispatch" \
    --exclude="docs/demos/duel-2/dispatch" \
    --exclude="docs/demos/dispatch"

# Mechanical content transforms (documented in PUBLISH-SET.md).
grep -r -l "/Users/josh" "$EXPORT" 2>/dev/null | while IFS= read -r f; do
  sed -i '' 's|/Users/josh|~|g' "$f"
done
grep -r -l "encrypted_content" "$EXPORT" 2>/dev/null | while IFS= read -r f; do
  sed -i '' 's|encrypted_content|ENCRYPTED_BLOB|g' "$f"
done

# The lane's absolute core.hooksPath would enforce lane commit-subject discipline
# inside the export too; the export is a build artifact, not the lane, so it opts
# out locally (this config lives in the export's own .git/, never here).
# Pre-commit worktree scan: fail before minting history, not after.
scan_export "$EXPORT" >/dev/null || { echo "EXPORT SCAN FAIL (worktree)"; scan_export "$EXPORT"; exit 1; }
# One commit on an orphan branch: tip == history by construction.
git -C "$EXPORT" init -q -b "$BRANCH"
git -C "$EXPORT" config core.hooksPath ""
git -C "$EXPORT" add -A
git -C "$EXPORT" -c user.name="jev-export" -c user.email="jev-export@local" \
  commit -qm "jev_playground export $(date -u +%Y-%m-%d): allowlisted tip, scrubbed, worktree-scanned [test]"
echo "   export history: $(git -C "$EXPORT" rev-list --count HEAD) commit(s)"

if scan_export "$EXPORT"; then
  echo "EXPORT SCAN PASS  $EXPORT  ($(git -C "$EXPORT" ls-files | wc -l | tr -d ' ') files, 1 commit)"
else
  echo "EXPORT SCAN FAIL"; exit 1
fi
