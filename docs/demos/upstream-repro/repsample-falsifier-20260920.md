# Representative-sample re-run — pre-registered falsifier `[receipt]`

Committed BEFORE drawing or scoring (rule 3, `docs/RULES.md`). Draw
script and scorer do not exist yet at this commit. Locked n=138 export
stays pinned as the window-based comparison arm — new outputs use
distinct `rep1000` names, never overwrite it.

## Design (frozen)

- Frame: conversations (59,807), uniform random WITHOUT replacement —
  the retrieval attribution unit is the conversation (`top_path`), and
  per-message sampling would shred the unit the protocol scores.
- Size: **1,000 conversations** (~87k messages at whole-mean 87/conv —
  same order as the window's 120k ids). Stated before any result.
- Seed: **421337** (`random.Random(421337).sample`), recorded for redraw.
- Protocol, unchanged: same 138 queries, token rule (split `\W+`, len≥3,
  first 3, AND-match, limit 10 — mirrored from the committed fallback;
  the original in-memory matcher was never committed, stated), hit shape
  (`conversation:X`, line 0, 800-char snippet, score 10−rank), same
  mechanical Y (`cass_dig_y.py`), same loss at 1:1 and 1:2.

## Expectation on record (conductor's, pre-draw)

Aggregate direction holds; `S_wrong_selector` inversion weakens (that
slice's rows are long receipt-shaped messages; the window over-samples
long by ~4.7×).

## Branches (binding)

- Inversion holds at both ratios → finding robust to frame; page stands.
- Weakens but keeps direction → page qualified with the frame numbers.
- Vanishes or reverses → **public page wrong; correct tonight** (the
  outcome of interest).
- Queries un-runnable without live search → UNMEASURABLE, stop (not
  expected: sqlite LIKE works read-only).

## Open definitional notes (noted, not resolved)

- Window length discrepancy: mine 3,544 vs conductor 3,616 mean chars.
  NULLs excluded (zero nulls measured) — likely id-range window (mine)
  vs last-120k-rows window (theirs). Immaterial to 4.6–4.7×; recorded
  so the next reader is not confused by two numbers.
- Original matcher uncommitted: token rule mirrored, stated as
  assumption. Any divergence found later re-opens this receipt.
