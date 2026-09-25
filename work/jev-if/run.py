"""Run one game with one arm and append JSON rows (bead jev-jy7t.1.4).

  python run.py --game zork1 --arm uniform --seed 9001 --out rows.jsonl

Arms: uniform | jev (PUCT, same code path, prior swapped); fakejev (jev path with a keyless fake
asker and --fake-latency, dev only); random | look (floors, no search).
Defaults are MC-DML's Table 4 "w.o. Mc, Mi, DP" setting; see puct.GAMES for the per-game values.
One row per real step, one final row per run. Rows are appended, flushed and fsynced; an error
writes an error row and a final row before re-raising.
"""

import argparse
import faulthandler
import json
import os
import random
import signal
import sys
import time
import traceback

import puct


class JerichoEnv:
    """MC-DML src/env.py:5-93, with FrotzEnv.copy() for the per-simulation copy.

    MC-DML calls get_valid_actions() with jericho's default use_parallel=True, which builds a
    multiprocessing pool on each env copy (jericho.py:963-967 at 3.3.1). Here `pool` is one pool per
    run shared by every copy (same worker, same contiguous chunks; identical lists on 75 dev states).
    pool=None uses the serial ctypes filter in this process. It is not equivalent when a candidate
    halts the emulator: jericho then calls self.reset() (jericho.py:983-984), which would put the
    simulation env back at the game start, while the pool path resets only the worker.
    """

    def __init__(self, rom_path, cache, frotz=None, pool=None):
        from jericho import FrotzEnv

        self.rom_path = rom_path
        self.env = (
            frotz if frotz is not None else FrotzEnv(rom_path)
        )  # no seed: walkthrough seed in 3.x
        self.cache = cache
        self.pool = pool

    def valid_actions(self):
        if self.pool is None:
            return self.env.get_valid_actions(use_parallel=False)
        self.env.pool = self.pool
        return self.env.get_valid_actions(use_parallel=True)

    def step(self, action):
        ob, reward, done, info = self.env.step(action)
        info["look"] = "unknown"
        info["inv"] = "unknown"
        info["valid"] = ["wait", "yes", "no"]
        if not done:
            save = self.env.get_state()
            key = self.env.get_world_state_hash()
            if key in self.cache:
                info["look"], info["inv"], info["valid"] = self.cache[key]
            else:
                look, _, _, _ = self.env.step("look")
                info["look"] = look.lower()
                self.env.set_state(save)
                inv, _, _, _ = self.env.step("inventory")
                info["inv"] = inv.lower()
                self.env.set_state(save)
                valid = self.valid_actions()
                info["valid"] = valid if valid else ["wait", "yes", "no"]
                self.cache[key] = info["look"], info["inv"], info["valid"]
        return ob.lower(), reward, done, info

    def reset(self):
        ob, info = self.env.reset()
        save = self.env.get_state()
        info["look"], _, _, _ = self.env.step("look")
        self.env.set_state(save)
        info["inv"], _, _, _ = self.env.step("inventory")
        self.env.set_state(save)
        info["valid"] = self.valid_actions()
        return ob, info

    def copy(self):
        return JerichoEnv(
            self.rom_path, self.cache, frotz=self.env.copy(), pool=self.pool
        )

    def close(self):
        self.env.close()


class Rows:
    def __init__(self, path):
        self.path = path

    def write(self, row):
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--game", required=True, choices=sorted(puct.GAMES))
    p.add_argument(
        "--arm", required=True, choices=["uniform", "jev", "fakejev", "random", "look"]
    )
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--rom-dir", default="/opt/roms")
    p.add_argument(
        "--max-steps", type=int, help="real steps; default per game (35/35/50)"
    )
    p.add_argument("--c-puct", type=float, help="default per game (50/20/200)")
    p.add_argument(
        "--max-depth", type=int, help="fixed search depth; default per game (10)"
    )
    p.add_argument(
        "--dp",
        action="store_true",
        help="full MC-DML dynamic pruning: d 10 -> 30 step 20",
    )
    p.add_argument("--sims-per-act", type=int, default=50)
    p.add_argument("--discount", type=float, default=0.95)
    p.add_argument("--node-key", choices=["code", "fixed"], default="code")
    p.add_argument(
        "--prior-transform", choices=sorted(puct.TRANSFORMS), default="mcdml"
    )
    p.add_argument("--history-actions", type=int, default=3)
    p.add_argument("--max-inflight", type=int, default=1)
    p.add_argument("--prefetch", action="store_true")
    p.add_argument(
        "--max-prior-failures",
        type=int,
        default=-1,
        help="abort the run above this count; -1 = never",
    )
    p.add_argument(
        "--step-timeout",
        type=int,
        default=3600,
        help="seconds per real step before the run stops with an error row; 0 = none",
    )
    p.add_argument("--fake-latency", type=float, default=0.0, help="fakejev only")
    p.add_argument(
        "--dump-state", help="write the Jev request body for one real root node here"
    )
    p.add_argument("--dump-state-step", type=int, default=5)
    p.add_argument(
        "--valid-workers",
        type=int,
        default=2,
        help="processes in one shared jericho valid-action pool per run; 0 = serial filter",
    )
    return p.parse_args(argv)


def make_prior(args):
    if args.arm == "uniform":
        return puct.uniform_prior
    if args.arm == "jev":
        return puct.JevPrior(puct.SdkAsker())
    return puct.JevPrior(puct.FakeAsker(latency=args.fake_latency))


def main(argv=None):
    args = parse_args(argv)
    faulthandler.enable()  # a crash inside the emulator prints a Python stack to stderr
    # docker stop sends SIGTERM; make it an exception so the error and final rows are written.
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(128 + signum))

    def step_timeout(signum, frame):
        raise TimeoutError(
            "real step exceeded --step-timeout (a dead valid-action worker hangs pool.map)"
        )

    signal.signal(signal.SIGALRM, step_timeout)
    game = puct.GAMES[args.game]
    max_steps = args.max_steps if args.max_steps is not None else game["max_steps"]
    c_puct = args.c_puct if args.c_puct is not None else game["c_puct"]
    max_depth = args.max_depth if args.max_depth is not None else game["max_depth"]
    schedule = (10, 30, 20) if args.dp else (max_depth, max_depth, 20)
    config = {
        "game": args.game,
        "arm": args.arm,
        "seed": args.seed,
        "max_steps": max_steps,
        "c_puct": c_puct,
        "depth_schedule": schedule,
        "sims_per_act": args.sims_per_act,
        "discount": args.discount,
        "node_key": args.node_key,
        "prior_transform": args.prior_transform,
        "history_actions": args.history_actions,
        "max_inflight": args.max_inflight,
        "prefetch": args.prefetch,
        "valid_workers": args.valid_workers,
        "model": puct.MODEL if args.arm == "jev" else None,
    }
    if args.arm == "jev" and not os.environ.get("TYPESAFE_API_KEY", "").strip():
        raise puct.MissingKeyError(
            "TYPESAFE_API_KEY is not set; the jev arm refuses to run without it."
        )

    rows = Rows(args.out)
    rng = random.Random(args.seed)
    rom_path = os.path.join(args.rom_dir, game["rom"])
    pool = None
    if args.valid_workers > 0:
        import multiprocessing

        from jericho import FrotzEnv
        from jericho.jericho import init_worker

        seed = FrotzEnv(
            rom_path
        )._seed  # the seed every copy uses (walkthrough seed in 3.x)
        pool = multiprocessing.Pool(
            args.valid_workers, initializer=init_worker, initargs=(rom_path, seed)
        )
    env = JerichoEnv(rom_path, cache={}, pool=pool)
    priors = None
    started = time.monotonic()
    step = 0
    score = 0
    max_score = 0
    done = False
    status = "ok"
    try:
        ob, info = env.reset()
        score = max_score = info["score"]
        rows.write(
            {
                "kind": "start",
                "config": config,
                "game_seed": env.env._seed,
                "score": score,
            }
        )
        search = None
        if args.arm in ("uniform", "jev", "fakejev"):
            priors = puct.PriorService(
                make_prior(args),
                args.prior_transform,
                args.history_actions,
                args.max_inflight,
            )
            search = puct.PUCTSearch(
                env,
                priors,
                c_puct,
                rng,
                args.sims_per_act,
                args.discount,
                schedule,
                args.node_key,
                args.prefetch,
            )
        history = []
        for step in range(1, max_steps + 1):
            t0 = time.monotonic()
            signal.alarm(args.step_timeout)
            before = priors.snapshot() if priors else None
            steps_before = search.env_steps if search else 0
            n_valid = len(info["valid"])
            root_stats = None
            if search is not None:
                root, action = search.search(ob, info, tuple(history))
                root_stats = [
                    [c.action, c.N, round(c.Q, 4), round(p, 4)]
                    for c, p in zip(root.children, root.prior)
                ]
                if args.dump_state and step == args.dump_state_step:
                    body = {
                        "model": puct.MODEL,
                        "state": puct.node_state(root, args.history_actions),
                        "questions": {
                            "action": puct.JevPrior(None).question(root.valid_actions)
                        },
                    }
                    with open(args.dump_state, "w", encoding="utf-8") as fh:
                        json.dump(body, fh, indent=2, ensure_ascii=False)
            elif args.arm == "random":
                action = rng.choice(info["valid"])
            else:
                action = "look"
            ob, reward, done, info = env.step(action)
            score = info["score"]
            max_score = max(max_score, score)
            history.append(action)
            row = {
                "kind": "step",
                "step": step,
                "action": action,
                "reward": reward,
                "score": score,
                "done": done,
                "n_valid": n_valid,
                "wall_s": round(time.monotonic() - t0, 3),
            }
            if search is not None:
                after = priors.snapshot()
                row.update({k: after[k] - before[k] for k in after})
                row["sims"] = args.sims_per_act * n_valid
                row["env_steps"] = search.env_steps - steps_before
                row["root"] = root_stats
            signal.alarm(0)
            rows.write(row)
            if priors is not None and 0 <= args.max_prior_failures < priors.failed:
                status = "aborted_prior_failures"
                break
            if done:
                break
    except BaseException as error:
        status = "error"
        rows.write(
            {
                "kind": "error",
                "step": step,
                "error": "%s: %s" % (type(error).__name__, error),
                "traceback": traceback.format_exc()[-4000:],
            }
        )
        raise
    finally:
        final = {
            "kind": "final",
            "config": config,
            "status": status,
            "steps": step,
            "done": done,
            "final_score": score,
            "max_score": max_score,
            "wall_s": round(time.monotonic() - started, 3),
        }
        if priors is not None:
            final.update(priors.snapshot())
            final["prior_errors"] = priors.errors
            priors.close()
        rows.write(final)
        env.close()
        if pool is not None:
            pool.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
