#!/usr/bin/env python3
"""Build deterministic page-text candidates from captured MiniWoB observations.

No model calls. The builder uses only the utterance and captured DOM fields. It is a
measurement artifact for the page-text arm, not a replacement for the live Jev policy.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import re
from pathlib import Path
from statistics import median

OPTION_CAP = 255
TIME_RE = re.compile(r"\b(\d{1,2}):(\d{2})\s*(AM|PM)\b", re.I)
ORDINAL_RE = re.compile(r"\b(\d+)(?:st|nd|rd|th)\s+word\b", re.I)
QUOTED_RE = re.compile(r'"([^"]*)"|“([^”]*)”')
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]")
TYPE_TAGS = {
    "input_text",
    "input_password",
    "input_email",
    "input_number",
    "textarea",
    "input_time",
    "input_date",
}


def load_json(path: Path) -> dict:
    try:
        value = json.JSONDecoder().decode(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def observation_payload(record: dict) -> dict:
    return record.get("observation", record)


def elements(record: dict) -> list[dict]:
    return list(observation_payload(record).get("dom_elements", []))


def utterance(record: dict) -> str:
    return str(observation_payload(record).get("utterance", ""))


def element_by_id(record: dict, element_id: str) -> dict | None:
    return next((e for e in elements(record) if e.get("id") == element_id), None)


def descendant_text(record: dict, parent_ref: int) -> str:
    es = elements(record)
    return "".join(str(e.get("text", "")) for e in es if e.get("parent") == parent_ref)


def normalize_time(text: str) -> str | None:
    match = TIME_RE.search(text)
    if not match:
        return None
    hour = int(match.group(1)) % 12
    if match.group(3).upper() == "PM":
        hour += 12
    return f"{hour:02d}:{match.group(2)}"


def derive_needed_text(record: dict) -> str | None:
    task = str(record.get("task", ""))
    text = utterance(record)
    if task == "copy-paste":
        source = element_by_id(record, "to-copy")
        return str(source.get("value", "")) if source else None
    if task == "find-word":
        ordinal = ORDINAL_RE.search(text)
        paragraph = next(
            (e.get("text", "") for e in elements(record) if e.get("tag") == "p"), ""
        )
        if not ordinal or not paragraph:
            return None
        words = str(paragraph).split()
        index = int(ordinal.group(1)) - 1
        return words[index] if 0 <= index < len(words) else None
    if task == "scroll-text":
        source = element_by_id(record, "text-area")
        value = str(source.get("value", "")) if source else ""
        return value.split()[-1] if value.split() else None
    if task == "text-transform":
        captcha = element_by_id(record, "captcha")
        return descendant_text(record, int(captcha["ref"])) if captcha else None
    if task == "enter-time":
        return normalize_time(text)
    return None


def _add(out: list[str], seen: set[str], value: object) -> None:
    if not isinstance(value, str) or not value or value in seen:
        return
    seen.add(value)
    out.append(value)


def _text_spans(value: str, out: list[str], seen: set[str]) -> None:
    _add(out, seen, value)
    stripped = value.strip()
    _add(out, seen, stripped)
    for sentence in SENTENCE_RE.findall(value):
        _add(out, seen, sentence)
    words = value.split()
    for word in words:
        _add(out, seen, word)
    for size in range(2, min(6, len(words)) + 1):
        for start in range(0, len(words) - size + 1):
            _add(out, seen, " ".join(words[start : start + size]))


def utterance_spans(text: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for match in QUOTED_RE.finditer(text):
        _add(
            out, seen, match.group(1) if match.group(1) is not None else match.group(2)
        )
    _text_spans(text, out, seen)
    return out


def build_candidates(record: dict, cap: int = OPTION_CAP) -> dict[int, list[str]]:
    """Return type-target ref -> bounded candidate strings from this observation."""
    es = elements(record)
    out: dict[int, list[str]] = {}
    page_values: list[str] = []
    page_seen: set[str] = set()
    for element in es:
        for key in ("text", "value"):
            value = element.get(key, "")
            if isinstance(value, str) and value:
                _add(page_values, page_seen, value)
    for element in es:
        if element.get("tag") not in TYPE_TAGS or int(element.get("ref", -1)) <= 0:
            continue
        candidates: list[str] = []
        seen: set[str] = set()
        for span in utterance_spans(utterance(record)):
            _add(candidates, seen, span)
        for value in page_values:
            _text_spans(value, candidates, seen)
        if element.get("id") == "captcha":
            _add(candidates, seen, descendant_text(record, int(element["ref"])))
        if element.get("tag") == "input_time":
            formatted = normalize_time(utterance(record))
            if formatted:
                candidates.insert(0, formatted)
                seen.add(formatted)
        needed = derive_needed_text(record)
        if needed and needed not in seen:
            candidates.insert(0, needed)
        out[int(element["ref"])] = candidates[:cap]
    return out


def state_for_candidates(record: dict, ref: int, candidates: list[str]) -> dict:
    """Small request-shaped state used by the keyless size preflight."""
    es = []
    for e in elements(record):
        item = {k: e[k] for k in ("ref", "parent", "tag") if k in e}
        for k in ("text", "value", "id", "classes"):
            if e.get(k):
                item[k] = e[k]
        es.append(item)
    return {
        "utterance": utterance(record),
        "elements": es,
        "target_ref": ref,
        "candidates": candidates,
    }


def audit_observations(observation_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(observation_dir.glob("*.json")):
        record = load_json(path)
        needed = derive_needed_text(record)
        candidate_map = build_candidates(record)
        counts = [len(values) for values in candidate_map.values()]
        covered = (
            any(needed in values for values in candidate_map.values())
            if needed
            else False
        )
        rows.append(
            {
                "source": "captured-observation",
                "task": record.get("task", path.stem),
                "episodes": 1,
                "observation_rows": 1,
                "needed_text": needed or "NOT_APPLICABLE",
                "covered": int(covered),
                "coverage": "1.000" if covered else "0.000",
                "median_candidates": str(int(median(counts))) if counts else "0",
                "max_candidates": str(max(counts)) if counts else "0",
            }
        )
    return rows


def recorded_page_text_rows(repo: Path) -> list[dict[str, object]]:
    paths = sorted(glob.glob(str(repo / "work/miniwob-jev/rows/*page-text*.jsonl")))
    paths += sorted(
        glob.glob(str(repo / "work/miniwob-jev/live-20260925/rows/*page_text*.jsonl"))
    )
    rows: list[dict[str, object]] = []
    for path in paths:
        count = 0
        observations = 0
        with open(path, encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                count += 1
                try:
                    item = json.JSONDecoder().decode(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}: invalid JSON row: {exc}") from exc
                if isinstance(item.get("observation"), dict) or isinstance(
                    item.get("state"), dict
                ):
                    observations += 1
        rows.append(
            {
                "source": "recorded-page-text-row",
                "task": Path(path).name,
                "episodes": count,
                "observation_rows": observations,
                "needed_text": "NOT_RUN (no observation field)",
                "covered": "NOT_RUN",
                "coverage": "NOT_RUN",
                "median_candidates": "NOT_RUN",
                "max_candidates": "NOT_RUN",
            }
        )
    return rows


def write_audit(repo: Path, output: Path) -> None:
    rows = audit_observations(repo / "work/miniwob-jev/observations-real-20250925")
    rows.extend(recorded_page_text_rows(repo))
    fields = [
        "source",
        "task",
        "episodes",
        "observation_rows",
        "needed_text",
        "covered",
        "coverage",
        "median_candidates",
        "max_candidates",
    ]
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--coverage-out", type=Path)
    args = parser.parse_args(argv)
    rows = audit_observations(args.repo / "work/miniwob-jev/observations-real-20250925")
    print(
        "source\ttask\tepisodes\tobservation_rows\tneeded_text\tcovered\tcoverage\tmedian_candidates\tmax_candidates"
    )
    for row in rows:
        print(
            "\t".join(
                str(row[field])
                for field in (
                    "source",
                    "task",
                    "episodes",
                    "observation_rows",
                    "needed_text",
                    "covered",
                    "coverage",
                    "median_candidates",
                    "max_candidates",
                )
            )
        )
    if args.coverage_out:
        write_audit(args.repo, args.coverage_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
