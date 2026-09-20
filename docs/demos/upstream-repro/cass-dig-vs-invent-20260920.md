# CASS dig-vs-invent live mine — 2026-09-20 `[pending]`

promoted=0. Studio live. No second cass rebuild.

## Store / mode
- DB: `/Volumes/ZestData/cass-data/agent_search.db` (5,181,931 messages)
- `cass search` hung under rebuild; `fts_messages` virtual table absent (shadow tables only)
- Mode: **sqlite recent-window** — last **120,000** message ids, in-memory token AND-match, limit 10 hits/query
- Queries: 138 from `work/cass-mail-mines/scripts/cass_dig_queries.txt`

## Measured
| | |
|---|---|
| n | **138** |
| y_dig | **22** |
| prevalence | **0.159420290** |
| always-invent mean loss | **0.159420290** |
| dig-iff-count>0 | **0.057971014** **BEAT** |
| dig-iff-BM25/rank-hit | **0.057971014** **BEAT** |
| empty_success (count>0 & y=0) | 4 |
| n_hits exported | 192 |

Loss: invent-on-y1=1, dig-on-y0=2, else=0. Y from `cass_dig_y.py` (mechanical receipt-shaped / wrong-selector).

## Finding
On this recent window, **digging when any hit exists beats always-invent** (0.058 vs 0.159). CASS mountain has dig-vs-invent alpha under Jeff controls — unlike mail ack/importance where abstain won.

## NO-CLAIM
Not full-index cass search; not human edit-delta labels; not a promotion. Rebuild still wedged — re-run when FTS virtual table returns.

<!-- MERGE NOTE 2026-09-20 (conductor, resolving a concurrent-branch conflict):
     The other side of this conflict replaced everything above with a pointer reading
     "Canonical receipt moved to cass-dig-vs-invent-mine-20260920.md". That file EXISTS but its
     results section is still a stub -- line 47 reads
       "(n / prevalence / always-abstain / always-open-top1 / dig-iff-path-in-query -- TBD)"
     and it contains NONE of the numbers above (grep for 0.159420290 / 0.057971014 -> 0 hits).
     Accepting the pointer would have deleted the only copy of a live measurement and redirected
     readers to a TBD. Kept the data here. The sibling file is a DIFFERENT, unfinished mine, not a
     newer home for this one -- if it is later filled in and supersedes this, move the numbers
     first and make the pointer second. -->
