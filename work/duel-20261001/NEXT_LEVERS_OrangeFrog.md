# TOP 3 next levers — OrangeFrog, 2026-10-02 (keyless, read-only)

Sources read first: `work/jev-inventory/expected.json` (all 18 surfaces),
`NEGATIVE_EVIDENCE.md` R134–R139, `work/duel-20261001/DUELING_WIZARDS_REPORT.md`.
None of the three touches a refuted design (no rerank, no semantic shortlist,
no enrichment, no Noul rewording, no nimble cascade for memory/injection).
Tonight's shipped work (cascade fallback+prerule, duel, global shadow rollout,
memory enforce, uninstall, sweep) is not re-proposed.

Measurement window: last 7 days of hook logs + session files on this machine.
All commands below are reads.

## Lever 1 — restart 3 stale gate panes onto the cascade (deterministic, $0)

**Measured.** 1,235 gate commands went unscreened on daily-cap in one day,
all from old-code sessions (no `screen` key = pre-fallback code, legacy
direct-paid path), three sessions:

- `python3 work/jev-n4eu/levers-batch.py` ->
  cap sessions 01a0f608:541, 01a0f62b:339, 01a0f607:325; screen-key False on
  all 1235; hours spread 07–17Z (intraday exhaustion, then blind all day).

Legacy code calls paid Jev for every command until its small daily cap dies;
the cascade (nimble screens ~96% free) would cut their paid spend ~25x AND
restore coverage. Restarting is free.

**Fix (fleet ops, conductor executes):** restart the panes holding those
sessions onto current hooks (same as jev-6pjh wave). No code change.
**Cost/day:** $0 to restart; paid gate spend from those panes should FALL
(~1,205 paid calls/day today at ~800 in-tok ≈ $0.040/day -> cascade ~4%
of that).
**Seam:** fleet panes (muse/codex profiles per session-file locations).

**Bar (committed before restart counts):** daily-cap not-run rows from those
three sessions = 0 for 48h post-restart AND their rows carry `screen` keys
(current code). Fails closed: any recurrence reopens.


## Lever 2 — raise the injection-shadow daily cap to cover ~1,000 blind results/day

**Measured.** `python3 work/jev-n4eu/levers-batch.py` ->
`inj 7d: 9344 (cap 7567, not-run 1213, scored 274)`; cap-by-day
10-01:3098, 09-30:2610, 09-29:1808. Repeat screening is only 15%
(`levers-repeat.py`: 7841 scored+cap rows, 6693 distinct hashes), so dedup
is not the fix. ~1,000 tool results/day pass with NO injection judgment
while the screen itself is verified (clean 0/222, catch 268/300).

**Fix:** raise `MAX_DAILY_CALLS` for the injection hook (default, not remove
the cap; per-process shape and fail-open stay). Deterministic spend-for-
coverage trade, no model-quality claim.

**Seam:** project hook `.omp/hooks/post/jev-injection-shadow.ts` default
(the j0er global wrappers inherit it).

**Bar (committed before the change):** cap-status rows/day drops 90%+ for
7 days; withhold rate on the newly covered traffic reported with Wilson;
spend/day stated. Rollback = revert the constant.

**Cost/day:** ~1,000 extra calls x ~800 in-tok x $0.042/M ≈ **+$0.034/day**
for full coverage (vs blind results today).

## Lever 3 — raise the memory-filter daily cap (loss-making coverage gap)

**Measured.** `python3 work/jev-n4eu/levers-batch.py` ->
`mem 7d: 8638 (daily-cap 5243, scored 1630, memo 1580)`: **61% of filter
turns fail open on cap**, not on judgment. Unit economics over the same 7d:
tokensSaved 59,522 (≈$0.18 at model input rates) vs scored in-tok 760,036
($0.032 Jev spend) ≈ **5.6x ROI** — headroom to buy coverage.

**Fix:** raise the filter daily cap (200 -> ~600) so scored-share, not the
clock, decides coverage. Memo (18%) already dedups repeats; per-turn 20-item
cap stays. Proposal only: the file is pane 2's area.

**Seam:** project extension `.omp/extensions/jev-memory-filter.ts` default.

**Bar (committed before the change):** scored-share of turns rises toward
unmet demand with tokensSaved/spend ratio held >= 3x over 7 days; spend/day
stated. Rollback = revert the constant.

**Cost/day:** current ~$0.005/day Jev spend -> ~$0.015/day at 3x coverage
for ~3x the token savings (~$0.08/day equivalent).

## Explicitly not proposed

- Web-search rerank revival (R134 OFF: bottleneck is agent opens, unchanged).
- Semantic skill shortlist (R135 refuted; R133 vein-exhausted).
- Noul rewordings/conjunctions for keep precision (R137/R139 model-limit).
- Nimble cascade for memory or injection (R138/uhc5 refuted).
- Needs-human enrichment (R136 deleted on its own terms).
- Unconfigured-key sessions (~215/day fail open): key distribution, out of lane.
