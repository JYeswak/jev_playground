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
# --selftest — ruled into this file rather than stage 80 by pane 3
# (docs/demos/duel-2/runs/stage95-arms-ruling-20260918T162059Z.json, a575a1d): "PROMOTE into 95's own
# --selftest, not 80; co-locate test with logic. Hand-run unacceptable — a comm-direction inversion
# would fail toward allowlist SILENTLY."
#
# That named failure is the whole reason these arms are code and not a transcript. The two comm(1)
# calls below differ only in -23 versus -13. Swap them and the gate stops reporting new hits and
# starts reporting stale ones, which means it PASSES on an unruled numeral forever — a green that
# means the opposite of what it says. No human re-reading a green row would catch that.
if [[ "${1:-}" == "--selftest" ]]; then
  self="${BASH_SOURCE[0]}"
  root_s="${JEV_REPO:-$(cd "$(dirname "$self")/../.." && pwd)}"
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  live="$root_s/foundation/numerals-ruled.tsv"
  fails=0; arms=0
  arm() { # name expected_rc register_path
    local name="$1" want="$2" reg="$3" got
    JEV_NUMERALS_REGISTER="$reg" JEV_REPO="$root_s" bash "$self" >/dev/null 2>&1 && got=0 || got=$?
    arms=$((arms+1))
    if [[ "$got" == "$want" ]]; then
      printf '  ok   %-34s rc=%s\n' "$name" "$got"
    else
      printf '  FAIL %-34s rc=%s want=%s\n' "$name" "$got" "$want"; fails=$((fails+1))
    fi
  }

  cp "$live" "$tmp/full.tsv"
  arm "baseline: all hits registered" 0 "$tmp/full.tsv"

  # A ruled row removed must reappear as UNREGISTERED. This is the arm that dies under a comm swap.
  grep -v $'^demo-7-signals-starter\t76.25' "$live" > "$tmp/short.tsv"
  arm "ruled row removed -> RED" 1 "$tmp/short.tsv"

  arm "register missing -> refuse" 1 "$tmp/absent.tsv"

  # A dead row is surfaced, not fatal: the citation may simply have been fixed.
  cp "$live" "$tmp/stale.tsv"
  # The ghost row must carry a VALID class and a real receipt: an invalid one now REDs on the class
  # check, which is correct behaviour and would make this arm test the wrong thing. A stale row has no
  # live hit, so the class check skips it and only the STALE surfacing is under test here.
  printf 'ghost\t999\tLEGITIMATE_ROUNDING\tdocs/demos/duel-2/runs/numerals-hold-ruling-20260918T161328Z.json\n' >> "$tmp/stale.tsv"
  arm "dead row -> PASS with STALE" 0 "$tmp/stale.tsv"

  # ABSENCE SPEC, quoted from the ruling: "empty register + zero hits = PASS-with-EMPTY-note (failing
  # would demand pre-registration = laundering); empty + hits already REDs via new-hits path." Live
  # hits are nonzero here, so an empty register MUST be RED by the new-hits path — which is the half
  # of the spec this repo can actually witness today. The zero-hit half is unwitnessable until some
  # verdict stops citing an unopenable numeral, and is NOT asserted.
  printf '# empty register\n' > "$tmp/empty.tsv"
  arm "empty register, hits live -> RED" 1 "$tmp/empty.tsv"

  # CLASS-TRUTH ARMS. Arm 6 replays the exact row I committed at 8a46915 and had to retract: the
  # numeral 283 classed as a unit change when no single number in the census maps to it. All five
  # membership arms above PASS on that row, which is the whole reason this half of the gate exists.
  sed 's/LEGITIMATE_DERIVED_ROLLUP_TRUNCATION/LEGITIMATE_UNIT_CHANGE_KLOC/' "$live" > "$tmp/falseclass.tsv"
  arm "false class (my 8a46915 row) -> RED" 1 "$tmp/falseclass.tsv"

  # And the inverse: calling an honest rounding a derived rollup must also RED, or the gate catches
  # only one direction and a lazy "DERIVED" label becomes a universal pass.
  sed 's/LEGITIMATE_ROUNDING_AND_UNIT_CHANGE/LEGITIMATE_DERIVED_ROLLUP/' "$live" > "$tmp/wrongway.tsv"
  arm "rounding mislabelled derived -> RED" 1 "$tmp/wrongway.tsv"

  # A class outside the closed vocabulary is not silently tolerated.
  sed 's/LEGITIMATE_DERIVED_ROLLUP_TRUNCATION/VIBES/' "$live" > "$tmp/vocab.tsv"
  arm "class outside vocabulary -> RED" 1 "$tmp/vocab.tsv"

  if (( fails > 0 )); then echo "stage 95 selftest: $fails arm(s) FAILED"; exit 1; fi
  echo "stage 95 selftest: $arms arms ok"
  exit 0
fi


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

# SEMANTIC CLASS GATE — authorized by pane 2's non-author adjudication
# (docs/demos/duel-2/runs/numeral-adjudication-20260918T162500Z.json, c7615a2): "Stage95 current PASS
# is membership-only and cannot validate class truth ... BUILD_FOLLOW_UP_REQUIRED; current green is
# not semantic validation." It passed the creation gate there with all four fields named, which is the
# only reason this exists — I wrote the register and the gate, so I do not get to authorize my own
# successor.
#
# THE OBSERVED DEFECT IS MINE. I registered MU-H1-todo-judge/283 as LEGITIMATE_UNIT_CHANGE_KLOC. That
# class asserts the value IS in the receipt in another unit; it is not there in any unit — it is a sum
# over sixteen per-repo kloc floats with no total field. All five membership arms passed on that false
# row, and a human opening a control caught it.
#
# WHAT IS MECHANICALLY CHECKABLE, and no more: each class name makes a claim about LITERAL PRESENCE in
# the cited receipt, and literal presence is decidable by grep.
#
#   *ROUNDING* / *UNIT_CHANGE*   the value is PRESENT in some form -> a literal must exist
#   *DERIVED* / *ROLLUP*         the value is COMPUTED, not stored -> the literal must be ABSENT,
#                                because a stored literal makes "derived" the wrong class
#   *MISPOINTED*                 the receipt is the wrong one -> no presence claim to check
#
# NOT CHECKABLE, deliberately not attempted: whether the derivation is CORRECT. Summing the right
# sixteen fields is human judgment — I got it wrong once today by summing thirty-two. This checks that
# a class does not contradict the file it cites, nothing more.
classes_bad=""
while IFS=$'\t' read -r cand num class receipt; do
  [ -n "${cand:-}" ] || continue
  case "$cand" in \#*) continue ;; esac
  if [ -z "${receipt:-}" ]; then
    classes_bad="$classes_bad|$cand/$num: row cites NO receipt — a class with no evidence file is unfalsifiable"
    continue
  fi
  if [ ! -f "$root/$receipt" ]; then
    classes_bad="$classes_bad|$cand/$num: cited receipt does not exist: $receipt"
    continue
  fi
  # THE EVIDENCE FILE IS THE ONE STATUS CITES, NOT THE RULING RECEIPT. Column 4 holds the ruling — the
  # pane's judgment — and a ruling file naturally CONTAINS the numeral it is ruling on. Checking
  # presence there inverted the whole gate on its first run: it flagged the TRUE class and passed the
  # FALSE one I had committed. The verifier already prints the receipt STATUS cites for each hit, so
  # that is what a presence claim must be checked against.
  evidence="$(printf '%s\n' "$out" | sed -nE "s|^[[:space:]]*UNOPENABLE ${cand}: '${num}' does not appear in (.*)$|\1|p" | head -1)"
  if [ -z "$evidence" ]; then
    # No live hit for this row: it is stale, already surfaced below, and has no presence claim to test.
    continue
  fi
  if [ ! -f "$root/$evidence" ]; then
    classes_bad="$classes_bad|$cand/$num: STATUS cites a receipt that does not exist: $evidence"
    continue
  fi
  # PRESENCE IS THE WRONG TEST, AND MY FIRST VERSION USED IT. Every row in this register is a numeral
  # the verifier already proved LITERALLY ABSENT — that is why it is a hit at all. So "the literal must
  # exist" can never pass, and on its first run the gate REDed the two honest roundings. The checkable
  # claim is NUMERIC: a rounding or unit change means some number in the receipt maps to the cited one
  # by rounding and/or a power of ten. A derived rollup means NO single number does, because the value
  # is a sum over parts.
  #
  # Decidable and narrow. It does NOT check that a sum is the RIGHT sum — that stays human judgment.
  verdict_class="$(JEV_N="$num" JEV_F="$root/$evidence" python3 "$root/foundation/numeral-maps.py")"
  case "$class" in
    *ROUNDING*|*UNIT_CHANGE*)
      [ "$verdict_class" = MAPS ] || classes_bad="$classes_bad|$cand/$num: class $class claims a rounding or unit change, but NO number in $evidence maps to '$num' by rounding or a power of ten" ;;
    *DERIVED*|*ROLLUP*)
      [ "$verdict_class" != MAPS ] || classes_bad="$classes_bad|$cand/$num: class $class claims the value is COMPUTED from parts, but a single number in $evidence already maps to '$num' — stored, not derived" ;;
    *MISPOINTED*) : ;;
    *) classes_bad="$classes_bad|$cand/$num: class $class is outside the closed vocabulary (ROUNDING / UNIT_CHANGE / DERIVED / ROLLUP / MISPOINTED)" ;;
  esac
done < <(grep -vE '^[[:space:]]*(#|$)' "$register")

if [ -n "$classes_bad" ]; then
  echo "FAIL  stage 95 numerals ratchet          a register row's CLASS contradicts the file it cites."
  printf '%s' "$classes_bad" | tr '|' '\n' | grep -v '^$' | sed 's/^/      /'
  echo "      A class is a claim about evidence. Fix the class, or fix the citation — not the gate."
  exit 1
fi

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
