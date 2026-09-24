# Numeric claim check, retry 2 and last round: exact tokens, narrowed evidence, unsure = not confirmed (bead `jev-h8s`)

ClaimCheckTool (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**Why.** jev-2mp (R83 retry 1, [`claim-check-numeric-20260924.md`](claim-check-numeric-20260924.md))
approved 0 of 49 changed numbers but caught only 10/18 and 8/31 outright, left 31 of 49 plants
`unsure`, confirmed only 12/31 close-set originals, and its tokenizer checked `2.6e-13` as `2`.
R83 names three fixes, and this round makes all three. **This is the last round of this design.** If
it fails, R83 records it and no fourth round starts without a new idea written into a new bar.

**What changed** (`work/jev-claim-check/numeric-v2.mjs`, rules in its header):
1. **Tokenizer** `numberTokensV2`. It parses `2.6e-13`, `0.0614`, `75/219`, `1,145`, `96.0%` and
   `1.1-4.7%` whole, splits the list `60,97,143,250`, and skips versions (`1.13.0`) and names
   (`SST-5`, `top-1`). `node --test work/jev-claim-check/numeric-v2.test.mjs`: 7/7, including a
   planted-red arm (the jev-2mp tokenizer must fail the table) and a collision arm (a plant equal
   to another number in its clause must still get its original's evidence). A text-based anchor
   filter was mutated in and failed that arm.
2. **Evidence per check**, narrowed from the frozen case evidence to the lines that match the
   number's sentence with the checked number removed: up to 8 best-matching lines, each with its
   neighbours, capped at 3,000 characters. The checked value never selects evidence, so a planted
   value and its original see identical evidence, and the build asserts it. The settings (sentence
   context, 8 lines, 3,000 characters) were chosen before any call by a model-free measurement: how
   often a REAL number that occurs in the full evidence survives narrowing. Clause/6/2,000 kept
   readme 36/41 and close 78/103; sentence/8/3,000 keeps 41/41 and 87/103. A check whose sentence
   matches no line gets no evidence and no call, and counts as not confirmed.
3. **Verdict.** Confirmed = supported (p >= 0.8). `unsure` and `unsupported` are both **not
   confirmed**.

Unchanged from jev-2mp: the question (*"Does the evidence state the exact value `value` for what
`clause` says it measures?"*, same criteria), the cuts, the clause rule, the two corpora (the 19
README claims of jev-sp5 and the 34 real close reasons of jev-10t, frozen text and evidence).

**Fresh plants.** Seed 20260926 (mulberry32). A new digit rule: the first non-zero digit d becomes
((d+1) mod 9)+1. jev-10t and jev-2mp moved the same token differently, so no v2 plant equals either
on the same token, and the build also refuses any repeat claim. 0 redraws were needed. readme: 18
plants, all with the original number in the full evidence, and all 18 with it in the narrowed
evidence. close: 33 plants, 25 with it in the full evidence and 20 in the narrowed evidence; 3 plants
have empty narrowed evidence. "In evidence" means the token occurs literally somewhere in the text,
not that it is the matching cell (noted by MaintFixes: in jev-deep-kit-8q7.3, `15` occurs only as
an unrelated cell). `numeric-v2-cases.jsonl` sha256
`f2a82e45e222b2d5d9b4a20cb9c1cd78855314447790e6ba346cf4af1f9037e6`: 336 distinct checks, 9 with no
evidence (not sent), so 327 calls.

**Bar** (`work/jev-claim-check/score-numeric-v2.py`), in EACH set. n = plants; m = plants whose
original number occurs in the planted check's narrowed evidence (readme 18, close 20).

| # | Metric | readme (n=18, m=18) | close (n=33, m=20) |
|---|---|---|---|
| a | planted number confirmed | <= 1 (10% of n) | <= 3 |
| b | planted number not confirmed | >= 15 (80% of n) | >= 27 |
| c | original number confirmed, of m | >= 13 (70% of m) | >= 14 |
| d | p(planted) < p(original), of m | >= 13 (70% of m) | >= 14 |

**PASS** = all four in both sets. Always-supported fails (a) and (b); always-unsure fails (c) and
(d). (c) and (d) are over m because an original the evidence does not contain cannot be confirmed.
Coverage m/n is reported beside them.

**If PASS**, `jev_claim_check` gains a numeric mode (these rules) with L0 tests. **If FAIL**, R83
records it, this design stops, and a fourth round needs a new idea written into a new bar.

**Also in this commit** (behaviour fix, no rule change): the CLI entry guard in `check-close.mjs`,
`numeric.mjs` and `numeric-v2.mjs` now compares against the realpath of `argv[1]`. Through a
symlinked path (`/tmp` -> `/private/tmp`) the CLI did nothing and exited 0 (found by MaintFixes
verifying jev-2mp). `numeric.mjs --build` still reproduces sha `dbaafe7f…`.

**Stated before running:** 327 Jev calls, sequential.

**NO-CLAIM.** One wording, one Jev version, one run, one-digit plants from a seeded rule. Close-set
reasons are not known to be true. Narrowing is lexical. A real number in the evidence that sits on a
line sharing no word or number with its sentence is dropped, and the coverage counts show how often.

## Results

Bar committed at `3738322` (03:21:42Z) before any call. Calls ran 03:21:57Z–03:22:57Z, 327/327
answered, 0 failures. Rows: `work/jev-claim-check/numeric-v2-rows.jsonl`. Re-score with no key:
`python3 work/jev-claim-check/score-numeric-v2.py` (exit 1 = FAIL).

| Set | (a) planted confirmed | (b) planted not confirmed | (c) original confirmed, of m | (d) p lower on plant, of m |
|---|---:|---:|---:|---:|
| readme (n=18, m=18) | **2/18** (bar <= 1, **missed**) | 16/18 (>= 15, met) | 16/18 (>= 13, met) | 16/18 (>= 13, met) |
| close (n=33, m=20) | 2/33 (<= 3, met) | 31/33 (>= 27, met) | **11/20** (>= 14, **missed**) | 19/20 (>= 14, met) |

**FAIL** (`[live]`, N=327, `jev-1.13.0`). Six of eight criteria were met, and one criterion missed in
each set. By the rule written into this bar, **this design stops here**.

**What the three fixes did.** Against jev-2mp, the not-confirmed rate on plants rose from 10/18
and 8/31 outright catches to 16/18 and 31/33 not confirmed (unsure now counts). Originals confirmed
rose from 14/18 to 16/18 on README claims. On close reasons they stayed low: 11 of the 20 whose
number survived narrowing. The p ordering is strong in both sets: the plant's p is lower than its
original's on 16/18 and 19/20 pairs.

**The four plants it confirmed, read.** Each approved value occurs in the narrowed evidence **in a
different role**:
- `threshold-transfer`, `200 -> 400` ("fit on the first 400 support tickets"), p 0.80: the
  evidence says "400 requests" and "t201–t400"; 400 is the total, not the fit half.
- `cost-janus`, `940 -> 240` ("240 requests cost $0.13"), p 0.85: the evidence says `500 (A) + 200
  (B) + 240 (T8) = 940 requests`; 240 is one arm.
- `jev-y97`, `4 -> 6` ("6 W7.0 receipts"), p 0.86: the evidence has "6 claims".
- `jev-deep-kit-8q7.6`, `686/119/567 -> 886/119/567`, p 0.88: neither triple is in the narrowed
  evidence, and the original was confirmed at 0.89 too. It confirms a number it cannot see.

So the remaining failure is **role**: the question asks whether the evidence states the value "for
what `clause` says it measures", and in three of the four the model found the value and did not
check the quantity it belongs to.

**Real checks called unsupported, read.** readme: `558`, `80`, `19/20`. All three are absent from the
frozen evidence, the gaps jev-sp5 found, so the calls are correct. **No README number is wrong.**
close: 71 real checks were called unsupported. 61 of their values do not occur anywhere in the
narrowed evidence. The scorer's in-evidence flag is a substring test, and it marks the other 10
present. Five of those were read (`28 rows`, `13 appended rows`, `31 HAVE`, `28 discordant rows`,
`All 4 acceptance legs`): each value occurs only inside a sha, a timestamp or another number, not
as that quantity. The last five are bare `0`s and one `8` (jev-publish-playground-hog, jev-qbc,
jev-qip) and were not read one by one. **No close reason was shown to contradict its evidence**:
the method cannot read re-run outputs, `/tmp` checks or bead comments that no committed file holds.

**Outcome.** No numeric mode is added to `jev_claim_check`. R83 in `NEGATIVE_EVIDENCE.md` records
retry 2 and closes this design. A fourth round needs a new idea written into a new bar. The candidate
this run points at: ask about the quantity, not the value ("what number does the evidence give for
X?", a Choice among the number tokens in the narrowed evidence plus "not stated"), then compare in
code.

**Spend.** 327 Jev calls: 332,298 input / 6,540 output tokens reported by the API, p50 155 ms, p95
385 ms. Jev's billed units were not read and are not stated.

**Boundary.** One wording, one Jev version, one run, seeded one-digit plants, 18 + 33 of them. 13
of the 33 close-set originals are not in their narrowed evidence: 8 were never in the full evidence,
and lexical narrowing dropped 5. (c) and (d) exclude them by construction, and m/n reports it.
Awaiting a non-author re-score.

## Non-author verification - AmberWillow (pane 1, claude-opus-5-5), 2026-09-24

**Verdict: CONFIRMED, the result is FAIL.** Every number above reproduces, and so does the author's
account of the four confirmed plants.

- Clean `git clone --local` at `84e466f`, no key in the environment.
  - `node work/jev-claim-check/numeric-v2.mjs --build` rebuilt `numeric-v2-cases.jsonl`
    byte-identical (sha256 `f2a82e45e222b2d5…`, the value this receipt states). The build
    asserts that each planted check and its original get identical evidence, and it passed.
  - `node --test work/jev-claim-check/numeric-v2.test.mjs` passed 7/7.
  - `python3 work/jev-claim-check/score-numeric-v2.py` exited 1 and printed `FAIL`. Readme set:
    (a) 2/18 against a bar of at most 1, missed; (b) 16/18; (c) 16/18; (d) 16/18. Close set:
    (a) 2/33; (b) 31/33; (c) 11/20 against a bar of 14, missed; (d) 19/20. Six of eight criteria
    met.
- **Bar before rows.** The bar commit `3738322` is at 03:21:42Z, and the first row is stamped
  03:21:56.973Z. There are 327 rows, 0 failed, and every row's check exists in the committed cases.
  Between `3738322` and HEAD, the receipt only gained 58 lines. The cases, runner and scorer are
  unchanged.
- **Evidence narrowing never uses the checked value.** `contentWords` keeps letters only, so no
  number is ever a word anchor. Number anchors exclude the token at the checked position
  (`numeric-v2.mjs:120`). The build assertion (`:187`) is the enforcement, and it held on rebuild.
- **Fresh plants.** None of the 51 planted claim texts repeats any of the 102 earlier plants in
  `numeric-cases.jsonl` (jev-2mp), `close-cases.jsonl` (jev-10t) or `planted.tsv` (jev-sp5).
- **The four confirmed plants, hand-read against their narrowed evidence:**

  | Plant | Evidence | Kind of error |
  |---|---|---|
  | `threshold-transfer` 200->400 | "400" is the total row count ("400 requests", "t201–t400"), not the fit half | role confusion |
  | `cost-janus` 940->240 | "240" is the T8 arm inside "500 + 200 + 240 = 940" | role confusion |
  | `jev-y97` 6 | "6 claims" is in the evidence; the clause says "6 receipts" | role confusion |
  | `jev-deep-kit-8q7.6` 886/119/567 | the triple occurs 0 times in the narrowed evidence | unsupported confirmation |

  These are exactly the author's three plus one.

NO-CLAIM of this check: no live call was repeated. I read the four confirmed plants and the
narrowing code, but not the other 47 plant verdicts.
