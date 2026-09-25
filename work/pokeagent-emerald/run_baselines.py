#!/usr/bin/env python3
"""Run fixed-script and uniform-random Emerald macro baselines without a model."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any

from capture_state import BOOT_MACROS
from macro_choice import LEGAL_INPUTS

START_MACRO = 228
START_LOCATION = "MOVING_VAN"
DEFAULT_CAP = 500
SCRIPTED_SEED = 20260925
_scripted_rng = random.Random(SCRIPTED_SEED)
SCRIPTED_TAIL = [_scripted_rng.choice(LEGAL_INPUTS) for _ in range(DEFAULT_CAP)]


def _state(env: Any) -> dict[str, Any]:
    reader = env.memory_reader
    coords = reader.read_coordinates()
    return {
        "game_state": reader.get_game_state(),
        "location": reader.read_location(),
        "position": {"x": coords[0], "y": coords[1]},
    }


def _press(env: Any, button: str) -> None:
    if button == "WAIT":
        env.tick(18)
    else:
        env.press_buttons([button], hold_frames=10, release_frames=8)


def _boot_to_start(env: Any) -> dict[str, Any]:
    for button in BOOT_MACROS[: START_MACRO + 1]:
        _press(env, button)
    return _state(env)


def run_one(
    emulator_cls: Any, rom: str, policy: str, seed: int, cap: int, scripted: list[str]
) -> dict[str, Any]:
    # A separate worker process per run avoids the native mGBA crash caused by
    # accumulating cores across repeated runs in one interpreter.
    env = emulator_cls(rom, headless=True, sound=False)
    env.initialize()
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
        if final["location"] not in (None, START_LOCATION):
            goal = True
            break
    return {
        "policy": policy,
        "seed": seed,
        "start_macro": START_MACRO,
        "start": start,
        "goal": {"location_not": START_LOCATION},
        "goal_reached": goal,
        "macros_after_start": macros,
        "macro_cap": cap,
        "final": final,
        "wall_s": round(time.monotonic() - started, 3),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def _single(args: argparse.Namespace) -> int:
    emulator_cls = import_module("pokemon_env.emulator").EmeraldEmulator
    row = run_one(
        emulator_cls, args.rom, args.policy, args.seed, args.cap, SCRIPTED_TAIL
    )
    print(json.dumps(row, separators=(",", ":")))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--output")
    parser.add_argument("--scripted", type=int, default=20)
    parser.add_argument("--random", type=int, default=20)
    parser.add_argument("--cap", type=int, default=DEFAULT_CAP)
    parser.add_argument("--harness-sha", required=True)
    parser.add_argument("--seed-offset", type=int, default=0)
    parser.add_argument("--rom-sha1", required=True)
    parser.add_argument("--single", action="store_true")
    parser.add_argument("--policy", choices=("scripted", "random"))
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    if args.single:
        if args.policy is None or args.seed is None:
            parser.error("--single requires --policy and --seed")
        return _single(args)
    if not args.output:
        parser.error("--output is required unless --single is set")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rows = []
    jobs = [("scripted", args.seed_offset + seed) for seed in range(args.scripted)] + [
        ("random", 1000 + args.seed_offset + seed) for seed in range(args.random)
    ]
    for policy, seed in jobs:
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--single",
            "--rom",
            args.rom,
            "--policy",
            policy,
            "--seed",
            str(seed),
            "--cap",
            str(args.cap),
            "--harness-sha",
            args.harness_sha,
            "--rom-sha1",
            args.rom_sha1,
        ]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            row = json.loads(result.stdout.strip().splitlines()[-1])
        except subprocess.CalledProcessError as exc:
            row = {
                "policy": policy,
                "seed": seed,
                "start_macro": START_MACRO,
                "goal": {"location_not": START_LOCATION},
                "goal_reached": False,
                "macros_after_start": None,
                "macro_cap": args.cap,
                "final": None,
                "wall_s": None,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "child_error": f"exit_{exc.returncode}",
            }
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
