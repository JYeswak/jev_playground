"""Build the exact typed Choice request and keyless budget for one Emerald macro."""

from __future__ import annotations

import json
import math
from statistics import median
from typing import Any, Iterable

MODEL = "jev-1.13.0"
LEGAL_INPUTS = (
    "A",
    "B",
    "START",
    "SELECT",
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    "L",
    "R",
    "WAIT",
)
REQUESTS_PER_MINUTE = 1_200
INPUT_PRICE_PER_MILLION = 0.042
DEFAULT_MACRO_RATE_HZ = 80 / 18


def _porymap_ascii(state_text: str) -> str | None:
    marker = "=== PORYMAP MAP LAYOUT ==="
    ascii_marker = "ASCII Map:\n"
    legend_marker = "\n(Legend:"
    start = state_text.find(marker)
    if start < 0:
        return None
    ascii_start = state_text.find(ascii_marker, start)
    if ascii_start < 0:
        return None
    ascii_start += len(ascii_marker)
    ascii_end = state_text.find(legend_marker, ascii_start)
    if ascii_end < 0:
        return None
    return state_text[ascii_start:ascii_end].strip()


def compact_state(row: dict[str, Any]) -> dict[str, Any]:
    """Return only the JSON projection sent for one macro; excludes state_text/images."""
    source = row.get("state", row)
    return {
        "visual": {"resolution": source.get("visual", {}).get("resolution")},
        "player": {
            "position": source.get("player", {}).get("position"),
            "location": source.get("player", {}).get("location"),
            "name": source.get("player", {}).get("name"),
            "party": source.get("player", {}).get("party"),
            "inventory": source.get("player", {}).get("inventory"),
        },
        "game": {
            "game_state": source.get("game", {}).get("game_state"),
            "is_in_battle": source.get("game", {}).get("is_in_battle"),
            "dialog_text": source.get("game", {}).get("dialog_text"),
            "dialogue_detected": source.get("game", {}).get("dialogue_detected"),
            "battle_info": source.get("game", {}).get("battle_info"),
            "money": source.get("game", {}).get("money"),
            "badges": source.get("game", {}).get("badges"),
            "time": source.get("game", {}).get("time"),
            "progress_context": source.get("game", {}).get("progress_context"),
        },
        "map": {"porymap_ascii": _porymap_ascii(row.get("state_text", ""))},
    }


def build_choice_request(row: dict[str, Any]) -> dict[str, Any]:
    """Build the exact no-network request envelope for one legal macro Choice."""
    criteria = {
        label: f"Press the {label} macro for one emulator decision."
        for label in LEGAL_INPUTS
    }
    return {
        "model": MODEL,
        "state": compact_state(row),
        "questions": {
            "macro": {
                "type": "choice",
                "instructions": "Choose exactly one legal Emerald input macro for the current screen.",
                "criteria": criteria,
            }
        },
    }


def _percentile(values: list[int], fraction: float) -> int | float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1)]


def estimate_budget(
    rows: Iterable[dict[str, Any]],
    macros: int,
    *,
    macro_rate_hz: float = DEFAULT_MACRO_RATE_HZ,
    requests_per_minute: int = REQUESTS_PER_MINUTE,
    input_price_per_million: float = INPUT_PRICE_PER_MILLION,
) -> dict[str, Any]:
    """Estimate time, request rate, tokens, and input cost without contacting Jev.

    Token count is explicitly a 4-bytes-per-token planning estimate, not a tokenizer
    measurement. The live prereg must record actual SDK usage separately.
    """
    if macros < 1:
        raise ValueError("macros must be positive")
    requests = [
        len(
            json.dumps(
                build_choice_request(row), ensure_ascii=False, separators=(",", ":")
            ).encode()
        )
        for row in rows
    ]
    if not requests:
        raise ValueError("rows must be non-empty")
    token_estimates = [math.ceil(size / 4) for size in requests]
    limit_hz = requests_per_minute / 60
    return {
        "macros": macros,
        "macro_rate_hz": macro_rate_hz,
        "request_limit_hz": limit_hz,
        "throttled": macro_rate_hz > limit_hz,
        "duration_s": macros / macro_rate_hz,
        "request_bytes": {"p50": median(requests), "p95": _percentile(requests, 0.95)},
        "estimated_input_tokens": {
            "method": "ceil(serialized_request_bytes / 4)",
            "p50": median(token_estimates),
            "p95": _percentile(token_estimates, 0.95),
        },
        "estimated_input_cost_usd": {
            "p50": macros
            * median(token_estimates)
            * input_price_per_million
            / 1_000_000,
            "p95": macros
            * _percentile(token_estimates, 0.95)
            * input_price_per_million
            / 1_000_000,
        },
    }
