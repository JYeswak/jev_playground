# VBH1B: distinguisher moved inside the rule — 0 fires on 81,373 (2026-09-20)

## Composition-order finding (the second bug this unit caught)

Blank-after-strip FIRED on 3 of my own debug commands: `stripQuotedPayload`
replaces quoted spans with `<QUOTED>` but leaves the trigger BARE
(`<QUOTED>' chmod -R 777...`), destroying the literal structure blanking needs.
Blank-FIRST (original spans intact) then strip: 0 fires. Order recorded in
`classify()` comments. All four legs re-verified after the reorder.


Level: `live` (81k-command census) + `test` (11/11).

## The three acceptance legs (R44's revised trigger: a property of the product)

1. `node work/omp-harm-rule/organic-fires.mjs` → **0 fires** on 81,373 scored,
   with NO filter in the harness — the distinguisher lives INSIDE `classify()`
   (blank data-literals, then stripQuotedPayload, then regexes), so the census
   testifies about what ships.
2. `node work/omp-harm-rule/verify-claim.mjs` (unmodified rule run as own
   control, same session) → `VERDICT: REPRODUCIBLE COMMITTED CORPUS` (12/12,
   0/38).
3. `node --test work/toolcall-judge-v3/rules-v4.test.mjs` → 14/14 green, both
   ground files untouched. New arms live in `exec-data.test.mjs` (11/11) and
   `harm-exec-data.test.mjs` (3/3: probe declines, exec fires, bare fires) —
   NOT in rules-v4.test.mjs, deliberate: %71 owns that file.

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
