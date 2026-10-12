from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

HOUR = 3600
HISTORY_HOURS = 7 * 24
HISTORY_SECONDS = HISTORY_HOURS * HOUR
ERROR_STATUSES = frozenset({"error", "failed", "failure", "timeout", "invalid"})


class HeartbeatError(ValueError):
    pass


@dataclass(frozen=True)
class Surface:
    id: str
    owner: str
    event_kind: str
    source: str
    path: Path | None
    timestamp_field: str
    status_field: str | None
    error_field: str | None
    error_statuses: frozenset[str]
    surface_field: str | None
    surface_value: str | None
    custom_types: tuple[str, ...]
    error_rate_ceiling: float
    minimum_error_rows: int
    switch_path: Path | None
    switch_polarity: str | None
    eligible_tool_names: frozenset[str] = frozenset()
    exclude_cwd_roots: tuple[Path, ...] = ()
    paused_statuses: frozenset[str] = frozenset()
    operator_off_path: Path | None = None
    # None means undeclared scope, never all profiles. "default" is omp_root/agent.
    eligible_profiles: frozenset[str] | None = None


class _ScopedEvents(list[float]):
    """List-compatible samples with explicit session-file coverage."""

    def __init__(self) -> None:
        super().__init__()
        self.scope_covered = False


@dataclass(frozen=True)
class Observation:
    timestamp: float
    error: bool
    status: str | None = None

@dataclass
class Telemetry:
    observations: list[Observation] = field(default_factory=list)
    invalid_rows: int = 0
    available: bool = True

    def add(
        self, timestamp: float, is_error: bool, status: str | None = None
    ) -> None:
        self.observations.append(Observation(timestamp, is_error, status))

    def counts(self, start: float, end: float) -> tuple[int, int]:
        rows = errors = 0
        for row in self.observations:
            if start <= row.timestamp < end:
                rows += 1
                errors += row.error
        return rows, errors


@dataclass(frozen=True)
class RateInterval:
    lower: float
    upper: float
    active_hours: int


@dataclass(frozen=True)
class Assessment:
    surface_id: str
    state: str
    reason: str
    host_events: int
    rows: int
    errors: int
    rate: float | None
    interval: RateInterval | None

    @property
    def unhealthy(self) -> bool:
        return self.state in {
            "silent",
            "stale-telemetry",
            "telemetry-unavailable",
            "invalid-telemetry",
            "error-rate",
            "unexpected-volume",
        }


def parse_timestamp(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        stamp = float(value)
        if not math.isfinite(stamp):
            return None
        return stamp / 1000 if stamp > 100_000_000_000 else stamp
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    stamp = parsed.timestamp()
    return stamp if math.isfinite(stamp) else None


def load_registry(path: Path) -> list[Surface]:
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise HeartbeatError(
            f"cannot read surface registry: {type(error).__name__}"
        ) from error
    if (
        not isinstance(registry, dict)
        or registry.get("schema_version") != "blast-radius-surfaces.v1"
    ):
        raise HeartbeatError("unsupported surface registry schema")
    entries = registry.get("surfaces")
    if not isinstance(entries, list):
        raise HeartbeatError("surface registry has no surfaces array")

    result: list[Surface] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise HeartbeatError("surface registry entry must be an object")
        surface_id = entry.get("id")
        if not isinstance(surface_id, str) or not surface_id or surface_id in seen:
            raise HeartbeatError("surface registry has a missing or duplicate id")
        seen.add(surface_id)
        if surface_id == "injection-global-retired-noop":
            continue
        owner = entry.get("owner")
        if not isinstance(owner, str) or not owner.strip():
            raise HeartbeatError(f"{surface_id}: live surface has no owner")
        heartbeat = entry.get("heartbeat")
        if heartbeat is None and entry.get("telemetry") == "none":
            result.append(
                Surface(
                    id=surface_id,
                    owner=owner,
                    event_kind="",
                    source="none",
                    path=None,
                    timestamp_field="ts",
                    status_field=None,
                    error_field=None,
                    error_statuses=ERROR_STATUSES,
                    surface_field=None,
                    surface_value=None,
                    custom_types=(),
                    error_rate_ceiling=1.0,
                    minimum_error_rows=1,
                    switch_path=None,
                    switch_polarity=None,
                )
            )
            continue
        if not isinstance(heartbeat, dict):
            raise HeartbeatError(
                f"{surface_id}: live surface has no heartbeat configuration"
            )
        source = heartbeat.get("source")
        event_kind = heartbeat.get("eligible_event")
        log_path = heartbeat.get("path")
        if source not in {"jsonl", "omp_session"} or not isinstance(event_kind, str):
            raise HeartbeatError(
                f"{surface_id}: invalid heartbeat source or eligible event"
            )
        if source == "jsonl" and not isinstance(log_path, str):
            raise HeartbeatError(f"{surface_id}: JSONL telemetry path is required")
        status_field = heartbeat.get("status_field", "status")
        error_field = heartbeat.get("error_field")
        surface_field = heartbeat.get("surface_field")
        surface_value = heartbeat.get("surface_value")
        if status_field is not None and not isinstance(status_field, str):
            raise HeartbeatError(f"{surface_id}: status_field must be a string or null")
        if error_field is not None and not isinstance(error_field, str):
            raise HeartbeatError(f"{surface_id}: error_field must be a string or null")
        if surface_field is not None and not isinstance(surface_field, str):
            raise HeartbeatError(
                f"{surface_id}: surface_field must be a string or null"
            )
        if surface_field is not None and not isinstance(surface_value, str):
            raise HeartbeatError(
                f"{surface_id}: surface_value is required with surface_field"
            )
        off_switch = entry.get("off_switch")
        switch_path = None
        switch_polarity = None
        if off_switch is not None:
            if not isinstance(off_switch, dict):
                raise HeartbeatError(f"{surface_id}: invalid off-switch declaration")
            raw_switch = off_switch.get("path")
            switch_polarity = off_switch.get("polarity")
            if not isinstance(raw_switch, str) or switch_polarity not in {
                "presence-ON",
                "presence-OFF",
            }:
                raise HeartbeatError(f"{surface_id}: invalid switch path or polarity")
            switch_path = Path(raw_switch).expanduser()
        raw_operator_off = entry.get("operator_off_marker")
        if raw_operator_off is not None and not isinstance(raw_operator_off, str):
            raise HeartbeatError(f"{surface_id}: operator_off_marker must be a path")
        operator_off_path = (
            Path(raw_operator_off).expanduser()
            if isinstance(raw_operator_off, str)
            else None
        )
        ceiling = heartbeat.get("error_rate_ceiling")
        minimum_errors = heartbeat.get("minimum_error_rows", 3)
        if (
            isinstance(ceiling, bool)
            or not isinstance(ceiling, (int, float))
            or not 0 <= ceiling <= 1
        ):
            raise HeartbeatError(f"{surface_id}: error-rate ceiling must be in [0, 1]")
        if (
            isinstance(minimum_errors, bool)
            or not isinstance(minimum_errors, int)
            or minimum_errors < 1
        ):
            raise HeartbeatError(f"{surface_id}: minimum_error_rows must be positive")
        statuses = heartbeat.get("error_statuses", [])
        custom_types = heartbeat.get("custom_types", [])
        if not isinstance(statuses, list) or not all(
            isinstance(item, str) for item in statuses
        ):
            raise HeartbeatError(f"{surface_id}: error_statuses must be strings")
        if not isinstance(custom_types, list) or not all(
            isinstance(item, str) for item in custom_types
        ):
            raise HeartbeatError(f"{surface_id}: custom_types must be strings")
        eligible_tools = heartbeat.get("eligible_tool_names", [])
        eligible_profiles = heartbeat.get("eligible_profiles")
        if "eligible_profiles" in heartbeat and (
            not isinstance(eligible_profiles, list)
            or not eligible_profiles
            or not all(
                isinstance(item, str)
                and item not in {".", ".."}
                and item
                and all(char.isascii() and (char.isalnum() or char in "-_.") for char in item)
                for item in eligible_profiles
            )
            or len(set(eligible_profiles)) != len(eligible_profiles)
        ):
            raise HeartbeatError(f"{surface_id}: eligible_profiles must be nonempty exact profile names")
        excluded_cwds = heartbeat.get("exclude_cwd_roots", [])
        paused_statuses = heartbeat.get("paused_statuses", [])
        if not isinstance(eligible_tools, list) or not all(
            isinstance(item, str) for item in eligible_tools
        ):
            raise HeartbeatError(f"{surface_id}: eligible_tool_names must be strings")
        if not isinstance(excluded_cwds, list) or not all(
            isinstance(item, str) for item in excluded_cwds
        ):
            raise HeartbeatError(f"{surface_id}: exclude_cwd_roots must be strings")
        if not isinstance(paused_statuses, list) or not all(
            isinstance(item, str) for item in paused_statuses
        ):
            raise HeartbeatError(f"{surface_id}: paused_statuses must be strings")
        result.append(
            Surface(
                id=surface_id,
                owner=owner,
                event_kind=event_kind,
                source=source,
                path=Path(log_path).expanduser() if isinstance(log_path, str) else None,
                timestamp_field=str(heartbeat.get("timestamp_field", "ts")),
                status_field=status_field,
                error_field=error_field,
                error_statuses=frozenset(item.casefold() for item in statuses)
                | ERROR_STATUSES,
                surface_field=surface_field,
                surface_value=surface_value,
                custom_types=tuple(custom_types),
                error_rate_ceiling=float(ceiling),
                minimum_error_rows=minimum_errors,
                switch_path=switch_path,
                switch_polarity=switch_polarity,
                eligible_tool_names=frozenset(eligible_tools),
                exclude_cwd_roots=tuple(Path(item).resolve() for item in excluded_cwds),
                paused_statuses=frozenset(item.casefold() for item in paused_statuses),
                operator_off_path=operator_off_path,
                eligible_profiles=frozenset(eligible_profiles) if eligible_profiles is not None else None,
            )
        )
    return result


def is_error(row: dict, surface: Surface) -> bool:
    status = row.get(surface.status_field) if surface.status_field else None
    if isinstance(status, str) and status.casefold() in surface.paused_statuses:
        return False
    if surface.error_field and row.get(surface.error_field) not in (None, False, "", 0):
        return True
    if not isinstance(status, str):
        return False
    normalized = status.casefold()
    return normalized in surface.error_statuses or normalized.endswith("_error")


def read_jsonl(path: Path, surface: Surface, start: float, end: float) -> Telemetry:
    telemetry = Telemetry()
    pause_timestamps: set[float] = set()
    try:
        handle = path.open(encoding="utf-8")
    except OSError:
        telemetry.available = False
        return telemetry
    with handle:
        for line in handle:
            try:
                row = json.loads(line)
            except ValueError:
                telemetry.invalid_rows += 1
                continue
            if not isinstance(row, dict):
                telemetry.invalid_rows += 1
                continue
            if (
                surface.surface_field
                and row.get(surface.surface_field) != surface.surface_value
            ):
                continue
            if surface.status_field and not isinstance(
                row.get(surface.status_field), str
            ):
                telemetry.invalid_rows += 1
                continue
            stamp = parse_timestamp(row.get(surface.timestamp_field))
            if stamp is None:
                telemetry.invalid_rows += 1
            elif start <= stamp < end:
                status = row.get(surface.status_field) if surface.status_field else None
                if (
                    isinstance(status, str)
                    and status.casefold() in surface.paused_statuses
                ):
                    # A pause is a state marker; duplicate rows at the same instant are one pause.
                    if stamp in pause_timestamps:
                        continue
                    pause_timestamps.add(stamp)
                telemetry.add(
                    stamp,
                    is_error(row, surface),
                    status,
                )
    return telemetry


def _session_files(omp_root: Path) -> list[Path]:
    agents = [omp_root / "agent"]
    profiles = omp_root / "profiles"
    try:
        agents.extend(profile / "agent" for profile in profiles.iterdir())
    except OSError:
        pass
    paths = []
    for agent in agents:
        try:
            paths.extend(
                path
                for path in (agent / "sessions").rglob("*.jsonl")
                if path.is_file()
            )
        except OSError:
            continue
    return paths


def scan_omp_sessions(
    omp_root: Path,
    start: float,
    end: float,
    custom_types: set[str],
    surfaces: tuple[Surface, ...] | list[Surface] = (),
) -> tuple[dict[str, list[float]], dict[str, Telemetry], bool]:
    host_events: dict[str, list[float]] = {
        "turn": [],
        "tool_result": [],
        "tool_call": [],
    }
    host_events.update({surface.id: _ScopedEvents() for surface in surfaces})
    custom_rows = {name: Telemetry() for name in custom_types}
    custom_scopes: dict[str, frozenset[str] | None] = {}
    for surface in surfaces:
        for name in surface.custom_types:
            if name in custom_scopes and custom_scopes[name] != surface.eligible_profiles:
                raise HeartbeatError(f"{name}: conflicting eligible_profiles for shared telemetry")
            custom_scopes[name] = surface.eligible_profiles
    files = _session_files(omp_root)
    if not omp_root.exists():
        return host_events, custom_rows, False
    for path in files:
        try:
            if path.stat().st_mtime < start:
                continue
            handle = path.open(encoding="utf-8")
        except OSError:
            continue
        profile = _session_profile(path, omp_root)
        eligible_surfaces = [
            surface for surface in surfaces
            if surface.eligible_profiles is not None and profile in surface.eligible_profiles
        ]
        for surface in eligible_surfaces:
            samples = host_events[surface.id]
            if isinstance(samples, _ScopedEvents):
                samples.scope_covered = True
        session_cwd: Path | None = None
        with handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(row, dict):
                    continue
                if row.get("type") == "session":
                    cwd = row.get("cwd")
                    session_cwd = Path(cwd).resolve() if isinstance(cwd, str) else None
                    continue
                event = _host_event(row, start, end)
                if event is not None:
                    kind, stamp, tool_name = event
                    host_events[kind].append(stamp)
                    for surface in eligible_surfaces:
                        if _surface_event_eligible(surface, kind, tool_name, session_cwd):
                            host_events[surface.id].append(stamp)
                if row.get("type") == "custom":
                    _count_custom_decision(row, profile, custom_rows, custom_scopes, start, end)
    return host_events, custom_rows, True


def _host_event(row: dict, start: float, end: float) -> tuple[str, float, object] | None:
    """Parse one eligible host event; decision rows are counted separately."""
    if row.get("type") == "message":
        message = row.get("message")
        if not isinstance(message, dict):
            return None
        role = message.get("role")
        if role == "user":
            kind = "turn"
        elif role == "toolResult" and message.get("isError") is not True:
            kind = "tool_result"
        else:
            return None
        tool_name = message.get("toolName")
    elif row.get("type") == "custom" and row.get("customType") == "tool_execution_start":
        kind = "tool_call"
        data = row.get("data")
        tool_name = data.get("toolName") if isinstance(data, dict) else None
    else:
        return None
    stamp = parse_timestamp(row.get("timestamp"))
    if stamp is None or not start <= stamp < end:
        return None
    return kind, stamp, tool_name


def _surface_event_eligible(
    surface: Surface, kind: str, tool_name: object, session_cwd: Path | None
) -> bool:
    """Qualify an event after the scanner establishes its profile scope."""
    if surface.event_kind != kind:
        return False
    if surface.eligible_tool_names and tool_name not in surface.eligible_tool_names:
        return False
    if surface.exclude_cwd_roots:
        if session_cwd is None:
            return False
        if any(_path_is_within(session_cwd, root) for root in surface.exclude_cwd_roots):
            return False
    return True


def _count_custom_decision(
    row: dict,
    profile: str | None,
    custom_rows: dict[str, Telemetry],
    custom_scopes: dict[str, frozenset[str] | None],
    start: float,
    end: float,
) -> None:
    custom_type = row.get("customType")
    if custom_type not in custom_rows:
        return
    if custom_type in custom_scopes:
        scope = custom_scopes[custom_type]
        if scope is None or profile not in scope:
            return
    telemetry = custom_rows[custom_type]
    data = row.get("data")
    if not isinstance(data, dict):
        telemetry.invalid_rows += 1
        return
    stamp = parse_timestamp(data.get("timestamp", row.get("timestamp")))
    if stamp is None:
        telemetry.invalid_rows += 1
    elif start <= stamp < end:
        telemetry.add(stamp, bool(data.get("error")), data.get("status"))



def _session_profile(path: Path, omp_root: Path) -> str | None:
    """Attribute only by the session file location, not titles or payload hints."""
    try:
        parts = path.resolve().relative_to(omp_root.resolve()).parts
    except ValueError:
        return None
    if len(parts) >= 3 and parts[:2] == ("agent", "sessions"):
        return "default"
    if len(parts) >= 5 and parts[0] == "profiles" and parts[2:4] == ("agent", "sessions"):
        return parts[1]
    return None


def _path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def fit_rate_interval(
    host_events: list[float], surface_rows: list[Observation], start: float, end: float
) -> RateInterval | None:
    if end - start < HISTORY_SECONDS:
        return None
    event_buckets: dict[int, int] = {}
    row_buckets: dict[int, int] = {}
    for stamp in host_events:
        if start <= stamp < end:
            bucket = int(stamp // HOUR) * HOUR
            event_buckets[bucket] = event_buckets.get(bucket, 0) + 1
    for row in surface_rows:
        if start <= row.timestamp < end:
            bucket = int(row.timestamp // HOUR) * HOUR
            row_buckets[bucket] = row_buckets.get(bucket, 0) + 1
    rates = [
        row_buckets.get(hour, 0) / count
        for hour, count in event_buckets.items()
        if count
    ]
    if len(rates) < 24:
        return None
    mean = statistics.mean(rates)
    margin = (
        0.0
        if len(rates) < 2
        else 1.96 * statistics.stdev(rates) / math.sqrt(len(rates))
    )
    return RateInterval(max(0.0, mean - margin), mean + margin, len(rates))


def assess_surface(
    surface: Surface,
    host_events: list[float],
    telemetry: Telemetry,
    history_start: float,
    current_start: float,
    current_end: float,
) -> Assessment:
    events = sum(current_start <= stamp < current_end for stamp in host_events)
    rows, errors = telemetry.counts(current_start, current_end)
    if surface.source != "none" and (
        surface.eligible_profiles is None
        or isinstance(host_events, _ScopedEvents) and not host_events.scope_covered
    ):
        return Assessment(
            surface.id, "unknown", "eligible profile scope is undeclared or uncovered by readable session files",
            events, rows, errors, None, None
        )
    interval = fit_rate_interval(
        host_events, telemetry.observations, history_start, current_start
    )
    rate = rows / events if events else None
    if surface.source == "none":
        return Assessment(
            surface.id, "unmeasurable", "surface has no telemetry source", events,
            rows, errors, rate, interval
        )
    if rate is None:
        return Assessment(
            surface.id,
            "idle",
            "no eligible host traffic",
            0,
            rows,
            errors,
            None,
            interval,
        )
    if not telemetry.available:
        return Assessment(
            surface.id,
            "telemetry-unavailable",
            "telemetry log is missing or unreadable",
            events,
            rows,
            errors,
            rate,
            interval,
        )
    if telemetry.invalid_rows:
        reason = f"{telemetry.invalid_rows} invalid telemetry row(s)"
        return Assessment(
            surface.id,
            "invalid-telemetry",
            reason,
            events,
            rows,
            errors,
            rate,
            interval,
        )
    current_rows = [
        row
        for row in telemetry.observations
        if current_start <= row.timestamp < current_end
    ]
    if (
        current_rows
        and current_rows[-1].status is not None
        and current_rows[-1].status.casefold() in surface.paused_statuses
    ):
        return Assessment(
            surface.id,
            "paused",
            f"latest telemetry status is {current_rows[-1].status}",
            events,
            rows,
            errors,
            rate,
            interval,
        )
    if rows == 0:
        state = (
            "silent"
            if interval is not None and interval.lower > 0
            else "stale-telemetry"
        )
        reason = f"no current telemetry rows for {events} eligible {surface.event_kind} events"
        return Assessment(
            surface.id, state, reason, events, rows, errors, rate, interval
        )
    if (
        errors >= surface.minimum_error_rows
        and errors / rows > surface.error_rate_ceiling
    ):
        reason = f"{errors}/{rows} telemetry rows errored; ceiling {surface.error_rate_ceiling:.3f}"
        return Assessment(
            surface.id, "error-rate", reason, events, rows, errors, rate, interval
        )
    if interval is None:
        return Assessment(
            surface.id,
            "baseline-unavailable",
            "fewer than 24 active hours in the seven-day baseline",
            events,
            rows,
            errors,
            rate,
            None,
        )
    if rate < interval.lower:
        state = "silent"
        reason = f"rate {rate:.4f} below seven-day 95% CI [{interval.lower:.4f}, {interval.upper:.4f}]"
    elif rate > interval.upper:
        state = "unexpected-volume"
        reason = f"rate {rate:.4f} above seven-day 95% CI [{interval.lower:.4f}, {interval.upper:.4f}]"
    else:
        state = "healthy"
        reason = f"rate {rate:.4f} inside seven-day 95% CI [{interval.lower:.4f}, {interval.upper:.4f}]"
    return Assessment(surface.id, state, reason, events, rows, errors, rate, interval)
