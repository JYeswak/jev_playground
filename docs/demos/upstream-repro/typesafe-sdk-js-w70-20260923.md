# typesafe-sdk-js — W7.0 SDK profile (T1–T3 + T9 + T10)

- **Repo:** first-party `typesafe-ai/typesafe-sdk-js` @
  `66880ccded6cb642dc1809620c2b108c33730214` (2026-09-15, Release v0.6.0).
  MIT (`LICENSE`, Copyright 2026 TypeSafe; package.json 0.6.0).
- **`git status`:** `M package-lock.json` (78 deletions) BEFORE and AFTER —
  pre-existing dirt, byte-identical, untouched by us. T1 cleanliness leg
  FAILS on the pre-existing dirt; untouched-by-us holds.
- **Runtimes:** node v22.22.0, npm 10.9.4. **Lane:** keyless, 2026-09-23.

| id | result | evidence |
|---|---|---|
| T1 | FAIL (pre-existing dirt) | SHA + MIT + runtimes above; `M package-lock.json` before == after |
| T2 | PASS-WITH-NOTE | `env -u TYPESAFE_API_KEY npx vitest run` → **189/189 pass,
  10 files, 0 skips, typecheck clean — but exit 1 via 8 unhandled
  AbortError rejections** from `test/native-transport.test.ts` timers
  (re-run by parent, identical). The suite's own timers leak the same
  AbortError our client leaks (see jev-client receipt). RED plant (/tmp
  copy only, `validateQuestions` neutered): exactly 1 failure at
  `test/client.test.ts:383` — the suite guards the claim |
| T3 | PASS | 6 claims: missing-key throws (`client.ts:48-52`); browser
  refused without flag (`client.ts:60-65`); client-side question
  validation pre-send (`questions.ts:70-89`, requests 0); timeout →
  APITimeoutError ⊂ APIConnectionError (`client.ts:418-437`);
  429 → RateLimitError + Retry-After (`errors.ts:91-95`,
  `retry.ts:11-23,38-49`); models.list refuses bad shapes
  (`resources/models.ts:23-28`) |
| T9 | PASS | 4/4 vs local stub (re-run by parent): hang → APITimeoutError;
  429 → RateLimitError; malformed-200 → TypeSafeError; unset key →
  TypeSafeError. Probe process survives, exit 0 |
| T10 | SELF | no FLOOR/INCUMBENT (correct per profile). `test:integration`
  NOT-RUN (needs key; four fields in subagent record). T4–T8
  NOT-APPLICABLE. NO-CLAIM: nothing about live model behaviour |

## Boundary

No live calls, no key. Clone untouched (all probes/defects in /tmp).
