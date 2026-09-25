#!/usr/bin/env python3
"""Keyless component-level evaluation for PokéJev loss-depth work.

The split is deterministic and label-blind: Stage A rows are split 250/250 per
Elo band and Stage B is split by whole battle, 100/100 battles.  This file never
calls Jev and never runs battles.  It can emit the frozen split manifest and score
the dev side of the three component ground truths.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POKE = ROOT / "work" / "poke-jev"
STAGE_A = POKE / "stage-a"
STAGE_B = POKE / "stage-b"
SPLIT_SEED = "pokejev-component-split-v1"
BANDS = ("1200-1399", "1400-1599", "1600-1799", "1800+")

sys.path.insert(0, str(POKE))
import replay  # noqa: E402


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_key(key: str) -> str:
    return hashlib.sha256(f"{SPLIT_SEED}:{key}".encode()).hexdigest()


def make_split() -> dict:
    stage_a = load_jsonl(STAGE_A / "sample.jsonl")
    stage_b_decisions = load_jsonl(STAGE_B / "decisions-abyssal.jsonl")
    stage_b_results = load_jsonl(STAGE_B / "results-abyssal.jsonl")

    stage_a_dev: list[str] = []
    stage_a_holdout: list[str] = []
    for band in BANDS:
        ids = sorted(
            (row["id"] for row in stage_a if row["band"] == band),
            key=split_key,
        )
        midpoint = len(ids) // 2
        stage_a_dev.extend(ids[:midpoint])
        stage_a_holdout.extend(ids[midpoint:])

    battles = sorted({row["battle"] for row in stage_b_decisions}, key=split_key)
    midpoint = len(battles) // 2
    stage_b_dev = battles[:midpoint]
    stage_b_holdout = battles[midpoint:]

    return {
        "version": 1,
        "seed": SPLIT_SEED,
        "rule": "Stage A: hash-sort ids within each band, first half dev; Stage B: hash-sort whole battle ids, first half dev.",
        "sources": {
            "stage_a_sample": sha256_file(STAGE_A / "sample.jsonl"),
            "stage_a_jev": sha256_file(STAGE_A / "jev.jsonl"),
            "stage_b_decisions": sha256_file(STAGE_B / "decisions-abyssal.jsonl"),
            "stage_b_results": sha256_file(STAGE_B / "results-abyssal.jsonl"),
        },
        "stage_a": {
            "dev_ids": stage_a_dev,
            "heldout_ids": stage_a_holdout,
            "dev_count": len(stage_a_dev),
            "heldout_count": len(stage_a_holdout),
            "dev_by_band": dict(
                Counter(
                    next(row["band"] for row in stage_a if row["id"] == rid)
                    for rid in stage_a_dev
                )
            ),
            "heldout_by_band": dict(
                Counter(
                    next(row["band"] for row in stage_a if row["id"] == rid)
                    for rid in stage_a_holdout
                )
            ),
        },
        "stage_b": {
            "dev_battles": stage_b_dev,
            "heldout_battles": stage_b_holdout,
            "dev_count": len(stage_b_dev),
            "heldout_count": len(stage_b_holdout),
        },
    }


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.96
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def argmax(probabilities: dict[str, float]) -> str | None:
    return (
        max(probabilities.items(), key=lambda item: (item[1], item[0]))[0]
        if probabilities
        else None
    )


def metrics(rows: list[tuple[str, dict[str, float], list[str]]]) -> dict:
    """Score (label, probabilities, support) rows; absent labels are top-1 misses and omitted from LL."""
    top1 = 0
    logloss: list[float] = []
    for label, probabilities, support in rows:
        if argmax(probabilities) == label:
            top1 += 1
        if label in support:
            logloss.append(-math.log(max(probabilities.get(label, 0.0), 1e-6)))
    n = len(rows)
    return {
        "n": n,
        "top1": top1 / n if n else 0.0,
        "top1_k": top1,
        "top1_wilson95": wilson(top1, n),
        "logloss": sum(logloss) / len(logloss) if logloss else None,
        "logloss_n": len(logloss),
        "coverage": len(logloss) / n if n else 0.0,
    }


def calibration_params() -> tuple[float, float]:
    rows = load_jsonl(STAGE_A / "calib.jsonl")
    switch_rows = [row for row in rows if row["switch_available"]]
    move_rows = [row for row in rows if row["kind"] == "move" and row["tera_available"]]
    return (
        sum(row["kind"] == "switch" for row in switch_rows) / len(switch_rows),
        sum(row["tera"] for row in move_rows) / len(move_rows),
    )


def stage_a_floor(
    row: dict, p_switch: float, p_tera: float, sets: dict
) -> dict[str, float]:
    return replay.usage_floor(
        row["player_options"],
        row["player_species_id"],
        sets,
        p_switch,
        p_tera,
    )


def stage_a_rows(split: dict) -> tuple[list[dict], dict[str, dict]]:
    sample = {row["id"]: row for row in load_jsonl(STAGE_A / "sample.jsonl")}
    jev = {row["id"]: row for row in load_jsonl(STAGE_A / "jev.jsonl")}
    dev = [sample[rid] for rid in split["stage_a"]["dev_ids"]]
    return dev, jev


def score_stage_a(split: dict) -> list[dict]:
    rows, jev = stage_a_rows(split)
    p_switch, p_tera = calibration_params()
    sets = json.loads(
        (
            ROOT
            / "pokechamp"
            / "poke_env"
            / "data"
            / "static"
            / "gen9"
            / "ou"
            / "sets_1000.json"
        ).read_text()
    )
    result: list[dict] = []
    for side, label_key, options_key in (
        ("player", "player_label", "player_options"),
        ("opponent", "opp_label", "opp_options"),
    ):
        observed: list[tuple[str, dict[str, float], list[str]]] = []
        usage: list[tuple[str, dict[str, float], list[str]]] = []
        for row in rows:
            answer = jev[row["id"]][side]
            options = row[options_key]
            observed.append((row[label_key], answer["probabilities"], options))
            if side == "player":
                floor = stage_a_floor(row, p_switch, p_tera, sets)
            else:
                floor = replay.usage_floor(
                    options,
                    row["opp_species_id"],
                    sets,
                    p_switch,
                    p_tera,
                )
            usage.append((row[label_key], floor, options))
        result.append(
            {
                "dataset": "stage_a_dev",
                "component": side,
                "arm": "jev_existing",
                **metrics(observed),
            }
        )
        result.append(
            {
                "dataset": "stage_a_dev",
                "component": side,
                "arm": "usage_floor",
                **metrics(usage),
            }
        )
        if side == "opponent":
            result.extend(score_tempering(observed, usage, "stage_a_dev", side))
    return result


def score_tempering(
    observed: list[tuple[str, dict[str, float], list[str]]],
    usage: list[tuple[str, dict[str, float], list[str]]],
    dataset: str,
    component: str,
) -> list[dict]:
    best: tuple[float, float] | None = None
    for step in range(21):
        alpha = step / 20
        mixed = []
        for (label, probabilities, support), (_, floor, _) in zip(observed, usage):
            keys = set(probabilities) | set(floor)
            p = {
                key: alpha * probabilities.get(key, 0.0)
                + (1 - alpha) * floor.get(key, 0.0)
                for key in keys
            }
            mixed.append((label, p, support))
        score = metrics(mixed)["logloss"]
        if score is not None and (best is None or score < best[0]):
            best = (score, alpha)
    assert best is not None
    alpha = best[1]
    mixed = []
    for (label, probabilities, support), (_, floor, _) in zip(observed, usage):
        keys = set(probabilities) | set(floor)
        p = {
            key: alpha * probabilities.get(key, 0.0) + (1 - alpha) * floor.get(key, 0.0)
            for key in keys
        }
        mixed.append((label, p, support))
    return [
        {
            "dataset": dataset,
            "component": component,
            "arm": f"dev_fit_mixture_alpha={alpha:.2f}",
            **metrics(mixed),
        }
    ]


def replay_actions(path: Path) -> dict[int, tuple[str, str | None]]:
    """Return turn -> (opponent action, active opponent species id)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    marker = '<script type="text/plain" class="battle-log-data">'
    payload = text.split(marker, 1)[1].split("</script>", 1)[0]
    turn = 0
    active: str | None = None
    actions: dict[int, tuple[str, str | None]] = {}
    for line in __import__("html").unescape(payload).splitlines():
        if line.startswith("|turn|"):
            turn = int(line.split("|")[2])
        elif line.startswith("|switch|p2a:"):
            parts = line.split("|")
            species = parts[3].split(",", 1)[0].strip()
            active = replay.to_id(species)
            actions[turn] = (f"switch {active}", active)
        elif line.startswith("|move|p2a:"):
            actions[turn] = (f"move {replay.to_id(line.split('|')[3])}", active)
    return actions


def stage_b_rows(split: dict) -> list[tuple[dict, str, str | None]]:
    decisions = load_jsonl(STAGE_B / "decisions-abyssal.jsonl")
    results = {
        row["battle"]: row for row in load_jsonl(STAGE_B / "results-abyssal.jsonl")
    }
    replay_cache: dict[str, dict[int, tuple[str, str | None]]] = {}
    out = []
    dev_battles = set(split["stage_b"]["dev_battles"])
    for decision in decisions:
        if decision["battle"] not in dev_battles or decision.get("fallback"):
            continue
        if decision["battle"] not in replay_cache:
            replay_cache[decision["battle"]] = replay_actions(
                POKE / results[decision["battle"]]["replay"]
            )
        action, species = replay_cache[decision["battle"]].get(
            decision["turn"], (None, None)
        )
        if action is not None:
            out.append((decision, action, species))
    return out


def score_stage_b(split: dict) -> list[dict]:
    rows = stage_b_rows(split)
    observed = []
    for decision, label, _species in rows:
        probabilities = decision.get("opponent") or {}
        observed.append((label, probabilities, list(probabilities)))
    return [
        {
            "dataset": "stage_b_dev",
            "component": "opponent",
            "arm": "jev_existing",
            **metrics(observed),
        }
    ]


def markdown_table(rows: list[dict]) -> str:
    lines = [
        "| Dataset | Component | Arm | N | Coverage | Top-1 | Log-loss |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        top = f"{row['top1']:.4f}"
        loss = "—" if row["logloss"] is None else f"{row['logloss']:.4f}"
        lines.append(
            f"| {row['dataset']} | {row['component']} | {row['arm']} | {row['n']} | "
            f"{row['coverage']:.4f} | {top} | {loss} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-split", type=Path)
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    split = make_split()
    if args.write_split:
        args.write_split.write_text(json.dumps(split, indent=2) + "\n")
        print(f"WROTE_SPLIT {args.write_split}")
    if args.dev:
        rows = score_stage_a(split) + score_stage_b(split)
        if args.json:
            print(json.dumps(rows, indent=2, sort_keys=True))
        else:
            print(markdown_table(rows))
    if not args.write_split and not args.dev:
        print(json.dumps(split, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
