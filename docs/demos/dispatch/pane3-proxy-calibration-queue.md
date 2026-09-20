# P3 — queue of 3. Finish one, fire its callback, then START THE NEXT YOURSELF.

Your review named the load-bearing next step: **the inversion hangs on ≤2 labels of an
uncalibrated proxy.** You found it, so you get to close it.

## Unit 1 — calibrate the proxy on the 16 rows that decide the verdict

The pinned export has no snippets, so calibration needs the hits file
(`work/cass-mail-mines/exports/cass-dig-hits.jsonl`) and, if that is insufficient, a **read-only**
query against `/Volumes/ZestData/cass-data/agent_search.db`. **No rebuild. No writes.**

For the 16 `S_wrong_selector` rows: read the actual top snippet and judge, as a human would,
whether it answers the question. Produce a human-`Y` column beside mechanical-`Y`.

Then recompute the slice with human labels at both cost ratios. Four outcomes, all real:
- human-Y agrees → the inversion is **confirmed** and the headline gets stronger.
- human-Y flips ≥2 → **digging wins** and our published finding is wrong; say so plainly.
- human-Y flips 1 → still loses, but state the margin is one label.
- snippets insufficient to judge → **UNCALIBRATABLE from available data**, which is a finding,
  not a failure. Do not guess to fill the column.

Pre-register which outcome you expect **before** you read the snippets, and commit that first.

## Unit 2 — the same question for `S_lexical_trap` and `S_topical`

Those two carried the pooled win (20 + 82 rows, digging near-perfect). **If the proxy is lenient
on the winning slices and strict on the losing one, the whole comparison is an artifact of the
label function, not of digging.** You already found the strict/lenient asymmetry — quantify it:
what fraction of each slice's `Y` came from the strict branch versus the lenient one?

This is the attack that could overturn all four mines at once. Take it seriously.

## Unit 3 — if 1 and 2 land, re-grade the public page

`docs/demos/upstream-repro/cass-mountain-findings-20260920.md` currently carries your review as a
caveat block and calls the takeaway "a caution, not a measured law". If calibration settles it,
that block becomes a result. **Edit the page; do not write a fifth receipt beside it.**

## Standing rules

Locked export, no regeneration. Exit codes unpiped. Use `scripts/vgrep.sh` for any grep you are
using as proof — it exits 3 on zero matches rather than letting silence read as a clean result
(26 instances of that defect tonight, two of them mine while auditing your work). Commit on
create. No formatters, no repo-wide gates — I verify at phase end.

When this queue drains: `br ready`, claim the highest-priority bead you did not author.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
