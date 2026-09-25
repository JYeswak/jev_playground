"""PokéChamp bootstrap: import its poke_env fork, LocalSim and translator from the vendored clone.

PokéChamp (github.com/sethkarten/pokechamp @0f84c46, MIT, Seth Karten) is wrapped, never patched.
Its data files load by paths relative to the clone root, so importing this module chdirs there;
every path in this package is therefore absolute.
"""

from __future__ import annotations

import contextlib
import copy
import io
import logging
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PC_ROOT = os.path.join(ROOT, "pokechamp")
PC_SHA = "0f84c46"

if PC_ROOT not in sys.path:
    sys.path.insert(0, PC_ROOT)
os.chdir(PC_ROOT)

with contextlib.redirect_stdout(
    io.StringIO()
):  # PokéChamp prints ASCII banners on import
    # translate first: it imports llm_player -> poke_env in the order PokéChamp itself uses; importing
    # data_cache first hits a circular import (data_cache -> poke_env.player.baselines -> data_cache).
    from pokechamp.translate import recursive_nick_removal  # noqa: E402
    from pokechamp import data_cache  # noqa: E402
    from pokechamp.prompts import state_translate2  # noqa: E402
    from poke_env.data.gen_data import GenData  # noqa: E402
    from poke_env.environment.battle import Battle  # noqa: E402
    from poke_env.environment.move import Move  # noqa: E402
    from poke_env.player.local_simulation import LocalSim  # noqa: E402

import replay  # noqa: E402

GEN = GenData.from_format("gen9ou")
SIM_FORMAT = "gen9ou"  # PokéChamp's LocalSim switches its set data on this exact string
CLOCK_FORMAT = "gen9ouclock"  # Stage B's server format: Gen 9 OU rules plus a clock (showdown/custom-formats.ts)


def alias_clock_format() -> None:
    """Give the clocked format PokéChamp's Gen 9 OU Bayesian set predictor.

    poke-env Pokémon carry their battle's format string, and PokéChamp's predictor singleton keys its
    model by that string; for "gen9ouclock" it tries to download a model that does not exist (HTTP 404)
    and every decision falls back. The rules are Gen 9 OU's, so the Gen 9 OU model is the right one.
    """
    from bayesian import predictor_singleton

    with contextlib.redirect_stdout(io.StringIO()):
        model = predictor_singleton.get_pokemon_predictor(SIM_FORMAT)
    predictor_singleton._predictor_instances.setdefault(CLOCK_FORMAT, model)


def memoize_predictor() -> None:
    """Memoize PokéChamp's Bayesian predictor queries by their arguments.

    Every damage calculation calls Pokemon.calculate_stats, which asks the predictor for the species'
    most likely nature and EV spread (pokemon.py:972-1129): about 66 ms a call, dozens per decision.
    The answer is a pure function of (species, teammates, observed moves) on a trained model, so a
    cache returns the same answer; each hit hands back a deep copy so no caller can alter the cache.
    `stage_a.py verify-copy` checks state texts and one-step leaves with and without the memo.
    """
    from bayesian import predictor_singleton

    with contextlib.redirect_stdout(io.StringIO()):
        model = predictor_singleton.get_pokemon_predictor(SIM_FORMAT)
    if getattr(model, "_pokejev_memo", None) is not None:
        return
    raw = model.predict_component_probabilities
    cache: dict = {}

    def memo(species, teammates=None, observed_moves=None):
        key = (species, tuple(teammates or ()), tuple(observed_moves or ()))
        if key not in cache:
            cache[key] = raw(species, teammates, observed_moves)
        return copy.deepcopy(cache[key])

    model._pokejev_memo = cache
    model._pokejev_raw = raw
    model.predict_component_probabilities = memo


def unmemoize_predictor() -> None:
    from bayesian import predictor_singleton

    model = predictor_singleton.get_pokemon_predictor(SIM_FORMAT)
    if getattr(model, "_pokejev_memo", None) is not None:
        model.predict_component_probabilities = model._pokejev_raw
        model._pokejev_memo = None


def fast_copy(battle):
    """deepcopy(battle), sharing the read-only static data every Pokémon points at.

    Each poke-env Pokémon holds the whole GenData and its format's full sets table (406 species);
    a plain deepcopy copies both for every Pokémon, about 3-5 s per battle on this machine. Those
    objects are never written during a battle, so sharing them gives the same simulation. The
    equivalence is checked, not assumed: `stage_a.py verify-copy` rebuilds committed Stage A states
    through this path and compares their sha256 with the ones built by LocalSim's own deepcopy.
    """
    memo = {}
    for obj in (getattr(battle, "_data", None), getattr(battle, "logger", None)):
        if obj is not None:
            memo[id(obj)] = obj
    mons = list(getattr(battle, "_team", {}).values()) + list(
        getattr(battle, "_opponent_team", {}).values()
    )
    mons += list(getattr(battle, "_teampreview_opponent_team", []) or [])
    for mon in mons:
        for attr in ("_data", "_sets"):
            obj = getattr(mon, attr, None)
            if obj is not None:
                memo[id(obj)] = obj
    return copy.deepcopy(battle, memo)


def sim_args() -> tuple:
    """LocalSim's positional arguments after the battle, from PokéChamp's own data cache."""
    return (
        data_cache.get_cached_move_effect(),
        data_cache.get_cached_pokemon_move_dict(),
        data_cache.get_cached_ability_effect(),
        data_cache.get_cached_pokemon_ability_dict(),
        data_cache.get_cached_item_effect(),
        data_cache.get_cached_pokemon_item_dict(),
        GEN,
        False,
        "",
    )


def new_sim(battle) -> "LocalSim":
    """PokéChamp's LocalSim over a private copy of `battle`, made by fast_copy.

    LocalSim.__init__ deep-copies whatever battle it is given and reads nothing else from it, so it
    is constructed on None and handed the fast copy.
    """
    sim = LocalSim(
        None, *sim_args(), format=SIM_FORMAT, prompt_translate=state_translate2
    )
    sim.battle = fast_copy(battle)
    return sim


def move_name(move_id: str) -> str:
    entry = GEN.moves.get(move_id)
    return entry["name"] if entry else move_id


def sets_data() -> dict:
    return data_cache.get_cached_moves_set(SIM_FORMAT)


def replay_sim(
    lines: list[str], player: str, turn: int, battle_id: str, active_key: str
):
    """A LocalSim holding the battle as the player saw it at |turn|N, via PokéChamp's replay path.

    Mirrors pokechamp/translate.py add_battle: nickname removal, |premove| lines giving the player's
    team the moves each species used anywhere in the battle, then the log replayed through LocalSim.
    One difference, toward a correct state: the player's switch list is the team's non-fainted,
    non-active members (spectator logs carry no |request|, and poke-env's spectator list included
    fainted ones).
    """
    names = replay.players(lines)
    text = recursive_nick_removal(list(lines))
    hind = replay.hindsight_moves(text)[player]
    species_text = {}
    for ln in text:
        f = ln.split("|")
        if len(f) > 3 and f[1] in ("switch", "drag") and f[2].startswith(player + "a"):
            species_text[replay.species_key(f[3])] = f[3].split(",")[0].strip()
    start = next(
        i
        for i, ln in enumerate(text)
        if ln.startswith("|start") or ln.startswith("|teampreview")
    )
    pre = [
        f"|premove|{player}a: {species_text[k]}|{m}"
        for k, ms in hind.items()
        if k in species_text
        for m in ms
    ]
    text = text[:start] + pre + text[start:]

    battle = Battle(
        f"battle-gen9ou-{battle_id}",
        names[player],
        logging.getLogger("poke-jev"),
        gen=9,
    )
    sim = new_sim(battle)
    reached = False
    for ln in text:
        msg = ln.split("|")
        if len(msg) < 2 or not msg[1]:
            continue
        try:
            sim._handle_battle_message(msg)
        except (
            KeyError,
            ValueError,
            NotImplementedError,
        ):  # add_battle skips the same three
            pass
        if msg[1] == "turn" and int(msg[2]) == turn:
            reached = True
            break
    if not reached:
        raise ValueError(f"turn {turn} not reached")
    b = sim.battle
    b._available_moves = [Move(m, gen=9) for m in hind.get(active_key, [])]
    b._available_switches = [
        m for m in b.team.values() if not m.active and not m.fainted
    ]
    return sim


def build_state(
    lines: list[str], player: str, turn: int, battle_id: str, active_key: str
) -> dict:
    """PokéChamp's state_translate2 text at |turn|N, plus its opponent move candidates.

    The action labels come from replay.label, not from the last move line in a chunk as in add_battle.
    """
    sim = replay_sim(lines, player, turn, battle_id, active_key)
    b = sim.battle
    with contextlib.redirect_stdout(io.StringIO()):
        system_prompt, state_prompt, action_prompt = state_translate2(sim, b)
        seen, potential = sim.get_opponent_current_moves(
            mon=b.opponent_active_pokemon, return_separate=True
        )
    return {
        "text": system_prompt + "\n" + state_prompt + "\n" + action_prompt,
        "opp_seen": [replay.to_id(m) for m in seen],
        "opp_potential": [replay.to_id(m) for m in potential],
    }
