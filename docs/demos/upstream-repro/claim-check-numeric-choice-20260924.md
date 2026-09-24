# Numeric claim check by Choice: hide the number, ask which evidence number is that quantity (bead `jev-25r`)

ClaimCheckTool (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**Why a different primitive.** jev-h8s (R83 retry 2,
[`claim-check-numeric-v2-20260924.md`](claim-check-numeric-v2-20260924.md)) closed the Noul design.
3 of its 4 false confirmations were **role confusion**: the planted value was in the evidence as
another quantity (`240` is one arm of `940`; `400` is the total, not the fit half), and a Noul asked
"does the evidence state X" finds X anywhere. This round never shows the model the claimed value. The
number is masked in its clause as `[N]`, and a Jev **Choice** picks which of the evidence's own number
tokens is that quantity, or `not_stated`. Code then compares the pick with the claimed value.
**This is the last round.** If it fails, R83 records `jev_claim_check` as permanently non-numeric and
the thread stops.

**Instrument.** `work/jev-claim-check/numeric-choice.mjs` (rules in its header). Choice instructions:
*"`clause` is a claim with one number replaced by [N]. Which number in `evidence` is the value that [N]
stands for, meaning the evidence's figure for the same quantity? Choose not_stated if the evidence
gives no figure for that quantity."* The options are every distinct number token in the narrowed
evidence, in order, capped at 60. Each is described by the token and the 40 characters on either
side of its first occurrence. `not_stated` is added. A value is **confirmed** when the chosen token
equals it exactly (thousands commas ignored), or when the evidence value rounded to the claim's
decimal places equals it. A claim may round its evidence; the evidence may not round the claim.
`node --test work/jev-claim-check/numeric-choice.test.mjs`: 5/5.

**Same corpora, same evidence.** The real checks of `numeric-v2-cases.jsonl` (jev-h8s) are used as
they are: the 19 README claims and the 34 close reasons, the same clause per number, and the same
narrowed evidence. Because the value is masked, **an original and its plant get the identical
question**, and one call answers both; only the comparison differs. For this reason a digit plant
whose new value is not an evidence token cannot be confirmed at all, and (a) mostly tests that
property. The real test is (b).

**Fresh plants**, seed 20260927 (mulberry32):
- **digit**: one per claim. The first non-zero digit moves +7 (mod 9); earlier rounds moved it +5
  and +2, or moved another digit +4. The tests assert no collision with either earlier rule.
- **role**: one per claim that allows it. The claimed value is replaced by ANOTHER number token from
  the same check's options, which is the role-confusion case by construction. Reported separately.

Counts from `--build` (`numeric-choice-cases.jsonl`, sha256
`5dbf534e02ac50fcea9300d753d1fdce8ceb7d9d632f06bf57b23bc0a9b5e6ea`):

| Set | real checks | m (value among its options) | digit plants (landing on an option) | role plants | notes |
|---|---:|---:|---:|---:|---|
| readme | 46 | 30 | 18 (1) | 14 | 11 checks hit the 60-option cap |
| close | 197 | 69 | 33 (2) | 18 | 8 checks have no option, not asked |

**Feasibility arm.** 8 unambiguous single-number sentences (the `FEASIBILITY` list in the file:
`189`, `639`, `0.0614`, `1,145`, `96.0%`, `2.6e-13`, `30`, `940`), each with one or two distractor
numbers in another sentence, asked the same way.

**Bar** (`work/jev-claim-check/score-numeric-choice.py`):

| # | Metric | readme | close |
|---|---|---|---|
| F | feasibility: expected token chosen | >= 7 of 8 (once) | |
| a | digit plants confirmed | <= 1 of 18 | <= 3 of 33 |
| b | **role plants confirmed** | <= 1 of 14 | <= 1 of 18 |
| c | real numbers confirmed, of m | >= 21 of 30 (70%) | >= 49 of 69 (70%) |

**PASS** = F, and (a), (b), (c) in both sets. Always choosing `not_stated` passes (a) and (b) and
fails (c). **If PASS**: `jev_claim_check` gains a numeric mode with L0 tests. **If FAIL**: R83
records the tool as permanently non-numeric and the thread stops.

**Stated before running:** 243 Jev calls (235 corpus + 8 feasibility), sequential.

**NO-CLAIM.** One wording, one Jev version, one run. The narrowed evidence and its lexical coverage
are inherited from jev-h8s, so m < all real checks. The 60-option cap can cut the right token
(11 README checks). Role plants are drawn at random from the other options, so many are easy
(a fraction for a count). The subtle cases are the minority and are listed one by one.
