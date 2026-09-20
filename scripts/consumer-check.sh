#!/usr/bin/env bash
# consumer-check — WHAT READS THIS AND WHERE IS THE CALL. One command, one screen.
#
# WHY (docs/NEEDS.md need 2, inverts R63 + R10): answering "does anything
# read this" took three manual probes and one wrong turn through 2,374
# false hits. Before any instrument ships, run this. REFUSES ON ZERO.
#
# The whole value is invocation-vs-mention. A wide grep counted 33
# "callers" that were captured HTTP-400 payloads — the word inside logged
# LLM requests. So: executable surfaces count, everything else is
# classified, never counted. Transcripts, session JSONL, logs and plugin
# templates are EXCLUDED outright; docs/tests are MENTIONS, not consumers.
#
# Usage: scripts/consumer-check.sh "<name>" [--repo DIR] [--extra DIR]...
#   exit 0  consumers found (COMMAND and/or PATHREF listed)
#   exit 1  ZERO CONSUMERS (refusal; surfaces searched are named)
#   exit 2  usage error
set -uo pipefail
Q="${1:-}"; shift 2>/dev/null || true
[ -n "$Q" ] || { echo "usage: $0 \"<name>\" [--repo DIR] [--extra DIR]..." >&2; exit 2; }
REPO="$PWD"
EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --extra) EXTRA+=("$2"); shift 2 ;;
    *) echo "unknown flag $1" >&2; exit 2 ;;
  esac
done
F="${Q%% *}"; SUB="${Q#* }"; [ "$SUB" = "$Q" ] && SUB=""

have() { command -v "$1" >/dev/null 2>&1; }
RG=""; have rg && RG="rg" ; [ -n "$RG" ] || { echo "REFUSE_NO_RG: install ripgrep" >&2; exit 2; }

# Executable surfaces: repo seams + live global extensions + local bins.
ROOTS=()
for d in "$REPO/.omp/extensions" "$REPO/.omp/hooks" "$REPO/.omp/tools" \
         "$REPO/scripts" "$REPO/bin" "$REPO/githooks" \
         "$HOME/.omp/omp-extensions" "$HOME/.local/bin"; do
  [ -d "$d" ] && ROOTS+=("$d")
done
for d in "${EXTRA[@]}"; do [ -d "$d" ] && ROOTS+=("$d"); done
[ "${#ROOTS[@]}" -gt 0 ] || { echo "REFUSE_NO_SURFACES" >&2; exit 2; }

# Excluded everywhere, always: transcripts/sessions/logs, vendored noise,
# fixtures, plugin templates. Tests and docs are MENTION tier, never consumers.
XCL=(--glob '!*.jsonl' --glob '!*.log' --glob '!node_modules' --glob '!.git'
     --glob '!vendor' --glob '!*.min.*' --glob '!*fixtures*' --glob '!*templates*')
# Command position: line start (after prompt/keyword) or shell separator.
# PATHREF: quoted path to the binary (bridges that spawn it, e.g. DCG_PATH).
QPAT=$(printf '%s' "$Q" | sed 's/ /\\s+/g')
cmd_hits=$($RG -n --no-messages "${XCL[@]}" --glob '!*.test.*' --glob '!*.md' \
  "(^${QPAT}|^[^#\\n]*[;&|]\\s*${QPAT}|\\$\\(\\s*${QPAT})([\\s\\-]|$)" "${ROOTS[@]}" 2>/dev/null || true)
path_hits=""
if [ -z "$SUB" ]; then
  path_hits=$($RG -n --no-messages "${XCL[@]}" --glob '!*.test.*' --glob '!*.md' \
    "/[\\w./-]*bin/${F}([\"']|$)" "${ROOTS[@]}" 2>/dev/null || true)
fi
 argv_hits=""
if [ -n "$SUB" ]; then
  # argv-array form: the binary (CONST_BIN, /bin/<name>) and the subcommand
  # (quoted literal in an args array) never share a line, so command-position
  # grep cannot see them. A file carrying BOTH on code lines (full-line
  # comments stripped) is a consumer. Missing this produced a false ZERO on
  # 'ee orient' (EE_BIN + COMMAND_ARGS spread) — the dangerous direction:
  # a false zero retires live wiring. Over-count risk (SUB literal in a
  # comment-adjacent code line) is the safe direction; lines are shown.
  FBIN="$(printf '%s' "$F" | tr '[:lower:]' '[:upper:]')_BIN"
  while read -r f; do
    ev1=$($RG --with-filename -n --no-messages -e "${FBIN}" -e "/[\\w./-]*bin/${F}([\"']|$)" "$f" 2>/dev/null | grep -vE ':[0-9]+[:-][[:space:]]*(//|#|\*|<!--)' | head -3 || true)
    [ -z "$ev1" ] && continue
    ev2=$($RG --with-filename -n --no-messages -e "\"${SUB}\"" -e "'${SUB}'" "$f" 2>/dev/null | grep -vE ':[0-9]+[:-][[:space:]]*(//|#|\*|<!--)' | head -3 || true)
    [ -z "$ev2" ] && continue
    argv_hits=$(printf '%s\n%s\n%s' "$argv_hits" "$ev1" "$ev2")
  done <<EOF
$($RG -l --no-messages "${XCL[@]}" --glob '!*.test.*' --glob '!*.md' -e "\"${SUB}\"" -e "'${SUB}'" "${ROOTS[@]}" 2>/dev/null | grep -vE '(consumer-check|selftest-consumer-check)\.' || true)
EOF
fi
consumers=$(printf '%s\n%s\n%s' "$cmd_hits" "$path_hits" "$argv_hits" | grep -v '^$' | sort -u)

# Mentions (classified, never counted): docs + tests touching the query.
mentions=$($RG -l --no-messages --glob '*.md' --glob '*.test.*' \
  "$Q" "$REPO" 2>/dev/null | head -5 || true)

echo "consumer-check: '$Q'"
if [ -n "$consumers" ]; then
  echo "CONSUMERS (invocation, not mention):"
  printf '%s\n' "$consumers" | head -20
  [ -n "$mentions" ] && { echo "mentions (not consumers):"; printf '%s\n' "$mentions"; }
  exit 0
fi
echo "ZERO CONSUMERS — nothing invokes '$Q' on the surfaces above."
if [ -n "$SUB" ]; then
  # Sibling subcommands of the same binary: shell form (`ee orient`),
  # path-const form (`EE_BIN, "journal"`), or array form
  # (`COMMAND_ARGS = ["orient", ...]`). Refusal case only.
  # Separate rg calls: groups renumber across -e alternations, so one -e
  # per call keeps $1 bound. -U only where the match spans lines.
  rel=$($RG -l --no-messages "${XCL[@]}" --glob '!*.test.*' --glob '!*.md' \
    -e "(^|[;&|][[:space:]]*)${F}([[:space:]\\-]|$)" \
    -e "/[\\w./-]*bin/${F}([\"']|$)" "${ROOTS[@]}" 2>/dev/null | while read -r f; do
    sub=$({
      $RG -o --no-messages --no-filename -N -e "(^|[^a-zA-Z0-9_-])${F}[[:space:]]+([a-z][\\w-]*)" -r '$2' "$f" 2>/dev/null
      $RG -o --no-messages --no-filename -N -e "COMMAND_ARGS\\s*=\\s*\\[[^]]*?[\"']([a-z][\\w-]*)" -r '$1' "$f" 2>/dev/null
      $RG -U -o --no-messages --no-filename -N -e "EE_BIN\\s*,\\s*[\"']([a-z][\\w-]*)" -r '$1' "$f" 2>/dev/null
    } | sort -u | tr '\n' ' ')
    [ -n "$sub" ] && echo "$f :: $sub"
  done || true)
  if [ -n "$rel" ]; then
    echo "related live callers (same binary, sibling subcommand — read to confirm):"
    printf '%s\n' "$rel" | head -10
  else
    echo "no related callers of '$F' found either."
  fi
fi
[ -n "$mentions" ] && { echo "mentions (not consumers):"; printf '%s\n' "$mentions"; }
exit 1
