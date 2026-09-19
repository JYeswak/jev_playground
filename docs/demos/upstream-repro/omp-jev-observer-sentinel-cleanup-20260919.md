# OMP observer sentinel cleanup

**Unit:** P2-31
**Source:** `work/omp-jev-observer/src/observer.mjs`
**Commit:** pending at receipt authoring

## Changes

- Removed `context.dcgVerdict ?? 'unknown'` from the injected default DCG function.
- Removed the `?? 'unknown'` fallback from the gate result path.
- Fail-open behavior remains: only an explicit `block` verdict returns early; an absent verdict
  continues observation and never blocks.
- Removed the invented `sessionId: 'unknown'` record value. A missing session ID is now absent from
  the decision object.
- Decision records already omitted `dcgVerdict` before this unit (`a2e2035`). This unit did not
  remove stored verdict fiction; it removed the gate-path sentinel and documents that no verdict
  was stored in the first place.

## Offline proof

```text
node --test work/omp-jev-observer/test/observer.test.mjs
7 tests passed
```

The new negative arm invokes the installed observer seam with no session context and no DCG verdict.
It proves:

- the handler returns `undefined`;
- a decision row is still emitted;
- `toolCallId` remains present;
- `sessionId` is absent;
- `dcgVerdict` is absent.

## NO-CLAIM

This is an offline gate-path cleanup only. It is not evidence about live traffic, a working-profile
claim, or production dogfood. The existing n=1 lab ID join remains a mechanism proof, not a rate.

## Required JSM trio

- `omp-integration`
- `reality-check-for-project`
- `beads-compliance-and-completion-verification`
