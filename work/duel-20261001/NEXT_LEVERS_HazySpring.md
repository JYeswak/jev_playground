# NEXT LEVERS (HazySpring): top 3 from 7d session/log measurement

Grounded in R134–R139 (rerank OFF, hints exhausted, enrichment deleted, wording MODEL-LIMIT, nimble-memory REFUTED, conjunction MODEL-LIMIT), the round-1/2 duel files, expected.json, and fresh keyless counts below. Nothing refuted re-proposed. No edits/commits by this doc.

## Lever 1 — Mandate serialized commits, measure loop extinction (fxm2 follow-through)

**Measured:** 265 jev session files, 7d:
- 55 `seq 1 20` commit-retry tool calls and 60 `fatal: Unable to create index.lock` results (avg 6.2 s wasted wall each)
- commands: session-file scan for `seq 1 20` toolCalls and `index.lock ... File exists` toolResults (re-runnable; counts above)
- 25 abandoned empty locks moved aside in 24 h (var/agent-tmp/git-index.lock.stale-*)
**Fix (deterministic, shipped):** scripts/git-commit-serialized.sh (mkdir mutex + stale-sweep) — adoption is the lever, not more code.
**Seam:** fleet commit practice + watcher log (stale-move lines stop).
**Bar:** 7 days with 0 retry-loop toolCalls and 0 fatal-lock results in session files; every remaining lock move names a bypassing (non-wrapper) command or it fails the mandate.
**Cost/day:** $0 Jev; saves ~6 s × fatals/day of agent wall plus the unblocking wait.
**Planted negative:** run a raw `git commit` loop during the window: its fatal-lock error must appear (proving the mandate is load-bearing, not vacuous).

## Lever 2 — Session-scoped exact-match cache for pure reads

**Measured:** 2,969 pure-read tool calls (`git log/show/status/diff`, `ls`, `br show/list`, `head`, `grep`, single commands only) across 265 files/7d; 210 exact-duplicate runs = 7.1% (top: `git diff --cached --stat` 16×, `br list --status=in_progress` 12×).
**Fix (deterministic):** exact (cwd, command) match cache scoped to one session, invalidated on any repo/index mutation (mtime gate); never across mutations, never for writes.
**Seam:** bash tool wrapper or agent-side read cache.
**Bar:** ≥30% of the duplicate runs served from cache over a fleet week with ZERO stale serves, proven by a planted mid-window file mutation whose re-issued read must miss.
**Cost/day:** $0 new model spend; saves duplicated wall seconds + their result tokens.
**Planted negative:** mutate a file, re-issue the identical read: a cached (stale) answer kills the design on the spot.

## Lever 3 — Supervise the local nimble gateway (cascade health)

**Measured:** 24,176 gate rows 7d: 681 paid-fallbacks, of which 186 `local-screen-gateway-unreachable` + 53 `gateway-http` = 239 loopback-gateway failures (~34/day); plus 2,912 permission-required and 1,506 unconfigured-key not-runs (coverage gaps, second-order).
**Fix (deterministic):** health supervision for the :11300 loopback gateway (liveness probe + auto-restart + alert on consecutive failures); no model change.
**Seam:** localbench gateway process + gate-observe fallback rows as the monitor.
**Bar:** gateway-unreachable/http rows → ~0 over 7 days with paid-fallback ratio falling proportionally and no rise in unscreened rows.
**Cost/day:** $0 Jev; each avoided fallback also avoids its paid call.
**Planted negative:** stop the gateway deliberately for one minute: the monitor must page and fallback rows must carry the gateway cause (not counted as safe clears).

## Deliberately not proposed

- Memory wording/conjunction/nimble variants (R137/R138/R139 closed, tonight).
- Budget ceilings without an enforcement mechanism (process, not a lever).
- Anything needing baselines I did not take (hook startup, CI parallelism, find repeat value beyond #2's count).
