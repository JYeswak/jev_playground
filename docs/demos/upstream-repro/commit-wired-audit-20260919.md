# Unit 1: omp-jev-commit is real Jev, observe-only, installed nowhere (2026-09-19)

Level: `test` — code read only. No Jev call was executed for this receipt.

1. REAL JEV, no stand-in. `work/omp-jev-commit/src/index.ts:23` imports `askJev` from
   `../../jev-client/src/index.ts`; lines 95–103 call it live with
   `state: { message, diff }` and three noul questions (describes/overstates/omits).
   There is no hand-written score, no regex, no mock anywhere in the file. Unlike
   `work/toolcall-judge-v3/score.mjs` (regex simulator per 1d4e0c8), every scored path
   here awaits a network answer or records `commit_error`.
2. INSTALLED NOWHERE. No `omp.extensions` entry references it (grep over all profile
   configs: zero hits); `.git/hooks/` holds only `commit-msg` (verification-level
   wrapper) and `commit-msg-verification-level.sh`, neither mentions it (grep count 0
   both files); this repo's `.omp/` holds only `hooks/pre/jev-compact.ts` +
   `skills/jev-compact`. Nothing runs it on a real commit today.
3. OBSERVE-ONLY, plainly. Header line 20 says so; every path returns `undefined`
   (lines 67, 71, 93, 121, 122–124). A failed call records `commit_error`, never a
   silent pass (line 21, R40).

NO-CLAIM: no real Jev call was executed for this receipt; the live-probe.mjs scored
path is asserted by its author, not re-run here.
