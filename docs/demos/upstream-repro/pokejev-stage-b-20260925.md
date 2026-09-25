# PokéJev Stage B: local Gen 9 OU battles under an enforced clock (preregistration)

Bead `jev-jy7t.1.3`, Stage B. Author: SapphireFalcon (pane 3). Written and committed **before the
first live battle**. The bar comes from the bead and does not move after data. Stage A's result
(`pokejev-stage-a-results-20260925.md`) **does not change this design**, as Stage A's preregistration
promised.

**Status: PREREGISTERED.** Results will go in `pokejev-stage-b-results-20260925.md`, which cites this
file's commit.

## Question

Does Jev (`jev-1.13.0`), placed in PokéChamp's three LLM slots, beat the heuristic bots PokéChamp
reported against, with **zero losses on time**? The three slots are the action prior, the opponent
model and the leaf judgment. The clock is no looser than the Showdown ladder's.

**Comparator (an LLM row, not the overall SOTA).** PokéChamp (arXiv 2503.04094, Table 2, Gen 9 OU,
custom teams):
- GPT-4o wins **84% vs Abyssal**, from "at least 25 matches" per pairing;
- on the human ladder it lost about a third of its games on the clock.

The overall SOTA is Metamon (offline RL, arXiv 2504.04395). That comparison is the stretch below.

## Environment

- **Server.** Pokémon Showdown, `jakegrigsby/pokemon-showdown` at `e64915c0e` (the fork PokéChamp's
  README names, the PokéAgent Challenge server), started by `work/poke-jev/serve.sh`. Its tracked
  `config/config.js` sets `forcetimer = true`, so the timer runs in every battle without either
  player asking for it.
- **Format.** "Gen 9 OU Clock" (`gen9ouclock`), from `work/poke-jev/showdown/custom-formats.ts`,
  copied into the clone's `config/` as an untracked file. It has the fork's Gen 9 OU ruleset and
  banlist. The fork's tournament clock (600 s bank) is replaced by one **no looser than either
  source**:

  | Setting | This format | Ladder (`room-battle.ts`) | PokéChamp paper |
  |---|---|---|---|
  | Bank | 150 s | 150 s | 150 s |
  | Added per turn | 15 s | 10 s | 15 s |
  | Cap per decision | **15 s** | 150 s | 15 s |
  | Grace | 1 s | 60 s | none stated |

  "Timer Grace = 1" is the smallest value the rule accepts.
- **Clock verified.** The battle log prints `Time left: 15 sec this turn | 150 sec total | 1 sec
  grace`. The keyless selftest's RED arm, a player that waits 20 s per move, loses with `lost due to
  inactivity` (`stage_b.py selftest`).
- **Teams.** PokéChamp's 13 pinned Gen 9 OU teams (`poke_env/data/static/teams/gen9ou/gen9ou1..13.txt`
  at `0f84c46`).
  - Battle k uses the ordered pair `team_pairs()[k // 2]`: all 156 ordered pairs, shuffled with seed
    20260925.
  - Even k gives PokéJev the first team; odd k swaps sides, so each pair is played both ways.
  - Team preview is poke-env's default (random order) for every player.
- **Opponents.** All three are code at pinned SHAs, and none makes a model call. 200 battles each:

  | Opponent | Code | Role |
  |---|---|---|
  | `abyssal` | PokéChamp's `AbyssalPlayer` (`poke_env/player/baselines.py:433` at `0f84c46`); its code is poke-env's `SimpleHeuristicsPlayer` | **the bar** |
  | `onestep` | PokéChamp's `OneStepPlayer`, its "admissible heuristic" one-step-lookahead bot | reported |
  | `maxpower` | poke-env's `MaxBasePowerPlayer` | reported |

- **Feasibility arm.** 20 battles vs `RandomPlayer`. If PokéJev wins fewer than 18 of them, the
  harness is broken; the run is INVALID, not a result.

## PokéJev (`work/poke-jev/player.py`, `policy.py`; constants fixed here)

**Per decision:**
1. **Root request.** State = PokéChamp's `state_translate2` text (the same translator as Stage A).
   Two Choice questions:
   - `player_action`: *"Which action the player … should choose for the current turn … to win it"*,
     over all legal moves, their tera variants when tera is available, and switches.
   - `opponent_action`: *"Which action the opponent chooses …"*, over the opponent's moves seen or
     predicted by PokéChamp's `get_opponent_current_moves` (its Bayesian set predictor) plus its
     unfainted bench from team preview.
2. **Candidates.**
   - Player: the prior's top **3** plus PokéChamp's damage-calculator move, if legal and not already
     in.
   - Opponent: actions by Jev probability until **0.8** of the mass is covered, at most **4**,
     renormalized.
3. **Simulation.** Each pair is stepped in PokéChamp's `LocalSim` on its own copy of the battle.
   PokéChamp's own tree search shares Pokémon objects across siblings; each pair here gets a
   private copy.
4. **Leaf request.** One Choice per opponent candidate: *"Suppose the opponent's action this turn is
   '…'. … After which of the player's actions is the player best placed to win the battle?"*, over
   the player candidates. The state is the root text plus a compact after-state per pair.
5. **Choice.** Play `argmax_a Σ_o P(o) · P(a best | o)`. The prior breaks ties.
6. **Forced cases.**
   - One legal action: played with no call.
   - A forced switch: the prior alone decides, one request.

**Speed: two wrappers, neither of which changes an answer, both checked.** Built as PokéChamp
ships it, one decision took **72–134 s** (keyless selftest and cProfile, 2026-09-25). That is the
same order as the ladder clock PokéChamp lost to. Two costs dominated:
- **`LocalSim` deep-copies the battle.** Every poke-env Pokémon holds the whole GenData and a
  406-species sets table, so one copy took about 3–5 s.
  - `pc.fast_copy` shares those read-only objects: 1.87 s for 40 copies, against 112.63 s for plain
    `deepcopy`.
- **Every damage calculation asks PokéChamp's Bayesian predictor for the species' likeliest spread**
  (about 66 ms a call, dozens per decision).
  - `pc.memoize_predictor` caches that pure function of (species, teammates, observed moves).

**Equivalence check:** `stage_a.py verify-copy 40`, run on 40 committed Stage A states, keyless.
It passed: 40/40, with 37 of them stepped.
- Under one seed, the state text is identical whether it comes from the original battle, LocalSim's
  own deepcopy, the fast copy, or the fast copy with the memo on.
- A one-step leaf is identical across the copies and with the memo.
- The original battle is left untouched.
- **Planted negative:** a "copy" that shares the battle fails 6 of 6.

With both wrappers, a fake-Jev battle took **0.35–1.05 s of CPU per decision**.

**Process and threads.** The CPU work runs in a worker thread on the private copy, so the
event loop keeps answering the server. Each shard of battles runs in its own process, so battles do
not share one interpreter lock against the clock.

**Guards:**
- **Validator.** Every Jev answer passes `policy.validated`: the labels must be exactly the options
  asked, every value finite in [0, 1], and the sum within 0.02 of 1. A refused answer plays nothing
  from Jev.
- **Deadline.** Each decision is bounded by **5 s**. Each request has a 2.5 s SDK timeout and one
  retry.
- **Fallback.** On a timeout, a refusal or any error, the player plays the fallback: PokéChamp's
  damage-calculator move, computed before the first request (its `estimate_matchup` with its 4-turn
  cut). When there is none, it plays max base power (PokéChamp's `choose_max_damage_move`). The
  decision log records every fallback, its reason and which policy played.

**Client.** `typesafe-sdk-python` `0ffd094` (v0.7.1), `AsyncTypeSafeClient`, model `jev-1.13.0`.

**Zero-call control, reported and not barred.** 200 battles vs `abyssal` with Jev disabled: the
same player, where every decision plays the fallback (damage calculator, else max base power). This
is guidance rule 4's scripted floor. **What Jev adds is the difference between the live arm and
this control, not the live arm's raw rate.**

**Keyless selftest (`stage_b.py selftest`, 4 arms), required to pass before the first live battle:**
1. A uniform fake Jev plays a full battle with no fallback and no time loss.
2. A hostile fake Jev (a wrong label set) is refused on every unforced decision, and the battle still
   finishes.
3. A fake Jev that answers after 6 s makes every unforced decision fall back inside the clock, with
   no time loss.
4. **The clock's RED arm:** a player that waits 20 s per move loses with `lost due to inactivity`.

## The bar (bead `jev-jy7t.1.3`, fixed)

Over the 200 battles vs `abyssal`:

| Verdict | Condition |
|---|---|
| **PASS (tier 1)** | win rate **≥ 0.84** and **0** losses on time |
| **KILL** | win rate **< 0.70**, or more than **1%** of battles (more than 2 of 200) lost on time |
| **FAIL** | anything in between |

- A **loss on time** is a battle whose log shows `<PokéJev's name> lost due to inactivity.`
- **Harness errors:**
  - A battle that ends in a harness error (no result row) is replayed with the same k and counted
    separately.
  - It is never counted as a win.
  - If more than 5% of battles error, the run is INVALID.
- **Reported, not barred:**
  - win rate and Wilson 95% interval per opponent;
  - the control's rate, and the live-minus-control difference with a two-proportion z-test;
  - losses on time by either side;
  - fallbacks, with reasons;
  - decision latency p50, p95 and max;
  - Jev calls, input tokens and spend;
  - resolved model ids.

**Cost estimate.** About 25 decisions per battle × 2 requests × about 3,000 tokens is about 150k
tokens, or about $0.006, per battle. That is about $4 for 620 live battles.

## Stretch (tier 2): Metamon

A released Metamon checkpoint (arXiv 2504.04395, `github.com/UT-Austin-RPL/metamon`) will be run on
the same server, format and team schedule, as a separate addendum committed before its first battle.
It will be reported as BEAT / TIE / LOSE by the Wilson interval of PokéJev's win rate against it
(above 0.5, spanning 0.5, below 0.5).

## Non-claims

- **Not a ladder result.** Stage C, the public ladder, is **not authorized** and waits for Joshua.
- **Not like for like with PokéChamp's 84%:**
  - Their teams, matches and Abyssal port are the same code family, but their n was about 25 and
    their clock and server were theirs.
  - Our clock is stricter.
- **No LLM arm.** Paid comparisons stopped on 2026-09-24.
- **LocalSim is PokéChamp's one-step damage approximation, not the real engine.** Leaf states are
  approximate by construction, as they are in PokéChamp.
- **PokéChamp's state text is not deterministic across processes.** Its stat guesses sample, and
  some of its inputs are sets. Seeded rebuilds matched the committed Stage A text on 18 and 25 of
  40 rows in two runs. Within one process and one seed, every path agrees (the verify-copy check).
- **Stage A found Jev's probabilities overconfident** (R103). This design uses them as chance
  weights anyway, as preregistered before that result. A PASS here does not certify them as
  calibrated.

## Amendment 1: a harness defect found by the feasibility arm (before any bar battle)

Committed after the first feasibility and control runs and **before any live battle against
`abyssal`, `onestep` or `maxpower`**. No bar, threshold or search constant changes.

**Defect.** PokéChamp's team file `gen9ou12.txt` gives all six Pokémon a nickname, for example
"Lynrd Spynrd (Great Tusk) @ Rocky Helmet". PokéChamp's poke-env fork then fails to match the
nicknamed switch-in to its team-preview entry and raises `team already has 6 pokemons`. The side
holding team 12 never moves and loses on time.

**Measured.** Every team-12 battle ended in a loss on time by the side holding team 12:
- first control run: 34 of 34;
- first feasibility run: 2 of 2.

No other battle in either run was lost on time.

**Fix.** `stage_b.py team_text` strips the cosmetic nicknames: "Species (G) @ Item" is the same
team with no game effect. Checked:
- only team 12's six header lines change;
- a gender tag such as "Latios (M) @ Soul Dew" is kept;
- four team-12 battles (k = 12, 13, 28, 29, both sides) then finished with no loss on time.

**The invalid first runs are kept, not scored:** `work/poke-jev/stage-b/invalid-team12-nickname-crash/`.
That covers the control (72/200 wins) and the feasibility arm (18/20 wins). Both arms are rerun from
k = 0 with the fix.

## Amendment 2: a GC stall found by the control rerun (before any bar battle)

Committed before any live battle against `abyssal`, `onestep` or `maxpower`. No bar, threshold or
search constant changes.

**Defect.** Each battle left about **270k tracked objects** behind in its process: 7.46M after 25
battles, in a keyless single-process run. A garbage collection triggered in the middle of a decision
then stalled the event loop. In the rerun control arm (79/200 wins):
- **8 of 4,979 decisions** took 5.9–15.9 s, all spent in a 30 ms copy;
- **3 battles were lost on time by PokéJev** and 2 by the opponent, which shares the event loop.

The rerun feasibility arm (18/20 wins, 0 losses on time) ran in the same window.

**Fix, in `stage_b.py`.**
- Finished battles are dropped and collected between battles, off the clock.
- The static heap is frozen once the players load (`gc.freeze()`: the Pokédex, sets and the Bayesian
  model, 666k objects).
- Each shard process runs with one BLAS thread.
- `pc.fast_copy` also shares the battle's `logger` (it had looked for `_logger`).

**Checked.** Over 10 battles in one process, tracked objects stayed at 11.8–12.0k and each
collection took 2–24 ms.

**Superseded runs are kept, not scored:** `work/poke-jev/stage-b/superseded-gc-stall/`. Both arms
are rerun from k = 0 on this code.

## Commands

```bash
work/poke-jev/serve.sh                                                   # local server (hub process)
work/poke-jev/.venv/bin/python work/poke-jev/stage_a.py verify-copy 40   # keyless copy/memo equivalence
work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py selftest         # keyless, 4 arms
work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py battles abyssal 200 --control    # zero-call control
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py battles random 20              # live feasibility
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py battles abyssal 200            # the bar
#   and the same for onestep 200, maxpower 200; 8 processes each (--workers)
work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py score            # keyless receipt
```
