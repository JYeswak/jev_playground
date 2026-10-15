# N6 outcome persistence — preregistration floor (jev-n6-outcome-logging-vfnv.1)

Bead: jev-n6-outcome-logging-vfnv.1. Status: floor only; no persistence change yet.

## Persisting code per surface

No jev-owned extension, hook, tool, or profile path observes native
smart-stop verdicts or auto-thinking levels: both are omp-native
(`modelRoles.judge`, `defaultThinkingLevel`, smart-stop detection) and no
file under `.omp/hooks/`, `.omp/tools/`, or `.omp/extensions/` sees those
decisions (verified 2026-10-15 by repository search; empty result).
Session transcripts record prompts, not decisions, so post-hoc mining is a
separate N0-style task, not live persistence.

**Route: UPHILL to omp-kit.** omp must persist these decisions natively
(score, level or verdict, turn id, and whether Jev or the session-model
fallback answered). No uphill bead id exists yet in the omp-kit tracker;
filing there belongs to the omp-test director (fleet rule: project workers
do not file in the omp-kit tracker). The external_ref will be recorded
here when the director files it; until then this PREREG is the floor
record, not an implementation claim.

## Persisted-share floor (before the change)

- smart-stop checks persisted: 0 of ~8,009 judge calls (floor 0.0).
- auto-thinking decisions persisted: 0 of ~7,610 (floor 0.0).
- Any future implementation must show persisted share strictly above
  these floors on the same session population, with turn-id join keys,
  or report NOT_IMPROVED.

## Boundary

This file names the route and the floor. It authorizes no hook,
extension, or config change, no session-log mining as persistence, and
no model call. Every unexpected-stop check must be persisted before
jev-mvvh can rate smart stop KEEP or KILL (jev-nwo1 follow-up).
