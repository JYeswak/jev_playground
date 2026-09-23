#!/bin/sh
# Fixed port of franken-assessments-44-v7 starter-kit/scripts/check-readiness.sh.
#
# Measured 2026-09-23: the zip resolves a relative packet against the caller
# cwd, so `sh /path/to/check-readiness.sh notes/packet.md` from /tmp reports
# the file missing. This port takes an explicit root. A relative packet is
# resolved against that root, never against whatever directory the caller
# happened to be in.
#
# Two vocabulary holes closed, named as divergences:
# - SIGN-OFF required the substring "sign", so a section that only says
#   "design" passed. It now requires the whole word "signed" or "sign-off".
# - SOTA passed on the bare word "version". It now requires the whole word
#   "commit" or "sha".
#
# Usage: check-readiness.sh <packet> <root>
#        check-readiness.sh --selftest
# Exit 0: READY. Exit 1: NOT READY.
set -u

MIN_LINES="${KIT_MIN_LINES:-3}"

section_spec() {
  case "$1" in
    *PROBLEM*)          printf '3\n0|\n' ;;
    *NON-GOALS*)        printf '3\n1|w:not,w:never,w:no,out of scope,will not,won'"'"'t,does not\n' ;;
    *SOTA*)             printf '3\n1|w:commit,w:sha\n' ;;
    *PACKETS*)          printf '3\n5|goal,anchor,target,oracle,fixture,risk,acceptance\n' ;;
    *CLAIM-INVENTORY*)  printf '3\n1|planned,claims.tsv\n' ;;
    *EVIDENCE-DESIGN*)  printf '3\n2|commit,version,host,worker\n' ;;
    *HONESTY-MACHINERY*) printf '3\n2|ledger,demot,resurrect,predicate\n' ;;
    *PROOF-TAXONOMY*)   printf '3\n1|non-proof,non_proof\n' ;;
    *RELEASE-GATE*)     printf '3\n1|waiv\n' ;;
    *EXIT-CRITERIA*)    printf '3\n2|exit,entry\n' ;;
    *REVIEW*)           printf '3\n1|chang\n' ;;
    *SIGN-OFF*)         printf '2\n1|w:signed,w:sign-off\n' ;;
    *)                  printf '%s\n0|\n' "$MIN_LINES" ;;
  esac
}

SECTIONS='<!-- CHECK: PROBLEM -->|problem statement
<!-- CHECK: NON-GOALS -->|non-goals ("what this is not")
<!-- CHECK: SOTA -->|state-of-the-art survey
<!-- CHECK: PACKETS -->|work packets
<!-- CHECK: CLAIM-INVENTORY -->|claim inventory
<!-- CHECK: EVIDENCE-DESIGN -->|evidence design
<!-- CHECK: HONESTY-MACHINERY -->|honesty machinery
<!-- CHECK: PROOF-TAXONOMY -->|proof taxonomy
<!-- CHECK: RELEASE-GATE -->|release gate
<!-- CHECK: EXIT-CRITERIA -->|phase exit criteria
<!-- CHECK: REVIEW -->|independent review
<!-- CHECK: SIGN-OFF -->|execution sign-off'

resolve_packet() {
  packet=$1
  root=$2
  case "$packet" in
    /*) printf '%s\n' "$packet" ;;
    *)  printf '%s\n' "$root/$packet" ;;
  esac
}

check_packet() {
  PACKET=$1
  if [ ! -f "$PACKET" ]; then
    echo "NOT READY: $PACKET not found."
    echo "Pass the packet path and the root it is relative to. This checker does not use the caller cwd."
    return 1
  fi

  TMPD="${TMPDIR:-/tmp}/kit-readiness-$$"
  rm -rf "$TMPD"
  mkdir -p "$TMPD" || { echo "NOT READY: cannot create temp dir."; return 1; }

  fail=0
  missing=""
  OLDIFS="$IFS"
  NL='
'
  IFS="$NL"
  for entry in $SECTIONS; do
    IFS="$OLDIFS"
    if [ -z "$entry" ]; then
      IFS="$NL"
      continue
    fi
    marker="${entry%%|*}"
    label="${entry#*|}"
    SECF="$TMPD/section.txt"
    : > "$SECF"

    if ! grep -qF -- "$marker" "$PACKET"; then
      missing="${missing}  - ${label}: marker ${marker} not found
"
      fail=1
      IFS="$NL"
      continue
    fi

    awk -v m="$marker" '
      /^## / { if (found) exit; next }
      /^<!-- CHECK:/ { if (found) exit; if (index($0, m)) found = 1; next }
      found { print }
    ' "$PACKET" | grep -v '^[[:space:]]*$' | grep -v '^[[:space:]]*>' | grep -v '^[[:space:]]*<!--' > "$SECF"

    spec=$(section_spec "$marker")
    min_lines=$(printf '%s' "$spec" | sed -n '1p')
    vocspec=$(printf '%s' "$spec" | sed -n '2p')
    need="${vocspec%%|*}"
    kws="${vocspec#*|}"

    n=$(wc -l < "$SECF" | tr -d ' ')
    if [ "$n" -lt "$min_lines" ]; then
      missing="${missing}  - ${label}: only ${n} content line(s); need >= ${min_lines} real (non-guidance) lines
"
      fail=1
      IFS="$NL"
      continue
    fi

    if tr 'A-Z' 'a-z' < "$SECF" | tr -s ' \t' ' ' | grep -v '^ *$' \
        | sort | uniq -c | sort -rn | head -1 | grep -qE '^ *([3-9]|[1-9][0-9])'; then
      missing="${missing}  - ${label}: a line is repeated 3+ times — filler, not content
"
      fail=1
      IFS="$NL"
      continue
    fi

    if [ "$need" -gt 0 ] && [ -n "$kws" ]; then
      hits=0
      IFS=','
      for kw in $kws; do
        IFS="$OLDIFS"
        case "$kw" in
          w:*)
            w="${kw#w:}"
            if grep -qiE "(^|[^[:alnum:]_])${w}([^[:alnum:]_]|$)" "$SECF"; then
              hits=$((hits + 1))
            fi
            ;;
          *)
            if grep -qiF -- "$kw" "$SECF"; then
              hits=$((hits + 1))
            fi
            ;;
        esac
        IFS=','
      done
      IFS="$OLDIFS"
      if [ "$hits" -lt "$need" ]; then
        missing="${missing}  - ${label}: section vocabulary too thin (${hits}/${need} required terms: ${kws})
"
        fail=1
        IFS="$NL"
        continue
      fi
    fi

    case "$marker" in
      *SIGN-OFF*)
        if ! grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}' "$SECF"; then
          missing="${missing}  - ${label}: sign-off must carry a date (YYYY-MM-DD)
"
          fail=1
        fi
        ;;
    esac
    IFS="$NL"
  done
  IFS="$OLDIFS"
  rm -rf "$TMPD"

  if [ "$fail" -eq 0 ]; then
    echo "READY: all 12 planning-packet sections present with substance."
    return 0
  fi
  printf 'NOT READY: %s is missing/incomplete in:\n' "$PACKET"
  printf '%s' "$missing"
  return 1
}

selftest() {
  d=$(mktemp -d "${TMPDIR:-/tmp}/kit-readiness-selftest.XXXXXX") || {
    echo "SELFTEST_FAIL: cannot make temp dir"
    exit 1
  }
  trap 'rm -rf "$d"' EXIT INT TERM
  mkdir -p "$d/sub"
  # A sign-off that only says "design" must not pass. The zip checker accepts it.
  cat > "$d/sub/packet.md" << 'EOF'
<!-- CHECK: PROBLEM -->
one
two
three
<!-- CHECK: NON-GOALS -->
This will not do that.
It never does the other.
It does not include a third.
<!-- CHECK: SOTA -->
Pinned at commit abcdef1.
The sha is recorded.
The incumbent is named.
<!-- CHECK: PACKETS -->
goal anchor target oracle fixture risk acceptance are the fields.
Second line of the packet body.
Third line of the packet body.
<!-- CHECK: CLAIM-INVENTORY -->
planned claims live in claims.tsv.
Second inventory line.
Third inventory line.
<!-- CHECK: EVIDENCE-DESIGN -->
Receipts record commit and version.
They also name the host.
Third evidence line.
<!-- CHECK: HONESTY-MACHINERY -->
The ledger has a retry predicate.
Demotion is written down.
Resurrection is a cadence, not a rumor.
<!-- CHECK: PROOF-TAXONOMY -->
The non-proof list is explicit.
Second taxonomy line.
Third taxonomy line.
<!-- CHECK: RELEASE-GATE -->
A waiver must be public.
Second release line.
Third release line.
<!-- CHECK: EXIT-CRITERIA -->
Phase entry is this packet.
Phase exit is the checker.
Third exit line.
<!-- CHECK: REVIEW -->
Nothing was changed by review.
Second review line.
Third review line.
<!-- CHECK: SIGN-OFF -->
The design review happened on 2026-09-23.
The designer wrote three lines.
The design board accepted the date.
EOF
  # Invoke from /tmp with a relative path. The zip checker would look in /tmp.
  bad=$("$0" packet.md "$d/sub" 2>&1) && {
    echo "SELFTEST_FAIL: design-only sign-off was accepted"
    printf '%s\n' "$bad"
    exit 1
  }
  case "$bad" in
    *sign-off*|*SIGN-OFF*|*signed*) ;;
    *) echo "SELFTEST_FAIL: RED did not name the sign-off"; printf '%s\n' "$bad"; exit 1 ;;
  esac
  # Same relative path, wrong root, must say not found rather than a silent pass.
  missing=$("$0" packet.md /tmp 2>&1) && {
    echo "SELFTEST_FAIL: relative path resolved outside the given root"
    exit 1
  }
  case "$missing" in
    *"/tmp/packet.md"*) ;;
    *) echo "SELFTEST_FAIL: missing-file RED did not name the resolved path"; printf '%s\n' "$missing"; exit 1 ;;
  esac
  printf '%s\n' 'Signed as draft: pane, 2026-09-23.' 'No execution is authorized.' > "$d/sub/sign.txt"
  # Replace the design sign-off with a real signed line and expect READY.
  awk '
    /CHECK: SIGN-OFF/ { print; skip=1; next }
    skip && /^<!-- CHECK:/ { skip=0 }
    skip { next }
    { print }
  ' "$d/sub/packet.md" > "$d/sub/good.md"
  cat "$d/sub/sign.txt" >> "$d/sub/good.md"
  "$0" good.md "$d/sub" >/dev/null || {
    echo "SELFTEST_FAIL: a signed packet did not pass"
    exit 1
  }
  echo "SELFTEST_PASS: design-only sign-off refused, relative path uses the given root, signed packet passed"
  exit 0
}

if [ "${1:-}" = "--selftest" ]; then
  selftest
fi

PACKET_IN=${1:?packet path required}
ROOT=${2:?root required}
PACKET=$(resolve_packet "$PACKET_IN" "$ROOT")
check_packet "$PACKET"
