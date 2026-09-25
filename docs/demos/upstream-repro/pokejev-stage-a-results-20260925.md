# PokéJev Stage A results: replay action prediction

Bead `jev-jy7t.1.3`, Stage A.

| | |
|---|---|
| Preregistration | `pokejev-stage-a-20260925.md`, commit `4452865`, committed before any call |
| Sample | drawn offline and committed at `6b0f798` before any call |
| Live run | 2026-09-25 (UTC), 2,000 requests, `jev-1.13.0` (all 2,000 resolved to it), `typesafe-sdk-python` `0ffd094` |
| Author | SapphireFalcon (pane 3). A non-author check is pending. |

**Verdict: FAIL.** Both top-1 checks pass; both log-loss checks fail.

## Result against the bar

Pooled over 2,000 rows (500 per Elo band):

| Check | Jev | Threshold | Pass |
|---|---:|---|:---:|
| Player top-1 | **0.3365** (Wilson 95% 0.316–0.358) | ≥ 0.30 | yes |
| Opponent top-1 | **0.2235** (0.206–0.242) | ≥ 0.16 | yes |
| Player log-loss | **2.046** | < 1.735 (usage floor) | **no** |
| Opponent log-loss | **3.900** | < 2.541 (usage floor) | **no** |

- **Top-1 vs PokéChamp.** Jev's top-1 is above PokéChamp-GPT-4o's published rows: player 26–30%,
  opponent 13–16% (arXiv 2503.04094, Table 1). This is under our stricter protocol and is not like
  for like; see the prereg.
- **Log-loss.** Jev's log-loss is worse than the usage-frequency floor on both sides. It is also
  worse than **uniform** on both sides (player 2.034, opponent 3.144).
- **Opponent-label coverage.** The opponent's actual action was among its options on 97.9% of rows.

## All arms, same rows

| Arm (model calls) | Player top-1 | Player log-loss | Opponent top-1 | Opponent log-loss |
|---|---:|---:|---:|---:|
| Jev `jev-1.13.0` (2,000) | 0.3365 | 2.046 | **0.2235** | 3.900 |
| Usage frequency (0) | **0.3495** | **1.735** | 0.1865 | **2.541** |
| Repeat last move (0) | 0.3305 | n/a | 0.2200 | n/a |
| Uniform (0) | 0.0740 | 2.034 | 0.0730 | 3.144 |

**Floor constants.** Fit on the 1,000 disjoint calibration battles: `p_switch` = 0.2395 (n = 1,925
decisions with a switch available), `p_tera` = 0.0631 (n = 1,061).

**Per band, top-1, player / opponent:**

| Band | Jev | Usage | Repeat | Uniform |
|---|---|---|---|---|
| 1200–1399 | .346 / .242 | .364 / .186 | .340 / .232 | .060 / .060 |
| 1400–1599 | .344 / .228 | .350 / .196 | .312 / .234 | .084 / .078 |
| 1600–1799 | .302 / .196 | .352 / .182 | .352 / .212 | .094 / .056 |
| 1800+ | .354 / .228 | .332 / .182 | .318 / .202 | .058 / .098 |

## What the numbers say

1. **PokéChamp's Table 1 is a weak bar.**
   - A zero-model usage-frequency floor clears the player row (0.3495 ≥ 0.30) and the opponent row
     (0.1865 ≥ 0.16) on the same rows.
   - "Beats the published LLM row" therefore says little on its own. That is exactly why the bead
     added the log-loss checks against the floor.
2. **Player slot: Jev does not beat usage frequency.**
   - McNemar test on the discordant rows: Jev alone right on 378, usage alone right on 404,
     χ² = 0.80, not significant.
   - The top-1 rates are statistically tied.
3. **Opponent slot: Jev beats usage frequency on top-1.**
   - Jev alone right on 289, usage alone right on 215, χ² = 10.57, p ≈ 0.001.
   - Repeat-last is close behind at 0.2200.
4. **Both slots are overconfident, and that is why log-loss fails.**
   - Mean top-1 confidence is 0.551 for the player against an accuracy of 0.337; ECE 0.215 over 10
     bins.
   - Opponent: 0.398 confidence against 0.224 accuracy; ECE 0.174.
   - Jev puts under 1% on the true action for 2.2% of player rows and **11.8%** of opponent rows.
     Those rows dominate the log-loss.
   - The distribution ranks usefully and is not calibrated. The ranking is what the Stage B search
     uses; the probability scale is what this gate measured.

## What this changes

- **Stage B.** Nothing. The Stage A prereg fixed the Stage B design before any data. Stage B keeps
  Jev in all three slots, and its receipt will state that both prediction slots failed this gate.
- **Negative evidence.** A new entry, recorded with its retry condition.
  - **Fact:** Jev's action distribution is overconfident on human replays. Its log-loss is worse
    than uniform on both sides.
  - **Retry condition:** a preregistered mixture of Jev's distribution with the usage floor, its
    weight fit only on the calibration battles, that beats the floor's log-loss on a fresh sample.

## Cost

- 2,000 requests, 5,776,848 input tokens.
- About **$0.24** at $0.042 per million input tokens (`docs-mirror/typesafe/models.md:13`); output
  tokens are free.
- Latency p50 152 ms, p95 266 ms. 0 errors. 42.8 s wall time at concurrency 8.

## Non-claims

- **Not like for like with Table 1.** That was preregistered: the label rule, the option sets
  (including tera variants) and the sample all differ.
- **Not a statement about GPT-4o on these rows.** No LLM arm ran; paid comparisons stopped on
  2026-09-24.
- **Not a battle result.**
- One run. Jev's run-to-run stability on this task was not measured here.

## Reproduce (keyless)

```bash
cd work/poke-jev && python3 -m unittest test_replay        # labeller and floors, 19 tests
work/poke-jev/.venv/bin/python work/poke-jev/stage_a.py score   # recomputes receipt.json from jev.jsonl
```

**Files.** `work/poke-jev/stage-a/`:
- `sample.jsonl`, `states.jsonl.gz`, `calib.jsonl`: fixed before the calls;
- `jev.jsonl`: raw answers;
- `receipt.json`.
