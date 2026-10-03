# Jev single-writer rollout bar

Pre-registered: 2026-10-03 UTC, before live integration changes.
Source: `jev-vkc0` bead description; its reported baseline is 74 stale-lock moves/24 h (about 3.08/hour, rounded in the bead to 3/hour), and 24 raw commits versus 215 wrapped commits. These are issue-reported, not independently recounted in this bar.

Consumer: the `jev-vkc0` rollout operator and its named verifier use this bar to judge the live writer. Gate: do not promote the writer or close rollout acceptance until every acceptance item below passes.

Retirement: once the continuous 24-hour window is complete and its result is recorded in the bead, this bar leaves active operational use; retain this committed preregistration as the audit record.

## Acceptance

- Observe one complete, continuous UTC 24-hour window after all live Jev panes route commits through the daemon.
- Count distinct `STALE LOCK moved:` records in the fleet-idle-watch log for `/Users/josh/Developer/jev/.git/index.lock`. Pass only at fewer than 1 move per 24 hours (therefore zero); missing or partial log coverage is `INSUFFICIENT_COVERAGE`, not a pass.
- Reconcile every live commit in the same window to exactly one daemon request and commit. Each commit's changed path set must equal its request; no lost, duplicate, raw-bypass, or cross-contaminated commits.
- With the daemon unavailable, a scratch-clone commit request must fail nonzero with a clear daemon-unavailable reason and no raw Git fallback. Do not stop the live daemon for this probe.

## Falsifiers and scope

Any stale-lock move, unaccounted/raw commit, missing or duplicate commit, path mismatch, or daemon-down success fails the rollout bar. Do not weaken thresholds. The 600/600 `jev-ohpt` scratch trial is implementation evidence only; it does not satisfy the live 24-hour window. Do not change `githooks/`, `.git/hooks/`, or `.omp/` gate files outside a session that confirms `KIT_GATE_EDIT=1` at startup.
