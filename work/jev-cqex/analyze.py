#!/usr/bin/env python3
"""Keyless H3 strata and Wilson-interval analysis."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "var/agent-tmp/jev-oioo/climate-fever.jsonl"
ITEMS = ROOT / "work/jev-oioo/items.jsonl"
ANSWERS = ROOT / "work/jev-oioo/live-results.jsonl"
PREREG = ROOT / "work/jev-cqex/prereg.md"
OUT = ROOT / "work/jev-cqex/strata.jsonl"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(correct: int, total: int) -> list[float | None]:
    if total == 0:
        return [None, None]
    z = 1.959963984540054
    p = correct / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return [max(0.0, center - margin), min(1.0, center + margin)]


def main() -> int:
    source_rows = {str(row["claim_id"]): row for row in read_jsonl(SOURCE)}
    items = read_jsonl(ITEMS)
    answers = {row["id"]: row for row in read_jsonl(ANSWERS)}
    prereg_sha = sha(PREREG)
    if len(items) != 907 or len(answers) != 907:
        raise SystemExit("expected exactly 907 items and answers")
    strata: list[dict[str, Any]] = []
    for item in items:
        source = source_rows[str(item["claim_id"])]
        labels = [evidence["evidence_label"] for evidence in source["evidences"]]
        counts = Counter(labels)
        top = max(counts.values())
        leaders = sorted(label for label, count in counts.items() if count == top)
        claim_label = item["label"]
        if len(leaders) > 1:
            stratum = "ambiguous"
            majority = None
        else:
            majority = leaders[0]
            stratum = "agree" if majority == claim_label else "disagree"
        answer = answers[item["id"]]
        jev = answer["jev"]
        if jev["model"] != "jev-1.13.0" or jev["status"] != "scored":
            raise SystemExit(f"invalid committed Jev row: {item['id']}")
        prediction = "SUPPORTS" if jev["noul"] > 0.5 else "REFUTES"
        strata.append(
            {
                "id": item["id"],
                "stratum": stratum,
                "claim_label": claim_label,
                "majority_label": majority,
                "majority_count": top,
                "evidence_label_counts": dict(sorted(counts.items())),
                "jev_prediction": prediction,
                "correct": prediction == claim_label,
                "noul": jev["noul"],
            }
        )
    OUT.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in strata
        )
    )
    summary: dict[str, dict[str, Any]] = {}
    for name in ("agree", "disagree", "ambiguous"):
        rows = [row for row in strata if row["stratum"] == name]
        correct = sum(bool(row["correct"]) for row in rows)
        summary[name] = {
            "n": len(rows),
            "correct": correct,
            "accuracy": correct / len(rows) if rows else None,
            "wilson95": wilson(correct, len(rows)),
        }
    result = {
        "source_sha256": sha(SOURCE),
        "items_sha256": sha(ITEMS),
        "answers_sha256": sha(ANSWERS),
        "prereg_sha256": prereg_sha,
        "strata_sha256": sha(OUT),
        "summary": summary,
        "total": len(strata),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
