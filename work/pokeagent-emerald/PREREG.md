# Emerald macro Choice preregistration

**Bead:** `jev-jy7t.1.12`
**Date:** 2026-09-25
**Lane:** keyless design and baselines; **no TypeSafe call until Joshua confirms the key rotation**
**Harness:** `sethkarten/continual-harness` `62bf6f614b66ff76b79954e5a3f04f91c3c6a049`
**ROM:** SHA-1 `f3ae088181bf583e55daf962a92bb46f4f1d07b7`

## One-macro Jev request

The function `macro_choice.build_choice_request(row)` builds the exact no-network envelope. It sends only the compact `visual/player/game/map` projection from `row["state"]`; it excludes `state_text` and screenshots.

The fixed Choice labels, in order, are:

```text
A, B, START, SELECT, UP, DOWN, LEFT, RIGHT, L, R, WAIT
```

The question is:

```json
{
  "model": "jev-1.13.0",
  "state": {"visual": {}, "player": {}, "game": {}, "map": {}},
  "questions": {
    "macro": {
      "type": "choice",
      "instructions": "Choose exactly one legal Emerald input macro for the current screen.",
      "criteria": {
        "A": "Press the A macro for one emulator decision.",
        "B": "Press the B macro for one emulator decision.",
        "START": "Press the START macro for one emulator decision.",
        "SELECT": "Press the SELECT macro for one emulator decision.",
        "UP": "Press the UP macro for one emulator decision.",
        "DOWN": "Press the DOWN macro for one emulator decision.",
        "LEFT": "Press the LEFT macro for one emulator decision.",
        "RIGHT": "Press the RIGHT macro for one emulator decision.",
        "L": "Press the L macro for one emulator decision.",
        "R": "Press the R macro for one emulator decision.",
        "WAIT": "Press the WAIT macro for one emulator decision."
      }
    }
  }
}
```

The live answer would be read from `answers.macro.choice`; the keyless builder never calls the API.

## Measured budget

The committed state trace has 372 rows. The builder's serialized request estimate is based on `ceil(bytes / 4)`; this is a planning estimate, not a tokenizer measurement.

| Quantity | p50 | p95 |
|---|---:|---:|
| Serialized request bytes | 2,035 | 2,279 |
| Estimated input tokens | 509 | 570 |
| Estimated input cost at $0.042/M input tokens | $0.0000214 | $0.0000239 |

At the harness normal preset (80 frames/s, 18 frames per macro), the rate is 4.444 macros/s. TypeSafe's 1,200 requests/minute limit is 20 requests/s, so the normal macro loop is not rate-limited. A 200-macro segment takes 45.0 s and estimates $0.00428 p50 / $0.00479 p95 input spend if every macro makes one call. No TypeSafe request has been made for this bead.

## First live segment, frozen before any call

**Start:** the first controllable overworld row in `states/emerald-boot.jsonl`, macro 142: `game_state=overworld`, `location=PETALBURG CITY`, `position={"x":0,"y":0}`. The runner replays the fixed boot prefix to this state; it does not load a save state.

**Goal:** `state.player.location == "MOVING_VAN"`.

**Action cap:** 100 macros after the fixed start. Legal inputs are exactly the 11 labels above. No screenshots, save states, ROM bytes, chat, or model output enter the baseline rows.

**Scripted baseline:** replay the committed fixed button tail from macro 143 through the first `MOVING_VAN` row (86 macros). Repeat for N=33 seed rows; the seed is provenance only because the script is deterministic.

**Uniform-random baseline:** for each seed `1000..1032`, choose each legal input independently and uniformly for at most 100 macros. Stop on the goal or at the cap. The runner records the goal boolean, macro count, start/final compact state, UTC timestamp, runner SHA-256, harness SHA, and ROM SHA-1.

**Power/MDE choice:** N=33 per arm was selected a priori with `statsmodels.stats.power.NormalIndPower`, one-sided alpha 0.05, power 0.80, equal arms, and a minimally important success-rate difference of 0.70 scripted/Jev versus 0.40 random. The same calculation gives N=30 for 0.80 versus 0.50 and N=15 for 0.90 versus 0.50. These are planning assumptions, not observed power.

**Future Jev bar:** after key rotation, run the same start/goal/cap on held-out seeds not used here. Jev must reach the goal on at least 70% of held-out seeds and have a lower median macro count than the random baseline among successful runs. If fewer than five random runs reach the goal, the macro-count comparison is `NO-CLAIM` rather than a fabricated median.

**No-call boundary:** this prereg, builder, and both baselines run with no TypeSafe API key and no model. A live segment may not start until Joshua explicitly confirms the key rotation.
