# Emerald macro Choice preregistration

**Bead:** `jev-jy7t.1.12`
**Date:** 2026-09-25
**Lane:** keyless design and baselines; **no TypeSafe call until Joshua confirms the key rotation**
**Harness:** `sethkarten/continual-harness` `62bf6f614b66ff76b79954e5a3f04f91c3c6a049`
**ROM:** SHA-1 `f3ae088181bf583e55daf962a92bb46f4f1d07b7`

## One-macro Jev request

The function `macro_choice.build_choice_request(row)` builds the exact no-network envelope. It sends only the compact `visual/player/game/map` projection from `row["state"]`; it excludes the full `state_text` and screenshots. The `map` projection carries only the extracted PORYMAP ASCII layout block from `state_text`, so doors and warps remain visible without sending the full formatter output.

The fixed Choice labels, in order, are:

```text
A, B, START, SELECT, UP, DOWN, LEFT, RIGHT, L, R, WAIT
```

The question is:

```json
{
  "model": "jev-1.13.0",
  "state": {"visual": {}, "player": {}, "game": {}, "map": {"porymap_ascii": "..."}},
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

The committed state trace has 372 rows. The builder's serialized request estimate is based on `ceil(bytes / 4)`; this is a planning estimate, not a tokenizer measurement. The budget values below are regenerated after the PORYMAP block was added.

| Quantity | p50 | p95 |
|---|---:|---:|
| Serialized request bytes | 1,974 | 2,895 |
| Estimated input tokens | 494 | 724 |
| Estimated input cost at $0.042/M input tokens | $0.0000207 | $0.0000304 |

At the harness normal preset (80 frames/s, 18 frames per macro), the rate is 4.444 macros/s. TypeSafe's 1,200 requests/minute limit is 20 requests/s, so the normal macro loop is not rate-limited. A 200-macro segment takes 45.0 s before any live API latency. No TypeSafe request has been made for this bead.

## First live segment, frozen before any call

**Start:** macro 228 in the committed trace: `game_state=overworld`, `location=MOVING_VAN`, `position={"x":2,"y":2}`, money `$3000`. Rows 142–227 are excluded: the harness labels the intro/name sequence as `overworld` at `PETALBURG CITY`, `(0,0)`, `$0`, while the player name changes from `TERU` to `AAAAAAA`; they are not a controllable start.

**Goal:** `state.player.location != "MOVING_VAN"` (leave the starting truck). This is checkable from state and does not depend on screenshot interpretation.

**Action cap:** 500 macros after the fixed start. Legal inputs are exactly the 11 labels above. No screenshots, save states, ROM bytes, chat, or model output enter the baseline rows.

**Scripted baseline:** from macro 228, apply the deterministic SCRIPTED_SEED=20260925 sequence in run_baselines.py; N=33 seed rows. Keyless rerun: 33/33 reached the goal in 154 macros.

**Uniform-random baseline:** for each seed 1000..1032, choose each legal input independently and uniformly for at most 500 macros from the same macro-228 start. Stop on the goal or at the cap. The runner records the goal boolean, macro count, start/final compact state, UTC timestamp, runner SHA-256, harness SHA, and ROM SHA-1. Keyless rerun: 26/33 reached the goal; successful macro counts are the baseline distribution.

**Power/MDE choice:** N=33 per arm was selected a priori with statsmodels.stats.power.NormalIndPower, one-sided alpha 0.05, power 0.80, equal arms, and a minimally important success-rate difference of 0.70 scripted/Jev versus 0.40 random. The same calculation gives N=30 for 0.80 versus 0.50 and N=15 for 0.90 versus 0.50. These are planning assumptions, not observed power.

**Future Jev bar:** after key rotation, run the same start/goal/cap on held-out seeds not used here. Jev must reach the goal on at least 70% of held-out seeds and have a lower median macro count than the random baseline among successful runs. If fewer than five random runs reach the goal, the macro-count comparison is NO-CLAIM rather than a fabricated median.

**No-call boundary:** this prereg, builder, and both baselines run with no TypeSafe API key and no model. A live segment may not start until Joshua explicitly confirms the key rotation.
