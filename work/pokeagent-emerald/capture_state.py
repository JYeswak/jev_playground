#!/usr/bin/env python3
"""Capture compact per-macro Emerald state without an LLM.

The script runs inside the pinned continual-harness environment. It never writes
ROM bytes, save states, or screenshots to the output directory; screenshots go to
the caller-provided scratch directory.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import time
from importlib import import_module
from pathlib import Path
from typing import Any

# Fixed input sequence. The first section advances the title/intro; the repeated
# navigation pattern handles the name/menu screens without a model or feedback.
BOOT_MACROS: list[str] = ["START", "A"] + ["A"] * 160
BOOT_MACROS += [
    button for _ in range(35) for button in ("A", "DOWN", "A", "RIGHT", "A", "LEFT")
]
MOVEMENT_MACROS = ["RIGHT", "RIGHT", "DOWN", "DOWN", "LEFT", "LEFT", "UP", "UP"]
DIRECTION_BUTTONS = {"UP", "DOWN", "LEFT", "RIGHT"}


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return str(value)


def _compact_state(raw: dict[str, Any]) -> dict[str, Any]:
    visual = raw.get("visual", {})
    player = raw.get("player", {})
    game = raw.get("game", {})
    map_data = raw.get("map", {})
    return _jsonable(
        {
            "visual": {
                "resolution": visual.get("resolution"),
                "screenshot_present": visual.get("screenshot") is not None,
            },
            "player": {
                "position": player.get("position"),
                "location": player.get("location"),
                "name": player.get("name"),
                "party": player.get("party"),
                "inventory": player.get("inventory"),
            },
            "game": {
                "game_state": game.get("game_state"),
                "is_in_battle": game.get("is_in_battle"),
                "dialog_text": game.get("dialog_text"),
                "dialogue_detected": game.get("dialogue_detected"),
                "battle_info": game.get("battle_info"),
                "money": game.get("money"),
                "badges": game.get("badges"),
                "time": game.get("time"),
                "progress_context": game.get("progress_context"),
            },
            "map": {
                "visual_map": map_data.get("visual_map"),
                "object_events": map_data.get("object_events"),
                "stitched_map_info": map_data.get("stitched_map_info"),
            },
        }
    )


def _state_text(raw: dict[str, Any]) -> tuple[str, str | None]:
    try:
        format_state_for_llm = import_module(
            "utils.state_formatter"
        ).format_state_for_llm

        return format_state_for_llm(raw), None
    except (
        Exception
    ) as exc:  # state capture remains useful when optional formatting fails
        return "", f"{type(exc).__name__}: {exc}"


def _state_value(row: dict[str, Any], path: str) -> Any:
    value: Any = row
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    sizes = [int(row["state_bytes"]) for row in rows]
    fields = [
        "visual.resolution",
        "visual.screenshot_present",
        "player.position",
        "player.location",
        "player.name",
        "player.party",
        "player.inventory",
        "game.game_state",
        "game.is_in_battle",
        "game.dialog_text",
        "game.dialogue_detected",
        "game.battle_info",
        "game.money",
        "game.badges",
        "game.time",
        "game.progress_context",
        "map.visual_map",
        "map.object_events",
        "map.stitched_map_info",
        "state_text",
    ]
    field_stats = {}
    for field in fields:
        values = [
            row.get("state_text")
            if field == "state_text"
            else _state_value(row["state"], field)
            for row in rows
        ]
        encoded = [
            json.dumps(v, sort_keys=True, separators=(",", ":"), default=str)
            for v in values
        ]
        field_stats[field] = {
            "empty_rows": sum(v in (None, "", [], {}) for v in values),
            "unique_values": len(set(encoded)),
            "constant": len(set(encoded)) <= 1,
        }
    return {
        "state_bytes": {
            "count": len(sizes),
            "p50": statistics.median(sizes),
            "p95": sizes[min(len(sizes) - 1, math.ceil(len(sizes) * 0.95) - 1)],
            "min": min(sizes),
            "max": max(sizes),
        },
        "fields": field_stats,
    }


def _is_overworld(row: dict[str, Any]) -> bool:
    state = row["state"]
    game = state.get("game", {})
    player = state.get("player", {})
    return game.get("game_state") == "overworld" and player.get("location") not in (
        None,
        "Unknown",
        "TITLE_SEQUENCE",
    )


def _capture_state(
    env: Any, macro_index: int, button: str, started: float
) -> dict[str, Any]:
    raw = env.get_comprehensive_state(screenshot=None)
    state_text, state_text_error = _state_text(raw)
    compact = _compact_state(raw)
    row = {
        "macro_index": macro_index,
        "button": button,
        "wall_s": round(time.monotonic() - started, 6),
        "state": compact,
        "state_text": state_text,
        "state_text_error": state_text_error,
    }
    row["state_bytes"] = len(
        json.dumps(
            row, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    )
    return row


def _run_macro(env: Any, button: str) -> None:
    if button == "WAIT":
        env.tick(18)
    else:
        env.press_buttons([button], hold_frames=10, release_frames=8)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--scratch", required=True)
    parser.add_argument("--harness-sha", required=True)
    parser.add_argument("--rom-sha1", required=True)
    parser.add_argument("--image-digest", required=True)
    args = parser.parse_args()

    EmeraldEmulator = import_module("pokemon_env.emulator").EmeraldEmulator

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    scratch = Path(args.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    if not os.access(args.rom, os.R_OK):
        raise SystemExit(f"ROM is not readable: {args.rom}")

    started = time.monotonic()
    env = EmeraldEmulator(args.rom, headless=True, sound=False)
    env.initialize()
    rows: list[dict[str, Any]] = []
    script = BOOT_MACROS + MOVEMENT_MACROS
    found_overworld = False
    with output.open("w", encoding="utf-8") as handle:
        for index, button in enumerate(script):
            _run_macro(env, button)
            row = _capture_state(env, index, button, started)
            rows.append(row)
            handle.write(
                json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            )
            handle.flush()
            if (index + 1) % 50 == 0:
                screenshot = env.get_screenshot()
                screenshot.save(scratch / f"macro-{index + 1:04d}.png")
            if _is_overworld(row):
                found_overworld = True
                if index >= len(BOOT_MACROS) - 1:
                    break

    changes = []
    previous = None
    for row in rows:
        position = row["state"]["player"].get("position")
        if row["button"] in DIRECTION_BUTTONS and previous is not None:
            before = previous["state"]["player"].get("position")
            if before != position and before is not None and position is not None:
                changes.append(
                    {
                        "macro_index": row["macro_index"],
                        "button": row["button"],
                        "before": before,
                        "after": position,
                    }
                )
        previous = row

    receipt = {
        "image_digest": args.image_digest,
        "harness_sha": args.harness_sha,
        "rom_sha1": args.rom_sha1,
        "rom_mount": "read-only",
        "model_calls": 0,
        "macro_count": len(rows),
        "reached_controllable_overworld": found_overworld,
        "wall_time_s": round(time.monotonic() - started, 3),
        "state_stats": _stats(rows),
        "position_changes": changes[:2],
        "scratch_screenshots": str(scratch),
        "output_jsonl": str(output),
    }
    receipt_path = output.parent.parent / "RECEIPT.md"
    with receipt_path.open("w", encoding="utf-8") as handle:
        handle.write("# Emerald keyless state receipt\n\n")
        handle.write("```json\n")
        json.dump(receipt, handle, indent=2, ensure_ascii=False)
        handle.write("\n```\n")
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if found_overworld and len(changes) >= 2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
