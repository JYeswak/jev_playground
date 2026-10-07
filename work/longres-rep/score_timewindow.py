#!/usr/bin/env python3
"""Score the frozen long-result temporal replication from committed rows."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from work.longres.score import (  # noqa: E402, RUF100 -- standalone CLI needs repo-root path bootstrap
    CHARS_PER_TOKEN,
    CONTENT_TOOLS,
    INPUT_USD_PER_MILLION,
    JEV_MODEL,
    ArmMetrics,
    Sample,
    _arm_metrics,
    _candidate_thresholds,
    _choice_and_usage,
    _fit_threshold,
    _integer,
    _object,
    _samples,
)


class ZeroDropBaselineError(ValueError):
    """The equal-miss comparator has no reference drops to match Jev."""


BASE = Path(__file__).resolve().parent
DEFAULT_RECEIPT = BASE / "TIMEWINDOW-RECEIPT.md"
PROTECTED_CORPUS = (BASE / "corpus.json").resolve()


@dataclass(frozen=True)
class TimewindowReport:
    verdict: str
    model: str
    dev_rows: int
    held_rows: int
    held_referenced: int
    held_unreferenced: int
    jev: ArmMetrics
    held_matched: ArmMetrics
    held_matched_threshold_chars: int
    held_matched_miss_count_equal: bool
    held_matched_savings_ratio: float | str
    primary_advantage: bool
    youden_threshold_chars: int
    youden_baseline: ArmMetrics
    original_bar_pass: bool
    total_calls: int
    scored_calls: int
    fallback_keeps: int
    input_tokens: int
    calls_with_usage: int
    spend_complete: bool
    observed_spend_usd: float
    median_latency_ms: float | None
    weekly_volume_estimate: int
    weekly_tokens_saved_jev: int
    weekly_tokens_saved_held_matched: int
    weekly_tokens_saved_youden: int


def _baseline_decisions(rows: list[Sample], threshold: int) -> dict[str, str]:
    return {
        row.sample_id: (
            "drop" if row.tool in CONTENT_TOOLS and row.size >= threshold else "keep"
        )
        for row in rows
    }


def _held_matched_baseline(
    held: list[Sample], jev_misses: int
) -> tuple[int, dict[str, str], ArmMetrics]:
    best_key: tuple[int, int, int] | None = None
    best: tuple[int, dict[str, str], ArmMetrics] | None = None
    for threshold in _candidate_thresholds(held):
        decisions = _baseline_decisions(held, threshold)
        metrics = _arm_metrics(held, decisions)
        key = (
            abs(metrics.reference_drops - jev_misses),
            -metrics.savings_chars,
            -threshold,
        )
        if best_key is None or key < best_key:
            best_key = key
            best = (threshold, decisions, metrics)
    if best is None:
        raise ValueError("held split has no candidate baseline threshold")
    threshold, decisions, metrics = best
    total_drops = sum(action == "drop" for action in decisions.values())
    if total_drops == 0 and jev_misses > 0:
        raise ZeroDropBaselineError("zero-drop baseline cannot compare against Jev misses")
    return threshold, decisions, metrics


def score_data(corpus: object, result_rows: list[object]) -> TimewindowReport:
    source = _object(corpus, "corpus")
    if source.get("status") != "READY":
        raise ValueError("time-window corpus is not READY; no live scoring is permitted")
    dev = _samples(source.get("dev"), "dev")
    held = _samples(source.get("held"), "held")
    if not dev or not held:
        raise ValueError("corpus dev and held splits must both be non-empty")
    if {row.sample_id for row in dev} & {row.sample_id for row in held}:
        raise ValueError("sample IDs must be disjoint across dev and held")
    dev_records = source.get("dev")
    held_records = source.get("held")
    if not isinstance(dev_records, list) or not isinstance(held_records, list):
        raise TypeError("corpus dev and held fields must be arrays")
    dev_sources = {
        str(_object(item, "dev row").get("source_path_sha256")) for item in dev_records
    }
    held_sources = {
        str(_object(item, "held row").get("source_path_sha256")) for item in held_records
    }
    if dev_sources & held_sources:
        raise ValueError("source files must not cross dev and held splits")

    samples = dev + held
    expected_ids = {row.sample_id for row in samples}
    decisions, input_tokens, calls_with_usage, fallback_keeps, latencies = (
        _choice_and_usage(result_rows, expected_ids)
    )
    jev = _arm_metrics(held, decisions)
    matched_threshold, _, held_matched = _held_matched_baseline(
        held, jev.reference_drops
    )
    matched_miss_count_equal = jev.reference_drops == held_matched.reference_drops
    primary_advantage = (
        matched_miss_count_equal and jev.savings_chars > held_matched.savings_chars
    )
    if held_matched.savings_chars == 0:
        ratio: float | str = "infinite" if jev.savings_chars > 0 else "undefined"
    else:
        ratio = jev.savings_chars / held_matched.savings_chars

    youden_threshold, _, _ = _fit_threshold(dev, "youden")
    youden_baseline = _arm_metrics(held, _baseline_decisions(held, youden_threshold))
    original_bar_pass = (
        jev.reference_drops <= youden_baseline.reference_drops
        and jev.savings_chars >= 1.2 * youden_baseline.savings_chars
    )
    volume = _integer(source.get("weekly_volume_estimate"), "weekly_volume_estimate")

    def weekly(arm: ArmMetrics) -> int:
        return round(volume * arm.savings_chars / len(held) / CHARS_PER_TOKEN)

    spend = round(input_tokens * INPUT_USD_PER_MILLION / 1_000_000, 6)
    return TimewindowReport(
        verdict="PASS" if primary_advantage else "FAIL",
        model=JEV_MODEL,
        dev_rows=len(dev),
        held_rows=len(held),
        held_referenced=sum(row.referenced for row in held),
        held_unreferenced=sum(not row.referenced for row in held),
        jev=jev,
        held_matched=held_matched,
        held_matched_threshold_chars=matched_threshold,
        held_matched_miss_count_equal=matched_miss_count_equal,
        held_matched_savings_ratio=ratio,
        primary_advantage=primary_advantage,
        youden_threshold_chars=youden_threshold,
        youden_baseline=youden_baseline,
        original_bar_pass=original_bar_pass,
        total_calls=len(result_rows),
        scored_calls=len(result_rows) - fallback_keeps,
        fallback_keeps=fallback_keeps,
        input_tokens=input_tokens,
        calls_with_usage=calls_with_usage,
        spend_complete=calls_with_usage == len(result_rows),
        observed_spend_usd=spend,
        median_latency_ms=statistics.median(latencies) if latencies else None,
        weekly_volume_estimate=volume,
        weekly_tokens_saved_jev=weekly(jev),
        weekly_tokens_saved_held_matched=weekly(held_matched),
        weekly_tokens_saved_youden=weekly(youden_baseline),
    )


def _read_rows(path: Path) -> list[object]:
    rows: list[object] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSONL at line {line_number}") from error
    return rows


def _validate_result_lineage(source: dict[str, object], result_rows: list[object]) -> None:
    expected: dict[str, tuple[object, object]] = {}
    for split in ("dev", "held"):
        records = source.get(split)
        if not isinstance(records, list):
            raise TypeError(f"corpus {split} must be an array")
        for index, item in enumerate(records):
            row = _object(item, f"corpus {split}[{index}]")
            sample_id = row.get("sample_id")
            if not isinstance(sample_id, str):
                raise TypeError(f"corpus {split}[{index}].sample_id must be a string")
            expected[sample_id] = (
                row.get("source_path_sha256"),
                row.get("full_result_sha256"),
            )

    for index, item in enumerate(result_rows):
        row = _object(item, f"result row {index}")
        sample_id = row.get("sample_id")
        if not isinstance(sample_id, str) or sample_id not in expected:
            raise ValueError(f"result row {index} references an unknown sample")
        if (
            row.get("source_path_sha256"),
            row.get("full_result_sha256"),
        ) != expected[sample_id]:
            raise ValueError(f"result row {index} does not match its corpus hashes")


def score_files(corpus_path: Path, rows_path: Path) -> TimewindowReport | dict[str, object]:
    try:
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid corpus JSON in {corpus_path}") from error
    source = _object(corpus, "corpus")
    if source.get("status") != "READY":
        counts = source.get("counts", {})
        return {
            "verdict": "NOT ENOUGH DATA",
            "status": source.get("status"),
            "counts": counts,
            "model": JEV_MODEL,
            "live_calls": 0,
            "no_claim": "No claim beyond the preregistered temporal population.",
        }
    dev_records = source.get("dev")
    held_records = source.get("held")
    if not isinstance(dev_records, list) or not isinstance(held_records, list):
        raise TypeError("corpus dev and held fields must be arrays")
    if len(dev_records) != 100 or len(held_records) != 100:
        raise ValueError("READY temporal corpus must contain dev-100 and held-100")
    held_samples = _samples(held_records, "held")
    if sum(row.referenced for row in held_samples) < 20 or sum(not row.referenced for row in held_samples) < 20:
        raise ValueError("held split needs at least 20 referenced and 20 unreferenced rows")
    records = _read_rows(rows_path)
    _validate_result_lineage(source, records)
    try:
        return score_data(corpus, records)
    except ZeroDropBaselineError as error:
        return {
            "verdict": "NOT ENOUGH DATA",
            "status": "ZERO_DROP_BASELINE_REFUSED",
            "model": JEV_MODEL,
            "live_calls": len(records),
            "reason": str(error),
            "no_claim": "No claim beyond the preregistered temporal population.",
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def receipt_text(
    report: TimewindowReport | dict[str, object], corpus_path: Path, rows_path: Path
) -> str:
    if isinstance(report, dict):
        body = json.dumps(report, sort_keys=True, ensure_ascii=False)
        detail = (
            "No Jev calls were run. "
            if report.get("live_calls") == 0
            else "Recorded calls could not be scored because no valid comparator remained. "
        )
        return (
            "# Time-window replication receipt\n\n"
            "**Verdict: NOT ENOUGH DATA**\n\n"
            f"Report: `{body}`\n\n"
            f"{detail}No claim beyond the preregistered temporal population.\n"
        )
    data = asdict(report)
    summary = {
        "corpus_sha256": _sha256(corpus_path),
        "rows_sha256": _sha256(rows_path),
        **data,
    }
    return (
        "# Time-window replication receipt\n\n"
        f"**Verdict: {report.verdict}**\n\n"
        "Frozen window: 2026-10-02T22:00:00Z to 2026-10-04T22:00:00Z (end exclusive).\n\n"
        "Primary bar: Jev must have the same held referenced-drop count as the held-matched "
        "baseline and strictly greater savings on held unreferenced rows.\n\n"
        "Secondary original bar is reported separately. Weekly tokens are scaled from the "
        "48-hour labelable-result rate; this is an estimate, not a deployment claim.\n\n"
        "No claim beyond the preregistered temporal population. The report contains no result text.\n\n"
        "```json\n"
        f"{json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)}\n"
        "```\n"
    )


def write_receipt(path: Path, text: str) -> None:
    target = path.resolve()
    if target == PROTECTED_CORPUS:
        raise ValueError(f"refusing to write excluded prior corpus: {target}")
    target.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = score_files(args.corpus, args.rows)
    write_receipt(DEFAULT_RECEIPT, receipt_text(report, args.corpus, args.rows))
    if args.json:
        output = asdict(report) if isinstance(report, TimewindowReport) else report
        print(json.dumps(output, sort_keys=True, allow_nan=False))
    else:
        if isinstance(report, dict):
            print(f"NOT ENOUGH DATA: see {DEFAULT_RECEIPT}")
        else:
            print(f"{report.verdict}: see {DEFAULT_RECEIPT}")
    if isinstance(report, dict):
        return 3
    return 0 if report.verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
