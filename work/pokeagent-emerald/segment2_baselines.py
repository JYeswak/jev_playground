#!/usr/bin/env python3
"""Run the source-derived, position-dependent Emerald segment baselines."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess  # nosec B404 - argv is never shell-parsed
import sys
import time
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any

from capture_state import BOOT_MACROS
from macro_choice import LEGAL_INPUTS
from run_baselines import invalid_result_rows, pooled_metadata, write_receipt

START_MACRO = 228
DEFAULT_CAP = 50
BASE_LOCATION = "MOVING_VAN"


_JSON_DECODER = json.JSONDecoder()


def _json_line(raw: str, source: str | Path, line_number: int) -> Any:
    try:
        return _JSON_DECODER.decode(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{source} row {line_number} is not valid JSON: {exc.msg}"
        ) from exc


def _load_pooled_buttons(path: Path) -> list[str]:
    pooled: list[str] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        row = _json_line(line, path, line_number)
        if not isinstance(row, dict):
            raise TypeError(f"{path} row {line_number} is not a JSON object")
        button = row.get("button")
        if button not in LEGAL_INPUTS:
            raise ValueError(
                f"{path} row {line_number} has an invalid button {button!r}"
            )
        pooled.append(button)
    if not pooled:
        raise ValueError(f"{path} has no macro buttons")
    return pooled


def _position(state: dict[str, Any]) -> dict[str, int]:
    position = state["player"]["position"] if "player" in state else state["position"]
    return {"x": int(position["x"]), "y": int(position["y"])}


def derive_segment_spec(path: Path) -> dict[str, Any]:
    """Derive the two positions and reversible actions from the committed trace."""
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        row = _json_line(line, path, line_number)
        if not isinstance(row, dict):
            raise TypeError(f"{path} row {line_number} is not a JSON object")
        rows.append(row)
    by_macro = {int(row["macro_index"]): row for row in rows}
    base = by_macro[228]
    base_setup_end = by_macro[298]
    left = by_macro[299]
    right = by_macro[303]
    setup_to_base = [by_macro[index]["button"] for index in range(229, 299)]
    setup_to_left = [by_macro[index]["button"] for index in range(229, 300)]
    base_position = _position(base["state"])
    left_position = _position(left["state"])
    right_position = _position(right["state"])
    if base["state"]["player"]["location"] not in {BASE_LOCATION}:
        raise ValueError("segment base location drifted")
    if left["button"] not in {"LEFT"} or left_position != {"x": 1, "y": 2}:
        raise ValueError("recorded LEFT transition drifted")
    if right["button"] not in {"RIGHT"} or right_position != {"x": 2, "y": 2}:
        raise ValueError("recorded RIGHT transition drifted")
    if any(base_position[axis] != right_position[axis] for axis in ("x", "y")):
        raise ValueError("recorded base and RIGHT positions disagree")
    if sum(
        abs(
            base_setup_end["state"]["player"]["position"][axis]
            - base["state"]["player"]["position"][axis]
        )
        for axis in ("x", "y")
    ):
        raise ValueError("recorded base setup drifted")
    return {
        "base_position": base_position,
        "left_position": left_position,
        "right_position": right_position,
        "setup_to_base": setup_to_base,
        "setup_to_left": setup_to_left,
        "evidence_rows": [[299, "LEFT"], [303, "RIGHT"]],
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def setup_position(spec: dict[str, Any], seed: int) -> dict[str, int]:
    return dict(spec["left_position"] if seed % 2 else spec["base_position"])


def goal_reached(initial: dict[str, int], current: dict[str, int]) -> bool:
    return current["y"] == initial["y"] and current["x"] != initial["x"]


def sample_state_blind_buttons(
    rng: random.Random, pooled_buttons: list[str], cap: int
) -> list[str]:
    if cap < 0:
        raise ValueError(f"cap must be non-negative, got {cap}")
    if not pooled_buttons:
        raise ValueError("state-blind pool has no buttons")
    return [rng.choice(pooled_buttons) for _ in range(cap)]


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
    spec: dict[str, Any],
    pooled_buttons: list[str] | None,
) -> dict[str, Any]:
    env = emulator_cls(rom, headless=True, sound=False)
    env.initialize()
    started = time.monotonic()
    boot_state = _boot_to_start(env)
    if _position(boot_state) != spec["base_position"]:
        raise RuntimeError(f"fixed start drifted: {_position(boot_state)!r}")
    setup_button = "trace_to_left" if seed % 2 else "trace_to_base"
    setup_buttons = spec["setup_to_left"] if seed % 2 else spec["setup_to_base"]
    for button in setup_buttons:
        _press(env, button)
    initial_state = _state(env)
    initial_position = _position(initial_state)
    if initial_position != setup_position(spec, seed):
        raise RuntimeError(f"segment setup drifted: {initial_position!r}")
    rng = random.Random(seed)  # nosec B311 - deterministic experiment sampling only
    if policy == "uniform":
        buttons = [rng.choice(LEGAL_INPUTS) for _ in range(cap)]
    elif policy == "state_blind":
        buttons = sample_state_blind_buttons(rng, pooled_buttons or [], cap)
    else:
        raise ValueError(f"unknown segment-two policy: {policy}")
    goal = False
    macros = 0
    final_state = initial_state
    for button in buttons:
        _press(env, button)
        macros += 1
        final_state = _state(env)
        if goal_reached(initial_position, _position(final_state)):
            goal = True
            break
    return {
        "policy": policy,
        "seed": seed,
        "segment": "position_change",
        "start_macro": START_MACRO,
        "setup_button": setup_button,
        "start": initial_state,
        "goal": {"position_changed": True, "same_y": initial_position["y"]},
        "goal_reached": goal,
        "macros_after_start": macros,
        "macro_cap": cap,
        "final": final_state,
        "wall_s": round(time.monotonic() - started, 3),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def _single(args: argparse.Namespace) -> int:
    emulator_cls = import_module("pokemon_env.emulator").EmeraldEmulator
    spec = derive_segment_spec(Path(args.states_source))
    pooled = None
    metadata: dict[str, Any] = {"state_source_sha256": spec["source_sha256"]}
    if args.policy == "state_blind":
        if not args.pooled_rows:
            raise ValueError("state_blind requires --pooled-rows")
        pooled_path = Path(args.pooled_rows)
        pooled = _load_pooled_buttons(pooled_path)
        metadata.update(pooled_metadata(pooled_path, pooled))
    row = run_one(
        emulator_cls,
        args.rom,
        args.policy,
        args.seed,
        args.cap,
        spec,
        pooled,
    )
    row.update(metadata)
    print(json.dumps(row, separators=(",", ":")))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--states-source", required=True)
    parser.add_argument("--pooled-rows")
    parser.add_argument("--output")
    parser.add_argument("--receipt")
    parser.add_argument("--states-output")
    parser.add_argument("--uniform", type=int, default=80)
    parser.add_argument("--state-blind", type=int, default=80)
    parser.add_argument("--cap", type=int, default=DEFAULT_CAP)
    parser.add_argument("--harness-sha", required=True)
    parser.add_argument("--rom-sha1", required=True)
    parser.add_argument("--single", action="store_true")
    parser.add_argument("--policy", choices=("uniform", "state_blind"))
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if args.single:
        if args.policy is None or args.seed is None:
            parser.error("--single requires --policy and --seed")
        if args.policy == "state_blind" and not args.pooled_rows:
            parser.error("state_blind requires --pooled-rows")
        return _single(args)
    if not args.output or not args.receipt or not args.states_output:
        parser.error("parent mode requires --output, --receipt, and --states-output")
    if args.state_blind and not args.pooled_rows:
        parser.error("--state-blind requires --pooled-rows")
    spec = derive_segment_spec(Path(args.states_source))
    pooled_path = Path(args.pooled_rows) if args.pooled_rows else None
    pooled = _load_pooled_buttons(pooled_path) if pooled_path else None
    pool_metadata = (
        pooled_metadata(pooled_path, pooled) if pooled_path and pooled else {}
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    jobs = [("uniform", seed) for seed in range(args.uniform)] + [
        ("state_blind", seed) for seed in range(args.state_blind)
    ]
    rows: list[dict[str, Any]] = []
    for policy, seed in jobs:
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--single",
            "--rom",
            args.rom,
            "--states-source",
            args.states_source,
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
            result = subprocess.run(  # nosec B603 - argv list, shell=False, explicit inputs
                command, check=True, capture_output=True, text=True, timeout=300
            )
            child_lines = result.stdout.strip().splitlines()
            if not child_lines:
                raise ValueError("child produced no JSON row")
            row = _json_line(child_lines[-1], f"child {policy} seed {seed}", 1)
            if not isinstance(row, dict):
                raise TypeError("child produced a non-object JSON row")
        except subprocess.CalledProcessError as exc:
            row = {
                "policy": policy,
                "seed": seed,
                "segment": "position_change",
                "goal_reached": False,
                "macros_after_start": None,
                "macro_cap": args.cap,
                "final": None,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "child_error": f"exit_{exc.returncode}",
                "child_stderr": (exc.stderr or "").strip(),
            }
        except (TypeError, ValueError) as exc:
            row = {
                "policy": policy,
                "seed": seed,
                "segment": "position_change",
                "goal_reached": False,
                "macros_after_start": None,
                "macro_cap": args.cap,
                "final": None,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "child_error": "invalid_child_output",
                "child_stderr": str(exc),
            }
        row.update(
            {
                "code_sha256": code_sha,
                "harness_sha": args.harness_sha,
                "rom_sha1": args.rom_sha1,
                "state_source_sha256": spec["source_sha256"],
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
    for row in rows:
        row["scored"] = True
    output.write_text(
        "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    states_output = Path(args.states_output)
    states_output.write_text(
        "".join(
            json.dumps(
                {"id": f"{row['policy']}-{row['seed']}", "state": row["start"]},
                separators=(",", ":"),
            )
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )

    summary = {
        "status": "OK",
        "rows": len(rows),
        "scored_rows": len(rows),
        "uniform": args.uniform,
        "state_blind": args.state_blind,
        "cap": args.cap,
        "code_sha256": code_sha,
        "state_source_sha256": spec["source_sha256"],
        "goal_rates": {
            policy: sum(row["goal_reached"] for row in rows if row["policy"] == policy)
            / count
            for policy, count in (
                ("uniform", args.uniform),
                ("state_blind", args.state_blind),
            )
            if count
        },
        "pooled_source": pool_metadata,
    }
    summary["results_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    summary["states_sha256"] = hashlib.sha256(states_output.read_bytes()).hexdigest()
    write_receipt(Path(args.receipt), rows, summary)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
