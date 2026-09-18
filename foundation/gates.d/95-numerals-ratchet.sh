#!/usr/bin/env bash
# Stage 95 — the numeral-citation gate, wired as a RATCHET rather than a zero-hit demand.
#
# WHY THIS EXISTS, and it is the LAST unconsumed instrument in this lane getting its consumer.
#
# `verify-reason-numerals.sh` opens every numeral in a verdict's reason against the receipt cited for
# that verdict. It was hand-run all session, and pane 3 REFUSED to wire it repeatedly, always naming a
# real precondition. On 2026-09-18 it finally ruled (numerals-hold-ruling-20260918T161328Z.json,
# 20df1d7): HOLD binds FALSE, precondition MET, and all three live hits are legitimate in form.
#
# That ruling is exactly why this cannot be a zero-hit gate. A rounding, a unit change and a
# scope-narrowing are honest citations; REDing on them would demand that correct prose be rewritten to
# satisfy a substring match. Pane 3 said so about the sibling gate and the reasoning transfers:
# wiring a gate that REDs on legitimately-nonzero hits is worse than leaving it hand-run.
#
# So the gate checks NO UNREGISTERED HITS, against foundation/numerals-ruled.tsv, where every row is a
# hit a non-author pane examined and cleared with a ruling receipt. The ratchet only tightens: a new
# hit, or a changed numeral in an old one, is unregistered and RED.
#
#   CONSUMER            foundation/gates.sh (this stage)
#   GATE                numeral citations in verdict reasons open in their cited receipt
#   OBSERVED DEFECTS    mispointed receipt (demo-1 dropped-digit class) · absent measurement cited as
#                       present · silent renumbering of a reason after its receipt froze
#   RETIREMENT          retire only when a successor opens numerals with equal or stronger arms AND
#                       carries the register forward; NEVER because the current run is green
#
# THE ONE HARD CONSTRAINT: a row in the register must be preceded by its ruling, never the reverse.
# Registering first and ruling later is laundering, and the register's own header says so.
#
# NOTE ON THE UNDERLYING SCRIPT'S rc: it exits 0 even with hits, by design — it is advisory and a
# human rules its findings. This stage supplies the branch the script deliberately declines to take,
# which is what makes it a consumer rather than a second opinion.
set -euo pipefail

root="${JEV_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$root"

register="${JEV_NUMERALS_REGISTER:-foundation/numerals-ruled.tsv}"

if [[ ! -f "$register" ]]; then
  echo "FAIL  stage 95 numerals ratchet          register $register is MISSING — the gate cannot"
  echo "      distinguish a ruled hit from a new one, so it refuses to report a pass."
  exit 1
fi

out="$(./scripts/verify-reason-numerals.sh 2>&1)" || true

# Hits, as candidate<TAB>numeral. The verifier's line shape is fixed by its own selftest arms.
hits="$(printf '%s\n' "$out" \
  | sed -nE "s/^[[:space:]]*UNOPENABLE ([A-Za-z0-9_.-]+): '([0-9.]+)'.*/\1\t\2/p" \
  | LC_ALL=C sort -u)"

ruled="$(grep -vE '^[[:space:]]*(#|$)' "$register" | cut -f1,2 | LC_ALL=C sort -u)"

# Unregistered hits: present live, absent from the register.
new="$(LC_ALL=C comm -23 <(printf '%s\n' "$hits" | grep -v '^$' || true) \
                         <(printf '%s\n' "$ruled" | grep -v '^$' || true) || true)"

# Stale rows: registered but no longer observed. NOT a failure — the citation was fixed or the row
# retired — but it is surfaced, because a register that silently accumulates dead rows becomes an
# allowlist nobody rereads.
stale="$(LC_ALL=C comm -13 <(printf '%s\n' "$hits" | grep -v '^$' || true) \
                           <(printf '%s\n' "$ruled" | grep -v '^$' || true) || true)"

n_hits="$(printf '%s\n' "$hits" | grep -c . || true)"
n_ruled="$(printf '%s\n' "$ruled" | grep -c . || true)"

if [[ -n "$new" ]]; then
  echo "FAIL  stage 95 numerals ratchet          UNREGISTERED numeral citation(s) — a numeral in a"
  echo "      verdict reason does not open in the receipt cited for it, and NO pane has ruled it."
  printf '%s\n' "$new" | sed 's/^/        NEW  /'
  echo "      A non-author pane must rule each: mispointed receipt, rounded citation, or absent"
  echo "      measurement. Then cite that ruling in $register. Ruling first, row second."
  exit 1
fi

echo "PASS  stage 95 numerals ratchet          $n_hits live hit(s), all registered; $n_ruled ruled row(s)"
if [[ -n "$stale" ]]; then
  echo "      NOTE: registered row(s) no longer observed — citation fixed, or the row is dead weight:"
  printf '%s\n' "$stale" | sed 's/^/        STALE /'
fi
exit 0
