#!/usr/bin/env bash
# lane-status.sh — DERIVE the jev lane's live status. Never report it from memory.
#
# WHY THIS EXISTS (Joshua, 2026-09-18): "your cron should remind you to pull live status - keep
# close tabs on what work has been done, what is left, it should not come from memory - it needs
# to be up to date."
#
# The deeper defect this fixes: the conductor's status reports were assembled from PROSE IT HAD
# WRITTEN ITSELF (PLAN.md sections, its own commit messages). Prose is memory with extra steps. A
# verdict recorded in a paragraph cannot be checked against the artifact it claims.
#
# So: docs/demos/STATUS.tsv is the machine-readable state of record, and this script
#   (a) renders it,
#   (b) VERIFIES every cited receipt actually exists on disk,
#   (c) derives everything else live — beads, commits, uncommitted deliveries, worker panes,
#       artifact inventory with byte counts.
#
# FAIL-CLOSED: a STATUS row citing a receipt that does not exist exits 3. That is the known-bad
# this script fires on: a verdict with no evidence behind it.
set -uo pipefail

REPO="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$REPO" || { echo "lane-status: repo missing: $REPO" >&2; exit 2; }
# Test hook: point at an alternate state file. Exists so the missing-receipt RED arm can be proven
# to DISCRIMINATE — real receipts present, one planted bogus row — without mutating the shared
# worktree, which three panes are reading. A detector that fires on every row has not discriminated.
STATUS="${JEV_STATUS:-docs/demos/STATUS.tsv}"
[ -f "$STATUS" ] || { echo "lane-status: $STATUS missing — no state of record" >&2; exit 2; }

# ------------------------------------------------- receipt integrity (pane 2, RULE_receipt_integrity_COD.md)
# Ruling (c): CONTENT-NORMALISED digests — strip only the final run of terminal whitespace bytes,
# hash everything else. Chosen because the autofix hook that runs on EVERY commit appends trailing
# newlines to JSON receipts; a raw-sha gate would be broken by our own hook on every commit, which
# by §3h doctrine is a dead gate on arrival ("a gate nothing can satisfy is not a high bar").
# Normalisation is deliberately minimal: any NON-terminal byte change still drifts.
#
# Pane 2's binding constraint, quoted: "current existence-only behavior must not be mislabeled
# integrity." Existence and integrity are reported as SEPARATE claims with separate counts below.
#
# Scope, stated because it is not a repair: when this landed, pane 2 measured ZERO digest-dependent
# lane claims (digest-dependency-20260918T085000Z.json). This prevents a future failure; it does not
# fix a past one.
norm_digest() { perl -0777 -pe 's/\s+\z//' "$1" 2>/dev/null | shasum -a 256 | cut -c1-16; }

# ---------------------------------------------------------- TRANSIENT_UNSTABLE (pane 2, Q92 spec)
# docs/demos/duel-2/SPEC_transient_unstable_COD.md (185ccdd). Pane 2's Q89 ruling refused to promote
# the sidecar verifier to a foundation stage until this primitive existed, and named the reason:
# reading live shared state can observe A PEER'S PARTIAL EDIT and produce a transient RED, which
# "trains rerun-until-green". THREE PANES SHARE THIS WORKTREE, so lane-status has always been exposed
# to it — the tick has been trusting a reading that could have been wrong, with no way to tell.
#
# THE CONTRACT, as specified: fingerprint the evidentiary inputs (STATUS + sidecar + every referenced
# receipt) before and after the scan; MAX 2 CAPTURE ATTEMPTS; a first change triggers ONE bounded
# recapture; A STABLE SECOND SNAPSHOT IS VALIDATED EVEN IF RED; only a SECOND instability returns
# TRANSIENT_UNSTABLE, with the changed paths and NO VERDICT. Exit 10, reserved because 2-9 are taken.
#
# The bound is the whole design. One recapture is not "retry until green" — the second snapshot's
# verdict is accepted whatever it says, so instability can never launder a RED into a pass.
#
# SCOPE per the spec: this covers RECEIPT / SCHEMA / INTEGRITY claims. The mutable pane, bead and
# worktree surfaces below stay POINT-IN-TIME OBSERVATIONS and are deliberately not fingerprinted —
# they change constantly by design and snapshotting them would make every run unstable.
fingerprint() {
  {
    printf '%s\n' "$(git rev-parse HEAD 2>/dev/null || echo no-head)"
    for f in "$STATUS" docs/demos/duel-2/runs/receipt-other-reasons.json; do
      [ -f "$f" ] && printf '%s  %s\n' "$(shasum -a 256 <"$f" | cut -c1-16)" "$f"
    done
    awk -F'\t' '!/^#/ && $1!="candidate" {print $6}' "$STATUS" 2>/dev/null | sort -u | while read -r r; do
      [ -f "$r" ] && printf '%s  %s\n' "$(shasum -a 256 <"$r" | cut -c1-16)" "$r"
    done
  } 2>/dev/null
}

# COLUMN COLLISION, resolved in the author's favour: pane 3's CONCURRENCE_archaeology_MU.md proposed
# `kill_concurrence` at column 8 with a fail-closed schema rule; this script had already implemented
# `receipt_digest` at column 8. Both said "append after blocked_on". Concurrence keeps 8 (it is a
# verdict-semantic field and its author specified it); the digest moves to 9 (an integrity artifact,
# last). Recorded rather than silently reassigned — two independent authors appending to the same
# state of record is a collision class that will recur.
#
#   col 8  kill_concurrence  author-self | nonauthor-kill:<receipt>@<sha> | concur:<pane>:<r>@<sha> | none
#          empty ==> row is not RULED_OUT. A RULED_OUT row with an empty col 8 is a SCHEMA VIOLATION.
#   col 9  receipt_digest    content-normalised sha256 (16 hex); empty ==> existence-only
#
# --pin: emit STATUS.tsv with column 9 recomputed, to STDOUT. Never mutates the shared state file in
# place — three panes read it, and a script that silently rewrites the state of record is the exact
# hazard the autofix hook already demonstrated.
if [ "${1:-}" = '--pin' ]; then
  changed=0
  while IFS= read -r line; do
    case "$line" in '#'*|'') printf '%s\n' "$line"; continue ;; esac
    IFS=$'\037' read -r c r s v a rcpt b concur old <<<"$(printf '%s' "$line" | tr '\t' '\037')"
    [ "$c" = candidate ] && { printf '%s\n' "$line"; continue; }
    new=''
    if [ -n "$rcpt" ] && [ -f "$rcpt" ]; then new=$(norm_digest "$rcpt"); fi
    [ "$new" != "${old:-}" ] && changed=$((changed+1))
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$r" "$s" "$v" "$a" "$rcpt" "$b" "$concur" "$new"
  done < "$STATUS"
  printf 'lane-status --pin: %d row digest(s) would change. Redirect to apply.\n' "$changed" >&2
  exit 0
fi
rc=0
# Attempt counter for the bounded recapture. The spec allows MAX 2, so attempt 2 never re-execs.
: "${JEV_TRANSIENT_ATTEMPT:=1}"
FP_BEFORE="$(fingerprint)"
printf 'JEV LANE STATUS  %s  HEAD=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(git rev-parse --short HEAD)"
printf '%s\n' "----------------------------------------------------------------------"

# ---------------------------------------------------------------- gauntlet state
printf '\nGAUNTLET (state of record: %s)\n' "$STATUS"
printf '  %-30s %-4s %-5s %-10s %-6s %s\n' CANDIDATE RUNG SCORE VERDICT AUTHOR BLOCKED_ON
missing=0; rows=0; with_receipt=0; pinned=0; drifted=0; unpinned=0
ruled_out=0; concur_missing=0; schema_bad=0; type_bad=0
# SCHEMA WIDTH IS VALIDATED EXACTLY, and this is a PREREQUISITE, not a nicety. Pane 2,
# verify-exit-disaggregation-20260918T102000Z.json (a915e11), non-author, asked the question I had
# put in its packet and answered it with a blocker:
#   "ARM10 behaviour is UNSAFE for Q19: extra column is folded into final digest and false-REDs;
#    receipt_type column10 would break EVERY ROW until parser migrates to exact 10-column validation."
# `read` assigns all trailing fields to the last variable, so appending column 10 would have silently
# corrupted the digest of all 17 rows and reported drift on every one of them. It also found my own
# new arm passing for the wrong reason: "ARM9 returns rc5 because empty concurrence fires, NOT because
# schema width is validated; parser has no field-count check." I had pinned a behaviour and read it as
# validation — the pass-by-construction class I had asked it to attack.
#
# EXPECTED_COLS is the single constant to bump when a column lands. Bumping it is the migration.
# Overridable so the MIGRATION ITSELF is testable: JEV_EXPECTED_COLS=10 against a 10-column fixture
# must come back green, which is the proof that bumping this constant is all the migration requires.
# MIGRATED to 10 on 2026-09-18: receipt_type landed as column 10 from pane 3's opened-receipt typing
# (receipt-type-proposal-20260918T102335Z.tsv), audited by pane 2 as enum author. Bumping this
# constant WAS the whole migration, as ARM 11 requires — and the pre-migration state failed loudly
# at rc=8 with "17 of 17 rows have the wrong column count", never as 17 false drift reports.
EXPECTED_COLS="${JEV_EXPECTED_COLS:-10}"
# SEMANTIC validation, closing the bound pane 2 stated in verify-schema-width-20260918T103000Z.json:
# "ARM11 proves structural read, not semantic receipt_type enum validation." Structure said the field
# is there; nothing said its value was legal. Pane 2's Q19 ruling requires fail-closed on
# empty/missing/unknown/out-of-enum, NEVER inferred as non-score — so an illegal value is its own
# failure class (rc=9), not a silent demotion to "not a score receipt".
VALID_TYPES=' score hold-resolution verdict measurement other '
while IFS= read -r raw; do
  case "$raw" in '#'*|'') continue ;; esac
  nf=$(printf '%s' "$raw" | awk -F'\037' '{print NF}')
  # `receipt_type` is read NOW, while it is still empty at 9 columns. ARM 11 falsified my own comment
  # claiming "bumping one constant is the whole migration": `read` folds every trailing field into the
  # LAST variable, so at 10 columns `digest` came back as "<16hex>\037score" and every row false-RED'd
  # as drift — the exact breakage pane 2 predicted, reproduced by the arm written to test the fix.
  # With the variable present, the constant genuinely is the migration.
  # `overflow` exists so field 10 can never absorb an 11th column. ARM 11 caught this exact fold one
  # column along: with 11 fields and 10 variables, `receipt_type` arrived as "measurement\037EXTRA"
  # and failed the enum instead of failing the width. Reading N+1 fields makes EXPECTED_COLS the
  # whole migration for EXACTLY ONE more column OF WIDTH — and no further. Pane 3 graded this
  # sentence STRUCTURALLY_TRUE_SEMANTICALLY_MISLEADING: "the commit's own content falsifies any
  # semantic reading: receipt_type itself required VALID_TYPES + rc=9 + arms 13/14 + the overflow var
  # — far more than the constant. A future SEMANTIC column needs var+check+arms, not a bump." Correct:
  # I understated the cost of the very migration I had just performed. Width is one constant; MEANING
  # is a variable, a validator, an exit code and two arms. This comment is the honest scope of the
  # claim "bumping one constant is the migration".
  IFS=$'\037' read -r cand rung score verdict author receipt blocked concur digest receipt_type overflow <<<"$raw"
  case "$cand" in candidate) continue ;; esac
  rows=$((rows+1))
  mark=''
  if [ "$nf" -ne "$EXPECTED_COLS" ]; then
    mark="  <<< SCHEMA: $nf cols, want $EXPECTED_COLS"; schema_bad=$((schema_bad+1))
  fi
  if [ "$nf" -eq "$EXPECTED_COLS" ]; then
    case "$VALID_TYPES" in
      *" ${receipt_type:-} "*) : ;;
      *) mark="$mark  <<< TYPE: '${receipt_type:-<empty>}' not in enum"; type_bad=$((type_bad+1)) ;;
    esac
  fi
  if [ -n "$receipt" ]; then
    with_receipt=$((with_receipt+1))
    if [ ! -e "$receipt" ]; then
      mark="$mark  <<< RECEIPT MISSING"; missing=$((missing+1))
    elif [ ! -f "$receipt" ]; then
      mark='  (dir receipt: existence only)'; unpinned=$((unpinned+1))
    elif [ -n "${digest:-}" ]; then
      pinned=$((pinned+1)); have=$(norm_digest "$receipt")
      if [ "$have" != "$digest" ]; then
        mark="  <<< DIGEST DRIFT want=$digest have=$have"; drifted=$((drifted+1))
      fi
    else
      unpinned=$((unpinned+1))
    fi
  fi
  # Pane 3's mechanical watcher, promoted from prose into this gate: a RULED_OUT row with no
  # kill_concurrence value is a schema violation. "The condition fires observably or the file is red."
  # Deliberately OUTSIDE the receipt branch: a receiptless RULED_OUT row must still be caught.
  if [ "$verdict" = RULED_OUT ]; then
    ruled_out=$((ruled_out+1))
    if [ -z "${concur:-}" ]; then
      mark="$mark  <<< NO kill_concurrence"; concur_missing=$((concur_missing+1))
    fi
  fi
  printf '  %-30s %-4s %-5s %-10s %-6s %s%s\n' "$cand" "$rung" "$score" "$verdict" "$author" "$blocked" "$mark"
done < <(tr '\t' '\037' < "$STATUS")

printf '\nRECEIPT VERIFICATION (existence and integrity are SEPARATE claims — do not read one as the other)\n'
printf '  existence_checked: %-4d missing:  %d\n' "$with_receipt" "$missing"
printf '  integrity_checked: %-4d drifted:  %d   (content-normalised sha256; terminal whitespace stripped)\n' "$pinned" "$drifted"
printf '  NOT integrity-checked (no pinned digest): %d   <- existence proven, bytes unverified\n' "$unpinned"
printf '\nKILL CONCURRENCE (§3c rule 3, demoted to guidance — checked mechanically, not by a volunteer)\n'
printf '  ruled_out rows: %-4d missing kill_concurrence: %d\n' "$ruled_out" "$concur_missing"
printf '\nSCHEMA (exact width — a row of the wrong width makes every other counter on it unreliable)\n'
printf '  expected_cols: %-4d rows with wrong width: %d\n' "$EXPECTED_COLS" "$schema_bad"
printf '  receipt_type enum: %s\n' "$(printf '%s' "$VALID_TYPES" | sed 's/^ //; s/ $//; s/ /|/g')"
printf '  rows with illegal receipt_type: %d   (fail-closed; never inferred as non-score)\n' "$type_bad"

# ---------------------------------------------------------------- derived counts
printf '\nDERIVED FROM %s (not from prose)\n' "$STATUS"
awk -F'\t' '!/^#/ && $1!="candidate" && NF>=4 {v[$4]++; r[$2]++} END {
  printf "  verdicts:"; for (k in v) printf " %s=%d", k, v[k]; printf "\n";
  printf "  by rung :"; for (k in r) printf " r%s=%d", k, r[k]; printf "\n";
}' "$STATUS"
printf '  promoted: %s   (rung-5 rows)\n' "$(awk -F'\t' '!/^#/ && $2==5' "$STATUS" | wc -l | tr -d ' ')"
printf '  highest unscored candidate: %s\n' \
  "$(awk -F'\t' '!/^#/ && $1!="candidate" && $2==0 {print $3"\t"$1}' "$STATUS" | sort -rn | head -1 | cut -f2)"

# ---------------------------------------------------------------- live surfaces
printf '\nBEADS (live)\n'
printf '  open/in-progress: %s   closed: %s\n' \
  "$(br list 2>/dev/null | grep -cE '^[○◐]' || echo '?')" \
  "$(br list --status closed 2>/dev/null | grep -cE '^✓' || echo '?')"

printf '\nARTIFACTS (bytes, derived)\n'
for d in docs/demos/contracts docs/demos/duel-1 docs/demos/duel-2; do
  [ -d "$d" ] || continue
  n=$(find "$d" -name '*.md' -o -name '*.json' | wc -l | tr -d ' ')
  b=$(find "$d" -type f \( -name '*.md' -o -name '*.json' \) -exec cat {} + 2>/dev/null | wc -c | tr -d ' ')
  printf '  %-26s %3s files  %9s bytes\n' "$d" "$n" "$b"
done
printf '  %-26s %3s files  %9s bytes\n' 'plan corpus' \
  "$(ls docs/demos/PLAN.md docs/demos/BEAD-TEMPLATE.md docs/demos/contracts/*.md 2>/dev/null | wc -l | tr -d ' ')" \
  "$(cat docs/demos/PLAN.md docs/demos/BEAD-TEMPLATE.md docs/demos/contracts/*.md 2>/dev/null | wc -c | tr -d ' ')"

printf '\nUNCOMMITTED DELIVERIES (work sitting in the tree)\n'
git status --porcelain | sed 's/^/  /' | head -12
[ -z "$(git status --porcelain)" ] && printf '  (clean)\n'

printf '\nLAST 6 COMMITS\n'
git log --oneline -6 | sed 's/^/  /'

printf '\nWORKER PANES (workers-only; pane_index 0 is the user shell)\n'
if [ -x "$HOME/.local/bin/fleet-idle-monitor" ]; then
  FLEET_SESSION=jev FLEET_QUEUE_REPO="$REPO" "$HOME/.local/bin/fleet-idle-monitor" --report-only 2>&1 \
    | grep -vE 'pane=%70' | sed 's/^/  /' | head -8
  printf '  NOTE: this binary has 3 recorded defects (PLAN.md §6). Do NOT read WORKING as proof.\n'
else
  printf '  fleet-idle-monitor not installed\n'
fi

# ---------------------------------------------------------------- verdict
printf '\n%s\n' "----------------------------------------------------------------------"
# EXIT-CODE DISAGGREGATION — pane 2, audit-instruments-20260918T101000Z.json (965005a), non-author:
# "lane rc3 conflates missing receipt and missing concurrence (output distinguishes, exit does not;
# MISSING BRANCH MASKS CONCURRENCE IF BOTH)." Correct on both counts. The elif chain meant a tree
# with one absent receipt reported nothing about concurrence at the verdict line, and a caller
# reading only the exit code could not tell the two failures apart. Now: every failing class is
# REPORTED, and the exit code names which classes fired rather than which one was checked first.
#   3 = missing receipt (alone)      6 = missing receipt AND missing concurrence
#   4 = digest drift (alone)         7 = any other combination of two or more classes
#   5 = missing concurrence (alone)
fails=0
if [ "$missing" -gt 0 ]; then
  printf 'FAIL: %d of %d STATUS rows cite a receipt that does not exist.\n' "$missing" "$rows"
  printf 'A verdict with no artifact behind it is the known-bad this script fires on.\n'
  fails=$((fails+1))
fi
if [ "$concur_missing" -gt 0 ]; then
  printf 'FAIL: %d of %d RULED_OUT rows carry no kill_concurrence value.\n' "$concur_missing" "$ruled_out"
  printf 'A kill whose authorship boundary is unrecorded is the same known-bad as a missing receipt.\n'
  fails=$((fails+1))
fi
if [ "$drifted" -gt 0 ]; then
  printf 'FAIL: %d of %d integrity-checked receipts drifted from their pinned digest.\n' "$drifted" "$pinned"
  printf 'Content changed beyond terminal whitespace. Re-pin deliberately or explain the change.\n'
  fails=$((fails+1))
fi
# Schema is reported LAST but ranks FIRST in the exit code: a row of the wrong width makes every
# other counter on that row untrustworthy, so it must not be masked by a downstream class.
if [ "$schema_bad" -gt 0 ]; then
  printf 'FAIL: %d of %d rows have the wrong column count (want %d).\n' "$schema_bad" "$rows" "$EXPECTED_COLS"
  printf 'Every other counter on a malformed row is unreliable. Fix the width before reading anything else.\n'
  fails=$((fails+1))
fi
if [ "$type_bad" -gt 0 ]; then
  printf 'FAIL: %d of %d rows carry a receipt_type outside the enum (%s).\n' "$type_bad" "$rows" \
    "$(printf '%s' "$VALID_TYPES" | sed 's/^ //; s/ $//; s/ /|/g')"
  printf 'Per Q19: empty, unknown, or out-of-enum FAILS CLOSED and is never inferred as non-score.\n'
  fails=$((fails+1))
fi
if [ "$fails" -eq 0 ]; then
  # WORDING CORRECTED — pane 3, audit-migration-impl-20260918T103832Z.json (96cf7cc), non-author of
  # this code: "'4/4 kills concurrence-recorded' OVERSTATES: demo-1 col 8 is `none` (explicitly NO
  # concurrence); the gate checks non-empty, so ABSENCE-AS-RECORDED COUNTS AS RECORDED." The gate's
  # behaviour is correct — a recorded `none` IS the honest value per Q62 — but the summary line
  # asserted concurrence where the row asserts its absence. The instrument was overstating its own
  # result, which is the exact class of defect this lane exists to catch.
  explicit_none=$(awk -F'\t' '!/^#/ && $1!="candidate" && $4=="RULED_OUT" && $8=="none"' "$STATUS" | wc -l | tr -d ' ')
  printf 'OK: %d candidates. %d receipt(s) exist; %d integrity-checked, %d existence-only; concurrence-field-present %d/%d (of which explicit-none %d); %d-col schema and enum clean.\n' \
    "$rows" "$with_receipt" "$pinned" "$unpinned" "$((ruled_out-concur_missing))" "$ruled_out" \
    "$explicit_none" "$EXPECTED_COLS"
elif [ "$schema_bad" -gt 0 ]; then
  rc=8
  [ "$fails" -gt 1 ] && printf 'NOTE: %d classes fired; schema takes precedence because the other counters are unreliable.\n' "$fails"
elif [ "$type_bad" -gt 0 ]; then
  rc=9
  [ "$fails" -gt 1 ] && printf 'NOTE: %d classes fired; enum precedence — an illegal type makes the score/non-score read untrustworthy.\n' "$fails"
elif [ "$fails" -gt 1 ]; then
  if [ "$missing" -gt 0 ] && [ "$concur_missing" -gt 0 ] && [ "$drifted" -eq 0 ]; then rc=6; else rc=7; fi
  printf 'FAIL: %d distinct failure classes fired. Exit %d.\n' "$fails" "$rc"
elif [ "$missing" -gt 0 ]; then rc=3
elif [ "$drifted" -gt 0 ]; then rc=4
else rc=5
fi

# ---------------------------------------------------- TRANSIENT_UNSTABLE check (pane 2 Q92, 185ccdd)
# The evidentiary inputs are fingerprinted again HERE, after every receipt/schema/integrity claim
# above was computed. If they moved during the scan, the verdict above was computed against a state
# that no longer exists, so it is not reported as either a pass or a failure.
#
# BOUNDED AT TWO ATTEMPTS, and the bound is the design. One recapture is not retry-until-green: the
# second attempt's verdict is accepted WHATEVER IT SAYS, so instability can never launder a RED into
# a pass. Only a SECOND instability yields exit 10 with the changed paths and NO VERDICT.
#
# WITNESSED, not theoretical: pane 2's Q93 runtime run recorded "peer mutation of
# foundation/gates.sh caused syntax error mid-run, not a runtime sample" — and that peer was the
# conductor, editing a shared script while a pane executed it. One tick earlier this risk was
# recorded here as having no witness.
FP_AFTER="$(fingerprint)"
if [ "$FP_BEFORE" != "$FP_AFTER" ]; then
  if [ "${JEV_TRANSIENT_ATTEMPT}" -ge 2 ]; then
    printf '\n%s\n' "----------------------------------------------------------------------"
    printf 'TRANSIENT_UNSTABLE: the evidentiary inputs moved during BOTH capture attempts.\n'
    printf 'NO VERDICT is reported — the scan above was computed against a state that changed.\n'
    printf 'Changed paths:\n'
    diff <(printf '%s\n' "$FP_BEFORE") <(printf '%s\n' "$FP_AFTER") \
      | sed -n 's/^[<>] *[0-9a-f]\{16\}  /  /p' | sort -u
    printf 'A peer is mid-write. Re-run when the tree settles; do NOT read this as a pass or a RED.\n'
    exit 10
  fi
  printf '\nSNAPSHOT MOVED during attempt 1 — recapturing once (bounded at 2 per Q92 spec).\n'
  printf 'The second attempt'"'"'s verdict is accepted whatever it says; instability cannot launder a RED.\n'
  exec env JEV_TRANSIENT_ATTEMPT=2 "$0" "$@"
fi
exit "$rc"
