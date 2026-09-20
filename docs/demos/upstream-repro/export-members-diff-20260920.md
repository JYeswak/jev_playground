# Export member-identity diff — 2026-09-20 `[pending]`

**Verdict: SAME SET.** No substitutions.

## Method

The published census (§15, `ad1f8b9` 2026-09-19 23:45) never wrote the 19
names down — only the count, the 2 NAs, and 3 judgment calls. Baseline
reconstructed by archaeology: `git ls-tree -d ad1f8b9 -- work/` shows the
same 21 directories as today, including `omp-jev-dispatch` (added 18:04
that day, before the census). Published 19 = all dirs minus {preaction,
harm-rule}; mechanical re-sweep reproduces exactly that partition:

- export-YES (19): commit, default, dispatch, failure, field, firstlook,
  foreman, fork, heat, heckle, jargon, observer, promise, rerank, review,
  route, skip, uncanny, undo
- NOT-APPLICABLE (2): preaction (no model call), harm-rule (no model call)

## What this closes and what it does not

- Closes the flagged gap: the count is not a different set wearing the
  same number. No churn at directory level between census and re-sweep.
- Does NOT re-audit the 3 judgment wirings (observer inline,
  failure/foreman injectable-defaults) — pattern-match only, stated in
  both receipts. A wiring removal inside a still-present directory would
  hold the count only if its grep hits vanished too; the sweep would
  catch gross removal, not subtle unwiring.

## NO-CLAIM

Directory-level identity only. One machine, one window. The published set
was reconstructed, not quoted — if the census's 19 differed from
all-minus-2, this diff is against the reconstruction and says so.
