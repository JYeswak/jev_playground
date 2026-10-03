# Preregistered counterfactual replay (jev-jzgm)

Frozen 2026-10-02 before running the replay engine on the live sidecars. This tool is read-only: it does not call Jev, modify hook state, or change rollout switches.

## Scope and inputs

Replay the trailing 30 UTC days of the local `memory-filter.jsonl` + `memory-filter-full.jsonl` and `gate-observe.jsonl` logs. Each surface reports requested-window bounds and actual observed first/last timestamps; missing history is a coverage gap, not zero traffic. Raw prompts, memories, commands, and session IDs stay local and are never copied to receipts.

## Frozen checks

1. **Memory cap3 tokens.** Join main and sidecar on `(instance,promptHash,memoryHash)`, as `work/jev-i20b/cap3-tokens.mjs` does. Per item, tokens are `floor(memory.length / 4)`. `enforced`, `cap3-pruned`, or `decision=prune` counts as cut; all other sidecar items count as received. Report turns by `(instance,promptHash)`, received/cut totals, and received tokens/turn. The frozen reference is the committed `work/jev-i20b/cap3-before.json` for 2026-10-01T19:45Z..2026-10-02T19:45Z: 179 turns, 165,912 received, 846 cut. Reproduction passes only on exact totals from raw logs. Do not substitute the separate session-file census (306 tokens/turn) for this method.
2. **Gate-cascade free-screen share.** On the most recent complete 60-minute UTC interval in the logs, include only actual screen rows with a boolean `jevSkipped`; free-screen share = `jevSkipped=true / eligible screens`. Report eligible N and Wilson 95% interval. The independent live reference is 96% screened free in one hour (EVAL.md jev-nr3c); pass if 0.96 lies within the Wilson interval. Rows without a screen outcome are excluded and counted separately.
3. **No-op planted control.** `--policy noop` applies the identity transform to both surfaces. It must report exactly zero token, miss, latency, and screen-share deltas against its own baseline; any nonzero delta fails.

Policy interface is limited to `cap3` (replay observed cap3 decisions) and `noop` (identity control); this is a read-only historical replay, not a fitted threshold or a forecast. No live Jev calls; spend $0. The tool accepts at most a 30-day query window and discloses actual data coverage.

## Interpretation boundary

This replay can reproduce recorded outcomes and compare a policy transform over recorded units. It cannot estimate unobserved outcomes, prove a counterfactual Jev answer, or establish a full 30-day population when source logs retain less than 30 days. Any absent interval is `INSUFFICIENT_COVERAGE`, never imputed.

## Supplemental cap3 source-integrity bar (2026-10-03)

This is a new, prospective replay-source check, not a rewrite of the 2026-10-02 preregistered
result. The prior aggregate-only comparison remains a FAIL: the retained raw logs report 166,095
received tokens versus 165,912 in `work/jev-i20b/cap3-before.json` (+183); that artifact has no
per-turn rows or source hash, so the old inputs cannot be reconstructed.

Before rerunning the replay, freeze the retained raw-log result for the same UTC window in
`work/jev-jzgm/cap3-reference.jsonl`. Its manifest is `work/jev-jzgm/cap3-reference.json`.
The row file SHA-256 is
`f4479a5d940ca0df44fe51b155b37ddbe8c14b90c742824da06293d3f1fffb59`; the manifest also pins both
source-log hashes. It has 179 distinct pseudonymous turns, 3,238 sidecar items, 166,095 received
tokens, and 846 cut tokens. Turn rows contain only SHA-256 turn identifiers and per-turn totals.

**Pass condition:** the replay verifies the row-file SHA-256, then reproduces every frozen turn row
exactly (turn hash, item count, received tokens, cut tokens), with no missing, extra, or duplicate
turn. Aggregate equality alone is insufficient. A mismatch is FAIL; do not alter this fixture or
bar to obtain a pass. This supplemental check establishes replay reproducibility against the
retained source bytes only. It does not repair the prior +183-token historical mismatch, establish
the original raw inputs, or satisfy the separate n60 estimate comparison.
