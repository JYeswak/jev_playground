#!/usr/bin/env python3
"""No-model floors for ViZDoom defend_the_center in the See-Symbolize-Act setting.

Setting source: arXiv 2603.11601v2 (sections 3.3, 4.3, Table 4, appendix A.4) and its code at
github.com/Lossfunk/See-Symbolize-Act @ 051fca1 (vizdoom_symbolic_runner.py,
vizdoom_ground_truth.py). One run = one seed = `--decisions` agent decisions. Each decision
repeats its action for `--frame-skip`+1 game tics. When the player dies inside a run, the game is
reset with the same seed and the decision count continues, and the reward keeps accumulating.
All of this mirrors the published runner (vizdoom_symbolic_runner.py:1034-1065). The run's
headline metric is `cumulative_reward`: +1 per kill, -1 per death, summed over the run. That is
the runner's `total_reward`. `kills` and `deaths` are recorded as well, because Table 4 is
labelled "kills". `checkpoints` holds the same totals after fewer decisions. The run is
deterministic given the seed, so each checkpoint equals a shorter run from the same seed.

Stdlib plus the `vizdoom` package only. No model is called.
"""

import argparse
import json
import math
import os
import platform
import random
import sys
import time
import traceback

import vizdoom as vzd

SCENARIO = "defend_the_center"
SSA_COMMIT = "051fca10b3d84619ae33a0abaccbb264b27dfea0"

# Action sets. "code": what the published runner sends. vizdoom_ground_truth.py:502-506 gives
# the mapping and the bundled defend_the_center.cfg gives the buttons, one-hot per
# vizdoom_ground_truth.py:279-281. "paper": the controls listed in the paper's appendix A.4
# prompt. NOOP is no buttons pressed. The two lists disagree. See the report.
ACTION_SETS = {
    "code": ("TURN_LEFT", "TURN_RIGHT", "ATTACK"),
    "paper": ("NOOP", "ATTACK", "TURN_LEFT", "TURN_RIGHT"),
}
BUTTON_ORDER = (
    "TURN_LEFT",
    "TURN_RIGHT",
    "ATTACK",
)  # defend_the_center.cfg available_buttons

RESOLUTIONS = {
    "320x240": vzd.ScreenResolution.RES_320X240,
    "640x480": vzd.ScreenResolution.RES_640X480,
    "1280x720": vzd.ScreenResolution.RES_1280X720,
}

# The label-name -> category table copied from vizdoom_ground_truth.py:135-196. The S-GT prompt
# prints this category, and a name missing from the table becomes 'unknown'. Every name that
# occurs in defend_the_center (MarineChainsawVzd, DoomPlayer, BulletPuff) is missing.
SSA_CATEGORIES = {
    "Zombieman": "enemy",
    "ShotgunGuy": "enemy",
    "ChaingunGuy": "enemy",
    "DoomImp": "enemy",
    "Demon": "enemy",
    "Spectre": "enemy",
    "Cacodemon": "enemy",
    "BaronOfHell": "enemy",
    "HellKnight": "enemy",
    "LostSoul": "enemy",
    "PainElemental": "enemy",
    "Revenant": "enemy",
    "Arachnotron": "enemy",
    "Mancubus": "enemy",
    "Archvile": "enemy",
    "Cyberdemon": "enemy",
    "SpiderMastermind": "enemy",
    "HealthBonus": "health",
    "Stimpack": "health",
    "Medikit": "health",
    "Soulsphere": "health",
    "ArmorBonus": "armor",
    "GreenArmor": "armor",
    "BlueArmor": "armor",
    "Clip": "ammo",
    "Shell": "ammo",
    "RocketAmmo": "ammo",
    "Cell": "ammo",
    "ClipBox": "ammo",
    "ShellBox": "ammo",
    "RocketBox": "ammo",
    "CellPack": "ammo",
    "Pistol": "weapon",
    "Shotgun": "weapon",
    "SuperShotgun": "weapon",
    "Chaingun": "weapon",
    "RocketLauncher": "weapon",
    "PlasmaRifle": "weapon",
    "BFG9000": "weapon",
    "GreenCard": "key",
    "BlueCard": "key",
    "RedCard": "key",
    "GreenSkull": "key",
    "BlueSkull": "key",
    "RedSkull": "key",
    "ExplosiveBarrel": "hazard",
}

# vizdoom < 1.3 has no Label.object_category. There the self-label and effect sprites are
# excluded by name instead.
NON_MONSTER_NAMES = frozenset({"DoomPlayer", "BulletPuff", "Blood"})

GV = vzd.GameVariable


def parse_seeds(spec):
    seeds = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part[1:]:
            a, b = part.split("-", 1)
            a, b = int(a), int(b)
            if b < a:
                raise ValueError(f"empty seed range {part!r}")
            seeds.extend(range(a, b + 1))
        else:
            seeds.append(int(part))
    if not seeds:
        raise ValueError("no seeds given")
    return seeds


def make_game(resolution):
    """The same configuration as VizDoomGroundTruth.__init__ (vizdoom_ground_truth.py:211-240)."""
    game = vzd.DoomGame()
    game.load_config(os.path.join(vzd.scenarios_path, f"{SCENARIO}.cfg"))
    game.set_screen_resolution(RESOLUTIONS[resolution])
    game.set_screen_format(vzd.ScreenFormat.RGB24)
    game.set_labels_buffer_enabled(True)
    game.set_depth_buffer_enabled(True)
    game.set_automap_buffer_enabled(False)
    game.set_window_visible(False)
    game.init()
    return game


def _position_hint(screen_x, width):
    # Copied from vizdoom_symbolic_runner.py:826-831.
    if screen_x < width * 0.4:
        return "LEFT of center → need TURN_LEFT to aim"
    if screen_x > width * 0.6:
        return "RIGHT of center → need TURN_RIGHT to aim"
    return "CENTER → can ATTACK now!"


def serialize_state(game, state, width, action_set="code"):
    """The symbols-only (S-GT) state the published pipeline gave the model for one decision.

    This mirrors VizDoomSymbolicRunner.get_action_prompt_symbol_only
    (vizdoom_symbolic_runner.py:813-881), fed by VizDoomGroundTruth._extract_objects and
    _get_player_state (vizdoom_ground_truth.py:336-434). The pipeline prints these fields:
    - for every object in the labels buffer, in engine order: its category, its label name,
      screen_x, a LEFT/CENTER/RIGHT hint, and a distance rounded to 1 decimal;
    - the player's health and armor;
    - the action list and the screen-width / crosshair / threshold numbers.
    It prints no frame, no ammo, no y, no box size and no action history. Two quirks are kept on
    purpose, because the published models received them:
    - screen_x is Label.x, the LEFT edge of the box, not its centre. The code comments call it the
      centre.
    - the player's own weapon sprite appears as label 'DoomPlayer' with distance 0.0.
    The scenario-context text of the prompt is instruction text, not state, so it is left out.
    """
    px = game.get_game_variable(GV.POSITION_X)
    py = game.get_game_variable(GV.POSITION_Y)
    objects = []
    for label in state.labels:
        ox, oy = label.object_position_x, label.object_position_y
        # vizdoom_ground_truth.py:363: the distance is 0 whenever the world x is exactly 0.
        distance = math.hypot(ox - px, oy - py) if ox != 0 else 0.0
        screen_x = int(label.x)
        objects.append(
            {
                "category": SSA_CATEGORIES.get(label.object_name, "unknown"),
                "label": label.object_name,
                "screen_x": screen_x,
                "position_hint": _position_hint(screen_x, width),
                "distance": round(distance, 1),
            }
        )
    return {
        "scenario": SCENARIO,
        "actions": {str(i): name for i, name in enumerate(ACTION_SETS[action_set])},
        "screen": {
            "width": width,
            "crosshair_x": width // 2,
            "left_if_screen_x_below": int(width * 0.4),
            "right_if_screen_x_above": int(width * 0.6),
        },
        "objects": objects,
        "player": {
            "health": int(game.get_game_variable(GV.HEALTH)),
            "armor": int(game.get_game_variable(GV.ARMOR)),
        },
    }


def _is_monster(label):
    category = getattr(label, "object_category", None)
    if category is not None:
        return category == "Monster"
    return label.object_name not in NON_MONSTER_NAMES


class RandomPolicy:
    """Uniform over the action set, from a random.Random seeded with the run seed."""

    def __init__(self, seed, action_names, width):
        self.rng = random.Random(seed)
        self.n = len(action_names)

    def act(self, game, state):
        return self.rng.randrange(self.n)


class ScriptedPolicy:
    """A hand-written aim-and-shoot rule over the labels buffer. It uses no randomness.

    At each decision:
    1. Candidates are the labels whose engine category is 'Monster'. The player's own
       'DoomPlayer' label and 'BulletPuff' effects are excluded.
    2. If any candidate's box [x, x+width] contains the centre column (width//2), the policy
       plays ATTACK.
    3. Otherwise it takes the nearest candidate by world distance, the same distance the S-GT
       state carries, with ties broken by the smaller offset from centre. It plays TURN_LEFT if
       that box's centre is left of the centre column and TURN_RIGHT if it is right.
    4. If no monster is visible, it keeps turning in its last turn direction, which starts as
       TURN_RIGHT.
    It reads Label.width, which the S-GT prompt does not contain.
    """

    def __init__(self, seed, action_names, width):
        self.idx = {name: i for i, name in enumerate(action_names)}
        self.cx = width // 2
        self.sweep = "TURN_RIGHT"

    def act(self, game, state):
        monsters = [l for l in state.labels if _is_monster(l)]
        if any(l.x <= self.cx <= l.x + l.width for l in monsters):
            return self.idx["ATTACK"]
        if monsters:
            px = game.get_game_variable(GV.POSITION_X)
            py = game.get_game_variable(GV.POSITION_Y)

            def key(l):
                centre = l.x + l.width / 2.0
                return (
                    math.hypot(l.object_position_x - px, l.object_position_y - py),
                    abs(centre - self.cx),
                )

            target = min(monsters, key=key)
            self.sweep = (
                "TURN_LEFT" if target.x + target.width / 2.0 < self.cx else "TURN_RIGHT"
            )
        return self.idx[self.sweep]


POLICIES = {"random": RandomPolicy, "scripted": ScriptedPolicy}


def action_vector(name):
    return [1 if b == name else 0 for b in BUTTON_ORDER]


def run_one(seed, args, dump=None):
    """Play one run and return its JSON row. `dump` optionally captures a serialized state."""
    names = ACTION_SETS[args.action_set]
    vectors = [action_vector(n) for n in names]
    width = int(args.resolution.split("x")[0])
    row = {
        "env": f"vizdoom/{SCENARIO}",
        "decisions": args.decisions,
        "frame_skip": args.frame_skip,
        "tics_per_decision": args.frame_skip + 1,
        "resolution": args.resolution,
        "action_set": args.action_set,
        "reset_on_death": "same_seed",
        "vizdoom_version": getattr(vzd, "__version__", "unknown"),
        "policy": args.policy,
        "seed": seed,
        "cumulative_reward": None,
        "kills": None,
        "deaths": None,
        "episodes_started": 0,
        "episode_end_reasons": [],
        "steps": 0,
        "tics": 0,
        "action_counts": {n: 0 for n in names},
        "wall_seconds": None,
        "init_seconds": None,
        "mean_step_seconds": None,
        "mean_tic_seconds": None,
        "checkpoints": {},
        "error": None,
    }
    game = None
    step_time = 0.0
    total_reward = 0.0
    kills = 0
    deaths = 0
    t_start = time.perf_counter()
    try:
        t0 = time.perf_counter()
        game = make_game(args.resolution)
        row["init_seconds"] = round(time.perf_counter() - t0, 4)
        t_start = time.perf_counter()
        policy = POLICIES[args.policy](seed, names, width)
        game.set_seed(seed)
        game.new_episode()
        row["episodes_started"] = 1
        life_kills = 0
        for d in range(args.decisions):
            state = game.get_state()
            if dump is not None and d == dump["at"]:
                dump["state"] = serialize_state(game, state, width, args.action_set)
                dump["decision"] = d
                break  # dump-only run: the rest of the run is not needed
            a = policy.act(game, state)
            row["action_counts"][names[a]] += 1
            vec = vectors[a]
            finished = False
            t0 = time.perf_counter()
            for _ in range(args.frame_skip + 1):
                r = game.make_action(vec)
                row["tics"] += 1
                total_reward += r
                finished = game.is_episode_finished()
                if finished:
                    break
            step_time += time.perf_counter() - t0
            row["steps"] += 1
            life_kills = int(game.get_game_variable(GV.KILLCOUNT))
            if finished:
                dead = game.is_player_dead()
                deaths += int(dead)
                kills += life_kills
                row["episode_end_reasons"].append(
                    "death" if dead else "timeout_or_other"
                )
                # vizdoom_symbolic_runner.py:1056-1059: reset with the same seed and keep counting.
                game.set_seed(seed)
                game.new_episode()
                row["episodes_started"] += 1
                life_kills = 0
            if row["steps"] in args.checkpoints:
                # Totals so far. A run cut at this many decisions from the same seed is
                # identical up to here, so this is the shorter-run reading at no extra cost.
                row["checkpoints"][str(row["steps"])] = {
                    "cumulative_reward": total_reward,
                    "kills": kills + life_kills,
                    "deaths": deaths,
                    "tics": row["tics"],
                }
        kills += life_kills
        row["episode_end_reasons"].append("decision_budget")
    except Exception:
        row["error"] = traceback.format_exc(limit=5)
    finally:
        if game is not None:
            try:
                game.close()
            except Exception:
                pass
    row["cumulative_reward"] = total_reward
    row["kills"] = kills
    row["deaths"] = deaths
    row["reward_equals_kills_minus_deaths"] = (
        abs(total_reward - (kills - deaths)) < 1e-9
    )
    # An errored run keeps its partial metrics and is marked incomplete. It is never dropped.
    row["complete"] = row["error"] is None and row["steps"] == args.decisions
    row["wall_seconds"] = round(time.perf_counter() - t_start, 4)
    if row["steps"]:
        row["mean_step_seconds"] = round(step_time / row["steps"], 6)
    if row["tics"]:
        row["mean_tic_seconds"] = round(step_time / row["tics"], 6)
    return row


def summarize(rows, key):
    vals = [r[key] for r in rows if r["complete"] and r[key] is not None]
    n = len(vals)
    incomplete = sum(1 for r in rows if not r["complete"])
    if n == 0:
        return f"n=0 incomplete={incomplete}"
    mean = sum(vals) / n
    if n > 1:
        sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))
        return (
            f"n={n} mean={mean:.3f} se={sd / math.sqrt(n):.3f} min={min(vals)} "
            f"max={max(vals)} incomplete={incomplete}"
        )
    return f"n=1 mean={mean:.3f} incomplete={incomplete}"


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--policy", choices=sorted(POLICIES), required=True)
    p.add_argument(
        "--seeds", required=True, help="inclusive range a-b and/or comma list"
    )
    p.add_argument("--out", help="JSONL output path, one row per run. Overwritten.")
    p.add_argument(
        "--decisions",
        type=int,
        default=600,
        help="agent decisions per run. Paper: '600 frames'. Runner flag --frames "
        "counts decisions (vizdoom_symbolic_runner.py:1246-1247). Default 600.",
    )
    p.add_argument(
        "--frame-skip",
        type=int,
        default=2,
        help="action repeated frame_skip+1 tics per decision "
        "(vizdoom_symbolic_runner.py:1043, default 2 at :1248). Default 2.",
    )
    p.add_argument(
        "--resolution",
        choices=sorted(RESOLUTIONS),
        default="1280x720",
        help="paper section 3.3 and vizdoom_symbolic_runner.py:67. Default 1280x720.",
    )
    p.add_argument(
        "--action-set",
        choices=sorted(ACTION_SETS),
        default="code",
        help="code: TURN_LEFT/TURN_RIGHT/ATTACK (default). paper: appendix A.4 "
        "NOOP/ATTACK/TURN_LEFT/TURN_RIGHT.",
    )
    p.add_argument(
        "--checkpoints",
        default="200,300",
        help="decision counts at which to record the running totals. Default 200,300: "
        "200 decisions x 3 tics = the '600 tics' reading, and 300 = the runner's "
        "own --frames default (vizdoom_symbolic_runner.py:1246).",
    )
    p.add_argument(
        "--dump-state",
        help="write one serialized S-GT state from the first seed "
        "(must be >= 9000) to this path",
    )
    p.add_argument(
        "--dump-at", type=int, default=40, help="decision index to dump (default 40)"
    )
    args = p.parse_args(argv)

    seeds = parse_seeds(args.seeds)
    args.checkpoints = frozenset(
        int(c) for c in args.checkpoints.split(",") if c.strip()
    )
    if args.decisions < 1 or args.frame_skip < 0:
        p.error("--decisions must be >= 1 and --frame-skip >= 0")
    if args.dump_state and seeds[0] < 9000:
        p.error("--dump-state only runs on a development seed (>= 9000)")
    if not args.out and not args.dump_state:
        p.error("give --out and/or --dump-state")

    if args.dump_state:
        dump = {"at": args.dump_at}
        row = run_one(seeds[0], args, dump=dump)
        if "state" not in dump:
            sys.exit(f"no state captured at decision {args.dump_at}: {row['error']}")
        with open(args.dump_state, "w", encoding="utf-8") as f:
            json.dump(dump["state"], f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(
            f"dumped seed={seeds[0]} policy={args.policy} decision={dump['decision']} "
            f"-> {args.dump_state}",
            file=sys.stderr,
        )
        if not args.out:
            return

    rows = []
    with open(args.out, "w", encoding="utf-8") as f:
        for seed in seeds:
            row = run_one(seed, args)
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(
                f"seed={seed} policy={args.policy} reward={row['cumulative_reward']} "
                f"kills={row['kills']} deaths={row['deaths']} steps={row['steps']} "
                f"tics={row['tics']} wall={row['wall_seconds']}s "
                f"s/step={row['mean_step_seconds']} error={'yes' if row['error'] else 'no'}",
                file=sys.stderr,
            )
    print(
        f"[{args.policy} decisions={args.decisions} frame_skip={args.frame_skip} "
        f"action_set={args.action_set} python={platform.python_version()} "
        f"vizdoom={getattr(vzd, '__version__', '?')}]",
        file=sys.stderr,
    )
    for key in ("cumulative_reward", "kills", "deaths", "mean_step_seconds"):
        print(f"  {key}: {summarize(rows, key)}", file=sys.stderr)


if __name__ == "__main__":
    main()
