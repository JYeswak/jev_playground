#!/usr/bin/env python3
"""Run the frozen-alpha battle arm without modifying the committed Stage B tree.

This wrapper imports ``work/poke-jev/stage_b.py`` and its player/policy modules, then
replaces only the action-prior and opponent-model distributions.  It keeps the Stage B
battle, clock, team pairing, and decision machinery as the execution harness while writing
all arm output under this directory.
"""

from __future__ import annotations

import argparse
import asyncio
import contextvars
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

COMPONENT_DIR = Path(__file__).resolve().parents[1]
ROOT = COMPONENT_DIR.parents[2]

POKE = ROOT / "work" / "poke-jev"
OUT = COMPONENT_DIR / "stage-b"
ALPHA_PATH = COMPONENT_DIR / "frozen-alpha-v1.json"
STOP_PATH = OUT / "mix-v1-stop.json"

# Stage B is an import target, not a copied implementation.  It changes cwd while loading
# PokéChamp, so all paths used by this wrapper are absolute and computed first.
sys.path.insert(0, str(POKE))
import stage_b  # noqa: E402
import player as player_module  # noqa: E402
import replay  # noqa: E402


MODULE_PATHS = {
    name: POKE / name for name in ("stage_b.py", "player.py", "policy.py", "replay.py")
}
MODULE_SHA256 = {
    name: hashlib.sha256(path.read_bytes()).hexdigest()
    for name, path in MODULE_PATHS.items()
}
FROZEN_ALPHA_SHA256 = hashlib.sha256(ALPHA_PATH.read_bytes()).hexdigest()

with ALPHA_PATH.open(encoding="utf-8") as fh:
    ALPHA = json.load(fh)
PLAYER_ALPHA = float(ALPHA["components"]["player"]["alpha"])
OPPONENT_ALPHA = float(ALPHA["components"]["opponent"]["alpha"])
if (PLAYER_ALPHA, OPPONENT_ALPHA) != (0.4, 0.25):
    raise RuntimeError("frozen-alpha-v1.json does not contain the preregistered alphas")


def _calibration_params() -> tuple[float, float]:
    rows = [
        json.loads(line)
        for line in (POKE / "stage-a" / "calib.jsonl").read_text().splitlines()
        if line.strip()
    ]
    switch_rows = [row for row in rows if row["switch_available"]]
    move_rows = [row for row in rows if row["kind"] == "move" and row["tera_available"]]
    return (
        sum(row["kind"] == "switch" for row in switch_rows) / len(switch_rows),
        sum(row["tera"] for row in move_rows) / len(move_rows),
    )


P_SWITCH, P_TERA = _calibration_params()
SETS = json.loads(
    (
        ROOT
        / "pokechamp"
        / "poke_env"
        / "data"
        / "static"
        / "gen9"
        / "ou"
        / "sets_1000.json"
    ).read_text()
)


def _mix(
    jev: dict[str, float], floor: dict[str, float], alpha: float
) -> dict[str, float]:
    """Return alpha * Jev + (1-alpha) * usage floor on the exact asked support."""
    if set(jev) != set(floor):
        raise ValueError("frozen mixture support differs from the legal option set")
    mixed = {key: alpha * jev[key] + (1.0 - alpha) * floor[key] for key in jev}
    total = sum(mixed.values())
    if not math.isfinite(total) or total <= 0:
        raise ValueError("frozen mixture is not a positive finite distribution")
    return {key: value / total for key, value in mixed.items()}


def action_prior_distribution(
    jev: dict[str, float], display: dict[str, str], battle
) -> dict[str, float]:
    """The sole action-prior intervention, using the frozen 0.40 alpha."""
    opts = list(display)
    floor = replay.usage_floor(
        opts,
        replay.to_id(battle.active_pokemon.species),
        SETS,
        P_SWITCH,
        P_TERA,
    )
    return _mix(jev, floor, PLAYER_ALPHA)


def opponent_model_distribution(
    jev: dict[str, float], display: dict[str, str], battle
) -> dict[str, float]:
    """The sole opponent-model intervention, using the frozen 0.25 alpha."""
    opts = list(display)
    floor = replay.usage_floor(
        opts,
        replay.to_id(battle.opponent_active_pokemon.species),
        SETS,
        P_SWITCH,
        P_TERA,
    )
    return _mix(jev, floor, OPPONENT_ALPHA)


_MIX_CONTEXT: contextvars.ContextVar[dict | None] = contextvars.ContextVar(
    "pokejev_frozen_mix_context", default=None
)
_ORIGINAL_VALIDATED = player_module.validated
_ORIGINAL_PLAYER = player_module.PokeJevPlayer


def _mixed_validated(probabilities: dict[str, float], display: dict[str, str]):
    result = _ORIGINAL_VALIDATED(probabilities, display)
    context = _MIX_CONTEXT.get()
    if context is None:
        return result
    slot = context["slot"]
    context["slot"] += 1
    if slot == 0:
        return action_prior_distribution(result, display, context["battle"])
    if slot == 1:
        return opponent_model_distribution(result, display, context["battle"])
    # Leaf probabilities are intentionally unchanged.
    return result


player_module.validated = _mixed_validated


class FrozenAlphaPlayer(_ORIGINAL_PLAYER):
    """Stage B player with only the two preregistered distribution substitutions."""

    async def _decide(self, battle, rec, box):
        token = _MIX_CONTEXT.set({"battle": battle, "slot": 0})
        try:
            return await super()._decide(battle, rec, box)
        finally:
            _MIX_CONTEXT.reset(token)

    async def _ask(self, state, questions, rec):
        try:
            return await super()._ask(state, questions, rec)
        except Exception as exc:
            text = f"{type(exc).__name__}: {exc}".lower()
            status = getattr(exc, "status_code", getattr(exc, "status", None))
            if status == 402 or "402" in text or "credit" in text or "billing" in text:
                OUT.mkdir(parents=True, exist_ok=True)
                STOP_PATH.write_text(
                    json.dumps(
                        {
                            "reason": f"{type(exc).__name__}: {str(exc)[:300]}",
                            "module_sha256": MODULE_SHA256,
                            "frozen_alpha_sha256": FROZEN_ALPHA_SHA256,
                        },
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            raise


_ORIGINAL_MAKE_PLAYERS = stage_b.make_players


def _make_players(opp_name, w, replays, decisions, client_factory=None, cls=None):
    chosen = FrozenAlphaPlayer if cls is None or cls is _ORIGINAL_PLAYER else cls
    return _ORIGINAL_MAKE_PLAYERS(
        opp_name,
        w,
        replays,
        decisions,
        client_factory,
        cls=chosen,
    )


stage_b.make_players = _make_players

# Decision/result JSONL rows are emitted by imported Stage B code.  Add provenance at the
# serialization boundary so every row records precisely which imported source was used.
_ORIGINAL_JSON_DUMPS = json.dumps


def _dumps_with_provenance(obj, *args, **kwargs):
    if isinstance(obj, dict) and ("k" in obj or ("battle" in obj and "turn" in obj)):
        obj = dict(obj)
        obj["stage_b_import_sha256"] = MODULE_SHA256
        obj["frozen_alpha_sha256"] = FROZEN_ALPHA_SHA256
    return _ORIGINAL_JSON_DUMPS(obj, *args, **kwargs)


json.dumps = _dumps_with_provenance


def _tag(control: bool) -> str:
    return "-mix-v1-control" if control else "-mix-v1"


def _configure(seed: int) -> None:
    stage_b.PAIR_SEED = seed
    stage_b.OUT = str(OUT)
    OUT.mkdir(parents=True, exist_ok=True)


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


async def _run_shard(
    opp_name: str,
    n: int,
    workers: int,
    worker: int,
    control: bool,
) -> int:
    tag = _tag(control)
    replays, results, decisions = stage_b.arm_paths(opp_name, tag)
    done = {row["k"] for row in _load_jsonl(Path(results)) if "won" in row}
    mine = [k for k in range(n) if k % workers == worker and k not in done]
    client_factory = stage_b.DisabledJev if control else None
    me, opp = stage_b.make_players(
        opp_name,
        worker + 50,
        replays,
        decisions,
        client_factory,
    )
    for k in mine:
        if not control and STOP_PATH.exists() and STOP_PATH.stat().st_size:
            return 3
        try:
            row = await stage_b.play(me, opp, k, replays)
        except Exception as exc:
            row = {"k": k, "error": f"{type(exc).__name__}: {str(exc)[:300]}"}
        await asyncio.to_thread(_append_jsonl, Path(results), row)
        if not control and STOP_PATH.exists() and STOP_PATH.stat().st_size:
            return 3
    return 0


def _spawn(opp_name: str, n: int, workers: int, control: bool, seed: int) -> int:
    env = dict(
        os.environ,
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        VECLIB_MAXIMUM_THREADS="1",
    )
    base = [
        sys.executable,
        str(Path(__file__).resolve()),
        "_shard",
        opp_name,
        str(n),
        str(workers),
        "--pair-seed",
        str(seed),
    ]
    procs = [
        subprocess.Popen(
            base + [str(worker)] + (["--control"] if control else []),
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            env=env,
        )
        for worker in range(workers)
    ]
    codes = [proc.wait() for proc in procs]
    _, results, _ = stage_b.arm_paths(opp_name, _tag(control))
    rows = _load_jsonl(Path(results))
    complete = {row["k"] for row in rows if "won" in row and row["k"] < n}
    print(
        f"{opp_name}{'-control' if control else ''}: {len(complete)}/{n} battles with a result, "
        f"{sum(1 for row in rows if 'error' in row)} harness-error rows, child codes {codes}",
        file=sys.stderr,
    )
    if STOP_PATH.exists() and STOP_PATH.stat().st_size:
        print(f"STOPPED: credit exhaustion marker at {STOP_PATH}", file=sys.stderr)
    return max(codes)


def selftest() -> int:
    """Keyless wrapper test: frozen supports, alphas, leaf passthrough, and row provenance."""
    battle = SimpleNamespace(
        active_pokemon=SimpleNamespace(species="pikachu"),
        opponent_active_pokemon=SimpleNamespace(species="charizard"),
    )
    display = {"move thunderbolt": "Thunderbolt", "move protect": "Protect"}
    answer = {"Thunderbolt": 0.75, "Protect": 0.25}
    prior = action_prior_distribution(
        _ORIGINAL_VALIDATED(answer, display), display, battle
    )
    floor = replay.usage_floor(
        list(display),
        replay.to_id(battle.active_pokemon.species),
        SETS,
        P_SWITCH,
        P_TERA,
    )
    expected = _mix(_ORIGINAL_VALIDATED(answer, display), floor, PLAYER_ALPHA)
    if prior != expected or abs(sum(prior.values()) - 1.0) >= 1e-12:
        raise AssertionError("action-prior mixture mismatch")

    opponent = opponent_model_distribution(
        _ORIGINAL_VALIDATED(answer, display), display, battle
    )
    opp_floor = replay.usage_floor(
        list(display),
        replay.to_id(battle.opponent_active_pokemon.species),
        SETS,
        P_SWITCH,
        P_TERA,
    )
    expected_opponent = _mix(
        _ORIGINAL_VALIDATED(answer, display), opp_floor, OPPONENT_ALPHA
    )
    if opponent != expected_opponent:
        raise AssertionError("opponent-model mixture mismatch")

    token = _MIX_CONTEXT.set({"battle": battle, "slot": 2})
    try:
        leaf = _mixed_validated(answer, display)
    finally:
        _MIX_CONTEXT.reset(token)
    if leaf != _ORIGINAL_VALIDATED(answer, display):
        raise AssertionError("leaf distribution was modified")

    row = json.loads(json.dumps({"k": 0, "battle": "test", "turn": 1}))
    if row.get("stage_b_import_sha256") != MODULE_SHA256:
        raise AssertionError("row is missing imported module provenance")
    if row.get("frozen_alpha_sha256") != FROZEN_ALPHA_SHA256:
        raise AssertionError("row is missing frozen-alpha provenance")
    print("WRAPPER SELFTEST PASS 4/4")
    return 0


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 4), round(c + h, 4))


def _score_arm(opp_name: str, control: bool) -> dict | None:
    tag = _tag(control)
    rows = _load_jsonl(OUT / f"results-{opp_name}{tag}.jsonl")
    decisions = _load_jsonl(OUT / f"decisions-{opp_name}{tag}.jsonl")
    completed = list({row["k"]: row for row in rows if "won" in row}.values())
    errors = [row for row in rows if "error" in row]
    if not completed and not errors:
        return None
    fallback_reasons: dict[str, int] = {}
    for decision in decisions:
        if decision.get("fallback"):
            reason = str(decision["fallback"])
            fallback_reasons[reason] = fallback_reasons.get(reason, 0) + 1
    latencies = sorted(decision["ms"] for decision in decisions if "ms" in decision)
    tokens = sum(int(decision.get("input_tokens", 0)) for decision in decisions)
    wins = sum(bool(row["won"]) for row in completed)
    return {
        "battles": len(completed),
        "harness_errors": len(errors),
        "wins": wins,
        "losses": len(completed) - wins,
        "win_rate": round(wins / len(completed), 4) if completed else None,
        "wilson95": _wilson(wins, len(completed)),
        "own_time_losses": sum(row.get("time_loss") == "pokejev" for row in completed),
        "opponent_time_losses": sum(
            row.get("time_loss") == "opponent" for row in completed
        ),
        "unfinished": sum(not row.get("finished", False) for row in completed),
        "decisions": len(decisions),
        "fallbacks": sum(fallback_reasons.values()),
        "fallback_reasons": dict(sorted(fallback_reasons.items())),
        "decision_ms_p50": latencies[len(latencies) // 2] if latencies else None,
        "decision_ms_p95": latencies[int(len(latencies) * 0.95)] if latencies else None,
        "decision_ms_max": latencies[-1] if latencies else None,
        "jev_calls": sum(len(decision.get("jev_ms", [])) for decision in decisions),
        "input_tokens": tokens,
        "spend_usd_at_0.042_per_M_input": round(tokens * 0.042 / 1e6, 4),
        "models": sorted(
            {model for decision in decisions for model in decision.get("models", [])}
        ),
        "module_sha256": MODULE_SHA256,
        "frozen_alpha_sha256": FROZEN_ALPHA_SHA256,
    }


def score() -> int:
    out = {
        "model": "jev-1.13.0",
        "pair_seed": stage_b.PAIR_SEED,
        "arms": {
            "abyssal-mix-v1": _score_arm("abyssal", False),
            "abyssal-mix-v1-control": _score_arm("abyssal", True),
        },
        "stop_marker": str(STOP_PATH)
        if STOP_PATH.exists() and STOP_PATH.stat().st_size
        else None,
        "module_sha256": MODULE_SHA256,
        "frozen_alpha_sha256": FROZEN_ALPHA_SHA256,
    }
    live = out["arms"]["abyssal-mix-v1"]
    control = out["arms"]["abyssal-mix-v1-control"]
    if live and control and live["battles"] and control["battles"]:
        p_live = live["wins"] / live["battles"]
        p_control = control["wins"] / control["battles"]
        pooled = (live["wins"] + control["wins"]) / (
            live["battles"] + control["battles"]
        )
        se = (
            math.sqrt(
                pooled * (1 - pooled) * (1 / live["battles"] + 1 / control["battles"])
            )
            if 0 < pooled < 1
            else 0.0
        )
        z = (p_live - p_control) / se if se else 0.0
        out["live_minus_control"] = {
            "difference": round(p_live - p_control, 4),
            "z": round(z, 3),
            "p_two_sided": round(math.erfc(abs(z) / math.sqrt(2)), 4),
        }
    (OUT / "receipt-mix-v1.json").write_text(
        _ORIGINAL_JSON_DUMPS(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(_ORIGINAL_JSON_DUMPS(out, indent=1, sort_keys=True))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("command", choices=("selftest", "battles", "_shard", "score"))
    parser.add_argument("opponent", nargs="?")
    parser.add_argument("count", nargs="?", type=int)
    parser.add_argument("worker_count", nargs="?", type=int)
    parser.add_argument("worker", nargs="?", type=int)
    parser.add_argument("--workers", dest="workers", type=int, default=stage_b.WORKERS)
    parser.add_argument("--pair-seed", type=int, default=20260926)
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args(argv)
    _configure(args.pair_seed)
    if args.command == "selftest":
        return selftest()
    if args.command == "score":
        return score()
    if args.opponent not in stage_b.OPPONENTS or args.count is None:
        parser.error("an opponent and battle count are required")
    if args.command == "battles":
        if not args.control and not os.environ.get("TYPESAFE_API_KEY"):
            print(
                "unconfigured: TYPESAFE_API_KEY unset, no battle played (NOT_RUN)",
                file=sys.stderr,
            )
            return 2
        if not args.control:
            STOP_PATH.write_text("", encoding="utf-8")
        return _spawn(
            args.opponent, args.count, args.workers, args.control, args.pair_seed
        )
    if args.worker_count is None or args.worker is None:
        parser.error("_shard requires worker count and worker index")
    return asyncio.run(
        _run_shard(
            args.opponent, args.count, args.worker_count, args.worker, args.control
        )
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
