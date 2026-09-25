#!/usr/bin/env python3
"""Run fixed-script and uniform-random Emerald macro baselines without a model."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any

from capture_state import BOOT_MACROS
from macro_choice import LEGAL_INPUTS

START_MACRO = 142
GOAL_LOCATION = "MOVING_VAN"
DEFAULT_CAP = 100


def _state(env: Any) -> dict[str, Any]:
    raw = env.get_comprehensive_state(screenshot=None)
    return {
        "game_state": raw.get("game", {}).get("game_state"),
        "location": raw.get("player", {}).get("location"),
        "position": raw.get("player", {}).get("position"),
    }


def _reset(env: Any) -> None:
    env.core.reset()
    for attr in ("_cached_state", "_cached_state_time"):
        if hasattr(env, attr):
            delattr(env, attr)
    env._cached_dialog_state = False
    env._last_dialog_check_time = 0
    if env.memory_reader is not None:
        env.memory_reader._mem_cache = {}
        env.memory_reader.reset_dialog_tracking()


def _press(env: Any, button: str) -> None:
    if button == "WAIT":
        env.tick(18)
    else:
        env.press_buttons([button], hold_frames=10, release_frames=8)


def _boot_to_start(env: Any) -> dict[str, Any]:
    for button in BOOT_MACROS[: START_MACRO + 1]:
        _press(env, button)
    return _state(env)


def _scripted_tail(trace_path: Path) -> list[str]:
    rows = [
        json.loads(line) for line in trace_path.read_text().splitlines() if line.strip()
    ]
    tail = []
    for row in rows:
        if row["macro_index"] <= START_MACRO:
            continue
        tail.append(row["button"])
        if row["state"]["player"].get("location") == GOAL_LOCATION:
            break
    if not tail or len(tail) > DEFAULT_CAP:
        raise RuntimeError(f"bad scripted tail: {len(tail)} macros")
    return tail


def run_one(
    env: Any, policy: str, seed: int, cap: int, scripted: list[str]
) -> dict[str, Any]:
    _reset(env)
    started = time.monotonic()
    start = _boot_to_start(env)
    rng = random.Random(seed)
    buttons = (
        scripted
        if policy == "scripted"
        else [rng.choice(LEGAL_INPUTS) for _ in range(cap)]
    )
    goal = False
    macros = 0
    final = start
    for button in buttons[:cap]:
        _press(env, button)
        macros += 1
        final = _state(env)
        if final["location"] == GOAL_LOCATION:
            goal = True
            break
    return {
        "policy": policy,
        "seed": seed,
        "start_macro": START_MACRO,
        "start": start,
        "goal": {"location": GOAL_LOCATION},
        "goal_reached": goal,
        "macros_after_start": macros,
        "macro_cap": cap,
        "final": final,
        "wall_s": round(time.monotonic() - started, 3),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--trace", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--scripted", type=int, default=20)
    parser.add_argument("--random", type=int, default=20)
    parser.add_argument("--cap", type=int, default=DEFAULT_CAP)
    parser.add_argument("--harness-sha", required=True)
    parser.add_argument("--rom-sha1", required=True)
    args = parser.parse_args()

    EmeraldEmulator = import_module("pokemon_env.emulator").EmeraldEmulator
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    scripted = _scripted_tail(Path(args.trace))
    env = EmeraldEmulator(args.rom, headless=True, sound=False)
    env.initialize()
    code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rows = []
    for seed in range(args.scripted):
        row = run_one(env, "scripted", seed, args.cap, scripted)
        row.update(
            {
                "code_sha256": code_sha,
                "harness_sha": args.harness_sha,
                "rom_sha1": args.rom_sha1,
            }
        )
        rows.append(row)
    for seed in range(args.random):
        row = run_one(env, "random", 1000 + seed, args.cap, scripted)
        row.update(
            {
                "code_sha256": code_sha,
                "harness_sha": args.harness_sha,
                "rom_sha1": args.rom_sha1,
            }
        )
        rows.append(row)
    output.write_text(
        "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows)
    )
    print(
        json.dumps(
            {
                "rows": len(rows),
                "scripted": args.scripted,
                "random": args.random,
                "cap": args.cap,
                "code_sha256": code_sha,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
