# PREREG jev-4nyy live proof (2026-10-01)

Bar (fixed before the first call), fresh `omp --mode=rpc` session rooted in
this repo so project extension `.omp/extensions/jev-skill-hint.ts` loads:

- Positive: prompt `Help me set up a GA4 conversion funnel for the signup
  page` produces a `jev-skill-hint` custom message naming `ga4` or
  `analytics-tracking`. PASS iff the turn carries the hint with either name.
- Negative: prompt `what time is it` produces no `jev-skill-hint` message.
  PASS iff the turn has no hint.
- Latency: up to 12 prompts (mixed GA4/clock variants, <= 12 Jev calls),
  p95 of checkpoint `latencyMs` < 300 ms added per turn.

Bounds: <= 12 live Jev calls this run; stop on 401/402/403; one checkpoint
row per call in `~/.local/state/jev/skill-hint-calls.jsonl`; spend stated
from billed input tokens at $0.042 per million. Feasibility: state is one
prompt (<= 2000 chars), 21 Choice classes; both far below the ~32k-token
input limit. FAIL on any arm is a result about this design, not a retest.

NO-CLAIM: a hint is not proof the skill helped. The alternating-sessions
scoreboard (skill reads per session with hint vs without) needs multi-day
accumulation from the checkpoint log plus session files; it is instrumented
here and reported as accumulating, not proven.
