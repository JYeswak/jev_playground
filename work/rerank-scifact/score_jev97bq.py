#!/usr/bin/env python3
"""Score the preregistered free incumbent against the committed Jev rows."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import math
import statistics
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATES = HERE / "candidates-nfcorpus.jsonl"
JEV_ROWS = HERE / "rows-nfcorpus-v2-jev.jsonl"
MODEL = "dots-studio/dots-3-note-preview:free"
CANDIDATES_SHA256 = "1ef3835708d8522ed39f2f2bd4018ea07390e403bcfd8e00119580e69860e3ec"
N = 234


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def ndcg10(ranked: list[str], relevant: set[str]) -> float:
    dcg = sum(
        1 / math.log2(i + 2) for i, doc in enumerate(ranked[:10]) if doc in relevant
    )
    idcg = sum(1 / math.log2(i + 2) for i in range(min(10, len(relevant))))
    return dcg / idcg


def wilcoxon_signed_rank(a: list[float], b: list[float]) -> dict[str, Any]:
    differences = [x - y for x, y in zip(a, b) if x != y]
    if not differences:
        return {
            "n_nonzero": 0,
            "w_plus": 0.0,
            "w_minus": 0.0,
            "z": 0.0,
            "p_approx": 1.0,
        }
    ranked = sorted(
        (abs(value), index, value) for index, value in enumerate(differences)
    )
    ranks = [0.0] * len(differences)
    pos = 0
    while pos < len(ranked):
        end = pos + 1
        while end < len(ranked) and ranked[end][0] == ranked[pos][0]:
            end += 1
        rank = (pos + 1 + end) / 2
        for _, index, _ in ranked[pos:end]:
            ranks[index] = rank
        pos = end
    w_plus = sum(rank for rank, value in zip(ranks, differences) if value > 0)
    w_minus = sum(rank for rank, value in zip(ranks, differences) if value < 0)
    n = len(differences)
    mean = n * (n + 1) / 4
    variance = n * (n + 1) * (2 * n + 1) / 24
    z = (
        w_plus - mean - (0.5 if w_plus > mean else -0.5 if w_plus < mean else 0)
    ) / math.sqrt(variance)
    p = math.erfc(abs(z) / math.sqrt(2))
    return {"n_nonzero": n, "w_plus": w_plus, "w_minus": w_minus, "z": z, "p_approx": p}


def metrics(
    candidates: list[dict[str, Any]], choices: dict[str, str]
) -> tuple[list[float], list[bool]]:
    ndcgs, top1 = [], []
    for row in candidates:
        qid = row["qid"]
        ids = [doc for doc, _score in row["cands"]]
        selected = choices[qid]
        ranked = [selected] + [doc for doc in ids if doc != selected]
        relevant = set(row["rel"])
        ndcgs.append(ndcg10(ranked, relevant))
        top1.append(selected in relevant)
    return ndcgs, top1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rows", type=Path, default=HERE / "rows-jev-97bq-openrouter.jsonl"
    )
    parser.add_argument("--usage-before", type=Path, required=True)
    parser.add_argument("--usage-after", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=HERE / "receipt-jev-97bq.json")
    args = parser.parse_args()
    if not hmac.compare_digest(
        hashlib.sha256(CANDIDATES.read_bytes()).hexdigest(), CANDIDATES_SHA256
    ):
        raise SystemExit("candidate SHA mismatch")
    candidates = load_jsonl(CANDIDATES)
    if len(candidates) != N:
        raise SystemExit(f"expected {N} candidates, got {len(candidates)}")
    rows = load_jsonl(args.rows)
    jev_rows = load_jsonl(JEV_ROWS)
    docs = {r["qid"]: {doc for doc, _score in r["cands"]} for r in candidates}
    expected = set(docs)
    choices: dict[str, str] = {}
    invalid = 0
    errors = 0
    duplicate = 0
    for row in rows:
        qid = row.get("qid")
        if not isinstance(qid, str) or qid not in expected or qid in choices:
            duplicate += 1
            continue
        if row.get("status") == "error" or "error" in row:
            errors += 1
            continue
        choice = row.get("choice")
        if (
            row.get("status") != "ok"
            or not isinstance(choice, str)
            or choice not in docs[qid]
        ):
            invalid += 1
            continue
        choices[qid] = choice
    if set(choices) != expected:
        raise SystemExit(
            json.dumps(
                {
                    "status": "INCOMPLETE",
                    "answered": len(choices),
                    "expected": N,
                    "invalid": invalid,
                    "errors": errors,
                    "duplicate": duplicate,
                },
                sort_keys=True,
            )
        )
    jev_choices = {
        row["qid"]: row["choice"]
        for row in jev_rows
        if row.get("choice") in docs.get(row.get("qid"), set())
    }
    if set(jev_choices) != expected:
        raise SystemExit("committed Jev rows are incomplete or invalid")
    incumbent_ndcg, incumbent_top1 = metrics(candidates, choices)
    jev_ndcg, jev_top1 = metrics(candidates, jev_choices)
    b = sum(a and not j for a, j in zip(incumbent_top1, jev_top1))
    c = sum(j and not a for a, j in zip(incumbent_top1, jev_top1))
    usage_before = json.loads(args.usage_before.read_text())
    usage_after = json.loads(args.usage_after.read_text())
    usage_unchanged = hmac.compare_digest(
        json.dumps(usage_before.get("usage"), sort_keys=True),
        json.dumps(usage_after.get("usage"), sort_keys=True),
    )
    row_usage = [r.get("usage", {}) for r in rows if r.get("status") == "ok"]
    result = {
        "bead": "jev-97bq",
        "status": "SCORED",
        "model": MODEL,
        "n": N,
        "candidates_sha256": CANDIDATES_SHA256,
        "rows": str(args.rows),
        "invalid_rows": invalid,
        "error_rows": errors,
        "duplicate_rows": duplicate,
        "incumbent": {
            "ndcg10": statistics.fmean(incumbent_ndcg),
            "top1": statistics.fmean(incumbent_top1),
        },
        "jev": {
            "ndcg10": statistics.fmean(jev_ndcg),
            "top1": statistics.fmean(jev_top1),
        },
        "delta_incumbent_minus_jev": {
            "ndcg10": statistics.fmean(incumbent_ndcg) - statistics.fmean(jev_ndcg),
            "top1": statistics.fmean(incumbent_top1) - statistics.fmean(jev_top1),
        },
        "mcnemar_top1": {
            "incumbent_only_wins": b,
            "jev_only_wins": c,
            "discordant": b + c,
        },
        "wilcoxon_ndcg": wilcoxon_signed_rank(incumbent_ndcg, jev_ndcg),
        "usage": {
            "before": usage_before,
            "after": usage_after,
            "unchanged": usage_unchanged,
            "row_input_tokens": sum(u.get("input_tokens", 0) for u in row_usage),
            "row_output_tokens": sum(u.get("output_tokens", 0) for u in row_usage),
            "cost_claim": "$0 only if unchanged and all rows are :free",
        },
        "bar": {
            "both_metrics_tie_or_beat": statistics.fmean(incumbent_ndcg)
            >= statistics.fmean(jev_ndcg)
            and statistics.fmean(incumbent_top1) >= statistics.fmean(jev_top1)
            and usage_unchanged
            and invalid == 0
            and errors == 0
        },
        "boundary": "One free OpenRouter model on the frozen 234-query NFCorpus slice; no new Jev calls; invalid/error rows are counted separately and never scored as wrong.",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
