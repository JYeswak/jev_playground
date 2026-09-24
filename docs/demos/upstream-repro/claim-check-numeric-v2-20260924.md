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
