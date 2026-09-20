# Non-author review: four CASS/mail mines (2026-09-20)

Level: `test` (recomputation from pinned `work/cass-mail-mines/exports/cass-dig-rows.jsonl`
n=138 + scorer source reads; mines NOT re-run, export NOT regenerated; live DBs NOT
re-queried). I authored none of the four.

## Dig-subset breakdown (HELD): WEAKENED, direction stands, magnitude is a constant

- Recomputed from pinned file: pooled dig 8/138=0.058 vs invent 22/138=0.159 ✓;
  S_wrong dig 8/16=0.500 vs invent 4/16=0.250 ✓. Arithmetic exact.
- Loss attack: the 2:1 ratio is doing the magnitude work, not the direction.
  S_wrong at 1:1 is a 4:4 TIE (all 4 y1 rows have hits>0, so no invent-loss
  term exists on either side); dig wins iff dig-cost < invent-cost. Direction
  (dig never beats invent here) holds ∀c≥1; the "doubles the loss" 2× is the
  asserted constant, and pooled 0.058→0.029 at 1:1. If the verdict is read as
  "dig loses", it needs c>1 stated; at c=1 it is "dig ties".
- Proxy attack (the serious one): the 4 dug-y0 rows ("no such field/key",
  "keys present", ".distribution") are zeros from Y's STRICT branch (absence
  query + snippet must carry requireKey-evidence), while the 4 y1 rows
  ("missing field", "field does not exist", ...) pass the LENIENT generic bar
  (receipt-shaped suffices) because they miss the ABSENCE regex. The inversion
  is 4 strict-zeros vs 4 lenient-ones. Sensitivity: flipping ONE proxy zero to
  1 → dig 0.375 vs invent 0.3125 (still loses); flipping TWO → dig wins. The
  HELD hangs on ≤2 mechanical labels of a proxy the ruling admits is
  mechanical. Snippets are not in the export, so human calibration is
  impossible from this file — that grading is the load-bearing next step
  before this HELD constrains any playbook.
- Slice attack: table n sums to 150, not 138 — 12 "pass N" rows match both
  their content regex AND S_pass_probes and are counted twice (scorer matches
  each slice independently). Dilutes both sides equally (S_wrong ex-pass:
  0.8/0.4 at c=2, same 2:1 ratio), so verdict-neutral, but the table as
  printed is wrong and S_topical is the only disjoint slice. File as defect.

## A11 join yield (HELD): CONFIRMED, with the filed double-count noted

- F3 logic sound: K1 20 exact paths, plants P1/P2 zero-join by construction
  of exact-match; K2 token-intersect 0 and K3 UNMEASURED (not yield-0) is the
  right discipline. /Users/josh mega-pair limit stated honestly.
- 10 named + "10 further" = 20 ✓ consistent. Live-DB monotonicity already
  NO-CLAIMed; HELD is about the method (cheap covers id-joins), which does
  not depend on tonight's row counts.
- A11-gates-A18: same 20 (A18's pair 66↔617 is the precise clutterfreespaces.ios
  pair from the K1 table). Gating not vacuous for the measured pair; for the
  other 19 see A18 below. "A18 may proceed" has now been exercised once.

## A12 refusal (REFUSE): CONFIRMED, and the self-discount understates

- Tie arithmetic holds: 2 refused-empty vs 2 killed-good, F1 fires at boundary.
- Code read confirms R condition-2 IS query-regex (`ABSENCE.search(query)`,
  same family as the slice regex), so the author's "fitted, not generalizing"
  discount is exactly right — and extends one level deeper: Y's strict branch
  also keys on query wording, so this export grades query-wording against
  query-wording throughout. REFUSE stands; no eligible-grader exists in these
  columns (n_receipt_shaped maxed on all 4 empties — refuted as separator ✓).

## A18 off-bus (REFUSE pair-66; "all 20" generalization): SPLIT

- Pair 66↔617: CONFIRMED (conductor reproduced era gap; μs/ms normalization
  caught and fixed in scorer header — same-number-wrong-reason eliminated).
- "All 20 K1 pairs time-disjoint": WEAKENED — `score_a18_offbus.py` (94
  lines) covers ONLY pair 66↔617; no committed code or table backs the
  all-20 range check. The generalization is undescribed work. ±24h window
  choice is moot for pair 66 (35-day gap) but unexamined for the other 19.

## Overall: publishable as HELD/HELD/REFUSE/REFUSE-with-limits, none promoted

Yes — with four amendments in the receipt: (1) S_wrong direction needs c>1
stated, 2× magnitude is the constant; (2) HELD hangs on ≤2 proxy labels,
human snippet grading required before playbook use; (3) slice table
double-counts 12 rows (sums to 150); (4) A18's all-20 claim is unverified,
only pair 66 is evidenced. The inversion is NOT a pure loss-function
artifact (tie at worst for c≥1), but it is a proxy-calibration artifact
waiting for its second reader.

## Ledger line

REVIEW four mines — HELD/CONFIRMED(A11) WEAKENED(subset,A18-generalization)
CONFIRMED(A12) — publishable with 4 amendments, none promoted — NO-CLAIM:
no live re-query, no snippet reads, proxy-vs-human uncalibrated.
