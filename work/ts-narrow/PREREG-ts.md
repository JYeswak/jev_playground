# PREREG: V10-TS narrow — TypeScript-rule reminder applicability (jev-dr4p)

Committed pre-live 2026-10-02 (OrangeFrog). Live only with key present (len check passed 07:1xZ).

## Lineage (LOSS DEPTH place)
Widened V10 (R148, 108 live calls) FAILED on 0-miss harm bound (2 misses in dev-uncovered
families). Only sub-family where Jev beat every deterministic rival: TS reminders, 5/5
suppressed on 5 held inapplicables. This candidate narrows to TS-rule firings only.
Boldest testable difference from the last design: TS rules fire on shell events where no TS
exists, so a trigger-text regex is structurally weak here — context judgment is the only
lever. Honest rival carried as a baseline (not assumed away).

## Population
40 fresh TS-rule episodes from 23 sessions unseen in feasibility + widened dev/held
(`var/agent-tmp/ts-narrow.001/ts_ep.json`, sha-frozen at run time). 10 censored
(no prior bash in window: TS rules firing on edit events — out of population, reported as
coverage boundary: 25% of TS firings are edit-triggered). **Held n=30**: blind labels
frozen pre-live (`ts_labels.json`): 2 borderline-applicable (#15 sed-read surfacing the
violating file the next action fixes; #16 setup for the ReturnType fix), 28 inapplicable.

## Method
Model jev-1.13.0. One Choice per row (widened wording verbatim for comparability;
state = RULES + RULE TEXT + COMMAND + NEXT, <=2500 chars). Fail-safe KEEP
(interrupt) on invalid/conf-missing/timeout/error. <=30 calls, stop on 401/402/403.

## Baselines (frozen, keyless)
- B1 always-fire: 30 interruptions, 0 misses.
- B2 `.ts`-mention filter (fire iff trigger+next mentions .ts/typescript): keep 24,
  suppress 6, 0 misses.

## Bar (PASS = shadow surface, log-only; NEVER enforcement)
0 misses AND interruptions <= 20 (suppress >= 10 of 28 inapplicables: beats B1 by >= 10,
B2 by >= 4). Report suppression on inapplicables with Wilson 95% CI. Any miss = FAIL.
Known thinness (stated, not hidden): only 2 borderline applicables, so the 0-miss bound
is weak (true applicable rate 2/30, Wilson UB ~20%). A PASS earns shadow mode only;
enforcement needs a later sample with >= 5 clear applicables.

## Candidate-gate status
`scripts/jev-candidate-check.py` on this candidate: STOP (no >=20 double-labels for
G2 ceiling; headroom uncomputable; recomputable=false — rows frozen in scratch, not
committed). This run proceeds as a preregistered PILOT, never a GO claim.
