#!/usr/bin/env bash
# selftest for scripts/denominator-sweep.sh — discovered automatically by foundation/gates.d/80.
#
# The sweep is wired (not hand-run) because it is fast, read-only, and hermetic
# enough: every check regenerates from committed files or pinned fixtures, npm
# test runs the backtest suite without writing outside its own package, and no
# arm writes shared state.
set -uo pipefail
root=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd -P)
cd "$root" || exit 1
S="$root/scripts/denominator-sweep.sh"
P="$root/scripts/pinned-denominator.sh"
fail=0
pass=0

note() { printf '  %-4s %s\n' "$1" "$2"; }

# Arm 1: the sweep passes and SAYS SO (an exit-0 that stays silent would be an empty success —
# require a verdict line).
#
# ENVIRONMENT-DEPENDENT GREEN, FIXED 2026-09-20. This arm pinned the literal "ALL-AGREE", which
# is only reachable where every pinned source is present. On a fresh clone the honest verdict is
# "AGREE-WITH-1-SKIPPED" (cass-dig-rows.jsonl is gitignored by design), so this arm failed for
# strangers and passed for us: 4 ok locally, 3 ok 1 failed from a clone. Found by a real clone,
# not by reasoning. The seam is exactly why it hid — JEV_SWEEP_FORCE_ABSENT=1 drives arm 4, while
# arm 1 runs the real sweep, whose absent-source state is the DEFAULT on a clone and never the
# case here. Both verdicts are accepted now; the rc=0 conjunct and the no-silence rule stand.
out=$("$S" 2>&1); rc=$?
if [ "$rc" -eq 0 ] && grep -qE 'ALL-AGREE|AGREE-WITH-[0-9]+-SKIPPED' <<<"$out"; then
  note ok "sweep agreed and said so (rc=0)"; pass=$((pass + 1));
else
  note FAIL "sweep did not agree: rc=$rc"; printf '%s\n' "$out"; fail=$((fail + 1));
fi

# Arm 2: the underlying guard still fires on a planted drift (end-to-end proof
# the sweep's checks are checks, using tonight's verbatim numbers).
"$P" 77767 printf '78242\n' >/dev/null 2>&1
if [ "$?" -eq 3 ]; then note ok "planted drift fires (rc=3)"; pass=$((pass + 1));
else note FAIL "planted drift did not fire"; fail=$((fail + 1)); fi

# Arm 3: the conductor's exact scenario — a copy run from /tmp must REFUSE
# (rc=2), never report eight confident DRIFTs that are all false.
tmp=$(mktemp -d) || { echo "selftest-denominator-sweep: mktemp failed"; exit 1; }
trap 'rm -rf "$tmp"' EXIT
cp "$S" "$tmp/sweep-copy.sh"
"$tmp/sweep-copy.sh" >/dev/null 2>&1
if [ "$?" -eq 2 ]; then note ok "relocated copy refuses (rc=2)"; pass=$((pass + 1));
else note FAIL "relocated copy did not refuse"; fail=$((fail + 1)); fi


# ARM 4 (2026-09-20): a gitignored source must SKIP, never ERROR. A fresh clone lacks
# work/cass-mail-mines/exports/cass-dig-rows.jsonl (mined mail, .gitignore:95), and before the fix
# the sweep printed "ERROR ... the check itself is broken" and turned gates.sh RED for any stranger
# following the README Quick start. Absence is not breakage and it is not agreement.
OUT4="$(JEV_SWEEP_FORCE_ABSENT=1 "$S" 2>&1)"; RC4=$?
if [ "$RC4" -eq 0 ] \
   && printf '%s\n' "$OUT4" | grep -q '^  SKIP locked-dig-138' \
   && printf '%s\n' "$OUT4" | grep -q 'AGREE-WITH-1-SKIPPED' \
   && ! printf '%s\n' "$OUT4" | grep -q 'ERROR locked-dig-138'; then
  note ok "absent source SKIPs, is named in the verdict, and does not RED a fresh clone"; pass=$((pass + 1))
else
  note FAIL "absent source did not SKIP cleanly (rc=$RC4)"; fail=$((fail + 1))
fi

echo "scripts/selftest-denominator-sweep.sh: $pass ok, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
