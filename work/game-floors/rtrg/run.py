#!/usr/bin/env python3
"""Model-free floors for Real-Time Reasoning Gym (Wen et al., arXiv 2511.04898).

Runs three model-free policies through the gym's own environment classes
(realtimegym @ 3d5b3ef) and records the gym's own episode reward ``env.reward``
(the value ``agile_eval.game_loop`` reports) plus the paper's normalized score
S = (R - Rmin) / (Rmax - Rmin) with Rmin/Rmax from paper App. A Table 4.

Policies (all decide from ``serialize_state(...)``, i.e. what a Jev arm sees):
  default   never answers; every step the env gets the gym's DEFAULT_ACTION
            (realtimegym.prompts.<game>.DEFAULT_ACTION: freeway 'U', snake 'S'
            = keep heading, overcooked 'S' = stay).
  random    uniform over the legal actions, seeded by (game, level, seed, rep).
  scripted  hand-written reactive heuristic on the current state only.

Seeds (``--seeds``):
  freeway   0-7 are the published instances (freeway.seed_mapping); any seed
            >= 9000 is used directly as the FreewayEnv RNG seed (dev), and the
            instance's minimum steps S (App. A Table 5) is computed and must lie
            in the requested level's range.
  snake     0-31 are the gym's mapped instances (0-7 published); a seed s in
            [9000, 9099] maps to real seed N*1000 + 900 + (s - 9000), i.e. the
            same obstacle count N as the level, layout RNG seed 900-999 (dev).
  overcooked the gym ignores the seed (one fixed layout per level); the seed
            only seeds the random policy. 0-7 are the published seed labels.
Published seeds need ``--allow-published`` (wave 2 only).
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import os
import random
import sys
import time
import traceback
from collections import deque
from typing import Any

GAMES = ("freeway", "snake", "overcooked")
LEVELS = ("E", "M", "H")
ENV_ID = {
    g: {lvl: f"{g.capitalize()}-v{i}" for i, lvl in enumerate(LEVELS)} for g in GAMES
}
HORIZON = (
    100  # App. A: step limit M = 100 (freeway.py:146, snake.py:149, overcooked.py:113)
)
R_RANGE = {
    "freeway": (0.0, 89.0),
    "snake": (-1.0, 15.0),
    "overcooked": (0.0, 56.0),
}  # App. A Table 4
FREEWAY_S_RANGE = {"E": (1, 12), "M": (13, 16), "H": (17, 21)}  # App. A Table 5
SNAKE_DEV_BASE, SNAKE_DEV_TRUE_SEED0 = 9000, 900
DEV_MIN = 9000
DIRS = {
    "U": (0, 1),
    "D": (0, -1),
    "L": (-1, 0),
    "R": (1, 0),
}  # snake.py:99-106, overcooked.py:155-162 + prompt
REVERSE = {"U": "D", "D": "U", "L": "R", "R": "L"}


def _prompts(game: str) -> Any:
    return importlib.import_module(f"realtimegym.prompts.{game}")


def _jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if hasattr(x, "item") and not isinstance(x, (str, bytes)):  # numpy scalar
        return x.item()
    return x


# --------------------------------------------------------------------------- state


def serialize_state(game: str, obs: dict[str, Any]) -> dict[str, Any]:
    """The per-decision state a Jev arm receives.

    ``obs["state"]`` is the structured dict the gym's ReactiveAgent passes to
    ``prompts.<game>.state_to_description(..., mode="reactive")``
    (agents/reactive.py:26-28); every field of it is rendered into that prompt
    or is the turn counter, so nothing beyond what the published agents saw is
    exposed. The action alphabet and default action are the prompt module's
    ALL_ACTIONS / DEFAULT_ACTION. The prose prompt and ``state_string`` render
    are not included.
    """
    p = _prompts(game)
    actions = list(p.ALL_ACTIONS)
    return {
        "game": game,
        "turn": int(obs["game_turn"]),
        "horizon": HORIZON,
        "actions": actions,
        "default_action": p.DEFAULT_ACTION,
        "observation": _jsonable(obs["state"]),
    }


# --------------------------------------------------------------------------- envs


def make_env(
    game: str, level: str, seed: int, layout: str | None, allow_published: bool
) -> tuple[Any, dict[str, Any]]:
    import realtimegym
    from realtimegym.environments import freeway as fw
    from realtimegym.environments import snake as sn

    meta: dict[str, Any] = {"layout": None, "min_steps": None}
    published = (
        seed in fw.seed_mapping[level]
        if game == "freeway"
        else seed in sn.seed_mapping[level] and seed < 8
        if game == "snake"
        else layout is None and seed < 8
    )
    if published and not allow_published:  # checked before any env is built or reset
        raise ValueError(
            f"{game} {level} seed {seed} is a published instance; pass --allow-published (wave 2 only)"
        )
    if game == "freeway":
        if seed in fw.seed_mapping[level]:
            env, real, _ = realtimegym.make(ENV_ID[game][level], seed=seed)
        elif seed >= DEV_MIN:
            env = fw.FreewayEnv()
            env.set_seed(seed)
            real = seed
            s = freeway_min_steps(seed)
            lo, hi = FREEWAY_S_RANGE[level]
            if s is None or not lo <= s <= hi:
                raise ValueError(
                    f"freeway dev seed {seed} has min steps {s}, outside level {level} range {lo}-{hi}"
                )
            meta["min_steps"] = s
        else:
            raise ValueError(
                f"freeway seed {seed}: neither a published index {sorted(fw.seed_mapping[level])} nor a dev seed >= {DEV_MIN}"
            )
    elif game == "snake":
        if seed in sn.seed_mapping[level]:
            env, real, _ = realtimegym.make(ENV_ID[game][level], seed=seed)
        elif SNAKE_DEV_BASE <= seed < SNAKE_DEV_BASE + 100:
            n_obstacles = sn.seed_mapping[level][0] // 1000
            real = n_obstacles * 1000 + SNAKE_DEV_TRUE_SEED0 + (seed - SNAKE_DEV_BASE)
            env = sn.SnakeEnv()
            env.set_seed(real)
        else:
            raise ValueError(
                f"snake seed {seed}: use a mapped index 0-31 or a dev seed {SNAKE_DEV_BASE}-{SNAKE_DEV_BASE + 99}"
            )
    else:
        env, real, _ = realtimegym.make(
            ENV_ID[game][level], seed=seed
        )  # seed is inert for overcooked
        if layout:
            env.all_args.layout_name = layout
        meta["layout"] = env.all_args.layout_name
    meta.update({"real_seed": int(real), "published_instance": bool(published)})
    return env, meta


def freeway_min_steps(real_seed: int) -> int | None:
    """Minimum turns to cross (App. A Table 5 'S'): BFS over the real env with collisions forbidden."""
    from realtimegym.environments.freeway import FreewayEnv

    env = FreewayEnv()
    env.set_seed(real_seed)
    env.reset()
    frontier = {env.pos: env}
    for turn in range(1, HORIZON + 1):
        nxt: dict[int, Any] = {}
        for e in frontier.values():
            for a in "USD":
                c = copy.deepcopy(e)
                c.step(a)
                if c.terminal and c.reward > 0:
                    return turn
                if c.terminal or c.r:
                    continue
                nxt.setdefault(c.pos, c)
        frontier = nxt
        if not frontier:
            return None
    return None


# --------------------------------------------------------------------------- policies


def legal_actions(state: dict[str, Any]) -> list[str]:
    if (
        state["game"] == "snake"
    ):  # snake.py:179-189 get_possible_actions: no instant reverse
        heading = state["observation"]["snake_dir"]
        return [a for a in "LRUD" if a != REVERSE[heading]]
    return list(state["actions"])


def freeway_scripted(state: dict[str, Any]) -> str:
    """Up if the next lane is car-free at the arrival turn under the prompt's car rule, else stay, else down."""
    ob = state["observation"]
    y = ob["player_states"]

    def hit(lane: int, dt: int) -> bool:
        if lane <= 0 or lane >= 9:
            return False
        for c_lane, head, direction, speed, span in ob["car_states"]:
            if c_lane != lane or head is None:
                continue
            if direction == "left":  # Span(T) = [h - s dt, tau - s dt], tau = h + span
                lo, hi = head - speed * dt, head + span - speed * dt
            else:  # Span(T) = [tau + s dt, h + s dt], tau = h - span
                lo, hi = head - span + speed * dt, head + speed * dt
            if lo <= 0 <= hi:
                return True
        return False

    if not hit(y + 1, 1):
        return "U"
    if not hit(y, 1):
        return "S"
    if y > 0 and not hit(y - 1, 1):
        return "D"
    return "S"


def snake_scripted(state: dict[str, Any]) -> str:
    """Greedy BFS toward the nearest food still alive on arrival; never into wall/obstacle/body next step;
    avoid zero-exit cells when possible; ties -> more free neighbours."""
    ob = state["observation"]
    size = ob["size"]
    body = [tuple(p) for p in ob["snake"]]  # head first
    head, tail = body[0], body[-1]
    heading = ob["snake_dir"]
    foods = {(f[0], f[1]): (f[2], f[3]) for f in ob["foods"]}
    walls = {tuple(o) for o in ob["internal_obstacles"]}
    # snake.py:111-123 death: body except tail, obstacles, border, or tail cell holding positive food
    blocked = walls | set(body[:-1])
    if tail in foods and foods[tail][1] > 0 and len(body) > 1:
        blocked.add(tail)

    def free(c: tuple[int, int]) -> bool:
        return 0 < c[0] < size - 1 and 0 < c[1] < size - 1 and c not in blocked

    def step(c: tuple[int, int], a: str) -> tuple[int, int]:
        return (c[0] + DIRS[a][0], c[1] + DIRS[a][1])

    def dist_to(src: tuple[int, int], dst: tuple[int, int], extra: set) -> int | None:
        seen, q = {src}, deque([(src, 0)])
        while q:
            c, d = q.popleft()
            if c == dst:
                return d
            for a in DIRS:
                n = step(c, a)
                if n not in seen and free(n) and n not in extra:
                    seen.add(n)
                    q.append((n, d + 1))
        return None

    moves = [a for a in legal_actions(state) if free(step(head, a))]
    if not moves:
        return heading
    after = {a: step(head, a) for a in moves}
    exits = {
        a: sum(free(step(after[a], b)) and step(after[a], b) != head for b in DIRS)
        for a in moves
    }
    if any(exits.values()):
        moves = [a for a in moves if exits[a] > 0]
    target = None
    best = None
    for pos, (life, value) in foods.items():
        if value <= 0:
            continue
        d = dist_to(head, pos, set())
        if d is not None and 1 <= d <= life and (best is None or d < best):
            best, target = d, pos
    if target is None:
        return max(moves, key=lambda a: (exits[a], a == heading))

    def key(a: str) -> tuple:
        d = dist_to(after[a], target, {head})
        return (d if d is not None else 10**6, -exits[a], a != heading)

    return min(moves, key=key)


def overcooked_scripted(state: dict[str, Any]) -> str:
    """Onion -> pot until a pot has 3 (auto-cooks), fetch dish, wait at the cooking pot, pick soup, serve.
    Items that cannot be used are put on the nearest empty counter."""
    ob = state["observation"]
    lay = {k: {tuple(p) for p in v} for k, v in ob["layout"].items()}
    me, other = ob["state"]["players"]
    pos, facing = tuple(me["position"]), tuple(me["orientation"])
    held = me["held_object"]["name"] if me["held_object"] else None
    blocked_by_partner = tuple(other["position"])
    objects = {tuple(o["position"]): o for o in ob["state"]["objects"]}
    pots = {}
    for p in lay["P"]:
        o = objects.get(p)
        n = len(o["_ingredients"]) if o else 0
        pots[p] = {
            "n": n,
            "cooking": bool(o and o["is_cooking"]),
            "ready": bool(o and o["is_ready"]),
        }
    empty_counters = {c for c in lay["X"] if c not in objects}
    wait = False
    if held == "soup":
        targets = lay["S"]
    elif held == "dish":
        targets = {p for p, s in pots.items() if s["ready"]}
        if not targets:
            targets = {p for p, s in pots.items() if s["cooking"]}
            wait = True
        if not targets:
            targets, wait = empty_counters, False
    elif held in ("onion", "tomato"):
        targets = {
            p
            for p, s in pots.items()
            if s["n"] < 3 and not s["cooking"] and not s["ready"]
        } or empty_counters
    else:
        busy = any(s["cooking"] or s["ready"] for s in pots.values())
        targets = lay["D"] if busy else lay["O"]
    char = {v: k for k, v in DIRS.items()}
    walkable = lay[" "]

    def route(avoid_partner: bool) -> str | None:
        seen = {pos}
        q = deque([(pos, None)])
        while q:
            c, first = q.popleft()
            for t in targets:
                d = (t[0] - c[0], t[1] - c[1])
                if d in char:
                    if c == pos:
                        if facing == d:
                            return "S" if wait else "I"
                        return char[
                            d
                        ]  # target is not walkable: this only turns to face it
                    return first
            for d, a in char.items():
                n = (c[0] + d[0], c[1] + d[1])
                if (
                    n in walkable
                    and n not in seen
                    and not (avoid_partner and n == blocked_by_partner)
                ):
                    seen.add(n)
                    q.append((n, first or a))
        return None

    return route(True) or route(False) or "S"


SCRIPTED = {
    "freeway": freeway_scripted,
    "snake": snake_scripted,
    "overcooked": overcooked_scripted,
}


def make_policy(name: str, game: str, level: str, seed: int, rep: int):
    if name == "default":
        default = _prompts(game).DEFAULT_ACTION
        return lambda state: default
    if name == "random":
        rng = random.Random(f"rtrg|{game}|{level}|{seed}|{rep}")
        return lambda state: rng.choice(legal_actions(state))
    if name == "scripted":
        return SCRIPTED[game]
    raise ValueError(name)


# --------------------------------------------------------------------------- episodes


def run_episode(
    game: str,
    level: str,
    policy: str,
    seed: int,
    rep: int,
    layout: str | None,
    allow_published: bool,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "env": "rtrg",
        "game": game,
        "difficulty": level,
        "env_id": ENV_ID[game][level],
        "horizon": HORIZON,
        "time_pressure": "n/a (zero-latency policy: acts every step within any budget)",
        "policy": policy,
        "seed": seed,
        "rep": rep,
        "R": None,
        "R_min": R_RANGE[game][0],
        "R_max": R_RANGE[game][1],
        "score": None,
        "steps": 0,
        "wall_s": None,
        "mean_step_s": None,
        "errors": None,
    }
    t0 = time.perf_counter()
    step_time = 0.0
    try:
        env, meta = make_env(game, level, seed, layout, allow_published)
        row.update(meta)
        act = make_policy(policy, game, level, seed, rep)
        obs, done = env.reset()
        hits = 0
        actions = []
        while not done:
            a = act(serialize_state(game, obs))
            actions.append(a)
            ts = time.perf_counter()
            obs, done, _, reset = env.step(a)
            step_time += time.perf_counter() - ts
            row["steps"] += 1
            hits += bool(reset)
        R = float(env.reward)
        lo, hi = R_RANGE[game]
        row["R"] = R
        row["score"] = (R - lo) / (hi - lo)
        row["score_clipped"] = min(
            1.0, max(0.0, row["score"])
        )  # paper: "always between 0 and 1"; R can exceed Table 4 Rmax
        row["final_turn"] = int(env.game_turn)
        row["actions"] = "".join(actions)
        if game == "freeway":
            row["crossed"] = R > 0
            row["collisions"] = hits
        if game == "snake":
            row["died"] = env.game_turn < HORIZON
    except Exception as e:  # recorded, never dropped
        row["errors"] = f"{type(e).__name__}: {e}"
        row["traceback"] = traceback.format_exc(limit=6)
    row["wall_s"] = time.perf_counter() - t0
    row["mean_step_s"] = step_time / row["steps"] if row["steps"] else None
    return row


def parse_seeds(spec: str) -> list[int]:
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part[1:]:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def dump_state(path: str) -> None:
    """One real mid-episode state per game from a dev seed (default policy, decision turn 2, level M)."""
    samples = {}
    for game, seed in (("freeway", None), ("snake", 9000), ("overcooked", 9000)):
        if game == "freeway":
            seed = next(
                s
                for s in range(DEV_MIN, DEV_MIN + 2000)
                if FREEWAY_S_RANGE["M"][0]
                <= (freeway_min_steps(s) or 0)
                <= FREEWAY_S_RANGE["M"][1]
            )
        env, _ = make_env(game, "M", seed, None, allow_published=False)
        obs, done = env.reset()
        default = _prompts(game).DEFAULT_ACTION
        for _ in range(2):
            obs, done, _, _ = env.step(default)
        samples[game] = serialize_state(game, obs)
        print(f"{game}: dev seed {seed}, turn {obs['game_turn']}", file=sys.stderr)
    with open(path, "w") as f:
        json.dump(samples, f, indent=1)
        f.write("\n")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--game", nargs="+", choices=GAMES, default=list(GAMES))
    ap.add_argument(
        "--difficulty",
        nargs="+",
        choices=LEVELS,
        default=list(LEVELS),
        help="E/M/H = gym -v0/-v1/-v2",
    )
    ap.add_argument(
        "--policy",
        nargs="+",
        choices=("default", "random", "scripted"),
        default=["default", "random", "scripted"],
    )
    ap.add_argument(
        "--seeds",
        default="0-7",
        help="range a-b or comma list (published: 0-7; dev: >= 9000)",
    )
    ap.add_argument(
        "--reps",
        type=int,
        default=1,
        help="policy RNG repeats per game seed (random policy only)",
    )
    ap.add_argument(
        "--layout",
        default=None,
        help="overcooked layout override (dev only, not the published setting)",
    )
    ap.add_argument(
        "--allow-published",
        action="store_true",
        help="permit published instances (wave 2)",
    )
    ap.add_argument("--out", help="output JSONL path (appended)")
    ap.add_argument(
        "--workdir",
        default="/tmp/jev-game-floors/dev/rtrg-cwd",
        help="cwd for the gym (overcooked writes ./vislogs)",
    )
    ap.add_argument(
        "--dump-state",
        metavar="PATH",
        help="write one dev-seed state per game and exit",
    )
    ap.add_argument(
        "--min-steps",
        action="store_true",
        help="print freeway min steps S for --seeds (real seeds or published indices) and exit",
    )
    args = ap.parse_args()
    out = os.path.abspath(args.out) if args.out else None
    dump = os.path.abspath(args.dump_state) if args.dump_state else None
    os.makedirs(args.workdir, exist_ok=True)
    os.chdir(args.workdir)
    if dump:
        dump_state(dump)
        return
    seeds = parse_seeds(args.seeds)
    if args.min_steps:
        from realtimegym.environments import freeway as fw

        for lvl in args.difficulty:
            for s in seeds:
                real = fw.seed_mapping[lvl].get(s, s) if s < DEV_MIN else s
                if real != s and not args.allow_published:
                    raise SystemExit(
                        f"seed {s} is a published index; pass --allow-published"
                    )
                print(
                    json.dumps(
                        {
                            "difficulty": lvl,
                            "seed": s,
                            "real_seed": real,
                            "min_steps": freeway_min_steps(real),
                        }
                    )
                )
        return
    if not out:
        raise SystemExit("--out is required")
    with open(out, "a") as f:
        for game in args.game:
            for lvl in args.difficulty:
                for pol in args.policy:
                    for s in seeds:
                        for rep in range(args.reps if pol == "random" else 1):
                            row = run_episode(
                                game,
                                lvl,
                                pol,
                                s,
                                rep,
                                args.layout,
                                args.allow_published,
                            )
                            f.write(json.dumps(row) + "\n")
                            f.flush()
                            print(
                                f"{game} {lvl} {pol:8s} seed={s} rep={rep} R={row['R']} S={row['score']} steps={row['steps']} err={row['errors']}",
                                file=sys.stderr,
                            )


if __name__ == "__main__":
    main()
