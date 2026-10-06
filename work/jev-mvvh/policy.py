from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any

from core import LedgerInputError


def classify_memory_cap3_harm(upper_bound: float | None) -> dict[str, Any]:
    if upper_bound is None:
        return {"verdict": "UNMEASURED", "reason": "X8 cap-3 harm bound is absent"}
    if (
        isinstance(upper_bound, bool)
        or not isinstance(upper_bound, (int, float))
        or not math.isfinite(upper_bound)
        or not 0 <= upper_bound <= 1
    ):
        raise LedgerInputError("cap-3 harm upper bound must be a probability in [0,1]")
    if upper_bound <= 0.05:
        return {
            "verdict": "KEEP",
            "reason": "X8 upper confidence bound is at most 0.05",
        }
    return {"verdict": "KILL", "reason": "X8 upper confidence bound exceeds 0.05"}


def classify_surface(value_usd: float | None, cost_usd: float | None) -> dict[str, Any]:
    """Classify known-dollar value against cost; absent evidence stays UNMEASURED."""
    for name, value in (("value", value_usd), ("cost", cost_usd)):
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise LedgerInputError(f"{name} must be a finite dollar amount or None")
    if value_usd is None or cost_usd is None:
        return {
            "verdict": "UNMEASURED",
            "net_usd": None,
            "reason": "value or cost source is missing",
            "applied_action": None,
        }
    net = float(value_usd) - float(cost_usd)
    verdict = "KILL" if net < 0 else "KEEP"
    return {
        "verdict": verdict,
        "net_usd": net,
        "reason": "measured value-minus-cost is negative"
        if verdict == "KILL"
        else "measured value covers cost",
        "applied_action": None,
    }


def switch_recommendation(
    surface: dict[str, Any], verdict: str
) -> dict[str, Any] | None:
    """Return, but never apply, the declared off-switch recommendation."""
    if verdict != "KILL":
        return None
    switch_file = surface.get("switch_file")
    polarity = surface.get("switch_polarity")
    if not isinstance(switch_file, str) or not switch_file:
        return None
    if polarity not in ("presence-ON", "presence-OFF"):
        return None
    return {
        "action": "turn-off",
        "file": switch_file,
        "polarity": polarity,
        "applied": False,
    }


def validate_screen_attribution(rows: Iterable[dict[str, Any]]) -> None:
    """Refuse screen events that cannot be joined to a repo and session."""
    for number, row in enumerate(rows, start=1):
        session_id = row.get("sessionId", row.get("session_id", row.get("session")))
        if not isinstance(row.get("repo"), str) or not row["repo"].strip():
            raise LedgerInputError(f"screen row {number} lacks repo attribution")
        if not isinstance(session_id, str) or not session_id.strip():
            raise LedgerInputError(f"screen row {number} lacks session id")


def strict_failures(
    expected_surfaces: Iterable[dict[str, Any]], rows: Iterable[dict[str, Any]]
) -> list[str]:
    """Fail closed for claimed-on surfaces without a usable measured outcome."""
    by_id: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    for row in rows:
        surface_id = row.get("id")
        if not isinstance(surface_id, str) or not surface_id:
            failures.append("ledger row has no surface id")
            continue
        if surface_id in by_id:
            failures.append(f"{surface_id}: duplicate ledger rows")
            continue
        by_id[surface_id] = row

    for surface in expected_surfaces:
        if surface.get("expect") != "on":
            continue
        surface_id = surface.get("id")
        if not isinstance(surface_id, str) or not surface_id:
            failures.append("expected-on registry row has no surface id")
            continue
        row = by_id.get(surface_id)
        if row is None:
            failures.append(f"{surface_id}: missing ledger row")
            continue
        verdict = row.get("verdict")
        if verdict in ("KEEP", "PROMOTE"):
            if row.get("live") != "on":
                failures.append(
                    f"{surface_id}: claimed-on KEEP/PROMOTE surface is not live"
                )
            if verdict == "PROMOTE":
                bar_epoch = row.get("bar_commit_epoch")
                data_epoch = row.get("data_start_epoch")
                if (
                    isinstance(bar_epoch, bool)
                    or not isinstance(bar_epoch, int)
                    or isinstance(data_epoch, bool)
                    or not isinstance(data_epoch, int)
                    or bar_epoch >= data_epoch
                ):
                    failures.append(
                        f"{surface_id}: PROMOTE lacks a bar committed before data"
                    )
            continue
        if verdict == "KILL":
            if row.get("live") != "off":
                failures.append(f"{surface_id}: KILL surface is still live")
            elif row.get("switch_verified_off") is not True:
                failures.append(f"{surface_id}: off switch is not verified")
            elif row.get("fresh_session_rows") != 0:
                failures.append(
                    f"{surface_id}: fresh session has rows or no zero-row proof"
                )
            continue
        failures.append(
            f"{surface_id}: verdict is {verdict or 'missing'}, not KEEP/PROMOTE"
        )
    return failures


def screen_rows(
    rows: list[dict[str, Any]], sessions: dict[str, str]
) -> tuple[list[dict[str, Any]], list[str]]:
    attributable: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, item in enumerate(rows, start=1):
        row = dict(item)
        session_id = row.get("sessionId", row.get("session_id", row.get("session")))
        if (
            isinstance(session_id, str)
            and session_id in sessions
            and not row.get("repo")
        ):
            row["repo"] = sessions[session_id]
        try:
            validate_screen_attribution([row])
        except LedgerInputError as exc:
            errors.append(f"row {index}: {exc}")
        else:
            attributable.append(row)
    return attributable, errors
