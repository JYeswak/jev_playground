#!/usr/bin/env python3
"""Run fixed-sequence, random, and state-blind Emerald baselines without a model."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any

from capture_state import BOOT_MACROS
from macro_choice import LEGAL_INPUTS

START_MACRO = 228
START_LOCATION = "MOVING_VAN"
DEFAULT_CAP = 500
FIXED_SEQUENCE_SEED = 20260925
_fixed_rng = random.Random(FIXED_SEQUENCE_SEED)
FIXED_SEQUENCE = [_fixed_rng.choice(LEGAL_INPUTS) for _ in range(DEFAULT_CAP)]


def load_pooled_buttons(path: Path) -> list[str]:
    """Return observed buttons, one entry per committed live macro row."""
    buttons: list[str] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, raw in enumerate(stream, 1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            button = row.get("button") if isinstance(row, dict) else None
            if button not in LEGAL_INPUTS:
                raise ValueError(
                    f"{path} row {line_number} has invalid button {button!r}"
                )
            buttons.append(button)
    if not buttons:
        raise ValueError(f"{path} has no macro buttons")
    return buttons


def sample_state_blind_buttons(
    rng: random.Random, pooled_buttons: list[str], cap: int
) -> list[str]:
    """Sample each macro uniformly from the empirical pooled-button rows."""
    if cap < 0:
        raise ValueError(f"cap must be non-negative, got {cap}")
    if not pooled_buttons:
        raise ValueError("state-blind pool has no buttons")
    return [rng.choice(pooled_buttons) for _ in range(cap)]


def pooled_metadata(path: Path, buttons: list[str]) -> dict[str, Any]:
    return {
        "pooled_source": str(path),
        "pooled_source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "pooled_source_rows": len(buttons),
        "pooled_button_counts": dict(sorted(Counter(buttons).items())),
    }


def invalid_result_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return rows that cannot support a scored baseline result."""
    return [
        row
        for row in rows
        if row.get("child_error") is not None or row.get("final") is None
    ]


def write_receipt(
    path: Path, rows: list[dict[str, Any]], metadata: dict[str, Any]
) -> None:
    """Write a receipt only when every row has a final emulator state."""
    invalid = invalid_result_rows(rows)
    if invalid:
        raise ValueError(
            f"refusing receipt: {len(invalid)} rows are NOT-SCORED due to child_error or null final"
        )
    payload = dict(metadata)
    payload.setdefault("rows", len(rows))
    payload.setdefault("not_scored", 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Emerald baseline receipt\n\n```json\n"
        + json.dumps(payload, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )


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
    emulator_cls: Any,
    rom: str,
    policy: str,
    seed: int,
    cap: int,
    fixed_sequence: list[str],
    pooled_buttons: list[str] | None = None,
) -> dict[str, Any]:
    # A separate worker process per run avoids the native mGBA crash caused by
    # accumulating cores across repeated runs in one interpreter.
    env = emulator_cls(rom, headless=True, sound=False)
    env.initialize()
    started = time.monotonic()
    start = _boot_to_start(env)
    rng = random.Random(seed)
    if policy == "fixed_sequence":
        buttons = fixed_sequence
    elif policy == "state_blind":
        buttons = sample_state_blind_buttons(rng, pooled_buttons or [], cap)
    elif policy == "random":
        buttons = [rng.choice(LEGAL_INPUTS) for _ in range(cap)]
    else:
        raise ValueError(f"unknown baseline policy: {policy}")
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
    pooled_buttons = None
    metadata: dict[str, Any] = {}
    if args.policy == "state_blind":
        if not args.pooled_rows:
            raise ValueError("state_blind requires --pooled-rows")
        pooled_path = Path(args.pooled_rows)
        pooled_buttons = load_pooled_buttons(pooled_path)
        metadata = pooled_metadata(pooled_path, pooled_buttons)
    row = run_one(
        emulator_cls,
        args.rom,
        args.policy,
        args.seed,
        args.cap,
        FIXED_SEQUENCE,
        pooled_buttons,
    )
    row.update(metadata)
    print(json.dumps(row, separators=(",", ":")))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--output")
    parser.add_argument("--receipt")
    parser.add_argument("--fixed-sequence", type=int, default=33)
    parser.add_argument("--random", type=int, default=33)
    parser.add_argument("--state-blind", type=int, default=0)
    parser.add_argument("--pooled-rows")
    parser.add_argument("--cap", type=int, default=DEFAULT_CAP)
    parser.add_argument("--harness-sha", required=True)
    parser.add_argument("--seed-offset", type=int, default=0)
    parser.add_argument("--rom-sha1", required=True)
    parser.add_argument("--single", action="store_true")
    parser.add_argument("--policy", choices=("fixed_sequence", "random", "state_blind"))
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    if args.single:
        if args.policy is None or args.seed is None:
            parser.error("--single requires --policy and --seed")
        if args.policy == "state_blind" and not args.pooled_rows:
            parser.error("state_blind requires --pooled-rows")
        return _single(args)
    if not args.output:
        parser.error("--output is required unless --single is set")
    if args.state_blind and not args.pooled_rows:
        parser.error("--state-blind requires --pooled-rows")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    pooled_buttons = None
    pool_metadata: dict[str, Any] = {}
    if args.state_blind:
        pooled_path = Path(args.pooled_rows)
        pooled_buttons = load_pooled_buttons(pooled_path)
        pool_metadata = pooled_metadata(pooled_path, pooled_buttons)
    rows = []
    jobs = [
        ("fixed_sequence", args.seed_offset + seed)
        for seed in range(args.fixed_sequence)
    ] + [("random", 1000 + args.seed_offset + seed) for seed in range(args.random)]
    jobs += [
        ("state_blind", args.seed_offset + seed) for seed in range(args.state_blind)
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
        if policy == "state_blind":
            command.extend(["--pooled-rows", args.pooled_rows])
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
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "child_error": f"exit_{exc.returncode}",
                "child_stderr": (exc.stderr or "").strip(),
            }
        row["scored"] = (
            not bool(row.get("child_error")) and row.get("final") is not None
        )
        if not row["scored"]:
            row["not_scored_reason"] = "child_error_or_null_final"
        row.update(
            {
                "code_sha256": code_sha,
                "harness_sha": args.harness_sha,
                "rom_sha1": args.rom_sha1,
            }
        )
        if policy == "state_blind":
            row.update(pool_metadata)
        rows.append(row)
    invalid = invalid_result_rows(rows)
    if invalid:
        print(
            json.dumps(
                {
                    "status": "REFUSED",
                    "reason": "NOT-SCORED rows cannot be treated as capped failures",
                    "rows": len(rows),
                    "not_scored": len(invalid),
                    "child_errors": [
                        {
                            "seed": row.get("seed"),
                            "child_error": row.get("child_error"),
                            "child_stderr": row.get("child_stderr"),
                        }
                        for row in invalid
                    ],
                }
            ),
            file=sys.stderr,
        )
        return 2

    output.write_text(
        "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows)
    )
    summary = {
        "status": "OK",
        "rows": len(rows),
        "scored_rows": len(rows),
        "not_scored": 0,
        "fixed_sequence": args.fixed_sequence,
        "random": args.random,
        "state_blind": args.state_blind,
        "cap": args.cap,
        "code_sha256": code_sha,
        **pool_metadata,
    }
    summary["results_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    if args.receipt:
        write_receipt(Path(args.receipt), rows, summary)
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
