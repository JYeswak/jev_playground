# PokéJev Stage A: replay action prediction (preregistration)

Bead `jev-jy7t.1.3`, Stage A. Author: SapphireFalcon (pane 3). Written and committed **before any
Jev call** for this stage. The bar comes from the bead and does not move after data.

**Status: PREREGISTERED.** No live call has been made. Results will go in the same directory, in
`pokejev-stage-a-results-20260925.md`, which cites this file's commit.

## What is being tested

Jev fills two of PokéChamp's LLM slots in this test: the **action prior** and the **opponent model**.
Stage A checks both before any battle is played. For each human Gen 9 OU turn, Jev reads the state
text that PokéChamp's own translator builds, and predicts two things:
- the player's chosen action;
- the opponent's chosen action.

This is a **gate, not a win**. Predicting human actions stands in for playing well; it does not
measure play. A PASS licenses the two slots. A FAIL is reported as the gate verdict, and **Stage B's
design does not change either way**. The bead fixes Jev in all three slots, and changing the design
after seeing Stage A would be an adaptive choice.

**Comparator.** PokéChamp's published action-prediction table (arXiv 2503.04094, Table 1, read in
the paper's HTML):

| Elo | Player top-1 | Opponent top-1 |
|---|---:|---:|
| 1200 | 30% | 16% |
| 1400 | 26% | 16% |
| 1600 | 27% | 13% |
| 1800 | 30% | 15% |

- Random guessing scores 7% for the player and under 1% for the opponent.
- The LLM was GPT-4o.
- The paper does not state n per row, and its prediction script is marked "Coming Soon" in the
  repo README at `0f84c46`.

So this comparison is **against an LLM row**, not the overall SOTA, and it is not like for like in
four ways:
1. PokéChamp's label extraction and option sets are unpublished.
2. Ours are stricter, as defined below.
3. Our option sets include terastallize variants.
4. Our sample is our own draw from their test split.

## Data (not written by us)

- **Corpus.** `milkkarten/pokechamp` on Hugging Face, **test split**, revision
  `b5820ff5d0c8d5e5cec692d55f756b6e5a66a203`, `gamemode == gen9ou`.
- **Elo bands** (the dataset's `elo` field): `1200-1399`, `1400-1599`, `1600-1799`, `1800+`. There
  are 15,364 / 12,547 / 6,199 / 1,485 gen9ou test battles in each band, counted from the five test
  parquet shards.
- **Sampling.** This is `stage_a.py sample`, which is deterministic.
  1. Within each band, sort battles by `battle_id` and shuffle with `random.Random(f"20260925-{band}")`.
  2. Walk the order. Skip a battle if it:
     - contains Zoroark (Illusion breaks species tracking);
     - contains `|-transform|`;
     - is not singles;
     - lasts under 3 or over 80 turns (PokéChamp's own translator cap is 80);
     - has no single `|win|`.
  3. Pick one eligible turn per battle with the same RNG.
  4. The first **500** battles per band go to the evaluation set. The next **250** per band are a
     disjoint **calibration set**, used only for the floor's two constants.
  5. If state building throws, the battle is skipped and counted in `sample-stats.json`.
- **Perspective.** The player is the battle's **winner**, following PokéChamp's
  `pokechamp/translate.py` `add_battle(use_winner=True)`. The opponent is the loser.

## Labels (our code, `replay.py`, offline-tested in `test_replay.py`, 19 tests)

For side X in turn t, the lines after `|turn|t` up to the next `|turn|`:
- **Chosen switch:** a `|switch|` by X that comes before any `|move|` line and any `|faint|` line.
- **Chosen move:** a `|move|` by X with no `[from]` tag, other than Struggle. It carries **tera** if X
  terastallized earlier in the same block.
- **Unobservable, so the turn is not eligible:** anything else. That covers `|cant|`, `|drag|`, a
  locked or called move, fainting before acting, or no event.
- **Eligibility.** A turn is eligible only when **both** sides' actions are observable, so both
  questions are scored on the same rows.

## State

The state is PokéChamp's `state_translate2` text (`pokechamp` `0f84c46`), built by `pc.build_state`,
which mirrors `translate.add_battle`:
- `recursive_nick_removal`;
- `|premove|` lines giving the player's own team the moves each species used anywhere in the battle
  (PokéChamp's "standard player perspective");
- the battle replayed through `LocalSim` up to `|turn|t`.

**Two deviations**, both toward a correct state:
- The switch list is the non-fainted, non-active team. Spectator logs have no `|request|`, and
  poke-env's list included fainted members.
- Labels come from the rule above, not from the last move line in a chunk.

**Size.** The state is about 7,100 characters (dry run, n = 20).

## Options

| Side | Moves | Switches | Tera variants |
|---|---|---|---|
| Player | every move the active species used in the battle | non-fainted bench | `+ terastallize` per move while X has not terastallized |
| Opponent | moves revealed before turn t ∪ PokéChamp's own `get_opponent_current_moves` (its Bayesian predictor over Metamon's team data) | non-fainted bench (team preview) | same rule |

- The player's label is always among the player's options.
- The opponent's label can fall outside its options. Such a row scores as a top-1 miss for every arm
  and is left out of log-loss for every arm. Coverage is reported.

## The Jev call

- **Model and client.** Model `jev-1.13.0`, pinned. Client: `typesafe-sdk-python` `0ffd094`
  (v0.7.1), `TypeSafeClient(timeout=30.0)`.
- **Calls.** One request per row, 8 concurrent, no retries beyond the SDK default.
- **State.** The text above.
- **Questions:** two Choice questions, with criteria being the options' display names ("Knock Off",
  "Knock Off and Terastallize", "Switch to Ting-Lu") and no descriptions.
  - `player_action`: *"Which action the player (called 'You' and 'Your' in the state) chooses for the
    current turn of this Pokémon Showdown Gen 9 OU battle."*
  - `opponent_action`: *"Which action the opponent chooses for the current turn of this Pokémon
    Showdown Gen 9 OU battle."*
- **Guards.** A row whose state sha256 does not match `sample.jsonl` makes no call. A failed call is
  recorded and scored as wrong, and as p = 1e-6 for log-loss.
- **Cost estimate.** 2,000 requests × about 2,200 input tokens ≈ 4.4M tokens ≈ **$0.19** at $0.042 per
  million input tokens.

## Floors (no model, same rows)

1. **Uniform** over the options.
2. **Usage frequency.** This is the floor the log-loss bar is measured against.
   - **Move mass:** split by the active species' move usage percentages in PokéChamp's
     `poke_env/data/static/gen9/ou/sets_1000.json` (sha256 prefix `c3c7a8b3fdb09f58`), with +1
     smoothing.
   - **Switch mass:** `p_switch`, split evenly across the bench.
   - **Tera share:** `p_tera` of each move's mass.
   - **Constants:** `p_switch` is the share of switch decisions among calibration decisions where a
     switch was available. `p_tera` is the share of tera among calibration move decisions where tera
     was available. Both are pooled over both sides and never fit on evaluation rows.
3. **Repeat last.** The side's previous-turn move if the same Pokémon is still in and the move is an
   option; otherwise the usage floor's top choice. It is reported only; it has no log-loss.

## The bar (bead `jev-jy7t.1.3`, fixed)

Over all 2,000 evaluation rows, pooled across bands, **all four** must hold:

| Check | Threshold |
|---|---|
| Jev player top-1 | **≥ 0.30** |
| Jev opponent top-1 | **≥ 0.16** |
| Jev player log-loss | **<** usage-frequency floor's player log-loss |
| Jev opponent log-loss | **<** usage-frequency floor's opponent log-loss |

- Top-1 is the point estimate. Wilson 95% intervals are reported.
- **PASS** if all four hold, **FAIL** otherwise. Per check, a FAIL names which slot failed.
- **Reported, not barred:**
  - per-band top-1 for every arm;
  - each floor's top-1;
  - opponent coverage;
  - latency p50 and p95;
  - resolved model ids;
  - input tokens and spend.

## Non-claims

- **Not a battle result.** Stage B is the battle test.
- **Not like for like with Table 1**, for the four reasons above. A PASS says Jev reaches the
  published LLM row under our stricter protocol. It does not say Jev beats GPT-4o on the same rows.
  No LLM arm runs here: paid comparisons were stopped on 2026-09-24.
- **Not the overall SOTA.** Metamon (offline RL) is the non-LLM SOTA and is Stage B's stretch.

## Commands

```bash
work/poke-jev/.venv/bin/python work/poke-jev/stage_a.py sample      # offline, fixed seed
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  work/poke-jev/.venv/bin/python work/poke-jev/stage_a.py run       # live, 2,000 requests
work/poke-jev/.venv/bin/python work/poke-jev/stage_a.py score       # keyless
cd work/poke-jev && python3 -m unittest test_replay                 # 19 offline tests
```
