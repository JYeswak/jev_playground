# P3 — `jev-eww`: 30+ labelled route turns, trap classes kept as a named subset

`jev-gou` verified and closed. I checked the one collapse that could have lost information — old
`NO BETTER THAN ITS CONSTANT` and `WEAK — margin` both mapping to `WEAK` — and it is **correct**:
`measure-kit.mjs:12-14` defines `DEGENERATE` as *"says the same thing on every case"* (constant
output), while "no better than its constant" is a bar failure, which is `WEAK` by definition.
Recording it as a word change rather than a number change was the right call.

## The bead

Route has 10 labelled turns at 7/10 per question, and the traps showed length leaks —
`bump-version` missed both questions at **0.09**. Ten turns bounds nothing tightly.

**ACCEPTANCE (the bead's own words):** 30+ distinct turns, **labelled before scores are read**,
with the trap classes kept as a **named subset** so the length-leak finding can be re-tested
rather than re-discovered.

## What the session has learned that applies directly here

- **Label before scoring, and say so in the receipt.** `jev-fzw` closed because a label was the
  bottleneck, not a score; §8 found transcribed scores had rotted between three runs.
- **Prefer a COMPUTED label where one exists.** The only reportable correctness number all
  session (§14c) came from an exact semver oracle. If any part of "which route is correct" is
  derivable from the repo rather than judged, derive it and say which part.
- **Near-threshold count before prevalence** — §14e: half the verdicts in one run were made by
  our 0.50 line, not by Jev. `work/jev-prevalence-first/prevalence-check.mjs` enforces that order
  in code; use it rather than re-deriving.
- **Verdict words are computed, not chosen** — `gradeQuestion`, now the single table after `gou`.
- The route question is **already REFUTED as a product** (7/10, traps at 0.09). This bead is about
  bounding it honestly, not rescuing it. **"30 turns confirm the refutation" is a full-credit
  outcome** and probably the likeliest one.

## Constraints

- Live Jev calls are fine and expected here; the API is free to use. Record model version and
  pin the turn set.
- **Pin your inputs at quote time** — five reproducibility defects tonight were all "quoted a
  live number without pinning it". If the turn set can drift, commit it.
- Commit on create; test file + `TESTS.md` entry in the same commit.
- Exit codes unpiped. No Codex.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-EWW-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
