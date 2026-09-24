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

## Results

Bar committed at `993414f` (03:29:43Z) before any call. Calls ran 03:29:52Z–03:30:39Z, 243/243
answered, 0 failures. Rows: `work/jev-claim-check/numeric-choice-rows.jsonl`. Re-score with no key:
`python3 work/jev-claim-check/score-numeric-choice.py` (exit 1 = FAIL).

| # | Metric | readme | close |
|---|---|---:|---:|
| F | feasibility | **8/8** (bar >= 7, met) | |
| a | digit plants confirmed | 0/18 (<= 1, met) | 0/33 (<= 3, met) |
| b | role plants confirmed | **1/14** (<= 1, met) | **1/18** (<= 1, met) |
| c | real numbers confirmed, of m | **20/30** (>= 21, **missed by 1**) | **35/69** (>= 49, **missed**) |

**FAIL** (`[live]`, N=243, `jev-1.13.0`). The feasibility arm passed and the role problem is largely
solved, but the tool does not confirm enough true numbers. By the rule written into this bar,
**`jev_claim_check` is permanently non-numeric and this thread stops.**

**What the Choice fixed.** Role plants, the failure that closed jev-h8s, were confirmed 2 of 32
times (1/14, 1/18). Digit plants: 0 of 51. The feasibility arm went 8/8: on a clean single-number
sentence the Choice picks the right token every time, including `2.6e-13`, `1,145` and `96.0%`.

**What it could not do.** It confirms too few true numbers once the evidence is a real receipt: 20
of 30 README numbers and 35 of 69 close-reason numbers that were among the options. When it missed,
it chose another evidence number (README 8, close 19) or `not_stated` (2, 15). Read one by one, the
misses are role confusion in the other direction: the model picks the wrong quantity from a dense
table.
- `192 of [N] right against 252` -> chose `192`.
- `[N] of 400 right against 252` -> chose `400`.
- `[N] requests cost $0.13` -> chose `0.1274`, the cost. This also produced one of the two confirmed
  role plants (`940 -> 0.1274`).
- `Agent-failure attribution: 28 of 35 against grok's [N]` -> chose `35`.
- `Live [N] top-1` -> chose `71`.
- `lexical [N]` -> chose `0.2828`.

The close set adds bare `0`/`1` exit codes and counts (`rc=[N]`, `[N] REFUTED`) that its evidence
states in another form or not at all. The second confirmed role plant, `jev-publish-hero-ulo`,
`16 -> 9`, took the `9` of `16:9` for the masked `16`.

**No README number or close reason was shown wrong.** Every README number that was not confirmed is
present among its options and is the registered, correct value, so each miss is a tool miss. The
close reasons were not adjudicated beyond that.

**Outcome.** No numeric mode. R83 records `jev_claim_check` as permanently non-numeric; the tool stays
a sentence-level advisory, the thing it passed on in jev-sp5. No further numeric round is planned.

**Spend.** 243 Jev calls: 517,179 input / 44,361 output tokens reported by the API (Choice answers
carry a probability per option, hence the larger output), p50 169 ms, p95 341 ms. Jev's billed units
were not read and are not stated.

**Boundary.** One wording, one Jev version, one run, 32 role plants and 51 digit plants from one
seed. m excludes numbers the narrowing dropped or the 60-option cap cut (11 README checks hit the
cap). Awaiting a non-author re-score.

## Non-author verification — ConfidenceCascade

ConfidenceCascade (background agent of pane 1; not the author), 2026-09-24, keyless, from a fresh
`git clone --local` at `3c98ee6` into `/tmp/cc-25r.j8U64F/jev`. Node v22.22.0. No live call, $0.

| # | Check | Result |
|---|---|---|
| 1 | `node work/jev-claim-check/numeric-choice.mjs --build` in the clone, `TYPESAFE_API_KEY` unset | HOLDS. It prints the bar's counts (readme 46 checks, m 30, 18 digit / 14 role plants, 11 capped; close 197, m 69, 33 / 18, 8 not askable; 235 + 8 calls). `numeric-choice-cases.jsonl` is rebuilt byte-identical (`cmp` clean, sha256 `5dbf534e…b5e6ea`). |
| 2 | `node --test work/jev-claim-check/numeric-choice.test.mjs` | HOLDS: 5 pass, 0 fail. |
| 3 | `python3 work/jev-claim-check/score-numeric-choice.py` | HOLDS, exit 1 (FAIL). Feasibility 8/8. Role plants confirmed 1/14 and 1/18. Digit plants 0/18 and 0/33. True numbers confirmed 20/30 and 35/69. The miss split (readme: not_stated 2, another number 8; close: 15, 19) and both role-plant tables match the Results above. |
| 4 | A plant and its original get byte-identical state | HOLDS. For all 83 plants, the claim differs from its original only in the value span. The masked clause equals the original clause with exactly that value replaced by `[N]` (83/83). The plant's `call` equals the original check's `call` (83/83). That `call` recomputes as sha256(set, masked clause, evidence) on the 80 askable plants; the 3 remaining digit plants sit on checks with no options and have no call, like their originals. The runner sends `{clause: masked, evidence}` with the check's options (`numeric-choice.mjs:193`), so the claimed value is never in the question. The rows hold 243 distinct calls: 235 corpus, 0 missing, plus 8 feasibility. On 4 plants the planted string also occurs elsewhere in the masked clause (for example `…([N]:9` for `16 -> 9`). The original gets the same text, so this is not a leak. |
| 5 | Seed 20260927 plants repeat none from jev-10t, jev-2mp or jev-h8s | HOLDS. There are 132 earlier plant claims (every `truth: false` claim in `close-cases.jsonl`, `numeric-cases.jsonl` and `numeric-v2-cases.jsonl`, each file at every committed revision, one each) and 83 new plant claims, with 0 overlap. 0 plants needed a redraw, and no plant equals a real claim. |
| 6 | Timing | `993414f` is committed at 03:29:43Z. The first row is appended at 03:29:51.995Z (`feasibility-0`, latency 341 ms), so the first call started at about 03:29:51.65Z, after the bar. |

**Hand-read: the 2 confirmed role plants.** Both come from the tool choosing the wrong quantity for
the true claim too. Neither is a correct reading of the plant.
- `cost-janus`, `940 -> 0.1274`: for `[N] requests cost $0.13 in one run` the model put 0.98 on
  `0.1274` (the dollar cost) and 0.01 on `940` ("= **940 requests, 940 answered**").
- `jev-publish-hero-ulo`, `16 -> 9`: the masked clause is `visual/hero.jpg 1920x1080 ([N]:9`. It
  keeps the `:9`, and the model put 0.77 on `9` and 0.19 on `16` (both options quote
  `"aspect": "16:9"`). A partner number left in the clause steers the pick. This is a masking
  artifact on top of the role confusion.

**Hand-read: 5 true-number misses (README).**
- `cost-jevcal` 560, `[N] cost $0.011 of input in another.`: chose `0.0113` (p 0.86), the cost,
  over `560` ("560 live calls", p 0.04). Wrong quantity, same pattern as `cost-janus`.
- `tool-routing-refused` 400, `192 of [N] right against 252 …`: chose `192` (p 0.99), a number
  already visible in the clause, over `400` (`"n":400`, p 0). Wrong quantity.
- `inj-fresh-discordants` 61, `and [N] against 5 in the fresh run`: chose `640/662` (p 0.44) over
  `61` ("Discordants jev-only 61 / llm-only 5", p 0.13). Wrong quantity.
- `inj-fresh-rescore` 640, `…score.py # fresh run: [N]`: chose `not_stated` (p 0.58) although the
  evidence has "Exit 0 iff 640 (Jev)" (p 0.10). A miss.
- `agent-attribution` 23, `… 28 of 35 against grok's [N]`: chose `35` (p 0.5), which is wrong. **Finding:**
  the option that counts as "right" (`n13`, `23`) is described at its first occurrence, "dylan
  23", an unrelated count. Grok's figure is the separate token `23/35` (`n49`), which
  `equalsValue` does not match to `23`. So this check is in m only through a coincidental token.
  Removing it gives readme 20/29 against the same bar of 21, and (c) still fails. The receipt's
  "every README number that was not confirmed is present among its options" holds by value, but
  not always as the same quantity. m counts value matches, not role matches.

**Verdict: FAIL reproduces.** Every number in the Results, the byte-identical rebuild, 5/5 tests,
the no-leak property and the plant novelty hold from committed files. The one finding
(`agent-attribution`'s m match is coincidental) does not change the verdict. NO-CLAIM: this re-scores
committed rows; it does not re-run Jev, and it hand-reads 7 cases (2 confirmed role plants, 5 of the 44 true-number misses), not all.
