# P2 — REORDER: calibration first, then the hardening queue

Joshua moved pane 3 onto skillranker, so the proxy calibration is yours. **It outranks the
denominator guard** in `docs/demos/dispatch/pane2-hardening-queue.md` — do this first, then
resume that queue at Unit 1.

## Why this is the top item

Pane 3's non-author review found, and I reproduced, that our published inversion is fragile in
two measured ways:

- **The "twice as bad" is a chosen constant.** At a 1:1 cost the slice is an exact tie
  (0.250 vs 0.250). Only the direction survives every cost ≥1.
- **The inversion hangs on ≤2 labels.** Flip one mechanical `Y` zero → digging still loses
  (0.375 vs 0.3125). **Flip two → digging wins** (0.250 vs 0.375).

So 16 rows and 4 labels from an **uncalibrated proxy** are deciding a finding we have published.
You authored the mines; you know the proxy. Calibrate it.

## Unit C1 — human-label the 16 `S_wrong_selector` rows

Snippets are not in the pinned rows file. Use `work/cass-mail-mines/exports/cass-dig-hits.jsonl`,
and if that is insufficient a **read-only** query against
`/Volumes/ZestData/cass-data/agent_search.db`. **No rebuild, no writes, export stays locked.**

Read each top snippet and judge as a reader would: does it answer the question? Produce a
human-`Y` beside mechanical-`Y`, then recompute the slice at both cost ratios.

**Pre-register which outcome you expect before reading any snippet, and commit that first.** Four
real outcomes:
- agrees → inversion confirmed, headline strengthens;
- ≥2 flips → **digging wins and our published finding is wrong** — say so plainly and I will
  correct the public page myself;
- 1 flip → still loses, margin is one label, state it;
- snippets insufficient → **UNCALIBRATABLE from available data.** That is a finding. Do not guess
  to fill a column.

## Unit C2 — the strict/lenient asymmetry across all slices

Pane 3 found the losing rows' zeros come from `Y`'s **strict** branch while the winning rows'
ones pass a **lenient** generic bar. If the proxy is systematically stricter on the losing slice,
**the comparison is an artifact of the label function, not of digging** — and that overturns all
four mines at once, not just this one.

Quantify: per slice, what fraction of `Y` came from the strict branch vs the lenient one? This is
the most dangerous question open in the lane tonight. Take it seriously and report it even if it
embarrasses the mines you wrote.

## Then

Resume `docs/demos/dispatch/pane2-hardening-queue.md` at Unit 1 (denominator guard). Finish one,
fire its callback, start the next yourself.

Locked export. Exit codes unpiped. `scripts/vgrep.sh` for any grep used as proof. Commit on
create. No formatters or repo-wide gates — I verify at phase end.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
