"""PokéJev: Jev in PokéChamp's three LLM slots, as a clock-proof one-ply expectimax.

Per decision (Stage B prereg: docs/demos/upstream-repro/pokejev-stage-b-20260925.md):
  1. root request, two Choice questions over the same PokéChamp state text (state_translate2):
     the player's legal actions (the action prior) and the opponent's plausible actions (the
     opponent model: moves seen or predicted by PokéChamp's own Bayesian set predictor, plus switches)
  2. candidates: the prior's top K_PLAYER actions plus PokéChamp's damage-calculator move; opponent
     actions by Jev probability until OPP_MASS of the mass is covered, at most K_OPP, renormalized
  3. every (player, opponent) pair is stepped in PokéChamp's LocalSim on a private copy of the battle
  4. leaf request: per opponent candidate, one Choice over the player candidates: "after which of
     these is the player best placed to win" (relative, not absolute, judgments)
  5. value(a) = sum_o P(o) * P(a best | o); play the argmax, prior breaks ties
Every decision is bounded by DEADLINE_S; on a timeout or any error the player plays PokéChamp's own
fallback (damage-calculator move, else max base power), and the decision log says so.
"""

from __future__ import annotations

import asyncio
import contextlib
import io
import json
import logging
import os
import time

import pc  # noqa: F401 - imports PokéChamp and chdirs to its root
import replay
from policy import expectimax, pick_opponent, pick_player, validated
from pokechamp.llm_player import LLMPlayer
from pokechamp.prompts import state_translate2

JEV_MODEL = "jev-1.13.0"
DEADLINE_S = 5.0
REQUEST_TIMEOUT_S = 2.5
PRIOR_Q = "player_action"
OPP_Q = "opponent_action"
PRIOR_INSTR = (
    "Which action the player (called 'You' and 'Your' in the state) should choose for the current turn "
    "of this Pokémon Showdown Gen 9 OU battle to win it."
)
OPP_INSTR = "Which action the opponent chooses for the current turn of this Pokémon Showdown Gen 9 OU battle."
LEAF_INSTR = (
    "Suppose the opponent's action this turn is '{o}'. outcomes['{o}'] gives the position after each of the "
    "player's candidate actions. After which of the player's actions is the player best placed to win the battle?"
)


class NoLLM:
    """PokéChamp's LLMPlayer requires a backend object; PokéJev never calls one."""

    def get_LLM_action(self, *args, **kwargs):  # noqa: N802 - PokéChamp's interface name
        raise RuntimeError("PokéJev makes no LLM call")


def pretty_species(species: str) -> str:
    entry = pc.GEN.pokedex.get(species)
    return entry["name"] if entry else species


def mon_line(mon) -> str:
    if mon is None:
        return "none"
    hp = round(mon.current_hp_fraction * 100)
    parts = [f"{pretty_species(mon.species)} {hp}%"]
    if mon.status:
        parts.append(mon.status.name.lower())
    boosts = {k: v for k, v in mon.boosts.items() if v}
    if boosts:
        parts.append(" ".join(f"{k}{v:+d}" for k, v in sorted(boosts.items())))
    return ", ".join(parts)


def leaf_summary(battle) -> dict:
    """Compact after-state for a leaf question; the full history is in the root state text."""
    ours = [m for m in battle.team.values() if not m.active]
    theirs = [m for m in battle.opponent_team.values() if not m.active]
    return {
        "your_active": mon_line(battle.active_pokemon),
        "opponent_active": mon_line(battle.opponent_active_pokemon),
        "your_bench": [mon_line(m) for m in ours],
        "your_fainted": sum(1 for m in battle.team.values() if m.fainted),
        "opponent_bench_seen": [mon_line(m) for m in theirs],
        "opponent_fainted": sum(1 for m in battle.opponent_team.values() if m.fainted),
    }


class PokeJevPlayer(LLMPlayer):
    def __init__(
        self, *args, decision_log: str | None = None, client_factory=None, **kwargs
    ):
        kwargs.setdefault("llm_backend", NoLLM())
        kwargs.setdefault("prompt_translate", state_translate2)
        kwargs.setdefault("backend", "none")
        super().__init__(*args, **kwargs)
        pc.alias_clock_format()
        pc.memoize_predictor()
        self._decision_log = decision_log
        self._client_factory = client_factory
        self._client = None

    # ------------------------------------------------------------------ Jev
    def _jev(self):
        if self._client is None:
            if self._client_factory is not None:
                self._client = self._client_factory()
            else:
                if not os.environ.get("TYPESAFE_API_KEY"):
                    raise RuntimeError("unconfigured: TYPESAFE_API_KEY unset")
                from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy

                self._client = AsyncTypeSafeClient(
                    timeout=REQUEST_TIMEOUT_S,
                    retry=RetryPolicy(
                        max_retries=1, backoff_initial=0.2, backoff_max=0.5
                    ),
                )
        return self._client

    async def _ask(self, state, questions, rec):
        t0 = time.perf_counter()
        resp = await self._jev().system_one(state, questions, model=JEV_MODEL)
        rec["jev_ms"].append(int((time.perf_counter() - t0) * 1000))
        rec["input_tokens"] += int(resp.usage.input_tokens)
        rec["models"].add(resp.model)
        return resp

    # ------------------------------------------------------------------ options
    def _our_options(self, battle):
        opts, orders, display = [], {}, {}
        valid_moves = [m for m in battle.available_moves if m.id != "nothing"]
        for m in valid_moves:
            key = f"move {m.id}"
            opts.append(key)
            orders[key] = self.create_order(m)
            display[key] = pc.move_name(m.id)
        if battle.can_tera:
            for m in valid_moves:
                key = f"move {m.id}{replay.TERA_SUFFIX}"
                opts.append(key)
                orders[key] = self.create_order(m, terastallize=True)
                display[key] = pc.move_name(m.id) + " and Terastallize"
        for mon in battle.available_switches:
            key = f"switch {mon.species}"
            opts.append(key)
            orders[key] = self.create_order(mon)
            display[key] = "Switch to " + pretty_species(mon.species)
        return opts, orders, display

    def _opp_options(self, battle, sim):
        from poke_env.environment.move import Move

        opp = battle.opponent_active_pokemon
        opts, orders, display = [], {}, {}
        with contextlib.redirect_stdout(io.StringIO()):
            seen, potential = sim.get_opponent_current_moves(
                mon=opp, return_separate=True
            )
        for mid in [replay.to_id(m) for m in list(seen) + list(potential)]:
            key = f"move {mid}"
            if not mid or key in orders:
                continue
            try:
                orders[key] = self.create_order(Move(mid, gen=9))
            except Exception:  # noqa: BLE001 - an id PokéChamp predicts but poke-env does not know
                continue
            opts.append(key)
            display[key] = pc.move_name(mid)
        bench = {m.species: m for m in battle.opponent_team.values()}
        for m in getattr(battle, "teampreview_opponent_team", []) or []:
            bench.setdefault(m.species, m)
        for species, mon in bench.items():
            if mon.fainted or (opp is not None and species == opp.species):
                continue
            key = f"switch {species}"
            opts.append(key)
            orders[key] = self.create_order(mon)
            display[key] = "Switch to " + pretty_species(species)
        return opts, orders, display

    # ------------------------------------------------------------------ decision
    async def choose_move(self, battle):  # noqa: C901 - one decision, one log row
        t0 = time.perf_counter()
        rec = {
            "battle": battle.battle_tag,
            "turn": battle.turn,
            "jev_ms": [],
            "input_tokens": 0,
            "models": set(),
            "fallback": None,
            "forced": False,
            "cpu_ms": {},
        }
        box: dict = {}
        try:
            order = await asyncio.wait_for(
                self._decide(battle, rec, box), timeout=DEADLINE_S
            )
        except Exception as exc:  # noqa: BLE001 - every failure plays the fallback, never a Jev answer
            rec["fallback"] = f"{type(exc).__name__}: {str(exc)[:200]}"
            order = box.get("tool_order") or self.choose_max_damage_move(battle)
            rec["fallback_policy"] = (
                "damage-calculator" if box.get("tool_order") else "max-base-power"
            )
            rec["chosen"] = order.message
        rec["ms"] = int((time.perf_counter() - t0) * 1000)
        rec["models"] = sorted(rec["models"])
        if self._decision_log:
            with open(self._decision_log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
        return order

    def _tool_order(self, sim):
        """PokéChamp's dmg_calc_move on our fast copy: its estimate_matchup, its 4-turn cut.

        dmg_calc_move itself builds a LocalSim with a full deepcopy (seconds); the logic is the same.
        """
        b = sim.battle
        if (
            not b.available_moves
            or b.active_pokemon is None
            or b.active_pokemon.fainted
        ):
            return None
        with contextlib.redirect_stdout(io.StringIO()):
            order, turns = self.estimate_matchup(
                sim, b, b.active_pokemon, b.opponent_active_pokemon
            )
        return order if turns <= 4 else None

    def _prepare(self, sim, forced_switch, rec, box):
        """CPU-bound root work, run in a worker thread on the private copy `sim` holds."""
        t = time.perf_counter()
        box["tool_order"] = None if forced_switch else self._tool_order(sim)
        rec["cpu_ms"]["tool"] = int((time.perf_counter() - t) * 1000)
        t = time.perf_counter()
        with contextlib.redirect_stdout(io.StringIO()):
            system_prompt, state_prompt, action_prompt = state_translate2(
                sim, sim.battle
            )
        rec["cpu_ms"]["state"] = int((time.perf_counter() - t) * 1000)
        t = time.perf_counter()
        opp = ([], {}, {}) if forced_switch else self._opp_options(sim.battle, sim)
        rec["cpu_ms"]["opp_options"] = int((time.perf_counter() - t) * 1000)
        return system_prompt + "\n" + state_prompt + "\n" + action_prompt, opp

    @staticmethod
    def _leaves(sim, cands, opp, orders, o_orders, display, o_display, rec):
        """Step every (player, opponent) pair in LocalSim on its own copy; worker thread."""
        t = time.perf_counter()
        outcomes = {}
        for o in opp:
            row = {}
            for a in cands:
                try:
                    leaf = pc.new_sim(sim.battle)
                    with contextlib.redirect_stdout(io.StringIO()):
                        leaf.step(orders[a], o_orders[o])
                    row[display[a]] = leaf_summary(leaf.battle)
                except Exception as exc:  # noqa: BLE001 - an unsimulable pair is shown as such
                    row[display[a]] = {"unsimulated": type(exc).__name__}
            outcomes[o_display[o]] = row
        rec["cpu_ms"]["leaves"] = int((time.perf_counter() - t) * 1000)
        return outcomes

    async def _decide(self, battle, rec, box):
        from typesafe_sdk import Choice

        opts, orders, display = self._our_options(battle)
        rec["n_options"] = len(opts)
        if len(opts) == 1:
            rec["forced"] = True
            rec["chosen"] = opts[0]
            return orders[opts[0]]
        forced_switch = not battle.available_moves
        t = time.perf_counter()
        sim = pc.new_sim(
            battle
        )  # the only read of the live battle, on the event-loop thread
        rec["cpu_ms"]["copy"] = int((time.perf_counter() - t) * 1000)
        text, (o_opts, o_orders, o_display) = await asyncio.to_thread(
            self._prepare, sim, forced_switch, rec, box
        )
        tool_order = box.get("tool_order")
        tool_key = None
        if tool_order is not None:
            tool_key = next(
                (k for k, o in orders.items() if o.message == tool_order.message), None
            )
        rec["tool"] = tool_key
        questions = {
            PRIOR_Q: Choice(
                instructions=PRIOR_INSTR, criteria={display[k]: None for k in opts}
            )
        }
        if o_opts:
            questions[OPP_Q] = Choice(
                instructions=OPP_INSTR, criteria={o_display[k]: None for k in o_opts}
            )
        resp = await self._ask(text, questions, rec)
        prior = validated(resp.answers[PRIOR_Q].probabilities, display)
        rec["prior_top"] = max(prior, key=prior.get)
        if forced_switch or not o_opts:
            rec["forced"] = forced_switch
            rec["chosen"] = rec["prior_top"]
            return orders[rec["prior_top"]]
        opp = pick_opponent(validated(resp.answers[OPP_Q].probabilities, o_display))
        cands = pick_player(prior, tool_key)
        rec["candidates"] = cands
        rec["opponent"] = opp
        if len(cands) == 1:
            rec["chosen"] = cands[0]
            return orders[cands[0]]
        outcomes = await asyncio.to_thread(
            self._leaves, sim, cands, opp, orders, o_orders, display, o_display, rec
        )
        leaf_qs = {
            f"best_after_{i}": Choice(
                instructions=LEAF_INSTR.format(o=o_display[o]),
                criteria={display[a]: None for a in cands},
            )
            for i, o in enumerate(opp)
        }
        resp2 = await self._ask({"battle": text, "outcomes": outcomes}, leaf_qs, rec)
        best_given = {}
        for i, o in enumerate(opp):
            best_given[o] = validated(
                resp2.answers[f"best_after_{i}"].probabilities,
                {a: display[a] for a in cands},
            )
        chosen, values = expectimax(cands, opp, best_given, prior)
        rec["values"] = {k: round(v, 4) for k, v in values.items()}
        rec["chosen"] = chosen
        return orders[chosen]


logging.getLogger("poke-jev").setLevel(logging.WARNING)
