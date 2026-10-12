# N1 result-family preregistration: folded long-result time-window dataset

Bead: [1mjev-4se3[0m folded into [1mjev-n1-result-family-bakeoff-fcqw[0m.

## Scope and ordering

This addendum carries the already-frozen temporal replication as a separate result-family dataset. Its controlling preregistration is [1mwork/longres-rep/PREREG-timewindow.md[0m, committed as [1mfba075a1[0m before collection and calls. This N1 fold does not retroactively preregister, alter, or extend that run. It records no new scored rows and authorizes no new model calls.

The time-window rows remain separate from N1's held-session spill/drop arms (R/L/Em/TH/G). Never pool them, use them to tune the N1 arms, or treat the temporal replication as an N1-arm result. The N1 main-arm bake-off remains NOT_RUN until its own complete preregistration and run contract are committed.

## Frozen temporal population

- Eligible items: toolResult events with their own SessionEntry timestamp in [2026-10-02T22:00:00Z, 2026-10-04T22:00:00Z) and text length at least 10,000 characters.
- Exclude source-file hashes from [1mwork/longres/corpus.json[0m, [1mwork/longres-rep/corpus.json[0m, and [1mwork/longres/corpus2.json[0m (130 unique files at freeze); refuse any exact full-result hash already in those corpora. Never use a file modified after the cutoff as a substitute for its event timestamp.
- Frozen split: 200 rows; 100 DEV and 100 HELD by source file; seed 20261008; no source file crosses the split. Fewer than 200 total rows or fewer than 20 REFERENCED and 20 UNREFERENCED HELD rows means NOT ENOUGH DATA and no calls.
- Label: REFERENCED iff one of three evenly spaced 60-character probes appears later in the same source file. Retain event timestamp and full-result hash only; do not retain full result text.

## Frozen comparison and decision bars

Jev uses the preregistered keep/summarize/drop Choice with invalid/refused answers mapped to KEEP, exactly one call per row, model [1mjev-1.13.0[0m, 20-second timeout. The baseline drops only when size is at least a DEV-fitted Youden-J threshold and the tool is in the frozen content-tool set. No post-call tuning.

Primary: on HELD rows, match the baseline's REFERENCED-drop miss count to Jev's; ties choose higher UNREFERENCED savings, then larger threshold. PASS only if miss counts match and Jev's UNREFERENCED savings are strictly greater. Report miss counts/rates and Wilson 95% intervals, absolute savings, and ratio.

Secondary, separate: the original bar requires Jev misses no greater than the fitted baseline and savings at least 1.2 times fitted-baseline savings. Report this independently; do not substitute it for the primary matched-miss decision.

## Frozen call and privacy limits

At most 200 calls and $0.015 total at the recorded input-token price; no retry storm; stop on 401/402/403; checkpoint one row per call with status, tokens, latency, and spend. The accepted time-window run is complete; this addendum makes no authorization for another call or a post-hoc window extension.
