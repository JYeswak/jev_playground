from __future__ import annotations

import json
import math
import os
import pwd
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Callable

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from fleet_surface_telemetry import (
    HISTORY_SECONDS,
    Assessment,
    HeartbeatError,
    RateInterval,
    Surface,
    Telemetry,
    assess_surface,
    load_registry,
    read_jsonl,
    scan_omp_sessions,
)

HOUR = 3600
STATE_NAME = "fleet-surface-heartbeat-state.json"
EVENTS_NAME = "fleet-surface-heartbeat.jsonl"
LIVENESS_NAME = "fleet-watch-liveness.jsonl"
DRY_RUN = False
DRY_RUN_SENDS: list[tuple[int, str]] = []


def _under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _guard_write(path: Path) -> None:
    if DRY_RUN and (not dry_run_home_is_isolated() or not _under(path, Path.home())):
        raise HeartbeatError(f"dry-run write outside isolated HOME refused: {path}")


def switch_is_on(surface: Surface) -> bool | None:
    if surface.switch_path is None or surface.switch_polarity is None:
        return None
    exists = surface.switch_path.exists()
    return exists if surface.switch_polarity == "presence-ON" else not exists


def _set_switch(surface: Surface, *, on: bool, reason: str) -> bool:
    path, polarity = surface.switch_path, surface.switch_polarity
    if on and surface.operator_off_path is not None and surface.operator_off_path.exists():
        return False
    if path is None or polarity is None or switch_is_on(surface) == on:
        return False
    _guard_write(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if polarity == "presence-ON":
        if on:
            path.write_text("enabled by healthy log-only probe\n", encoding="utf-8")
        else:
            path.unlink()
    elif on:
        path.unlink(missing_ok=True)
    else:
        path.write_text(f"fleet heartbeat auto-off: {reason}\n", encoding="utf-8")
    return True


def _state_path(state_dir: Path) -> Path:
    return state_dir / STATE_NAME


def load_state(state_dir: Path) -> dict:
    try:
        state = json.loads(_state_path(state_dir).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {
            "schema_version": "fleet-surface-heartbeat-state.v1",
            "surfaces": {},
            "probes": {},
        }
    except (OSError, ValueError) as error:
        raise HeartbeatError(
            f"cannot read heartbeat state: {type(error).__name__}"
        ) from error
    if (
        not isinstance(state, dict)
        or state.get("schema_version") != "fleet-surface-heartbeat-state.v1"
        or not isinstance(state.get("surfaces"), dict)
        or not isinstance(state.get("probes"), dict)
    ):
        raise HeartbeatError("unsupported or malformed heartbeat state")
    return state


def save_state(state_dir: Path, state: dict) -> None:
    _guard_write(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    path = _state_path(state_dir)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(state, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _append_event(state_dir: Path, row: dict) -> None:
    _guard_write(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    record = {"schema_version": "fleet-surface-heartbeat.v1", **row}
    with (state_dir / EVENTS_NAME).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def append_liveness(state_dir: Path, *, now: float, status: str) -> None:
    _guard_write(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    row = {
        "schema_version": "fleet-watch-liveness.v1",
        "ts": datetime.fromtimestamp(now, timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "pid": os.getpid(),
        "status": status,
    }
    with (state_dir / LIVENESS_NAME).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def record_dry_run_send(message: str, *, pane: int = 1) -> bool:
    if not DRY_RUN:
        return False
    DRY_RUN_SENDS.append((pane, message))
    return True


def start_restore_probe(
    surface: Surface, state_dir: Path, *, now: float, duration_seconds: int
) -> None:
    if duration_seconds <= 0 or duration_seconds > 24 * HOUR:
        raise HeartbeatError("probe duration must be between one second and 24 hours")
    if switch_is_on(surface) is not False:
        raise HeartbeatError(
            f"{surface.id}: restore probe requires the surface to be OFF"
        )
    state = load_state(state_dir)
    state["probes"][surface.id] = {
        "mode": "log-only",
        "started_at": now,
        "ends_at": now + duration_seconds,
        "status": "running",
    }
    save_state(state_dir, state)
    _append_event(
        state_dir,
        {
            "ts": now,
            "surface": surface.id,
            "action": "probe-started",
            "reason": "operator requested log-only window",
        },
    )


def _probe_result(
    surface: Surface,
    probe: dict,
    *,
    now: float,
    host_events: list[float],
    telemetry: Telemetry,
    baseline: RateInterval | None,
) -> tuple[str, str]:
    if now < probe.get("ends_at", math.inf):
        return "pending", "log-only probe window is still running"
    if not telemetry.available:
        return "failed", "probe telemetry unavailable"
    if telemetry.invalid_rows:
        return (
            "failed",
            f"probe contains {telemetry.invalid_rows} invalid telemetry row(s)",
        )
    start, end = probe.get("started_at"), probe.get("ends_at")
    if (
        not isinstance(start, (int, float))
        or not isinstance(end, (int, float))
        or baseline is None
    ):
        return "failed", "probe has no valid seven-day baseline"
    events = sum(start <= stamp < end for stamp in host_events)
    rows, errors = telemetry.counts(start, end)
    rate = rows / events if events else None
    healthy = (
        events > 0
        and rows > 0
        and rate is not None
        and baseline.lower <= rate <= baseline.upper
        and errors < surface.minimum_error_rows
        and errors / rows <= surface.error_rate_ceiling
    )
    if not healthy:
        return (
            "failed",
            f"probe outside baseline or error ceiling ({rows}/{events} rows/events, {errors} errors)",
        )
    return "restored", "healthy log-only probe within seven-day CI"


def finish_restore_probe(
    surface: Surface,
    state: dict,
    state_dir: Path,
    *,
    now: float,
    host_events: list[float],
    telemetry: Telemetry,
    baseline: RateInterval | None,
    send: Callable[[str], bool],
) -> str:
    probe = state.get("probes", {}).get(surface.id)
    if not isinstance(probe, dict) or probe.get("mode") != "log-only":
        return "none"
    if probe.get("status") in {"restored", "failed"}:
        return "complete"
    result, reason = _probe_result(
        surface,
        probe,
        now=now,
        host_events=host_events,
        telemetry=telemetry,
        baseline=baseline,
    )
    if result == "pending":
        return result
    if result == "restored":
        record = state.get("surfaces", {}).get(surface.id, {})
        if not isinstance(record, dict) or record.get("auto_off") is not True:
            result, reason = "failed", "OFF state is not owned by heartbeat"
        elif surface.operator_off_path is not None and surface.operator_off_path.exists():
            result, reason = "failed", "operator OFF marker is present"
        elif surface.switch_polarity == "presence-OFF" and surface.switch_path is not None:
            try:
                marker_text = surface.switch_path.read_text(encoding="utf-8")
            except OSError:
                marker_text = ""
            if not marker_text.startswith("fleet heartbeat auto-off: "):
                result, reason = "failed", "operator OFF marker is present"
    if result == "restored" and not _set_switch(surface, on=True, reason=reason):
        result, reason = "failed", "operator OFF marker or switch state prevented restoration"
    probe["status"] = result
    probe["reason"] = reason
    if result == "restored":
        probe["restored_at"] = now
        record = state.setdefault("surfaces", {}).setdefault(surface.id, {})
        record.update(
            {"state": "healthy", "reason": reason, "updated_at": now, "auto_off": False}
        )
        send(f"SURFACE RESTORED {surface.id} owner={surface.owner}: {reason}")
        action = "restored"
    else:
        send(f"SURFACE RESTORE BLOCKED {surface.id} owner={surface.owner}: {reason}")
        action = "probe-kept-off"
    _append_event(
        state_dir,
        {"ts": now, "surface": surface.id, "action": action, "reason": reason},
    )
    return result


def _read_surface_telemetry(
    surface: Surface, start: float, end: float, session_telemetry: dict[str, Telemetry]
) -> Telemetry:
    if surface.source == "jsonl":
        if surface.path is None:
            return Telemetry(available=False)
        return read_jsonl(surface.path, surface, start, end)
    if not surface.custom_types:
        return Telemetry(available=False)
    combined = Telemetry()
    for custom_type in surface.custom_types:
        source = session_telemetry.get(custom_type)
        if source is not None:
            combined.observations.extend(source.observations)
            combined.invalid_rows += source.invalid_rows
            combined.available = combined.available and source.available
    return combined


def monitor(
    registry_path: Path,
    state_dir: Path,
    *,
    now: float,
    omp_root: Path,
    send: Callable[[str], bool],
) -> list[Assessment]:
    surfaces = load_registry(registry_path)
    current_end = int(now // HOUR) * HOUR
    current_start = current_end - HOUR
    history_start = current_start - HISTORY_SECONDS
    if DRY_RUN and not dry_run_targets_are_isolated(registry_path, state_dir):
        raise HeartbeatError("dry-run targets are not isolated under scratch HOME")
    custom_types = {custom for surface in surfaces for custom in surface.custom_types}
    host_events, session_telemetry, session_available = scan_omp_sessions(
        omp_root, history_start, now, custom_types, surfaces
    )
    state = load_state(state_dir)
    assessments = []
    for surface in surfaces:
        telemetry = _read_surface_telemetry(
            surface, history_start, now, session_telemetry
        )
        if surface.source == "omp_session" and not session_available:
            telemetry.available = False
        events = host_events.get(surface.id, host_events.get(surface.event_kind, []))
        assessment = assess_surface(
            surface, events, telemetry, history_start, current_start, current_end
        )
        assessments.append(assessment)
        probe_status = finish_restore_probe(
            surface,
            state,
            state_dir,
            now=now,
            host_events=events,
            telemetry=telemetry,
            baseline=assessment.interval,
            send=send,
        )
        if probe_status in {"restored", "failed"}:
            continue
        record = state.setdefault("surfaces", {}).setdefault(surface.id, {})
        prior_state = record.get("state")
        record.update(
            {
                "state": assessment.state,
                "reason": assessment.reason,
                "updated_at": now,
                "host_events": assessment.host_events,
                "rows": assessment.rows,
                "errors": assessment.errors,
                "rate": assessment.rate,
                "ci": None
                if assessment.interval is None
                else [assessment.interval.lower, assessment.interval.upper],
                "invalid_rows": telemetry.invalid_rows,
            }
        )
        switched = False
        if assessment.unhealthy:
            if switch_is_on(surface) is True:
                switched = _set_switch(surface, on=False, reason=assessment.reason)
                record["auto_off"] = switched
            elif switch_is_on(surface) is None:
                record["auto_off"] = False
            if prior_state != assessment.state or switched:
                send(
                    f"SURFACE ANOMALY {surface.id} owner={surface.owner}: "
                    f"{assessment.state}; {assessment.reason}"
                )
        elif (
            assessment.state == "baseline-unavailable"
            and prior_state != assessment.state
        ):
            send(
                f"SURFACE UNMEASURED {surface.id} owner={surface.owner}: "
                f"{assessment.reason}; staying on"
            )
        if prior_state != assessment.state or switched:
            action = (
                "off" if switched else "alert" if assessment.unhealthy else "observe"
            )
            _append_event(
                state_dir,
                {
                    "ts": now,
                    "surface": surface.id,
                    "state": assessment.state,
                    "reason": assessment.reason,
                    "action": action,
                    "polarity": surface.switch_polarity,
                },
            )
    save_state(state_dir, state)
    return assessments


def dry_run_home_is_isolated(home: Path | None = None) -> bool:
    requested = (home or Path.home()).resolve()
    actual = Path(pwd.getpwuid(os.getuid()).pw_dir).resolve()
    raw_tmp = os.environ.get("TMPDIR")
    if requested == actual or not raw_tmp:
        return False
    try:
        requested.relative_to(Path(raw_tmp).resolve())
    except ValueError:
        return False
    return True


def dry_run_targets_are_isolated(registry_path: Path, state_dir: Path) -> bool:
    if not dry_run_home_is_isolated() or not _under(state_dir, Path.home()):
        return False
    try:
        surfaces = load_registry(registry_path)
    except HeartbeatError:
        return False
    return all(
        (surface.path is None or _under(surface.path, Path.home()))
        and (surface.switch_path is None or _under(surface.switch_path, Path.home()))
        and (
            surface.operator_off_path is None
            or _under(surface.operator_off_path, Path.home())
        )
        for surface in surfaces
    )


def real_omp_root() -> Path:
    explicit = os.environ.get("JEV_OMP_ROOT")
    if explicit:
        return Path(explicit).expanduser()
    return Path(pwd.getpwuid(os.getuid()).pw_dir) / ".omp"


def resolve_state_dir() -> Path:
    return Path(
        os.environ.get("JEV_FLEET_STATE_DIR", "~/.local/state/jev")
    ).expanduser()
