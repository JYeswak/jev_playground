# PokéJev Leaf C r4 code-only partial receipt

**Status: `NOT-SCORED` — interim action-mix gate failed.** This receipt records the
partial supervised arm; it is not a 200-battle result and does not authorize a
continuation.

## Frozen run

- Bead: `jev-9gtw.1`.
- Run id: `leaf-c-r4-code`.
- Command: `work/poke-jev/.venv/bin/python work/loss-depth/pokejev-components/battle/run.py battles abyssal 200 --workers 8 --leaf code --run-id leaf-c-r4-code`.
- Pairing: `abyssal`, pair seed `20260925`, target `k=0..199`, eight workers.
- Frozen leaf model: `work/loss-depth/pokejev-components/leaf-model-v1.json`, SHA256 `ad8cd16482eb41e409409c94c968d0b2857f736bd6258b9afd556d785273c49b`.
- The preregistered run note is `docs/demos/upstream-repro/loss-depth-pokejev-leaf-c-r4-battle-note-20250925.md`; its bar is 140/200 wins, no harness errors, and a valid receipt.

## Partial artifacts

- `work/loss-depth/pokejev-components/decisions-abyssal-leaf-code-leaf-c-r4-code.jsonl`: 991 decision rows, `run_id=leaf-c-r4-code`, `run_py_sha256=3450051c7270106e00fbf148877028d9817e51506cf8f5726f2259efe2ee3209`.
- `work/loss-depth/pokejev-components/results-abyssal-leaf-code-v1.jsonl`: 45 partial result rows (39 completed rows and 6 error rows at receipt time).
- `work/loss-depth/pokejev-components/battle/stage-b/mix-v1-stop.json`: `{"reason":"r4 interim gate reached 200 eligible decisions"}`.
- The supervised log footer was `exit_code=1`; the child did not clear the gate and the run was not continued.

## Gate readings

The same verdict was observed at both required boundaries; the readings are not
backfilled into one another:

1. **Stop-time reading.** Pane 1 recorded the checker at `2026-09-25T09:39:29Z`
   on the file as it stood at the stop boundary: 245 eligible decisions,
   offered-switch rate `0.078` versus the Stage B reference `0.362`, absolute
   difference `0.284`, checker exit `1`.
2. **Final drained-file reading.** After workers drained, the committed-input
   991-row file had 415 eligible decisions. The keyless checker output was:

   ```text
   type=move arm=0.911 reference=0.638 diff=0.272 z=11.13 n=415/3396
   type=switch arm=0.089 reference=0.362 diff=0.272 z=-11.13 n=415/3396
   exit_code=1
   ```

Both readings fail the preregistered absolute-difference limit `0.10`, so the
arm remains `NOT-SCORED`. No battle win rate, Wilson interval, or Jev-vs-battle
claim is made from these rows.

## Opponent-reply autopsy

The proposed omission is **not** the cause. `work/poke-jev/player.py:248-262`
creates a fresh simulator for every candidate/opponent pair, then calls the same
`leaf.step(orders[a], o_orders[o])` for both move and switch candidates before
calling `leaf_summary`. `pokechamp/poke_env/player/local_simulation.py:440-454`
processes a switch before the opponent action; `:475-482` calculates the
post-action HP state, and `:500-512` applies damage to the active Pokémon. The
resulting summary records both sides at `work/poke-jev/player.py:74-85`.
The frozen scorer consumes both sides: `work/loss-depth/pokejev-components/battle/run.py:447-478`
parses `your_active` plus `your_bench` and `opponent_active` plus the seen bench,
then derives `hp_weighted_remaining`, `opponent_hp_remaining`, and
`hp_differential`.

Therefore a switch is **not** scored on opponent HP alone: the opponent reply is
simulated against the switched-in active Pokémon, and our post-action HP is in
the score inputs. The r4 failure is the observed action-mix mismatch, not a
missing opponent-reply update.

## Boundary and parked line

This was a code-only leaf arm; no new leaf Noul requests were made. The prior
r4 held-out read found a Noul delta of `-0.003` and no reason to carry the three
Nouls forward once both sides' HP are present. Further leaf rounds would tune
PokéChamp's action-ranking model, not test Jev. The leaf line is parked.
