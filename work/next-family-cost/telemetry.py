"""Attribute agent and Jev usage records to classifier-family bead IDs."""

from __future__ import annotations

import json
import math
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

HOME = Path.home()
STATE = HOME / ".local" / "state" / "jev"
JEV_INPUT_USD_PER_MILLION = 0.042


def _bead_ids(text: str) -> list[str]:
    found: set[str] = set()
    for index in range(len(text) - 3):
        if text[index : index + 4] != "jev-":
            continue
        if index and (text[index - 1].isalnum() or text[index - 1] in "-_"):
            continue
        end = index + 4
        while (
            end < len(text)
            and text[end].isascii()
            and (text[end].islower() or text[end].isdigit() or text[end] == "-")
        ):
            end += 1
        base_end = end
        if end + 1 < len(text) and text[end] == "." and text[end + 1].isdigit():
            end += 1
            while end < len(text) and text[end].isdigit():
                end += 1
            if end + 1 < len(text) and text[end] == "." and text[end + 1].isdigit():
                continue
        components = text[index + 4 : base_end].split("-")
        if len(components[-1]) != 4 or any(
            not component
            or any(
                not character.isascii()
                or not (character.islower() or character.isdigit())
                for character in component
            )
            for component in components
        ):
            continue
        if end < len(text) and (text[end].isalnum() or text[end] in "-_"):
            continue
        found.add(text[index:end])
    return sorted(found)


class MeasurementError(ValueError):
    """Required cost evidence is missing, malformed, or out of order."""


def _valid_cost(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


@contextmanager
def _open_log(path: Path, label: str) -> Iterator[TextIO]:
    try:
        with path.open(encoding="utf-8") as source:
            yield source
    except (OSError, UnicodeError) as exc:
        raise MeasurementError(f"cannot read {label} {path}: {exc}") from exc


def _instant(value: object, where: str) -> datetime:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            raise MeasurementError(f"invalid timestamp in {where}")
        try:
            return datetime.fromtimestamp(value, timezone.utc)
        except (OverflowError, OSError, ValueError) as exc:
            raise MeasurementError(f"invalid timestamp in {where}") from exc
    if not isinstance(value, str):
        raise MeasurementError(f"missing timestamp in {where}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MeasurementError(f"invalid timestamp in {where}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MeasurementError(f"timestamp lacks timezone in {where}")
    return parsed.astimezone(timezone.utc)


def _session_files(home: Path = HOME) -> list[Path]:
    roots = [home / ".omp" / "agent" / "sessions"]
    profiles = home / ".omp" / "profiles"
    if profiles.is_dir():
        roots.extend(
            profile / "agent" / "sessions"
            for profile in profiles.iterdir()
            if profile.is_dir()
        )
    return sorted(
        {file for base in roots if base.is_dir() for file in base.glob("*/*.jsonl")}
    )


def session_metrics(
    beads: list[str],
    start_epoch: int,
    end_epoch: int,
    *,
    root: Path,
    home: Path = HOME,
    state: Path = STATE,
) -> tuple[int, int, float, list[str]]:
    bead_ids = set(beads)
    project_root = str(root.resolve())
    matching_ids: set[str] = set()
    turns = 0
    calls = 0
    spend = 0.0
    source_paths: set[str] = set()
    usage_keys: set[tuple[str, str, str]] = set()

    for path in _session_files(home):
        try:
            if path.stat().st_mtime < start_epoch:
                continue
        except OSError as exc:
            raise MeasurementError(f"cannot stat session log {path}: {exc}") from exc
        with _open_log(path, "session log") as source:
            session_id = None
            session_ok = False
            active_family_work = False
            session_turns = session_calls = 0
            session_spend = 0.0
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                if session_id is None:
                    if (
                        '"type": "session"' not in line
                        and '"type":"session"' not in line
                    ):
                        continue
                    try:
                        header = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise MeasurementError(
                            f"invalid session header at {path}:{line_number}"
                        ) from exc
                    if not isinstance(header, dict):
                        raise MeasurementError(
                            f"invalid session header at {path}:{line_number}"
                        )
                    if header.get("cwd") != project_root:
                        break
                    session_id = header.get("id")
                    if not isinstance(session_id, str) or not session_id:
                        raise MeasurementError(
                            f"session id missing at {path}:{line_number}"
                        )
                    stamp = int(
                        _instant(header.get("timestamp"), str(path)).timestamp()
                    )
                    if stamp > end_epoch:
                        break
                    session_ok = True
                    continue
                if not session_ok:
                    continue
                if '"jev-' in line:
                    line_beads = set(_bead_ids(line))
                    if line_beads:
                        active_family_work = bool(bead_ids.intersection(line_beads))
                if '"model_usage"' not in line and '"final_answer"' not in line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise MeasurementError(
                        f"invalid cost event at {path}:{line_number}"
                    ) from exc
                if not isinstance(row, dict):
                    raise MeasurementError(
                        f"invalid cost event at {path}:{line_number}"
                    )
                stamp = int(
                    _instant(row.get("timestamp"), f"{path}:{line_number}").timestamp()
                )
                if not (start_epoch <= stamp <= end_epoch):
                    continue
                if row.get("type") == "message":
                    message = row.get("message")
                    text_metadata = (
                        message.get("textSignature")
                        if isinstance(message, dict)
                        else None
                    )
                    if (
                        active_family_work
                        and isinstance(text_metadata, dict)
                        and text_metadata.get("phase") == "final_answer"
                    ):
                        session_turns += 1
                elif row.get("type") == "model_usage":
                    if not active_family_work:
                        continue
                    usage = row.get("usage")
                    cost = usage.get("cost") if isinstance(usage, dict) else None
                    total = cost.get("total") if isinstance(cost, dict) else None
                    if not _valid_cost(total):
                        raise MeasurementError(
                            f"model_usage lacks valid cost.total at {path}:{line_number}"
                        )
                    model = row.get("model")
                    if not isinstance(model, str) or not model:
                        raise MeasurementError(
                            f"model_usage lacks model at {path}:{line_number}"
                        )
                    session_calls += 1
                    session_spend += float(total)
                    usage_keys.add((session_id, str(row["timestamp"]), model))
            if session_id and session_ok and (session_turns or session_calls):
                matching_ids.add(session_id)
                turns += session_turns
                calls += session_calls
                spend += session_spend
                source_paths.add(str(path))

    if not matching_ids:
        raise MeasurementError(
            "no attributable omp session logs contain the family bead IDs in the measurement window"
        )

    for path in sorted(state.glob("*.jsonl")) if state.is_dir() else []:
        with _open_log(path, "Jev call log") as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip() or not any(
                    session_id in line for session_id in matching_ids
                ):
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise MeasurementError(
                        f"invalid Jev call log row at {path}:{line_number}"
                    ) from exc
                if not isinstance(row, dict):
                    raise MeasurementError(
                        f"invalid Jev call log row at {path}:{line_number}"
                    )
                session_id = row.get(
                    "session", row.get("sessionId", row.get("session_id"))
                )
                model = row.get("model")
                stamp_value = row.get("ts", row.get("timestamp"))
                if not isinstance(session_id, str) or session_id not in matching_ids:
                    continue
                if not isinstance(model, str) or stamp_value is None:
                    continue
                stamp_text = str(stamp_value)
                stamp = int(_instant(stamp_value, f"{path}:{line_number}").timestamp())
                if not (start_epoch <= stamp <= end_epoch):
                    continue
                if (session_id, stamp_text, model) in usage_keys:
                    continue
                status = row.get("status")
                if isinstance(status, str) and status in {
                    "skipped",
                    "cached",
                    "off",
                    "disabled",
                }:
                    continue
                tokens = row.get("tokens")
                input_tokens = (
                    tokens.get("input_tokens")
                    if isinstance(tokens, dict)
                    else row.get("input_tokens")
                )
                if model == "jev-1.13.0":
                    if (
                        isinstance(input_tokens, bool)
                        or not isinstance(input_tokens, int)
                        or input_tokens < 0
                    ):
                        raise MeasurementError(
                            f"Jev call log lacks input_tokens at {path}:{line_number}"
                        )
                    try:
                        cost = input_tokens * JEV_INPUT_USD_PER_MILLION / 1_000_000
                    except OverflowError as exc:
                        raise MeasurementError(
                            f"invalid input_tokens at {path}:{line_number}"
                        ) from exc
                elif model.lower().startswith(("ollama", "nimble", "tev")):
                    cost = 0.0
                elif isinstance(row.get("usage"), dict) and isinstance(
                    row["usage"].get("cost"), dict
                ):
                    cost = row["usage"]["cost"].get("total")
                    if not _valid_cost(cost):
                        raise MeasurementError(
                            f"invalid recorded cost at {path}:{line_number}"
                        )
                else:
                    raise MeasurementError(
                        f"unknown model cost schedule for {model} at {path}:{line_number}"
                    )
                calls += 1
                spend += cost
                source_paths.add(f"{path}:{line_number}")

    if calls == 0:
        raise MeasurementError(
            "no attributable model-call spend rows; zero spend is not assumed"
        )
    if turns == 0:
        raise MeasurementError(
            "no completed assistant turns are attributable to family work"
        )
    if not math.isfinite(spend):
        raise MeasurementError("attributable spend total is not finite")
    return turns, calls, spend, sorted(source_paths)
