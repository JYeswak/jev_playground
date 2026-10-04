"""Small, dependency-free helpers for class-conditional split conformal."""

from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TypeVar

Row = TypeVar("Row", bound=Mapping[str, object])


@dataclass(frozen=True)
class PredictionSet:
    labels: frozenset[str]
    p_values: Mapping[str, float]


def _validate_probabilities(
    probabilities: Mapping[str, float], labels: Sequence[str]
) -> None:
    if set(probabilities) != set(labels):
        raise ValueError("probability keys must match the declared labels")
    values = list(probabilities.values())
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0.0
        or value > 1.0
        for value in values
    ):
        raise ValueError("probabilities must be finite numbers in [0, 1]")
    if abs(sum(values) - 1.0) > 0.02:
        raise ValueError("probabilities must sum to one within 0.02")


def conformal_prediction_set(
    calibration: Sequence[tuple[str, Mapping[str, float]]],
    probabilities: Mapping[str, float],
    labels: Sequence[str],
    *,
    alpha: float,
) -> PredictionSet:
    """Return a class-conditional split-conformal set for one candidate.

    Nonconformity is ``1 - P(class)``. Ties count against exclusion by using
    ``>=`` in the conformal p-value. A class absent from calibration is always
    included, so lack of support can only widen the set and cause abstention.
    Validity requires exchangeability within each class and the time regime.
    """
    if (
        isinstance(alpha, bool)
        or not isinstance(alpha, (int, float))
        or not math.isfinite(alpha)
        or not 0.0 < alpha < 1.0
    ):
        raise ValueError("alpha must be finite and strictly between zero and one")
    if not labels or len(set(labels)) != len(labels):
        raise ValueError("labels must be a non-empty sequence of unique values")
    if any(not isinstance(label, str) or not label for label in labels):
        raise ValueError("labels must be non-empty strings")
    _validate_probabilities(probabilities, labels)

    class_scores: dict[str, list[float]] = {label: [] for label in labels}
    for truth, calibration_probabilities in calibration:
        if truth not in class_scores:
            raise ValueError(f"unknown calibration label: {truth!r}")
        _validate_probabilities(calibration_probabilities, labels)
        class_scores[truth].append(1.0 - calibration_probabilities[truth])

    p_values: dict[str, float] = {}
    included: set[str] = set()
    for label in labels:
        scores = class_scores[label]
        if not scores:
            p_value = 1.0
        else:
            candidate_score = 1.0 - probabilities[label]
            p_value = (1 + sum(score >= candidate_score for score in scores)) / (
                len(scores) + 1
            )
        p_values[label] = p_value
        if p_value > alpha:
            included.add(label)

    return PredictionSet(frozenset(included), p_values)


def support_gated_prediction_set(
    calibration: Sequence[tuple[str, Mapping[str, float]]],
    probabilities: Mapping[str, float],
    labels: Sequence[str],
    *,
    alpha: float,
) -> PredictionSet:
    """Add a conservative actionability guard to the split-conformal set.

    A class p-value cannot reach ``alpha`` unless its calibration count ``n``
    satisfies ``1 / (n + 1) <= alpha``. If any class lacks that resolution,
    retain every label so the better-sampled class cannot trigger a one-sided
    action. The underlying p-values remain unchanged.
    """
    result = conformal_prediction_set(calibration, probabilities, labels, alpha=alpha)
    counts = dict.fromkeys(labels, 0)
    for truth, _ in calibration:
        counts[truth] += 1
    if any(1.0 / (count + 1) > alpha for count in counts.values()):
        return PredictionSet(frozenset(labels), result.p_values)
    return result


def _utc_timestamp(value: object) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp must be a non-empty ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def chronological_split(
    rows: Sequence[Row],
    *,
    timestamp_key: str = "ts",
    id_key: str = "id",
) -> tuple[list[Row], list[Row], str]:
    """Split at the nearest timestamp-group boundary to one half.

    Rows sharing an instant stay together. On equal-distance boundaries, use
    the earlier cut. Returns calibration rows, later holdout rows, and the
    last calibration timestamp in its original serialized form.
    """
    if len(rows) < 2:
        raise ValueError("at least two rows are required for a temporal split")

    ordered = sorted(
        rows,
        key=lambda row: (
            _utc_timestamp(row.get(timestamp_key)),
            str(row.get(id_key, "")),
        ),
    )
    instants = [_utc_timestamp(row.get(timestamp_key)) for row in ordered]
    candidates: list[tuple[int, datetime]] = []
    count = 1
    for index in range(1, len(ordered)):
        if instants[index] != instants[index - 1]:
            candidates.append((count, instants[index - 1]))
        count += 1
    if not candidates:
        raise ValueError("no timestamp-group boundary can form two partitions")

    target = len(ordered) / 2
    split_index, _ = min(
        candidates,
        key=lambda boundary: (
            abs(boundary[0] - target),
            boundary[0] > target,
            boundary[0],
        ),
    )
    calibration = ordered[:split_index]
    holdout = ordered[split_index:]
    return calibration, holdout, str(calibration[-1][timestamp_key])


def permute_labels(labels: Sequence[str], *, seed: int) -> list[str]:
    """Return a reproducible label permutation without changing class counts."""
    result = list(labels)
    random.Random(seed).shuffle(result)
    return result
