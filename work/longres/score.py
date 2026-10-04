#!/usr/bin/env python3
"""Recompute long-result Choice and size/tool baselines from committed rows."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, cast

JEV_MODEL = "jev-1.13.0"
INPUT_USD_PER_MILLION = 0.042
CHARS_PER_TOKEN = 4
SUMMARY_CHARS = 400
MATCHED_MISS_LIMIT = 0.04
CONTENT_TOOLS = frozenset(
    {
        "read",
        "bash",
        "eval",
        "grep",
        "glob",
        "find",
        "web_search",
        "web_extract",
        "fetch",
    }
)
CHOICES = frozenset({"keep", "summarize", "drop"})
FitMethod = Literal["matched", "youden"]


@dataclass(frozen=True)
class Sample:
    sample_id: str
    referenced: bool
    tool: str
    size: int


@dataclass(frozen=True)
class ArmMetrics:
    reference_drops: int
    miss_rate_held_rows: float
    wilson_95_held_rows: tuple[float, float]
    miss_rate_referenced: float
    wilson_95_referenced: tuple[float, float]
    savings_chars: int
    savings_row_units: float


@dataclass(frozen=True)
class ScoreReport:
    model: str
    fit_method: FitMethod
    fit_threshold_chars: int
    fit_rows: int
    fit_referenced: int
    fit_reference_drops: int
    fit_reference_miss_rate: float
    held_rows: int
    held_referenced: int
    held_unreferenced: int
    jev: ArmMetrics
    baseline: ArmMetrics
    matched_savings_bar_pass: bool
    primary_safety_bar_pass: bool
    primary_savings_bar_pass: bool
    primary_bar_pass: bool
    qualified: bool
    total_calls: int
    scored_calls: int
    fallback_keeps: int
    input_tokens: int
    calls_with_usage: int
    observed_spend_usd: float
    spend_complete: bool
    median_latency_ms: float | None
    weekly_volume: int
    weekly_tokens_saved_jev: int
    weekly_tokens_saved_baseline: int


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be a JSON object")
    if not all(isinstance(key, str) for key in value):
        raise TypeError(f"{label} keys must be strings")
    return cast(dict[str, object], value)


def _integer(value: object, label: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{label} must be an integer")
    if value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return value


def _samples(value: object, split: str) -> list[Sample]:
    if not isinstance(value, list):
        raise TypeError(f"corpus {split} must be an array")
    output: list[Sample] = []
    for index, item in enumerate(value):
        record = _object(item, f"corpus {split}[{index}]")
        sample_id, referenced, tool = (
            record.get("sample_id"),
            record.get("ref"),
            record.get("tool"),
        )
        if not isinstance(sample_id, str):
            raise TypeError(f"corpus {split}[{index}].sample_id must be a string")
        if not sample_id:
            raise ValueError(f"corpus {split}[{index}].sample_id must be non-empty")
        if not isinstance(referenced, bool):
            raise TypeError(f"corpus {split}[{index}].ref must be boolean")
        if not isinstance(tool, str):
            raise TypeError(f"corpus {split}[{index}].tool must be a string")
        output.append(
            Sample(
                sample_id=sample_id,
                referenced=referenced,
                tool=tool,
                size=_integer(
                    record.get("size"), f"corpus {split}[{index}].size", minimum=1
                ),
            )
        )
    return output


def _choice_and_usage(
    records: list[object], expected_ids: set[str]
) -> tuple[dict[str, str], int, int, int, list[float]]:
    decisions: dict[str, str] = {}
    input_tokens = 0
    calls_with_usage = 0
    fallback_keeps = 0
    latencies: list[float] = []
    for line_number, item in enumerate(records, start=1):
        record = _object(item, f"result row {line_number}")
        sample_id, model, status = (
            record.get("sample_id"),
            record.get("model"),
            record.get("status"),
        )
        if not isinstance(sample_id, str) or not sample_id:
            raise ValueError(f"result row {line_number}.sample_id must be non-empty")
        if sample_id in decisions:
            raise ValueError(f"duplicate result sample_id {sample_id}")
        if sample_id not in expected_ids:
            raise ValueError(f"unexpected result sample_id {sample_id}")
        if model != JEV_MODEL:
            raise ValueError(f"result {sample_id} model must be {JEV_MODEL}")
        if not isinstance(status, str) or not status:
            raise ValueError(f"result {sample_id}.status must be non-empty")

        if status == "scored":
            action = record.get("choice")
            if action not in CHOICES:
                raise ValueError(f"scored result {sample_id} has invalid choice")
        else:
            action = record.get("pred", "keep")
            if action != "keep":
                raise ValueError(f"unscored result {sample_id} must fail safe to keep")
            fallback_keeps += 1
        decisions[sample_id] = cast(str, action)

        usage = record.get("usage")
        if usage is not None:
            usage_record = _object(usage, f"result {sample_id}.usage")
            tokens = usage_record.get("input_tokens")
            if tokens is not None:
                input_tokens += _integer(
                    tokens, f"result {sample_id}.usage.input_tokens"
                )
                calls_with_usage += 1
        latency = record.get("latencyMs")
        if latency is not None:
            if (
                not isinstance(latency, (int, float))
                or isinstance(latency, bool)
                or not math.isfinite(latency)
                or latency < 0
            ):
                raise ValueError(
                    f"result {sample_id}.latencyMs must be a finite non-negative number"
                )
            latencies.append(float(latency))

    missing = expected_ids - decisions.keys()
    if missing:
        raise ValueError(f"missing {len(missing)} sample(s) from result rows")
    return decisions, input_tokens, calls_with_usage, fallback_keeps, latencies


def _candidate_thresholds(rows: list[Sample]) -> list[int]:
    candidates = sorted({row.size for row in rows if row.tool in CONTENT_TOOLS})
    if not candidates:
        raise ValueError("fit split has no content-tool results")
    return candidates + [max(row.size for row in rows) + 1]


def _fit_threshold(rows: list[Sample], method: FitMethod) -> tuple[int, int, int]:
    referenced = [row for row in rows if row.referenced]
    unreferenced = [row for row in rows if not row.referenced]
    if not referenced or not unreferenced:
        raise ValueError("fit split must contain referenced and unreferenced rows")
    candidates = _candidate_thresholds(rows)

    if method == "matched":
        for threshold in candidates:
            misses = sum(
                row.tool in CONTENT_TOOLS and row.size >= threshold
                for row in referenced
            )
            if misses / len(referenced) <= MATCHED_MISS_LIMIT:
                return threshold, misses, len(referenced)
        raise ValueError("no threshold meets the frozen matched-miss limit")

    best_score = float("-inf")
    best_threshold = -1
    best_misses = 0
    for threshold in candidates:
        true_positive = sum(
            row.tool in CONTENT_TOOLS and row.size >= threshold for row in unreferenced
        )
        false_positive = sum(
            row.tool in CONTENT_TOOLS and row.size >= threshold for row in referenced
        )
        score = true_positive / len(unreferenced) - false_positive / len(referenced)
        if score > best_score or (
            math.isclose(score, best_score, abs_tol=1e-12)
            and threshold > best_threshold
        ):
            best_score = score
            best_threshold = threshold
            best_misses = false_positive
    return best_threshold, best_misses, len(referenced)


def _saved_chars(row: Sample, action: str) -> int:
    if action == "drop":
        return row.size
    if action == "summarize":
        return max(0, row.size - SUMMARY_CHARS)
    return 0


def _wilson(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("Wilson interval denominator must be positive")
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total))
        / denominator
    )
    return center - margin, center + margin


def _arm_metrics(rows: list[Sample], decisions: dict[str, str]) -> ArmMetrics:
    referenced = [row for row in rows if row.referenced]
    unreferenced = [row for row in rows if not row.referenced]
    if not referenced or not unreferenced:
        raise ValueError("held split must contain referenced and unreferenced rows")
    misses = sum(decisions[row.sample_id] == "drop" for row in referenced)
    savings_chars = sum(
        _saved_chars(row, decisions[row.sample_id]) for row in unreferenced
    )
    savings_row_units = sum(
        _saved_chars(row, decisions[row.sample_id]) / row.size for row in unreferenced
    )
    return ArmMetrics(
        reference_drops=misses,
        miss_rate_held_rows=misses / len(rows),
        wilson_95_held_rows=_wilson(misses, len(rows)),
        miss_rate_referenced=misses / len(referenced),
        wilson_95_referenced=_wilson(misses, len(referenced)),
        savings_chars=savings_chars,
        savings_row_units=savings_row_units,
    )


def score_data(corpus: object, rows: list[object], *, fit_method: str) -> ScoreReport:
    if fit_method not in {"matched", "youden"}:
        raise ValueError("fit_method must be 'matched' or 'youden'")
    method = cast(FitMethod, fit_method)
    source = _object(corpus, "corpus")
    dev = _samples(source.get("dev"), "dev")
    held = _samples(source.get("held"), "held")
    if not dev or not held:
        raise ValueError("corpus dev and held splits must both be non-empty")
    volume = _integer(source.get("volume"), "corpus.volume")

    samples = dev + held
    expected_ids = {row.sample_id for row in samples}
    if len(expected_ids) != len(samples):
        raise ValueError("corpus sample_id values must be unique across dev and held")
    decisions, input_tokens, calls_with_usage, fallback_keeps, latencies = (
        _choice_and_usage(rows, expected_ids)
    )
    threshold, fit_misses, fit_references = _fit_threshold(dev, method)

    jev = _arm_metrics(held, decisions)
    baseline_decisions = {
        row.sample_id: (
            "drop" if row.tool in CONTENT_TOOLS and row.size >= threshold else "keep"
        )
        for row in held
    }
    baseline = _arm_metrics(held, baseline_decisions)
    matched_savings_bar_pass = jev.savings_chars >= baseline.savings_chars
    primary_safety_bar_pass = jev.miss_rate_held_rows <= baseline.miss_rate_held_rows
    primary_savings_bar_pass = jev.savings_chars >= 1.2 * baseline.savings_chars
    primary_bar_pass = primary_safety_bar_pass and primary_savings_bar_pass
    qualified = (
        method == "matched"
        and matched_savings_bar_pass
        and jev.reference_drops > baseline.reference_drops
    )
    observed_spend = round(input_tokens * INPUT_USD_PER_MILLION / 1_000_000, 6)
    spend_complete = calls_with_usage == len(rows)

    return ScoreReport(
        model=JEV_MODEL,
        fit_method=method,
        fit_threshold_chars=threshold,
        fit_rows=len(dev),
        fit_referenced=fit_references,
        fit_reference_drops=fit_misses,
        fit_reference_miss_rate=fit_misses / fit_references,
        held_rows=len(held),
        held_referenced=sum(row.referenced for row in held),
        held_unreferenced=sum(not row.referenced for row in held),
        jev=jev,
        baseline=baseline,
        matched_savings_bar_pass=matched_savings_bar_pass,
        primary_safety_bar_pass=primary_safety_bar_pass,
        primary_savings_bar_pass=primary_savings_bar_pass,
        primary_bar_pass=primary_bar_pass,
        qualified=qualified,
        total_calls=len(rows),
        scored_calls=len(rows) - fallback_keeps,
        fallback_keeps=fallback_keeps,
        input_tokens=input_tokens,
        calls_with_usage=calls_with_usage,
        observed_spend_usd=observed_spend,
        spend_complete=spend_complete,
        median_latency_ms=statistics.median(latencies) if latencies else None,
        weekly_volume=volume,
        weekly_tokens_saved_jev=round(
            volume * jev.savings_chars / len(held) / CHARS_PER_TOKEN
        ),
        weekly_tokens_saved_baseline=round(
            volume * baseline.savings_chars / len(held) / CHARS_PER_TOKEN
        ),
    )


def score_files(corpus_path: Path, rows_path: Path, *, fit_method: str) -> ScoreReport:
    try:
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid corpus JSON in {corpus_path}") from error
    result_rows: list[object] = []
    with rows_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                result_rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSONL at line {line_number}") from error
    return score_data(corpus, result_rows, fit_method=fit_method)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--fit-method", choices=("matched", "youden"), required=True)
    args = parser.parse_args()
    report = score_files(args.corpus, args.rows, fit_method=args.fit_method)
    print(json.dumps(asdict(report), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
