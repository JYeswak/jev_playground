"""PokéChamp bootstrap: import its poke_env fork, LocalSim and translator from the vendored clone.

PokéChamp (github.com/sethkarten/pokechamp @0f84c46, MIT, Seth Karten) is wrapped, never patched.
Its data files load by paths relative to the clone root, so importing this module chdirs there;
every path in this package is therefore absolute.
"""

from __future__ import annotations

import contextlib
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


def new_sim(battle) -> "LocalSim":
    return LocalSim(
        battle,
        data_cache.get_cached_move_effect(),
        data_cache.get_cached_pokemon_move_dict(),
        data_cache.get_cached_ability_effect(),
        data_cache.get_cached_pokemon_ability_dict(),
        data_cache.get_cached_item_effect(),
        data_cache.get_cached_pokemon_item_dict(),
        GEN,
        False,
        "",
        format=SIM_FORMAT,
        prompt_translate=state_translate2,
    )


def move_name(move_id: str) -> str:
    entry = GEN.moves.get(move_id)
    return entry["name"] if entry else move_id


def sets_data() -> dict:
    return data_cache.get_cached_moves_set(SIM_FORMAT)


def build_state(
    lines: list[str], player: str, turn: int, battle_id: str, active_key: str
) -> dict:
    """PokéChamp's own replay -> prompt path (pokechamp/translate.py add_battle), stopped at |turn|N.

    Differences from add_battle, both toward a correct state: the player's switch list is the
    team's non-fainted, non-active members (spectator logs carry no |request|, and poke-env's
    spectator list included fainted ones), and the action labels come from replay.label, not
    from the last move line in a chunk.
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
