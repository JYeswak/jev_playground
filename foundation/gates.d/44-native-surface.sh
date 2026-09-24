#!/usr/bin/env bash
# 44-native-surface: no Jev-calling code ships that bypasses the vendor SDK
# without a recorded exemption, and the four native pins stay current.
#
# NUMBERING NOTE: P1 ordered "40-native-surface.sh", but 40-omp-compact-replay.sh
# already holds 40. This is 44. Documented here so nobody "fixes" it into a collision.
#
# RULE 14 (Joshua, 2026-09-21): nothing built for Jev passes unless it uses native
# vendor surfaces. Consumer: foundation/gates.sh (Definition of Done runs it).
#
# DETECTION (two halves, different tools on purpose):
#   structural: ast-grep finds fetch(/axios POST call sites in OUR ts/js/mjs; a file
#     counts only if it also names the endpoint (literal or constant). A comment
#     mentioning the endpoint host with no call is NOT a violation.
#   literal: rg sweeps OUR sh for the endpoint (repro/canary scripts use curl).
# Vendored clones, upstream/, docs-mirror/, node_modules, .venv, .git and the big
# third-party work/ trees are out of scope — other people's trees are findings,
# not violations. This stage file and its exemptions ledger are excluded from
# their own sweep (a detector that fires on its own plant content is unproven).
#
# EXEMPTIONS live in 44-native-surface.exemptions as "EXEMPT <path> | <reason>".
# A path with an empty reason is refused by the parser. Every current violator
# is listed: an unlisted violator is RED, not a TODO.
#
# FRESHNESS: the four native repos must read behind=0 in upstream/MANIFEST.tsv
# (first match wins; surrounding whitespace stripped).
#
# Exit: 0 green · 1 RED · 3 instrument error (ast-grep/rg missing, ledger missing) · 8 SKIP, named
# missing scanner, only under gates.sh --portable.
# --selftest plants a direct-POST .ts file with no exemption, requires RED that
# NAMES THE PLANT, removes it, requires GREEN.
set -uo pipefail
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
root="$here/.."
stage="$0"
stage_abs=$(CDPATH='' cd -- "$(dirname -- "$stage")" && pwd -P)/$(basename -- "$stage")
EXEMPTIONS="$here/gates.d/44-native-surface.exemptions"
MANIFEST="$root/upstream/MANIFEST.tsv"
NATIVE_REPOS="typesafe-sdk-python typesafe-sdk-js system-one-adapter-python skills"

# The endpoint host is assembled at runtime so this source never contains the
# full literal (AGENTS.md precedent: a detector that fires on its own source
# is unproven). Fragments below match nothing on their own.
_EP_A="https://api."
_EP_B="typesafe.ai"
EP_FULL="${_EP_A}${_EP_B}"
EP_PAT="api\\.typesafe\\.ai"

# PORTABLE (jev-fmy): under `gates.sh --portable` a missing scanner is a named SKIP, exit 8, and
# it comes BEFORE the selftest branch so the stage-80 selftest skips too instead of reading the
# skip as "RED, but not on the plant". Default mode is untouched: the checks below exit 3.
if [ -n "${JEV_GATES_PORTABLE:-}" ]; then
    command -v ast-grep >/dev/null 2>&1 || { echo "SKIP (missing prerequisite: ast-grep, install: brew install ast-grep, or npm install -g @ast-grep/cli and link its sg as ast-grep)"; exit 8; }
    command -v rg >/dev/null 2>&1 || { echo "SKIP (missing prerequisite: rg, install: brew install ripgrep)"; exit 8; }
fi

if [ "${1:-}" = "--selftest" ]; then
    plant="$root/work/.selftest-plant-native.ts"
    printf '%s\n' 'export async function plant() {' "  return fetch(\"${EP_FULL}/v1/systemone\", { method: \"POST\", body: \"{}\" });" '}' >"$plant"
    hit=$("$stage" 2>&1) && { echo "SELFTEST_FAIL: planted direct POST accepted"; rm -f "$plant"; exit 1; }
    case "$hit" in
        *".selftest-plant-native.ts"*) ;;
        *) echo "SELFTEST_FAIL: RED fired, but not on the plant:"; printf '%s\n' "$hit" | head -3; rm -f "$plant"; exit 1 ;;
    esac
    rm -f "$plant"
    hit2=$("$stage" 2>&1) || { echo "SELFTEST_FAIL: still RED after plant removal:"; printf '%s\n' "$hit2" | head -3; exit 1; }
    echo "SELFTEST_PASS: planted direct POST refused, clean tree green"
    exit 0
fi

command -v ast-grep >/dev/null 2>&1 || { echo "RED: ast-grep not on PATH (instrument error)"; exit 3; }
command -v rg >/dev/null 2>&1 || { echo "RED: rg not on PATH (instrument error)"; exit 3; }
[ -f "$EXEMPTIONS" ] || { echo "RED: exemptions ledger missing: $EXEMPTIONS"; exit 3; }

# Parser: every non-blank non-comment line must be "EXEMPT <path> | <nonempty reason>".
while IFS= read -r line; do
    case "$line" in ''|'#'*) continue ;; esac
    case "$line" in
        "EXEMPT "*"|"*) ;;
        *) echo "RED: malformed exemption line (needs 'EXEMPT <path> | <reason>'): $line" | cut -c1-160; exit 1 ;;
    esac
    reason=${line##*|} ; reason=${reason#"${reason%%[![:space:]]*}"}
    [ -n "$reason" ] || { echo "RED: exemption with empty reason: $line" | cut -c1-160; exit 1; }
done < "$EXEMPTIONS"

is_exempt() { grep -qF "EXEMPT $1 |" "$EXEMPTIONS" 2>/dev/null; }
is_self() { [ "$1" = "$stage_abs" ] || [ "$1" = "$EXEMPTIONS" ]; }
fails=0

SCOPE="$root/work $root/.omp $root/probes $root/scripts $root/demos $root/foundation $root/compaction"
# shellcheck disable=SC2086
CALL_FILES=$(ast-grep run --lang ts --pattern 'fetch($$$ARGS)' $SCOPE --json 2>/dev/null | grep -o '"file": "[^"]*"' | sed 's/"file": "//;s/"//' | sort -u)
# shellcheck disable=SC2086
AXIOS_FILES=$(ast-grep run --lang ts --pattern 'axios.$$$M($$$ARGS)' $SCOPE --json 2>/dev/null | grep -o '"file": "[^"]*"' | sed 's/"file": "//;s/"//' | sort -u)

for hitfile in $CALL_FILES $AXIOS_FILES; do
    [ -n "$hitfile" ] || continue
    if is_self "$hitfile"; then continue; fi
    case "$hitfile" in
        */node_modules/*|*/.venv/*|*/upstream/*|*/docs-mirror/*|"$root"/skillranker/*|"$root"/jev-ultrafast/*|"$root"/fast-jev-compaction/*|"$root"/jev-review/*|"$root"/jev-mcp/*|"$root"/jev-spam-eval/*|"$root"/jev-rerank-bench/*|"$root"/jev-phishing-bench/*|"$root"/jev-router/*|"$root"/jev-benchmark/*|"$root"/s1-rs/*|"$root"/foreman/*|"$root"/bicameral/*|"$root"/ensemble/*|"$root"/pi-subagents/*|"$root"/commit-miner/*|"$root"/jev-align/*|"$root"/jev-agent-failure-benchmark/*|"$root"/jev-sec-bench/*|"$root"/jev-codex-router/*|"$root"/awesome-jev*|"$root"/awesome-typesafe/*|"$root"/typesafe-ai-benchmark/*) continue ;;
    esac
    rel=${hitfile#"$root"/}
    if ! rg -q -e "$EP_PAT" -e "SYSTEMONE_ENDPOINT" "$hitfile" 2>/dev/null; then continue; fi
    if is_exempt "$rel"; then continue; fi
    echo "RED: direct Jev call with no recorded exemption: $rel"
    fails=1
done

# shellcheck disable=SC2086
SH_FILES=$(rg -l --glob '*.sh' -e "$EP_PAT" $root/work $root/scripts $root/probes $root/demos $root/foundation $root/compaction 2>/dev/null | grep -v node_modules | sort -u)
for hitfile in $SH_FILES; do
    [ -n "$hitfile" ] || continue
    if is_self "$hitfile"; then continue; fi
    rel=${hitfile#"$root"/}
    if is_exempt "$rel"; then continue; fi
    echo "RED: endpoint literal in OUR sh with no recorded exemption: $rel"
    fails=1
done

if [ ! -f "$MANIFEST" ]; then echo "RED: $MANIFEST missing"; exit 1; fi
for repo in $NATIVE_REPOS; do
    row=$(awk -F'\t' -v r="$repo" '$1==r {print; exit}' "$MANIFEST")
    behind=$(printf '%s' "$row" | awk -F'\t' '{print $5}' | tr -d '[:space:]')
    if [ "$behind" != "0" ]; then echo "RED: native pin stale: $repo behind=$behind"; fails=1; fi
done

if [ "$fails" = "1" ]; then exit 1; fi
echo "PASS: no unexempted direct Jev calls; native pins current"
