#!/usr/bin/env bash
# 30-no-secrets: no secret VALUES in any file this repo can commit. Names (TYPESAFE_API_KEY)
# are fine and expected; values are not. Flags `apikey_` tokens and TYPESAFE_API_KEY
# assignments of a 16+ character value. The live key file (/tmp/.tskey) is outside the tree
# on purpose.
#
# SCOPE: tracked files plus untracked files that are not ignored (`git grep --untracked`, the
# set `git ls-files -co --exclude-standard` lists), from the repo root, minus *.log,
# node_modules/ and .venv/. Ignored trees (the vendored clones, the docs-mirror bytes) are not
# scanned because they cannot be committed here. Until 2026-09-24 (jev-09qj) this stage
# grepped only foundation/ while its PASS line said "workspace tree", so a key planted under
# work/ passed.
#
# A `$` followed by a name character or `{` right after the `=`/`:` is a variable REFERENCE
# (a recorded command passing "$TYPESAFE_API_KEY" through), not a value, and does not match.
# `$'...'` still matches: that is a literal.
#
# ALLOWLIST: 30-no-secrets.exemptions, one "EXEMPT <path> | <token> | <reason>" per hit, where
# <token> is the exact text `git grep -o` matched. An entry binds path AND token: the same token
# at another path, or another value in the same file, is RED. The exemptions file's own copies
# of listed tokens are exempt; anything else in it is scanned like any other file.
#
# RED names path:line and never prints the value. To see a value locally, run from the root:
#   git grep --untracked -n -o -E -e '<P_APIKEY>' -e '<P_ASSIGN>' -- <path>
#
# --selftest plants files under work/, docs/ and foundation/ and checks one scan: every planted
# key is named and its value is not printed; a $-reference is quiet while a literal in the same
# shape is named; an allowlisted token is quiet in its own file, while a key in that file and
# the same token at another path are named. Then a copy run outside any git work tree must exit
# 3, not PASS. Plants are removed on exit, pass or fail.
#
# Exit: 0 PASS, 1 RED (a hit, or a malformed exemption), 3 no verdict (git failed or the scan
# set is empty).
set -uo pipefail
# `pipefail` (pane 3's hardening plan, db97021) is behaviour-neutral here ONLY because this file
# does not `set -e`. The scan pipeline's status is read explicitly below: git grep exits 0 on a
# hit, 1 on none, anything else is an instrument error. IF `set -e` IS EVER ADDED, RE-AUDIT.
here=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
root=$(CDPATH='' cd -- "$here/.." && pwd -P)
EXEMPTIONS="$here/gates.d/30-no-secrets.exemptions"
P_APIKEY='apikey_[A-Za-z0-9_.-]{20,}'
P_ASSIGN='TYPESAFE_API_KEY.{0,3}[=:]([^$]|\$[^A-Za-z0-9_{]){0,3}["'\'']?[A-Za-z0-9_.\-]{16,}'
EXCLUDE=(':(exclude,glob)**/*.log' ':(exclude,glob)**/node_modules/**' ':(exclude,glob)**/.venv/**')

if [ "${1:-}" = "--selftest" ]; then
    # Keys are assembled at runtime so this file never holds a matchable literal: a selftest
    # that trips on its own source certifies nothing.
    key=$(printf '%s%s' "apikey_" "ffff0000111122223333444455556666777788889999aaaa")
    lit=$(printf '%s' "0f1e2d3c4b5a69788796a5b4c3d2e1f0")
    held=$(printf '%s="%s"' "TYPESAFE_API_KEY" "selftest-placeholder-not-a-key")
    plants=()
    tmpd=""
    cleanup() {
        if [ "${#plants[@]}" -gt 0 ]; then rm -f "${plants[@]}"; fi
        if [ -n "$tmpd" ]; then
            rm -f "$tmpd/foundation/gates.d/30-no-secrets.sh" "$tmpd/foundation/gates.d/30-no-secrets.exemptions"
            rmdir "$tmpd/foundation/gates.d" "$tmpd/foundation" "$tmpd" 2>/dev/null
        fi
    }
    trap cleanup EXIT
    plant() { # plant <repo-relative path> <line>...
        local p="$root/$1"; shift
        if [ -e "$p" ]; then echo "SELFTEST_FAIL: plant path already exists, not overwriting: $p"; exit 1; fi
        plants+=("$p")
        printf '%s\n' "$@" >"$p" || { echo "SELFTEST_FAIL: could not write plant $p"; exit 1; }
    }
    plant work/.selftest-30-scope.tmp "x = \"$key\""
    plant docs/.selftest-30-scope.tmp "x = \"$key\""
    plant foundation/.selftest-30-scope.tmp "x = \"$key\""
    plant work/.selftest-30-dollar.tmp \
        "$(printf '{"command": "%s=\\"$%s\\" node run.mjs"}' TYPESAFE_API_KEY TYPESAFE_API_KEY)" \
        "$(printf 'export %s="${%s}"' TYPESAFE_API_KEY TYPESAFE_API_KEY)"
    plant work/.selftest-30-literal.tmp \
        "$(printf '{"command": "%s=\\"%s\\" node run.mjs"}' TYPESAFE_API_KEY "$lit")" \
        "$(printf "export %s=\$'%s'" TYPESAFE_API_KEY "$lit")"
    plant work/.selftest-30-allow.tmp "$held" "y = \"$key\""
    plant work/.selftest-30-allow-elsewhere.tmp "$held"
    out=$(bash "$0" 2>&1)
    code=$?
    fails=0
    pass() { echo "SELFTEST_PASS: $1"; }
    fail() { echo "SELFTEST_FAIL: $1"; fails=$((fails + 1)); }
    named() { case "$out" in *"RED: $1 "*) pass "$2" ;; *) fail "$2 (not named: $1)" ;; esac; }
    quiet() { case "$out" in *"RED: $1"*) fail "$2 (named: $1)" ;; *) pass "$2" ;; esac; }
    if [ "$code" -eq 1 ]; then pass "planted tree exits 1"; else fail "planted tree exited $code, want 1"; fi
    named work/.selftest-30-scope.tmp:1 "key under work/ is named"
    named docs/.selftest-30-scope.tmp:1 "key under docs/ is named"
    named foundation/.selftest-30-scope.tmp:1 "key under foundation/ is named"
    quiet work/.selftest-30-dollar.tmp: "\$NAME and \${NAME} references are quiet"
    named work/.selftest-30-literal.tmp:1 "a literal in the recorded-command shape is named"
    named work/.selftest-30-literal.tmp:2 "a \$'...' literal is named"
    quiet "work/.selftest-30-allow.tmp:1 " "allowlisted token is quiet at its listed path"
    named work/.selftest-30-allow.tmp:2 "an unlisted key in an allowlisted file is named"
    named work/.selftest-30-allow-elsewhere.tmp:1 "the allowlisted token at an unlisted path is named"
    case "$out" in
        *"$key"* | *"$lit"*) fail "RED output printed a planted value" ;;
        *) pass "RED output withholds every planted value" ;;
    esac
    tmpd=$(mktemp -d)
    mkdir -p "$tmpd/foundation/gates.d"
    cp "$0" "$EXEMPTIONS" "$tmpd/foundation/gates.d/"
    nogit=$(cd "$tmpd" && env -u GIT_DIR -u GIT_WORK_TREE GIT_CEILING_DIRECTORIES="$(dirname -- "$tmpd")" \
        bash "$tmpd/foundation/gates.d/30-no-secrets.sh" 2>&1)
    nogit_code=$?
    case "$nogit_code:$nogit" in
        3:RED:*) pass "outside a git work tree it exits 3 without a verdict" ;;
        *) fail "outside a git work tree it exited $nogit_code: $(printf '%s' "$nogit" | head -c 160)" ;;
    esac
    if [ "$fails" -gt 0 ]; then
        echo "SELFTEST_FAIL: $fails arm(s) failed; stage output was:"
        printf '%s\n' "$out" | head -n 20
        exit 1
    fi
    exit 0
fi

[ -f "$EXEMPTIONS" ] || { echo "RED: exemptions ledger missing: $EXEMPTIONS"; exit 3; }
ex_path=()
ex_tok=()
n=0
while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    case "$line" in '' | '#'*) continue ;; esac
    # The line is never echoed: its token field may be shaped like a value.
    case "$line" in
        "EXEMPT "*" | "*" | "*) ;;
        *) echo "RED: malformed exemption at 30-no-secrets.exemptions:$n (needs 'EXEMPT <path> | <token> | <reason>')"; exit 1 ;;
    esac
    rest=${line#EXEMPT }
    p=${rest%% | *}
    rest=${rest#* | }
    t=${rest%% | *}
    r=${rest#* | }
    r=${r//[[:space:]]/}
    if [ -z "$p" ] || [ -z "$t" ] || [ -z "$r" ]; then
        echo "RED: exemption with an empty field at 30-no-secrets.exemptions:$n"; exit 1
    fi
    ex_path+=("$p")
    ex_tok+=("$t")
done <"$EXEMPTIONS"
ex_rel=${EXEMPTIONS#"$root"/}
is_exempt() { # is_exempt <path> <token>
    local i=0
    while [ "$i" -lt "${#ex_tok[@]}" ]; do
        if [ "${ex_tok[$i]}" = "$2" ] && { [ "${ex_path[$i]}" = "$1" ] || [ "$1" = "$ex_rel" ]; }; then return 0; fi
        i=$((i + 1))
    done
    return 1
}

files=$( (CDPATH='' cd -- "$root" && git ls-files -co --exclude-standard -- "${EXCLUDE[@]}") 2>/dev/null | wc -l | tr -d ' ')
if [ "${files:-0}" -eq 0 ]; then
    echo "RED: empty scan set: no committable files under $root (not a git work tree?); no verdict"
    exit 3
fi
# The fixed strings prefilter lines (every match contains one), so the ERE runs on a few
# thousand lines rather than ~290 MB: 0.4 s instead of 5 s on this tree, same matches. -o
# also prints the bare prefilter strings; they are skipped below. -z ends each path with NUL,
# mapped to US (0x1f) so a path with ':' still parses.
raw=$( (CDPATH='' cd -- "$root" && git grep --untracked -n -o -z -E \
    \( -e 'apikey_' -e 'TYPESAFE_API_KEY' \) --and \( -e "$P_APIKEY" -e "$P_ASSIGN" \) \
    -- "${EXCLUDE[@]}") 2>/dev/null | tr '\0' '\037')
grc=$?
case "$grc" in
    0 | 1) ;;
    *) echo "RED: scan failed (git grep exit $grc); no verdict"; exit 3 ;;
esac
US=$'\037'
red=()
allowed=0
while IFS= read -r hit; do
    [ -n "$hit" ] || continue
    case "$hit" in
        *"$US"*"$US"*) ;;
        "Binary file "*) red+=("RED: ${hit#Binary file } (binary file; value withheld)"); continue ;;
        *) red+=("RED: unparsed scan line (withheld)"); continue ;;
    esac
    path=${hit%%"$US"*}
    rest=${hit#*"$US"}
    lno=${rest%%"$US"*}
    tok=${rest#*"$US"}
    case "$tok" in apikey_ | TYPESAFE_API_KEY) continue ;; esac
    if is_exempt "$path" "$tok"; then allowed=$((allowed + 1)); continue; fi
    case "$tok" in apikey_*) kind="apikey_ token" ;; *) kind="TYPESAFE_API_KEY value" ;; esac
    red+=("RED: $path:$lno $kind (value withheld)")
done <<<"$raw"
if [ "${#red[@]}" -gt 0 ]; then
    echo "RED: ${#red[@]} possible secret value(s) in $files committable files:"
    printf '%s\n' "${red[@]}"
    exit 1
fi
echo "PASS: no secret values in $files committable files ($allowed allowlisted hit(s), listed in $ex_rel)"
