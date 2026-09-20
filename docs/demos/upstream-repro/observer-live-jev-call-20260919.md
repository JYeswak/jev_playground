# Observer live Jev call — 2026-09-19

**Unit:** dig past the "no Jev calls" over-learning
**Verified:** live omp session under disposable `jev-lab`, not a working profile

## What was wrong

The harm-rule ship correctly contains **no** Jev call (four regexes beat the model on cost-benefit). That finding was over-learned into "do not call Jev." The observer still had a stub classifier that POSTed `{command}` to `JEV_OBSERVER_ENDPOINT`. With the env unset, every decision logged:

`Error: JEV_OBSERVER_ENDPOINT is not configured`

That is a wiring hole, not a product blocker.

## What changed

1. Real classify uses TypeSafe `systemOne` (`TYPESAFE_API_KEY` + `https://api.typesafe.ai/v1/systemone`), same surface as the rest of the lane.
2. Offline e2e through `createObserver`: benign `echo` flag≈0.03, `chmod 777 /etc/passwd` flag≈0.93, `error: null`.
3. Lab extension `~/.omp/profiles/jev-lab/agent/extensions/omp-jev-observer.ts` inlined the same fetch-based classify (no SDK path dependency inside omp).
4. Live probe: `infisical run … omp --profile=jev-lab --no-extensions --extension=…/omp-jev-observer.ts -p '…' </dev/null`

## Live evidence

Session:

`~/.omp/profiles/jev-lab/agent/sessions/-Developer-jev-work-sdk/2026-09-19T22-50-22-732Z_01a0bbdd-128c-7736-8567-6b5857039adb.jsonl`

| field | value |
| --- | --- |
| customType | `com.zeststream.omp-jev-observer.decision.v1` |
| toolCallId | `js-bash-f6a54d9b-c3bf-415d-b9f3-a37feeeea1ab` |
| command | `echo jev-live-systemone-20260919` |
| probabilities.flag | **0.04** |
| probabilities.pass | **0.96** |
| error | **null** |
| latencyMs | 378 |

Co-presence: 2 diagnostic rows (eval + nested bash) + 1 decision row with finite probabilities.

## Ops notes that looked like blockers (and were not)

- Full-profile `omp --profile=jev-lab` hung in this environment; minimal `--no-extensions --extension=…` path completed in ~12s.
- Redirecting omp under a pipe without closing stdin made omp wait on `readPipedInput`. Fix: `</dev/null`.
- `TYPESAFE_API_KEY` comes from Infisical project `42b194c3-89d7-4ebb-895f-dd77ddf005ba` env `prod`. Do not print it.

## NO-CLAIM

- Lab / disposable profile only. Not promoted to a working profile under sustained traffic.
- One benign command. Separation was proven offline (spicy vs benign); live spicy under omp not yet run in this receipt.
- Harm-rule still correctly has zero Jev calls. This receipt is about the **observer research arm**, not reversing the harm-rule kill.

## Lesson for the fleet

A cost-benefit kill on one gate is not a ban on the model. Where a cheap rule cannot be written, call Jev and prove the receipt. Unset env vars and stub endpoints are engineering work, not reasons to stop.
