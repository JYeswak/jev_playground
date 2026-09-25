#!/usr/bin/env python3
"""Run the preregistered Emerald Choice segment with pinned Jev live calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import subprocess
import time
import sys
from datetime import datetime, timezone
from collections.abc import Sequence
from importlib import import_module
from pathlib import Path
from statistics import median
from typing import Any
from capture_state import BOOT_MACROS
from macro_choice import LEGAL_INPUTS, build_choice_request

MODEL = "jev-1.13.0"
START_MACRO = 228
START_LOCATION = "MOVING_VAN"


def _press(env: Any, button: str) -> None:
    if button == "WAIT":
        env.tick(18)
    else:
        env.press_buttons([button], hold_frames=10, release_frames=8)


def _raw_state(env: Any) -> dict[str, Any]:
    return env.get_comprehensive_state(screenshot=None)


def _location(raw: dict[str, Any]) -> str | None:
    return raw.get("player", {}).get("location")


def _live_choice(
    client: Any, request: dict[str, Any], rng: random.Random
) -> tuple[str, dict[str, float], int | None, str]:
    Choice = import_module("typesafe_sdk").Choice
    question = request["questions"]["macro"]
    response = client.system_one(
        state=request["state"],
        questions={
            "macro": Choice(
                instructions=question["instructions"],
                criteria=question["criteria"],
            )
        },
        model=MODEL,
    )
    answer = response.choices["macro"]
    probabilities = {
        str(key): float(value) for key, value in answer.probabilities.items()
    }
    if set(probabilities) != set(LEGAL_INPUTS):
        raise ValueError(f"Choice probability labels drifted: {sorted(probabilities)}")
    values = [probabilities[label] for label in LEGAL_INPUTS]
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("Choice probability contains a non-finite or negative value")
    total = sum(values)
    if abs(total - 1.0) > 0.02:
        raise ValueError(f"Choice probabilities do not normalize: {total}")
    selected = rng.choices(LEGAL_INPUTS, weights=values, k=1)[0]
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None)
    model = str(getattr(response, "model", MODEL))
    return selected, probabilities, input_tokens, model


def _is_auth_or_payment(exc: BaseException) -> bool:
    status = getattr(exc, "status_code", None)
    response = getattr(exc, "response", None)
    status = status or getattr(response, "status_code", None)
    if status in (401, 402):
        return True
    return bool(re.search(r"\b(?:401|402)\b", str(exc)))


def worker(args: argparse.Namespace) -> int:
    emulator_cls = import_module("pokemon_env.emulator").EmeraldEmulator
    format_state = import_module("utils.state_formatter").format_state_for_llm
    TypeSafeClient = import_module("typesafe_sdk").TypeSafeClient
    code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    env = emulator_cls(args.rom, headless=True, sound=False)
    env.initialize()
    for button in BOOT_MACROS[: START_MACRO + 1]:
        _press(env, button)
    start_raw = _raw_state(env)
    if _location(start_raw) != START_LOCATION:
        raise RuntimeError(f"fixed start drifted: {_location(start_raw)!r}")

    rng = random.Random(args.seed)
    output = Path(args.seed_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle, TypeSafeClient() as client:
        for macro_index in range(args.cap):
            raw = _raw_state(env)
            state_text = format_state(raw)
            request = build_choice_request({"state": raw, "state_text": state_text})
            started = time.monotonic()
            try:
                button, probabilities, input_tokens, model = _live_choice(
                    client, request, rng
                )
            except Exception as exc:
                error = {
                    "kind": "fatal",
                    "code_sha256": code_sha,
                    "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                    "seed": args.seed,
                    "macro_index": macro_index,
                    "error": f"{type(exc).__name__}: {exc}",
                    "auth_or_payment": _is_auth_or_payment(exc),
                }
                handle.write(json.dumps(error, separators=(",", ":")) + "\n")
                handle.flush()
                return 42 if error["auth_or_payment"] else 43
            latency_ms = (time.monotonic() - started) * 1000
            _press(env, button)
            after = _raw_state(env)
            row = {
                "kind": "macro",
                "code_sha256": code_sha,
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "seed": args.seed,
                "macro_index": macro_index,
                "button": button,
                "probabilities": probabilities,
                "input_tokens": input_tokens,
                "model": model,
                "latency_ms": round(latency_ms, 3),
                "state_bytes": len(
                    json.dumps(
                        request["state"], separators=(",", ":"), ensure_ascii=False
                    ).encode()
                ),
                "before": {
                    "location": _location(raw),
                    "position": raw.get("player", {}).get("position"),
                },
                "after": {
                    "location": _location(after),
                    "position": after.get("player", {}).get("position"),
                },
            }
            handle.write(
                json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n"
            )
            handle.flush()
            if _location(after) != START_LOCATION:
                return 0
    return 0


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1)]


def parent(args: argparse.Namespace) -> int:
    output = Path(args.output)
    receipt_path = Path(args.receipt)
    scratch = Path(args.scratch)
    output.parent.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    started = time.monotonic()
    seed_end = args.end_seed if args.end_seed is not None else args.seeds
    for seed in range(args.start_seed, seed_end):
        seed_output = scratch / f"seed-{seed:03d}.jsonl"
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
            "--rom",
            args.rom,
            "--seed",
            str(seed),
            "--cap",
            str(args.cap),
            "--seed-output",
            str(seed_output),
        ]
        print(f"LIVE seed={seed} start", flush=True)
        result = subprocess.run(command, check=False, text=True)
        seed_rows = [
            json.loads(line)
            for line in seed_output.read_text().splitlines()
            if line.strip()
        ]
        rows.extend(seed_rows)
        fatal = next((row for row in seed_rows if row.get("kind") == "fatal"), None)
        if result.returncode != 0 or fatal is not None:
            output.write_text(
                "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows)
            )
            print(
                f"LIVE STOP seed={seed} returncode={result.returncode} fatal={fatal}",
                flush=True,
            )
            return result.returncode or 43
        print(f"LIVE seed={seed} done rows={len(seed_rows)}", flush=True)

    output.write_text(
        "".join(
            json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n"
            for row in rows
        )
    )
    macro_rows = [row for row in rows if row.get("kind") == "macro"]
    latencies = [float(row["latency_ms"]) for row in macro_rows]
    tokens = [
        int(row["input_tokens"])
        for row in macro_rows
        if row.get("input_tokens") is not None
    ]
    goals = {}
    for seed in range(args.start_seed, seed_end):
        seed_rows = [row for row in macro_rows if row["seed"] == seed]
        goals[str(seed)] = bool(
            seed_rows and seed_rows[-1]["after"]["location"] != START_LOCATION
        )
    receipt = {
        "key_status": "OK",
        "model": MODEL,
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "seeds": seed_end - args.start_seed,
        "seed_start": args.start_seed,
        "seed_end": seed_end,
        "macro_cap": args.cap,
        "requests": len(macro_rows),
        "goals_reached": sum(goals.values()),
        "goal_by_seed": goals,
        "input_tokens": {
            "reported_rows": len(tokens),
            "total": sum(tokens),
            "p50": median(tokens) if tokens else None,
            "p95": _percentile(tokens, 0.95) if tokens else None,
        },
        "latency_ms": {
            "p50": median(latencies) if latencies else None,
            "p95": _percentile(latencies, 0.95) if latencies else None,
            "max": max(latencies) if latencies else None,
        },
        "estimated_input_cost_usd": sum(tokens) * 0.042 / 1_000_000 if tokens else None,
        "wall_time_s": round(time.monotonic() - started, 3),
        "rom_mount": "read-only",
        "screenshots_committed": False,
        "save_states_committed": False,
    }
    receipt_path.write_text(
        "# Emerald live segment receipt\n\n```json\n"
        + json.dumps(receipt, indent=2)
        + "\n```\n"
    )
    print(json.dumps(receipt, sort_keys=True), flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--output")
    parser.add_argument("--receipt")
    parser.add_argument("--scratch")
    parser.add_argument("--seeds", type=int, default=80)
    parser.add_argument("--cap", type=int, default=500)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--start-seed", type=int, default=0)
    parser.add_argument("--end-seed", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--seed-output")
    args = parser.parse_args()
    if args.worker:
        if args.seed is None or not args.seed_output:
            parser.error("--worker requires --seed and --seed-output")
        return worker(args)
    if not args.output or not args.receipt or not args.scratch:
        parser.error("parent mode requires --output, --receipt, and --scratch")
    return parent(args)


if __name__ == "__main__":
    raise SystemExit(main())
