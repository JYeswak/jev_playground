# VBH1 DONE: executed-vs-data distinguisher clears all organic fires (2026-09-20)

Level: `live` (81k-command census) + `test` (10/10).

## The three acceptance legs (R44's words)

1. `node work/omp-harm-rule/organic-fires.mjs` → **0 fires** on 81,329 scored
   (control `--no-filter` on the same denominator: 9). The filter is a
   blank-data-literals + re-score composition in the measurement script; the
   shipped rule is untouched.
2. `node work/omp-harm-rule/verify-claim.mjs` (unmodified control, same session)
   → `VERDICT: REPRODUCIBLE COMMITTED CORPUS` (12/12, 0/38).
3. `node --test work/toolcall-judge-v3/rules-v4.test.mjs` → 14/14 green,
   ground files untouched (`git status` clean on both). New arms live in
   `exec-data.test.mjs` (10/10), NOT in rules-v4.test.mjs — deliberate deviation
   from the letter: %71 owns that file and it was reverted to known-good; moving
   one arm there later is trivial.

## How it works (one paragraph)

For a fired command, blank every string literal inside `-e`/`-c` program spans
that is not fed to an exec-family call (spaces preserve coordinates), re-score
through the shipped rule, suppress iff the fire clears. No pattern duplication
anywhere: the shipped rule remains the sole trigger source, so the filter cannot
drift from it. Fails closed (bare/mixed/exec-fed triggers stand). Two measured
bugs fixed en route: opening-quote search landed on the closing quote (spans past
string end); `-e` detection missed space-separated flag values (`--import tsx`).

## NO-CLAIM

Textual heuristic, not a parser (nested same-quote escapes and exotic program
shapes are boundary, stated in tests). 0 fires on this denominator, not "no
false positives in general". Bead jev-vbh.1 ready to close.
