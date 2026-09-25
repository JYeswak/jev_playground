#!/usr/bin/env python3
"""PokéJev Stage B: local Gen 9 OU battles under an enforced clock (bead jev-jy7t.1.3).

Bar and protocol: docs/demos/upstream-repro/pokejev-stage-b-20260925.md, committed before the first battle.
Needs the local server: work/poke-jev/serve.sh (the pinned fork plus the "Gen 9 OU Clock" format).

  selftest            keyless: a fake Jev plays and falls back correctly, a hostile Jev is refused and
                      the battle still finishes, a deadline overrun falls back inside the clock, and
                      a deliberately slow player loses on time (the clock's RED arm)
  battles OPP N       live: N battles vs OPP (abyssal | onestep | maxpower | random), W workers,
                      appends stage-b/results-OPP.jsonl and decisions-OPP.jsonl, resumable
  battles OPP N --control
                      keyless zero-call control: the same player with Jev disabled, so every decision
                      plays PokéChamp's damage-calculator fallback; results-OPP-control.jsonl
  score               keyless: win rates, Wilson intervals, time losses, calls and spend per arm,
                      and the live-minus-control difference vs abyssal

Run (repo root): work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py selftest
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \\
    work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py battles abyssal 200
Never prints a key.
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import random
import re
import sys
import time
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pc  # noqa: E402  (chdirs into the PokéChamp clone)
import player as pj  # noqa: E402
from poke_env.player.baselines import AbyssalPlayer, MaxBasePowerPlayer, OneStepPlayer  # noqa: E402
from poke_env.player.player import Player  # noqa: E402
from poke_env.player.random_player import RandomPlayer  # noqa: E402
from poke_env.player.team_util import load_random_team  # noqa: E402
from poke_env.ps_client.account_configuration import AccountConfiguration  # noqa: E402
from poke_env.teambuilder.constant_teambuilder import ConstantTeambuilder  # noqa: E402

FORMAT = "gen9ouclock"
OUT = os.path.join(HERE, "stage-b")
TEAMS = list(
    range(1, 14)
)  # PokéChamp's pinned Gen 9 OU team files, poke_env/data/static/teams/gen9ou/
PAIR_SEED = 20260925
WORKERS = 8
OPPONENTS = {
    "abyssal": lambda **kw: AbyssalPlayer(**kw),
    "onestep": lambda **kw: OneStepPlayer(**kw),
    "maxpower": lambda **kw: MaxBasePowerPlayer(**kw),
    "random": lambda **kw: RandomPlayer(**kw),
}


def team_pairs():
    """Ordered team pairs, each used twice with sides swapped so neither player keeps the better team."""
    pairs = [(a, b) for a in TEAMS for b in TEAMS if a != b]
    random.Random(PAIR_SEED).shuffle(pairs)
    return pairs


def teams_for(k: int) -> tuple[int, int]:
    a, b = team_pairs()[(k // 2) % len(team_pairs())]
    return (a, b) if k % 2 == 0 else (b, a)


def time_loss(replay_path: str) -> str | None:
    """The username the server forfeited for inactivity, from the saved replay, or None."""
    if not os.path.exists(replay_path):
        return None
    with open(replay_path, encoding="utf-8", errors="replace") as fh:
        m = re.search(r"\|-message\|(.+?) lost due to inactivity\.", fh.read())
    return m.group(1) if m else None


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


NICKNAMED = re.compile(
    r"^(?P<nick>[^()\n]+?) \((?P<species>(?![MF]\))[^()\n]+)\)(?P<rest>.*)$", re.M
)


def team_text(tid: int) -> str:
    """PokéChamp's pinned team file with cosmetic nicknames removed.

    gen9ou12.txt nicknames all six Pokémon ("Lynrd Spynrd (Great Tusk) @ Rocky Helmet"). PokéChamp's
    poke-env fork then fails to match the nicknamed switch-in to its team-preview entry, raises
    "team already has 6 pokemons", and the player holding that team never moves and loses on time:
    34 of 34 team-12 battles in the first control run, and both such battles in the first feasibility
    run. A nickname has no game effect, so "Species (G) @ Item" is the same team.
    Gender tags such as "Latios (M) @ Soul Dew" are left as they are.
    """
    return NICKNAMED.sub(
        lambda m: m.group("species") + m.group("rest"), load_random_team(tid)
    )


def _team(tid: int) -> ConstantTeambuilder:
    return ConstantTeambuilder(team_text(tid))


async def play(me: Player, opp: Player, k: int, replays: str) -> dict:
    ours, theirs = teams_for(k)
    me._team = _team(ours)
    opp._team = _team(theirs)
    before = set(me.battles)
    t0 = time.time()
    await me.battle_against(opp, n_battles=1)
    tag = next(t for t in me.battles if t not in before)
    b = me.battles[tag]
    path = os.path.join(replays, f"{me.username} - {tag}.html")
    loser_on_time = time_loss(path)
    return {
        "k": k,
        "battle": tag,
        "our_team": ours,
        "opp_team": theirs,
        "won": bool(b.won),
        "finished": bool(b.finished),
        "turns": b.turn,
        "time_loss": None
        if loser_on_time is None
        else ("pokejev" if loser_on_time == me.username else "opponent"),
        "wall_s": round(time.time() - t0, 1),
        "replay": os.path.relpath(path, HERE),
    }


def make_players(
    opp_name: str,
    w: int,
    replays: str,
    decisions: str,
    client_factory=None,
    cls=pj.PokeJevPlayer,
):
    me = cls(
        battle_format=FORMAT,
        account_configuration=AccountConfiguration(f"pokejev{opp_name[:3]}{w}", None),
        save_replays=replays,
        decision_log=decisions,
        client_factory=client_factory,
    )
    opp = OPPONENTS[opp_name](
        battle_format=FORMAT,
        account_configuration=AccountConfiguration(f"{opp_name[:7]}bot{w}", None),
    )
    return me, opp


def arm_paths(opp_name: str, tag: str) -> tuple[str, str, str]:
    os.makedirs(OUT, exist_ok=True)
    replays = os.path.join(OUT, f"replays-{opp_name}{tag}")
    os.makedirs(replays, exist_ok=True)
    return (
        replays,
        os.path.join(OUT, f"results-{opp_name}{tag}.jsonl"),
        os.path.join(OUT, f"decisions-{opp_name}{tag}.jsonl"),
    )


async def run_shard(
    opp_name: str, n: int, workers: int, w: int, client_factory=None, tag: str = ""
) -> int:
    """Battles k < n with k % workers == w, in order, skipping k that already have a result.

    One shard per process: PokéChamp's simulator is CPU-bound Python, and battles sharing one
    interpreter would share one GIL and slow each other's decisions against the clock.
    A harness error is recorded and the k is played again on the next run; it is never a result.
    """
    replays, results, decisions = arm_paths(opp_name, tag)
    done = {r["k"] for r in load_jsonl(results) if "won" in r}
    mine = [k for k in range(n) if k % workers == w and k not in done]
    me, opp = make_players(
        opp_name, w + (50 if tag else 0), replays, decisions, client_factory
    )
    for k in mine:
        try:
            row = await play(me, opp, k, replays)
        except Exception as exc:  # noqa: BLE001 - recorded; a harness failure is not a result
            row = {"k": k, "error": f"{type(exc).__name__}: {str(exc)[:300]}"}
        with open(results, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    return 0


def spawn(opp_name: str, n: int, workers: int, control: bool) -> int:
    """One process per shard; returns the worst child exit code."""
    import subprocess

    args = [
        sys.executable,
        os.path.abspath(__file__),
        "_shard",
        opp_name,
        str(n),
        str(workers),
    ]
    procs = [
        subprocess.Popen(
            args + [str(w)] + (["--control"] if control else []),
            stdout=subprocess.DEVNULL,
        )
        for w in range(workers)
    ]
    codes = [p.wait() for p in procs]
    _, results, _ = arm_paths(opp_name, "-control" if control else "")
    rows = load_jsonl(results)
    ok = {r["k"] for r in rows if "won" in r and r["k"] < n}
    print(
        f"{opp_name}{'-control' if control else ''}: {len(ok)}/{n} battles with a result, "
        f"{sum(1 for r in rows if 'error' in r)} harness-error rows, child codes {codes}",
        file=sys.stderr,
    )
    return max(codes)


# ---------------------------------------------------------------------------------- selftest


class FakeJev:
    """Stands in for AsyncTypeSafeClient. mode: uniform | hostile | slow."""

    def __init__(self, mode: str):
        self.mode = mode
        self.calls = 0

    async def system_one(self, state, questions, model=None):
        self.calls += 1
        if self.mode == "slow":
            await asyncio.sleep(pj.DEADLINE_S + 1.0)
        answers = {}
        for name, q in questions.items():
            labels = list(q.criteria)
            if self.mode == "hostile":
                probs = {labels[0]: 1.0, "not an option": 0.0}
            else:
                probs = {lab: 1.0 / len(labels) for lab in labels}
            answers[name] = SimpleNamespace(
                probabilities=probs, choice=labels[0], confidence=0.5
            )
        return SimpleNamespace(
            answers=answers, usage=SimpleNamespace(input_tokens=0), model="fake"
        )


class SlowPlayer(RandomPlayer):
    """Planted clock violation: sleeps past the 15 s per-turn limit before every move."""

    def __init__(self, *a, decision_log=None, client_factory=None, **kw):
        super().__init__(*a, **kw)

    async def choose_move(self, battle):
        await asyncio.sleep(20)
        return self.choose_random_move(battle)


class DisabledJev:
    """The zero-call control: every decision falls back to PokéChamp's damage-calculator policy."""

    async def system_one(self, state, questions, model=None):
        raise RuntimeError("control arm: Jev disabled, no call made")


async def selftest() -> int:
    base = os.path.join("/tmp", f"pokejev-selftest-{os.getpid()}")
    os.makedirs(base, exist_ok=True)
    fails = []

    arms_seen: list[str] = []

    async def arm(name, mode, cls=pj.PokeJevPlayer):
        replays = os.path.join(base, name)
        os.makedirs(replays, exist_ok=True)
        dec = os.path.join(base, f"{name}.jsonl")
        fake = FakeJev(mode)
        arms_seen.append(name)
        worker = (
            80 + len(arms_seen) + (os.getpid() % 10) * 10
        )  # unique names per arm and per run
        me, opp = make_players("random", worker, replays, dec, (lambda: fake), cls=cls)
        row = await play(me, opp, 0, replays)
        return row, load_jsonl(dec), fake

    row, dec, fake = await arm("uniform", "uniform")
    fb = sum(1 for d in dec if d["fallback"])
    ok = (
        row["finished"]
        and row["time_loss"] is None
        and dec
        and fb == 0
        and fake.calls > 0
    )
    print(
        f"{'ok  ' if ok else 'FAIL'} uniform fake Jev: finished={row['finished']} won={row['won']} "
        f"decisions={len(dec)} fallbacks={fb} calls={fake.calls} time_loss={row['time_loss']}"
    )
    fails += [] if ok else ["uniform"]

    row, dec, fake = await arm("hostile", "hostile")
    unforced = [d for d in dec if not d["forced"] and d.get("n_options", 0) > 1]
    refused = sum(
        1 for d in unforced if d["fallback"] and "labels differ" in d["fallback"]
    )
    ok = row["finished"] and unforced and refused == len(unforced)
    print(
        f"{'ok  ' if ok else 'FAIL'} hostile fake Jev refused: {refused}/{len(unforced)} unforced decisions fell back, "
        f"finished={row['finished']}"
    )
    fails += [] if ok else ["hostile"]

    row, dec, fake = await arm("slow", "slow")
    unforced = [d for d in dec if not d["forced"] and d.get("n_options", 0) > 1]
    timed = sum(
        1
        for d in unforced
        if d["fallback"] and d["fallback"].startswith("TimeoutError")
    )
    worst = max((d["ms"] for d in dec), default=0)
    ok = (
        row["finished"]
        and row["time_loss"] is None
        and unforced
        and timed == len(unforced)
        and worst < 15000
    )
    print(
        f"{'ok  ' if ok else 'FAIL'} deadline guard: {timed}/{len(unforced)} slow decisions fell back at the "
        f"{pj.DEADLINE_S:.0f} s deadline, worst decision {worst} ms, time_loss={row['time_loss']}"
    )
    fails += [] if ok else ["deadline"]

    row, _, _ = await arm("clockred", "uniform", cls=SlowPlayer)
    ok = row["finished"] and row["time_loss"] == "pokejev" and not row["won"]
    print(
        f"{'ok  ' if ok else 'FAIL'} clock RED arm: a 20 s-per-move player lost on time={row['time_loss']} "
        f"won={row['won']} after {row['wall_s']} s"
    )
    fails += [] if ok else ["clock-red"]

    print("SELFTEST PASS 4/4" if not fails else f"SELFTEST FAIL {fails}")
    return 1 if fails else 0


# ------------------------------------------------------------------------------------- score


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 4), round(c + h, 4))


def score() -> int:
    out = {}
    for opp in OPPONENTS:
        for tag in ("", "-control"):
            arm = f"{opp}{tag}"
            results = load_jsonl(os.path.join(OUT, f"results-{arm}.jsonl"))
            rows = list(
                {r["k"]: r for r in results if "won" in r}.values()
            )  # a replayed k counts once
            errs = [r for r in results if "error" in r]
            dec = load_jsonl(os.path.join(OUT, f"decisions-{arm}.jsonl"))
            if not rows and not errs:
                continue
            wins = sum(r["won"] for r in rows)
            ms = sorted(d["ms"] for d in dec)
            calls = sum(len(d["jev_ms"]) for d in dec)
            toks = sum(d["input_tokens"] for d in dec)
            out[arm] = {
                "battles": len(rows),
                "harness_errors": len(errs),
                "wins": wins,
                "win_rate": round(wins / len(rows), 4) if rows else None,
                "wilson95": wilson(wins, len(rows)),
                "losses_on_time": sum(1 for r in rows if r["time_loss"] == "pokejev"),
                "opponent_losses_on_time": sum(
                    1 for r in rows if r["time_loss"] == "opponent"
                ),
                "unfinished": sum(1 for r in rows if not r["finished"]),
                "decisions": len(dec),
                "fallbacks": sum(1 for d in dec if d["fallback"]),
                "fallback_reasons": sorted(
                    {(d["fallback"] or "")[:40] for d in dec if d["fallback"]}
                )[:8],
                "decision_ms_p50": ms[len(ms) // 2] if ms else None,
                "decision_ms_p95": ms[int(len(ms) * 0.95)] if ms else None,
                "decision_ms_max": ms[-1] if ms else None,
                "jev_calls": calls,
                "input_tokens": toks,
                "spend_usd_at_0.042_per_M_input": round(toks * 0.042 / 1e6, 4),
                "models": sorted({m for d in dec for m in d.get("models", [])}),
            }
    a = out.get("abyssal")
    if a and a["battles"]:
        rate, n, tl = a["win_rate"], a["battles"], a["losses_on_time"]
        verdict = (
            "PASS"
            if (rate >= 0.84 and tl == 0)
            else ("KILL" if (rate < 0.70 or tl > 0.01 * n) else "FAIL")
        )
        out["bar"] = {
            "tier1_vs_abyssal": verdict,
            "win_rate": rate,
            "battles": n,
            "losses_on_time": tl,
        }
    c = out.get("abyssal-control")
    if a and c and a["battles"] and c["battles"]:
        # two-proportion z-test, pooled; reported, not barred
        n1, n2 = a["battles"], c["battles"]
        p1, p2 = a["wins"] / n1, c["wins"] / n2
        pp = (a["wins"] + c["wins"]) / (n1 + n2)
        se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2)) if 0 < pp < 1 else 0.0
        z = (p1 - p2) / se if se else 0.0
        out["live_minus_control_vs_abyssal"] = {
            "difference": round(p1 - p2, 4),
            "z": round(z, 3),
            "p_two_sided": round(math.erfc(abs(z) / math.sqrt(2)), 4),
        }
    with open(os.path.join(OUT, "receipt.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "selftest":
        return asyncio.run(selftest())
    if argv[0] in ("battles", "_shard") and len(argv) >= 3 and argv[1] in OPPONENTS:
        control = "--control" in argv
        if not control and not os.environ.get("TYPESAFE_API_KEY"):
            print(
                "unconfigured: TYPESAFE_API_KEY unset, no battle played (NOT_RUN)",
                file=sys.stderr,
            )
            return 2
        if argv[0] == "_shard":
            workers, w = int(argv[3]), int(argv[4])
            factory, tag = (DisabledJev, "-control") if control else (None, "")
            return asyncio.run(
                run_shard(
                    argv[1], int(argv[2]), workers, w, client_factory=factory, tag=tag
                )
            )
        workers = (
            int(argv[argv.index("--workers") + 1]) if "--workers" in argv else WORKERS
        )
        return spawn(argv[1], int(argv[2]), workers, control)
    if argv[0] == "score":
        return score()
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
