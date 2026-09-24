# Does an exact-value question catch a changed number? The R83 retry (bead `jev-2mp`)

ClaimCheckTool (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**Why.** `NEGATIVE_EVIDENCE.md` R83: asked "does the evidence support the claim?" over whole close
reasons, `jev_claim_check` caught 0 of 31 changed numbers and approved 4, including `75/219 ->
35/219` at p 0.91 against evidence that says `75/219` three times. R83's retry condition names two
changes, and this unit makes both: one number per check, and a question that asks for the exact value.

**Instrument.** `work/jev-claim-check/numeric.mjs` (rules in its header). For every number in a
claim, one Noul over state `{clause, value, evidence}`: instructions *"Does the evidence state the
exact value `value` for what `clause` says it measures?"*, criteria `true`: *"The evidence states this
same value for this quantity. A shorter rounding of the evidence's value, or the same value written
as a fraction, percent or decimal, also counts"*, `false`: *"The evidence gives a different value for
this quantity, or does not state it"*. The clause is the claim unit holding the number (split at
sentence ends, `; `, `, `, ` (`, `)`), widened backwards to at least 4 words. Per-check verdict uses
the tool's cuts (supported >= 0.8, unsupported <= 0.2). A whole claim is supported when every check
is, unsupported when any check is.

**Sets**, taken verbatim from files already committed:
- **readme**: the 19 true README claims of `jev-sp5` (`cases.jsonl`) with their frozen evidence. One
  (`official-sdk`) has no number, so 18 have checks.
- **close**: the 34 real close reasons of `jev-10t` that carry evidence (`close-cases.jsonl`). Two
  have no number.

**Fresh plants.** Drawn by `numeric.mjs --build` with seed 20260925 (mulberry32), one per claim that
has an eligible number (any token except a bare 0 or 1). The draw is uniform over eligible numbers
that occur in the evidence, else over all eligible numbers. The drawn number's first non-zero digit
run has its last digit changed (1->5 ... 9->4, 0->4). These plants are nearer the original than
jev-10t's: `75/219 -> 79/219`, `0.0614 -> 0.0618`, `189 -> 184`. The build refuses a plant equal to
any jev-10t plant or diagnostic clause. readme: 18 plants, all 18 with the original number in the
evidence. close: 31 plants, 25 with it in the evidence. `numeric-cases.jsonl` sha256
`dbaafe7f4a0564c1e634ba468ca5824ba7ce04486a1d0e67f1e88f811c4ca379`, 314 distinct checks to ask.

**Bar** (`work/jev-claim-check/score-numeric.py`), in EACH set over its n plants:

| # | Metric | readme (n=18) | close (n=31) |
|---|---|---|---|
| a | the planted number's check called `supported` | <= 1 | <= 3 |
| b | the planted number's check called `unsupported` | >= 11 | >= 19 |
| c | the original number's check (same position, real claim) called `supported` | >= 11 | >= 19 |

(10% floor, 60% ceil, 60% ceil.) **PASS** = all three in both sets. Always-`supported` fails (a) and
(b); always-`unsupported` fails (c). Whole-claim verdicts are reported descriptively, and every real
claim called unsupported as a whole is read against its evidence and classed: the claim is wrong, the
number is absent from the resolved evidence (resolver or registry gap), the check misread it, or the
value is not a measured quantity (a sample size, a seed, a count of calls).

**If PASS**, `jev_claim_check` gains a numeric mode with L0 tests. **If FAIL**, R83 is updated with
this result. The question, cuts and clause rule are not retuned after an answer.

**Stated before running:** 314 Jev calls, sequential.

**NO-CLAIM.** One wording, one Jev version, one run, plants from a one-digit rule. The close set's
labels assume the reasons are right; a real check called unsupported is read, not scored as an
error. The numberTokens rule reads `3.0e-09` as `3`, and such checks stay in as built.

## Results

Bar committed at `8210e02` (03:11:31Z) before any call. Calls ran 2026-09-24T03:11:41.585Z–2026-09-24T03:12:53.050Z, 314/314 checks
answered on the first pass, 0 failures. Rows: `work/jev-claim-check/numeric-rows.jsonl`. Re-score with
no key: `python3 work/jev-claim-check/score-numeric.py` (exit 1 = FAIL).

| Set | (a) planted number called supported | (b) planted number called unsupported | (c) original number called supported |
|---|---:|---:|---:|
| readme (n=18) | **0/18** (bar <= 1, met) | **10/18** (bar >= 11, **missed by 1**) | **14/18** (bar >= 11, met) |
| close (n=31) | **0/31** (bar <= 3, met) | **8/31** (bar >= 19, **missed**) | **12/31** (bar >= 19, **missed**) |

**FAIL** (`[live]`, N=314 checks, `jev-1.13.0`). Both sets must pass and neither did.

**What moved against R83.** The question approved **none of 49** changed numbers (0/18 readme,
0/31 close), against 4/31 for the sentence-level question. That includes plants closer to the
original than R83's: `75/219 -> 79/219` unsupported at p 0.08 (the original supported at 0.97),
`189 -> 184` at 0.07, `0.068 -> 0.063` at 0.18. It still misses the catch floor: 31 of the 49 plants
landed `unsure` (p 0.21–0.71), and `unsure` is not a catch. On the close set the original number
itself is confirmed on only 12 of 31. In 6 of those 31 plants it is absent from the resolved
evidence (all 6 unconfirmed).

**Whole claims (descriptive).** readme real: 11 supported, 4 unsure, 3 unsupported, 1 without a
number; readme planted: 0 supported, 8 unsure, 10 unsupported. close real: 5 supported, 13 unsure, 14
unsupported, 2 without a number; close planted: 0 / 14 / 17.

**Every real claim unsupported as a whole, read.** A check was classed by whether its value occurs
literally in the claim's evidence.
- **readme, 3 claims, 6 checks.** `inj-fresh-haiku` 558: absent from the evidence, which is correct.
  It is the registry gap jev-sp5 found; 087bd32 registered DIFF-RECEIPT.json for it, and this case
  file predates that. `calibration-2026-09-22` 80 and 19/20: absent from the tail window, which is
  correct, the jev-sp5 window miss. The same claim's `0.0614` and `0.0195` are present as JSON
  (`"ece": 0.0614, "brier": 0.0195`) and were called unsupported at p 0.11 and 0.12. That is a
  **tool miss**. `inj-fresh-discordants` "2" comes from `p = 2.6e-13`: the number rule reads
  scientific notation as its leading digit, a **tokenizer artifact**, stated before the run.
  **No README number is wrong.**
- **close, 14 claims, 43 checks.** 32 values are absent from the resolved evidence: re-run outputs,
  reviewer tallies and `/tmp` checks that no cited committed file holds, which the method cannot
  adjudicate. 11 are present. Most are small integers the tokenizer lifted out of a larger form
  (`1` from `Wilson 1.1-4.7%`, `2` from `p=2.74e-05`, `4` from `4.1e-10`, `0` from `rc=0`,
  `30` from "stage 30"). The rest are context misses: `28 discordant rows spot-read`, `0.5` in
  "flipped across 0.5". **No close reason was shown to contradict its evidence.**

**Descriptive safety number.** Of the 93 real checks whose value does not occur literally in the
evidence, 10 were called supported. Some are legitimate restatements (a percent of a stated
fraction); none was read one by one.

**Outcome.** No numeric mode is added to `jev_claim_check`. `NEGATIVE_EVIDENCE.md` R83 is updated
with this retry. The rows and cases stay for a non-author re-score. `numeric.mjs` stays as the
reproducer.

**Spend.** 314 Jev calls: 1,025,280 input / 6,280 output tokens reported by the API, p50 166 ms, p95
449 ms. Jev's billed units were not read and are not stated.

**Boundary.** One wording, one Jev version, one run, one-digit plants from a seeded rule. The
tokenizer artifacts count against the real-claim numbers here but do not touch (a)–(c), whose values
are the plants' own tokens. Close-set labels assume the reasons are right. Awaiting a non-author
re-score.

## Non-author verification — MaintFixes

MaintFixes (background agent of pane 1, not an author of this unit), 2026-09-24. Keyless, no model
call. Clean `git clone --local` in `mktemp -d` (`/tmp/maintfixes-2mp.CFzCIP/jev`) at `d29397c`.

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Bar before rows, text unchanged | `git diff 8210e02 f3b924e` on this receipt; `git diff --stat 8210e02 HEAD -- work/jev-claim-check/{numeric.mjs,score-numeric.py,numeric-cases.jsonl,check-close.mjs}` | 0 lines removed from the receipt (Results only appended); the four files have no diff. Bar 03:11:31Z; row `at` runs 03:11:41.585Z–03:12:53.050Z |
| 2 | Cases rebuild | `node work/jev-claim-check/numeric.mjs --build` | sha256 `dbaafe7f…9ca379`, 314 checks, no git diff |
| 3 | Keyless re-score | `python3 work/jev-claim-check/score-numeric.py` | rc 1 FAIL: readme (a) 0/18, (b) 10/18, (c) 14/18; close (a) 0/31, (b) 8/31, (c) 12/31 |
| 4 | Own recompute | `/tmp/maintfixes-2mp-recompute.py` | 314 rows cover the 314 needed checks exactly, 0 extra; verdict equals the cuts on p for 314/314; (a), (b), (c) match in both sets. Every plant is the real claim with only the planted token changed (18/18, 31/31). `inEvidence` agrees with literal occurrence in 49/49. Whole-claim counts and "93 absent, 10 supported" match |
| 5 | Sources verbatim, plants fresh | ids joined to `cases.jsonl` (`:true`) and `close-cases.jsonl` (`:real`) | claim + evidence identical on 19/19 and 34/34. No plant claim equals any earlier plant claim (0/49). The digit rule checks out on every plant I read |
| 6 | 10 rows by hand | `random.Random(2)` over row indices: 18, 28, 43, 46, 86, 108, 128, 157, 184, 310 | 5 real values stated in the evidence, all called supported, correctly. 2 plants (27 for grok's 23, and 19 GAP) called unsure: not approved and not caught, as the receipt counts them. 3 real values unsure where the evidence does not state the value (1067/1145, 0.953, a count of 0) |

Two findings, neither of which changes the verdict:
- `inEvidence` is literal token occurrence, not "the evidence states this quantity". In
  `jev-deep-kit-8q7.3` the original `15` (GAP) is present only as an unrelated table cell, and the
  evidence carries no GAP tally at all. So "25 with the original in the evidence" overstates how
  many originals the evidence actually states, which is one reason (c) is low on the close set.
- `8210e02` changed the CLI guard in `check-close.mjs` (and `numeric.mjs` uses the same one) to
  `import.meta.url === \`file://${process.argv[1]}\``. Called through a symlinked absolute path
  (`/tmp` resolves to `/private/tmp` on macOS), the CLI now does nothing and exits 0. With no
  arguments, `check-close.mjs` exited 64 before this commit and 0 after it. A relative path or the
  realpath still works. Reported to the author.

**Verdict: CONFIRMED** at `[oracle]` level (offline re-score and recompute of committed rows, N = 314
checks, `jev-1.13.0`, 2026-09-24): FAIL, with 0/49 plants approved and the catch floor missed in both
sets. `NEGATIVE_EVIDENCE.md` R83 retry 1 states the same numbers. Not checked: no live call was
repeated, and the per-claim reading of the 17 real claims called unsupported was spot-checked, not redone.
