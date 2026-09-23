# typesafe-ai-benchmark — W7.0 seat/benchmark run (2026-09-23)

Clone: `/Users/josh/Developer/jev/typesafe-ai-benchmark` (never edited; defects planted only in `/tmp` copies).
Profile: seat/benchmark → T1–T8 + T10. Live model: `jev-1.13.0` throughout. T4 bar committed at
`fec3f95` (`docs/demos/upstream-repro/w70-prereg-p5.md`): 7 fixture tasks re-asked live via the Jev arm;
PASS if ≥5/7 live verdicts match the recorded ones. Prior receipts are leads, never passes
(`benchmark-examples-20260918.md` is not cited as a pass anywhere below).

## T1 — Pin and environment

- SHA `e94fcdaf5058da3e8988f525c3a647f53588d5f3` (`git rev-parse HEAD`), commit date 2026-09-17
  (`git log -1 --format='%H %ad %s'`), remote `https://github.com/iammrduncan/typesafe-ai-benchmark`.
- License MIT (`LICENSE:1`). `git status --short` clean before (run start) and after (verified post-run,
  empty output; `node_modules/` from `npm ci` is gitignored).
- `OMP_PROFILE=muse`; `PI_*` present (`PI_CODING_AGENT_DIR`, `PI_PROFILE`, values withheld).
  Runtime: Node `v22.22.0`, npm `10.9.4` (repo wants Node `>=22.15.0 <23`, npm `>=10 <11` per `package.json:9-12`).
  Host `Joshs-Mac-Studio.local` (darwin arm64, Apple M3 Ultra).

## T2 — Own suite, fresh (PASS, can fail)

- `npm test` (root `package.json:24`: build api + `test --workspaces`), exit `NPM_TEST_EXIT=0`.
  - `@decision/api`: **38 pass / 0 fail / 0 skipped** (`node --import tsx --test 'src/**/*.test.ts'`).
  - `@decision/demos`: **24 pass / 0 fail / 0 skipped** (`node --import tsx --test 'tests/*.test.ts'`).
  - Total **62 pass, 0 fail, 0 skipped**. Skips: none (nothing listed by reason because there are none).
- Planted defect (in `/tmp/typesafe-w70-defect` copy only, staged via `git archive HEAD` + symlinked
  `node_modules`): `packages/api/src/examples/policies.ts:45`, `hazards.some(p => p >= 0.7)` → `>= 999`.
  `npm run test -w @decision/api` in the copy → **RED, `DEFECT_EXIT=1`**:
  `guardrail thresholds and malformed judgments fail safely` fails with
  `actual: { action: 'review' }` vs `expected: { action: 'block' }` (`ERR_ASSERTION`).
  The suite is able to fail. Bonus (offline, keyless): `npm run examples -- --only=E1` → status 200,
  `route_to_team`/`billing`/`refundReview:true`, 3 planned stub calls, $0.025 ceiling.

## T3 — Claim inventory (8 claims, each with file:line)

| # | Claim (clone's own) | File:line | Standing |
|---|---|---|---|
| C1 | Validated/dispatched 475/476 Qwen, 479/480 Jev; cost $0.310581 vs $0.011919 | `README.md:53-60` | partial — raw exports exist (`docs/benchmarks/comparison/`: 14 paired scene files + `summary.json` + `environment.json`, verified present); paired theater measurement itself not re-run here (needs both keys + browser run) |
| C2 | Successful-request p50/p95/p99 215/452/912 ms Qwen, 176/336/532 ms Jev | `README.md:57`, `docs/benchmarks/README.md:20` | partial — same basis as C1 |
| C3 | Exact fixture agreement: Tickets 75/100 both; Guardrails 100/100 both; Approvals 100/95; Scoring 93/100; Home 24/15 | `README.md:67-74` | partial — recomputable offline via `scripts/summarize-comparison.mjs` against committed exports; not recomputed in this run |
| C4 | Noul true only when probability strictly > 0.5; tie is false | `docs/jev.md:34-36`, enforced `packages/demos/lib/jev.ts:78` | demonstrated — live E1 `refund_requested` 0.99 → true; live E2 `compound` 0.15 → false |
| C5 | Native responses must carry exactly the requested answer IDs/types, full choice keys, finite [0,1] values, max-probability winner; ≤0.001 drift tolerated; values never normalized/rewritten; bad output fails closed | `docs/jev.md:61-64`, enforced `packages/demos/lib/jev.ts:60-83` | demonstrated — 7/7 live responses decoded without repair; malformed-rejection tests pass in T2 |
| C6 | 16-second deadline, bounded bodies, five-request admission, no retries/repair/fallback; errors sanitized, credentials never exposed | `docs/jev.md:65-67`, enforced `packages/demos/lib/jev.ts:104-122` | demonstrated by code + passing deadline/overload/sanitization tests in T2 |
| C7 | No retries, repaired answers, or fallback outputs hidden in results | `README.md:135` | demonstrated — `requestJev` contains no retry path; `decodeJev` throws rather than coerces |
| C8 | Independent benchmark, not a TypeSafe implementation or parity claim; exports preserve mistakes and native probabilities | `README.md:137-138` | demonstrated — `docs/jev-smoke.json:1413` retains the hall=bright mismatch as a mismatch; `docs/benchmarks/README.md` counts all fixture disagreements against both sides |

## T4 — Live Jev on its own questions (PASS 7/7, bar was ≥5/7)

- Method: each of E1–E7 (`packages/api/src/examples/fixtures.ts:16-66`) re-asked live as one
  `POST https://api.typesafe.ai/v1/systemone` with `model: 'jev-latest'`. The five `/v1/systemone`
  fixtures used their exact recorded payloads; E4/E7 (chat-route fixtures) used minimal Jev-native
  equivalents (E4: action choice list/summarize/chart + series A/B + window day/week + volume noul;
  E7: department choice billing/technical/other + refund noul), recorded in the probe
  (`/tmp/jev-w70-live.mjs`; clone tree untouched). Key via
  `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba` (`TYPESAFE_API_KEY`; `JEV_KEY` unset).
- Recorded verdicts = `outputs` in `fixtures.ts` (argmax for choice/score, >0.5 side for noul).
- Result: **7/7 task-level matches; 35/35 sub-verdicts** (E1 3/3: billing / refund+ / urgency-idx2;
  E2 5/5: command / all / lights / off / compound−; E3 13/13 incl. 8 checks+ / security / everyone /
  detail-2 / burden-1 / enforcement-2; E4 4/4: chart / B / week / volume+; E5 5/5 incl. severity-2;
  E6 3/3: Arbor / invoice+ / terms-1; E7 2/2: billing / refund+). **PASS** (bar ≥5/7).
- N=7 tasks (35 sub-verdicts). Prevalence: 16/17 recorded noul sub-verdicts positive (94.1%).
  Returned revision `jev-1.13.0` on all 7 calls. Cost: 7 calls, 3032 input / 773 output tokens,
  ≈$0.000121 at the account-owner price ($0.04/M input, free output, `docs/jev.md` pricing note).
  Latency run 1 (ms, E1–E7): 562.7, 219.52, 234.44, 204.53, 186.43, 236.18, 192.53;
  sorted p50 **219.52**, p95 **562.7** (nearest-rank, N=7).

## T5 — Floor arms (Jev beats every floor; seat not refused)

Same 7 rows, 35 sub-verdicts (12 choice / 17 noul / 6 score):

| Floor | Rule | Score | vs Jev |
|---|---|---|---|
| F-choice-const | always the first-listed alternative | 7/12 (misses E2-device, E3-owner, E4×3) | Jev 12/12 |
| F-choice-kw | alternative whose label occurs in the state text, else first-listed | 9/12 (misses E2-scope/device, E4-series) | Jev 12/12 |
| F-noul-const | always positive (majority: 16/17 recorded positive) | 16/17 (misses E2 compound−) | Jev 17/17 |
| F-noul-kw | positive iff state/instruction carries request language (misses E2 compound− the same way) | 16/17 | Jev 17/17 |
| F-score-const2 | always top index 2 | 4/6 | Jev 6/6 |
| F-score-const1 | always middle index 1 | 2/6 | Jev 6/6 |

No floor ties Jev at any question type. The task is neither class A (floor wins) nor class B (floor ties).

## T6 — Incumbent arm (NOT-RUN, earned)

- Command: `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --import tsx packages/api/examples/run.ts --live --only=E1`
- Verbatim output: `Error: CEREBRAS_API_KEY is required for live examples.` (thrown at
  `packages/api/examples/run.ts:18`; guard `run.ts:17-18`:
  `const providerKey = live ? process.env.CEREBRAS_API_KEY : 'synthetic-provider-key'; if (!providerKey) throw …`).
- Cause file:line: `packages/api/examples/run.ts:17-18`; live Qwen path also requires the key in
  `packages/api/examples/benchmark.ts` (`CEREBRAS_API_KEY required`) and `.env.example:4`
  (`CEREBRAS_API_KEY=replace-with-your-cerebras-key`).
- Two routes tried: (1) env-presence probe under the same `infisical run` → `cerebras:false`
  (no `CEREBRAS_API_KEY` in the 83 injected secrets); (2) the direct live command above, which throws
  before any provider call. (Third corroboration: the `npm run examples:live` wrapper fails even
  earlier on the missing `../../.env`, exit 9 — the live path cannot run keyless.)
- Substitute: a held grok key exists (`grok:true` on the same probe; `openai:true`) but **does not fit**
  this clone's incumbent path — the proxy builds Cerebras/Qwen-specific bodies (`src/cerebras.ts`,
  model alias `qwen-3.8-27b`) against the Cerebras endpoint, so neither key can drive the Qwen arm.
  Substitute not attempted, recorded with reason. No accuracy/cost/latency pair, no McNemar — nothing
  to pair against.

## T7 — Calibration (not observable at this N)

Choice confidences (run 1): 1.0 ×10, 0.99 (E2-intent), 0.24 (E2-scope); score confidences 0.96–1.0
(E1-urgency 0.96, E3-detail 0.99, E3-burden 0.98, rest 1.0). Noul answers carry probabilities, no
confidence field. Bins: [0.2,0.5): 1 row, correct; [0.5,0.9): 0 rows; [0.9,1.0]: 17 rows, all correct.
Nearly every row sits in one bin and every row is correct — **calibration is not observable at N=7**,
reported exactly as the standard requires. No reliability claim is made.

## T8 — Stability

- Three repeats of the identical 7 (runs 2–4, archived `/tmp/jev-w70-run{2,3,4}.json`): **7/7 tasks match
  on every repeat; flip rate 0/28 tracked fields** (E3's eight checks counted as one field).
  Repeat latencies (E1–E7 ms): run2 [401, 261, 220, 303, 232, 292, 181]; run3 [518, 173, 199, 184, 242,
  274, 167]; run4 [379.77, 228.11, 289.81, 190.2, 330.7, 212.9, 187.9]. Model `jev-1.13.0` every call.
- One reword (E1 state → "My card was billed two times … sent back as soon as possible", identical
  questions): department billing (same), refund 0.98 positive (same), urgency index **1** vs recorded 2 —
  framing flip 1/3. The flip is semantically correct: the reword dropped the named deadline ("today"),
  so "Soon, without a deadline" is the right reading, not instability.
- Extra T8 cost: 3×(3032 in/773 out) + reword (411 in/70 out); session total 29 live calls, 12,539 input
  tokens ≈ **$0.000502**, no rate limits or retries anywhere.

## T10 — Verdict

| id | result |
|---|---|
| T1 | PASS — `e94fcda` 2026-09-17, MIT, clean before/after, env fully recorded |
| T2 | PASS — 62/62 (api 38 + demos 24), 0 skipped; `/tmp` defect turns suite RED (exit 1, block→review) |
| T3 | PASS — 8 claims with file:line (4 demonstrated, 4 partial-historical with exports on disk) |
| T4 | PASS — 7/7 live verdicts match recorded (bar ≥5/7), `jev-1.13.0`, N/prevalence/cost/latency stated |
| T5 | PASS — best floors: choice 9/12, noul 16/17, score 4/6; Jev 35/35; no tie, seat not refused |
| T6 | NOT-RUN (earned: command + verbatim + `run.ts:17-18` + two routes; grok key held but unfitting, recorded) |
| T7 | PASS (negative) — not observable at N=7; bins with counts stated |
| T8 | PASS — 3× repeat flip 0/28; reword 2/3 with one semantically-correct flip |
| T10 | **SELF** — Jev's own numbers stand; floors below everywhere; incumbent unmeasured |

RULEBOOK tiers: C4–C8 count as maintainer claims reproduced here (independent re-run, N=7);
C1–C3 remain maintainer-reported (exports present, theater not re-run) — tier: reported-with-evidence,
not independently replicated. NO-CLAIM line: this run makes **no** calibration, general-quality,
security-guarantee, or Qwen-vs-Jev superiority claim — fixture agreement at N=7 on synthetic tasks is
exact-match bookkeeping, not evidence of general model parity (per `README.md:80-82,130-135`).

Boundary: clone unmodified (`git status` clean post-run); live spend ≈$0.0005 across 29 `jev-1.13.0`
calls; Qwen/Cerebras arm unrunnable here (no key); all `/tmp` artifacts (`jev-w70-live.mjs`,
`jev-w70-{run2,run3,run4}.json`, `jev-w70-compare.mjs`, `jev-w70-reword.mjs`, `typesafe-w70-defect/`)
kept outside the repo.
