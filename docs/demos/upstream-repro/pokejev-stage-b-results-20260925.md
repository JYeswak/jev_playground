# PokéJev Stage B: measured result

Preregistration: [`pokejev-stage-b-20260925.md`](pokejev-stage-b-20260925.md), committed at
`1a37ee4` before the bar arm. Code was unchanged from that preregistration during the bar run.
The run was live on `jev-1.13.0`; the zero-call control and scoring were keyless.

## Verdict

**KILL.** The 200-battle Abyssal arm won 112/200 = **56.0%**, with zero PokéJev losses on time.
The preregistered tier-1 bar required at least 84% and zero time losses. The preregistered KILL
condition is win rate below 70% or more than two time losses; the win rate alone triggers KILL.

This is a result about this PokéJev implementation under this pinned local server, team schedule,
and clock. It is not a ladder result and does not establish calibrated Jev probabilities.

## Commands and pins

The required keyless arms were run before the bar arm:

```text
work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py selftest
work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py battles abyssal 200 --control
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py battles random 20
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py battles abyssal 200
work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py score
```

- The bar arm completed 200/200 battles with 0 harness-error rows; all eight worker processes
  exited 0. The live command wall time was 927.63 seconds.
- The local Showdown fork, format, teams, clock, and client are the pins in the preregistration;
  the code/amendment commit was `1a37ee4`.
- The live decision records resolved to `jev-1.13.0`. The run made 9,334 Jev calls and consumed
  33,273,577 input tokens, estimated at **$1.397490234** using the documented $0.042/M input rate.
  Output tokens were not recorded by this runner.

## Arms

| Arm | Battles | Wins | Win rate | Wilson 95% interval | Time losses | Harness errors | Jev calls | Fallbacks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PokéJev vs Abyssal | 200 | 112 | 0.560 | 0.4907–0.6270 | 0 | 0 | 9,334 | 381 |
| Zero-call control vs Abyssal | 200 | 79 | 0.395 | 0.3298–0.4641 | 0 | 0 | 0 | 4,814 |
| Feasibility vs Random | 20 | 19 | 0.950 | 0.7639–0.9911 | 0 | 0 | 1,044 | 1 |

The feasibility arm met its preregistered validity gate of at least 18/20 wins. The live arm
outperformed the zero-call control by **16.5 percentage points**; the two-proportion test reported
`z=3.303`, two-sided `p=0.001`. This difference is reported context, not a replacement for the
Abyssal bar.

Decision latency for the live Abyssal arm was p50 **1,088 ms**, p95 **2,424 ms**, maximum
**5,064 ms**. The control was p50 103 ms, p95 396 ms, maximum 1,777 ms.

## Fallbacks and live boundary

The 381 live-Abyssal fallbacks were:

- 271 `TypeSafeAPIError`: the organization had no available TypeSafe API credits;
- 5 `TimeoutError`;
- 105 `ValueError: Unknown move: nothing`.

The player used the preregistered fallback policy on every such decision, so the run remained
clock-safe. The credit-exhaustion errors are part of the measured run; they are not hidden or
replayed. The 200-row win rate therefore includes the actual behavior after the API credit limit
was reached.

No raw battle trajectories, runtime logs, or API key were committed. The aggregate receipt is
`work/poke-jev/stage-b/receipt.json`; the three decision logs and three compact battle-result
JSONL files are committed as keyless re-score inputs. Replay HTML files remain local run
artifacts and are not part of this result. The receipt records their manifest: 420 files,
7,143,976 bytes, manifest SHA-256
`65e906ea8bd9e534eb3222b13a96e6cbf21f88dc2929b2f1c9c31487c5c8adc8`.

## Boundary and non-claims

- This is not a public-ladder or human-ladder result; Stage C remains unauthorized.
- The comparison is not like-for-like with PokéChamp's published 84%: their sample was about 25
  matches per pairing, with their server and clock.
- No paid LLM comparator was run. Paid comparisons were stopped by policy on 2026-09-24.
- The run does not validate Jev probability calibration. Stage A found overconfidence, and this
  stage uses the distributions as preregistered ranking weights.
- The Metamon stretch arm was not run here. A separate addendum and run are required before it can
  be reported.
