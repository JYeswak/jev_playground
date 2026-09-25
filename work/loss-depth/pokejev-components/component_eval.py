#!/usr/bin/env python3
"""Keyless component-level evaluation for PokéJev loss-depth work.

The split is deterministic and label-blind: Stage A rows are split 250/250 per
Elo band and Stage B is split by whole battle, 100/100 battles. This file never
calls Jev and never runs battles. It can emit the frozen split manifest and score
the dev and frozen-alpha held-out sides of the component ground truths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
from collections import Counter
from pathlib import Path

COMPONENT_DIR = Path(__file__).resolve().parent
ROOT = COMPONENT_DIR.parents[2]
POKE = ROOT / "work" / "poke-jev"
POKECHAMP_SETS = Path(
    os.environ.get(
        "POKECHAMP_SETS_PATH",
        str(
            ROOT
            / "pokechamp"
            / "poke_env"
            / "data"
            / "static"
            / "gen9"
            / "ou"
            / "sets_1000.json"
        ),
    )
)
STAGE_A = POKE / "stage-a"
STAGE_B = POKE / "stage-b"
SPLIT_SEED = "pokejev-component-split-v1"
BANDS = ("1200-1399", "1400-1599", "1600-1799", "1800+")
SPLIT_PATH = COMPONENT_DIR / "decision-split-v1.json"
ALPHA_PATH = COMPONENT_DIR / "frozen-alpha-v1.json"
BOOTSTRAP_REPS = 5000
BOOTSTRAP_SEED = 20260925


def require_pokechamp_sets() -> None:
    if not POKECHAMP_SETS.is_file():
        print(
            "NOT_RUN (missing prerequisite: git clone "
            "https://github.com/sethkarten/pokechamp && "
            "git -C pokechamp checkout 0f84c46)",
            file=sys.stderr,
        )
        raise SystemExit(2)


if any(flag in sys.argv for flag in ("--dev", "--heldout", "--leaf-dev")):
    require_pokechamp_sets()

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


def stage_a_rows(split: dict, part: str = "dev") -> tuple[list[dict], dict[str, dict]]:
    sample = {row["id"]: row for row in load_jsonl(STAGE_A / "sample.jsonl")}
    jev = {row["id"]: row for row in load_jsonl(STAGE_A / "jev.jsonl")}
    ids = split["stage_a"][f"{part}_ids"]
    return [sample[rid] for rid in ids], jev


def stage_a_component_rows(
    split: dict, part: str
) -> dict[
    str,
    tuple[
        list[tuple[str, dict[str, float], list[str]]],
        list[tuple[str, dict[str, float], list[str]]],
    ],
]:
    rows, jev = stage_a_rows(split, part)
    p_switch, p_tera = calibration_params()
    sets = json.loads(POKECHAMP_SETS.read_text())
    result = {}
    for side, label_key, options_key in (
        ("player", "player_label", "player_options"),
        ("opponent", "opp_label", "opp_options"),
    ):
        observed = []
        usage = []
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
        result[side] = (observed, usage)
    return result


def score_stage_a(split: dict) -> list[dict]:
    result: list[dict] = []
    for side, (observed, usage) in stage_a_component_rows(split, "dev").items():
        result.extend(
            [
                {
                    "dataset": "stage_a_dev",
                    "component": side,
                    "arm": "jev_existing",
                    **metrics(observed),
                },
                {
                    "dataset": "stage_a_dev",
                    "component": side,
                    "arm": "usage_floor",
                    **metrics(usage),
                },
            ]
        )
        if side == "opponent":
            result.extend(score_tempering(observed, usage, "stage_a_dev", side))
    return result


def mixed_rows(
    observed: list[tuple[str, dict[str, float], list[str]]],
    usage: list[tuple[str, dict[str, float], list[str]]],
    alpha: float,
) -> list[tuple[str, dict[str, float], list[str]]]:
    return [
        (
            label,
            {
                key: alpha * probabilities.get(key, 0.0)
                + (1 - alpha) * floor.get(key, 0.0)
                for key in set(probabilities) | set(floor)
            },
            support,
        )
        for (label, probabilities, support), (_, floor, _) in zip(observed, usage)
    ]


def fit_alpha(
    observed: list[tuple[str, dict[str, float], list[str]]],
    usage: list[tuple[str, dict[str, float], list[str]]],
) -> float:
    best: tuple[float, float] | None = None
    for step in range(21):
        alpha = step / 20
        score = metrics(mixed_rows(observed, usage, alpha))["logloss"]
        if score is not None and (best is None or score < best[0]):
            best = (score, alpha)
    assert best is not None
    return best[1]


def score_tempering(
    observed: list[tuple[str, dict[str, float], list[str]]],
    usage: list[tuple[str, dict[str, float], list[str]]],
    dataset: str,
    component: str,
) -> list[dict]:
    alpha = fit_alpha(observed, usage)
    return [
        {
            "dataset": dataset,
            "component": component,
            "arm": f"dev_fit_mixture_alpha={alpha:.2f}",
            **metrics(mixed_rows(observed, usage, alpha)),
        }
    ]


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot calculate a percentile from no values")
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def row_values(
    rows: list[tuple[str, dict[str, float], list[str]]],
    include_out_of_support: bool = False,
) -> tuple[list[int], list[float | None]]:
    tops = []
    losses = []
    for label, probabilities, support in rows:
        tops.append(int(argmax(probabilities) == label))
        losses.append(
            -math.log(max(probabilities.get(label, 0.0), 1e-6))
            if include_out_of_support or label in support
            else None
        )
    return tops, losses


def all_logloss(rows: list[tuple[str, dict[str, float], list[str]]]) -> float:
    return sum(
        -math.log(max(probabilities.get(label, 0.0), 1e-6))
        for label, probabilities, _support in rows
    ) / len(rows)


def bootstrap_heldout(
    observed: list[tuple[str, dict[str, float], list[str]]],
    usage: list[tuple[str, dict[str, float], list[str]]],
    alpha: float,
    component: str,
) -> dict:
    mixed = mixed_rows(observed, usage, alpha)
    mixed_tops, mixed_losses = row_values(mixed, include_out_of_support=True)
    floor_tops, floor_losses = row_values(usage, include_out_of_support=True)
    n = len(mixed)
    rng = random.Random(BOOTSTRAP_SEED + (0 if component == "player" else 1))
    mixed_top_samples = []
    floor_top_samples = []
    top_deltas = []
    mixed_loss_samples = []
    floor_loss_samples = []
    loss_deltas = []
    for _ in range(BOOTSTRAP_REPS):
        mixed_top = floor_top = 0
        mixed_loss = floor_loss = 0.0
        valid = 0
        for _ in range(n):
            index = rng.randrange(n)
            mixed_top += mixed_tops[index]
            floor_top += floor_tops[index]
            if mixed_losses[index] is not None:
                mixed_loss += mixed_losses[index]
                floor_loss += floor_losses[index]
                valid += 1
        mixed_top_rate = mixed_top / n
        floor_top_rate = floor_top / n
        mixed_top_samples.append(mixed_top_rate)
        floor_top_samples.append(floor_top_rate)
        top_deltas.append(mixed_top_rate - floor_top_rate)
        if valid:
            mixed_loss_rate = mixed_loss / valid
            floor_loss_rate = floor_loss / valid
            mixed_loss_samples.append(mixed_loss_rate)
            floor_loss_samples.append(floor_loss_rate)
            loss_deltas.append(mixed_loss_rate - floor_loss_rate)
    mixed_metrics = metrics(mixed)
    floor_metrics = metrics(usage)
    mixed_logloss = all_logloss(mixed)
    floor_logloss = all_logloss(usage)
    return {
        "dataset": "stage_a_heldout",
        "component": component,
        "arm": f"frozen_mixture_alpha={alpha:.2f}",
        "n": n,
        "coverage": mixed_metrics["coverage"],
        "top1": mixed_metrics["top1"],
        "top1_bootstrap95": [
            percentile(mixed_top_samples, 0.025),
            percentile(mixed_top_samples, 0.975),
        ],
        "logloss": mixed_logloss,
        "logloss_n": n,
        "logloss_bootstrap95": [
            percentile(mixed_loss_samples, 0.025),
            percentile(mixed_loss_samples, 0.975),
        ],
        "usage_floor": {
            "top1": floor_metrics["top1"],
            "logloss": floor_logloss,
            "logloss_n": n,
            "coverage": floor_metrics["coverage"],
            "top1_bootstrap95": [
                percentile(floor_top_samples, 0.025),
                percentile(floor_top_samples, 0.975),
            ],
            "logloss_bootstrap95": [
                percentile(floor_loss_samples, 0.025),
                percentile(floor_loss_samples, 0.975),
            ],
        },
        "paired_against": "usage_floor",
        "paired_top1_delta": mixed_metrics["top1"] - floor_metrics["top1"],
        "paired_top1_delta_bootstrap95": [
            percentile(top_deltas, 0.025),
            percentile(top_deltas, 0.975),
        ],
        "paired_logloss_delta": mixed_logloss - floor_logloss,
        "paired_logloss_delta_bootstrap95": [
            percentile(loss_deltas, 0.025),
            percentile(loss_deltas, 0.975),
        ],
        "bootstrap_reps": BOOTSTRAP_REPS,
        "bootstrap_seed": BOOTSTRAP_SEED + (0 if component == "player" else 1),
    }


def score_stage_a_heldout(split: dict) -> list[dict]:
    frozen = json.loads(ALPHA_PATH.read_text())
    components = stage_a_component_rows(split, "heldout")
    return [
        bootstrap_heldout(
            observed,
            usage,
            float(frozen["components"][side]["alpha"]),
            side,
        )
        for side, (observed, usage) in components.items()
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


def auc(scores: list[tuple[float, bool]]) -> float:
    positives = [score for score, label in scores if label]
    negatives = [score for score, label in scores if not label]
    if not positives or not negatives:
        raise ValueError("AUC requires both eventual-outcome classes")
    wins = sum(
        1 if positive > negative else 0.5 if positive == negative else 0
        for positive in positives
        for negative in negatives
    )
    return wins / (len(positives) * len(negatives))


def stage_b_leaf_rows(split: dict) -> tuple[list[tuple[str, float, bool]], dict]:
    decisions = load_jsonl(STAGE_B / "decisions-abyssal.jsonl")
    results = {
        row["battle"]: row for row in load_jsonl(STAGE_B / "results-abyssal.jsonl")
    }
    dev_battles = set(split["stage_b"]["dev_battles"])
    eligible = []
    total = fallback = missing = 0
    for decision in decisions:
        if decision["battle"] not in dev_battles:
            continue
        total += 1
        if decision.get("fallback"):
            fallback += 1
            continue
        result = results.get(decision["battle"])
        values = decision.get("values") or {}
        chosen = decision.get("chosen")
        if (
            result is None
            or not result.get("finished")
            or not isinstance(result.get("won"), bool)
            or not values
            or chosen not in values
        ):
            missing += 1
            continue
        eligible.append((decision["battle"], float(values[chosen]), result["won"]))
    return eligible, {
        "total_decisions": total,
        "fallback_decisions": fallback,
        "missing_or_unusable_decisions": missing,
    }


def bootstrap_leaf_auc(
    rows: list[tuple[str, float, bool]],
) -> tuple[float, list[float]]:
    by_battle: dict[str, list[tuple[float, bool]]] = {}
    for battle, value, won in rows:
        by_battle.setdefault(battle, []).append((value, won))
    battles = sorted(by_battle)
    rng = random.Random(BOOTSTRAP_SEED + 2)
    samples = []
    for _ in range(BOOTSTRAP_REPS):
        sampled = []
        for _ in battles:
            sampled.extend(by_battle[rng.choice(battles)])
        if any(label for _, label in sampled) and any(
            not label for _, label in sampled
        ):
            samples.append(auc(sampled))
    return auc([(value, won) for _, value, won in rows]), samples


def score_leaf_value(split: dict) -> dict:
    rows, exclusions = stage_b_leaf_rows(split)
    point, samples = bootstrap_leaf_auc(rows)
    return {
        "dataset": "stage_b_dev",
        "component": "leaf_value",
        "arm": "chosen_leaf_value_vs_eventual_battle_outcome",
        "n_decisions": len(rows),
        "n_battles": len({battle for battle, _, _ in rows}),
        "positive_decisions": sum(won for _, _, won in rows),
        "negative_decisions": sum(not won for _, _, won in rows),
        "auc": point,
        "auc_bootstrap95": [
            percentile(samples, 0.025),
            percentile(samples, 0.975),
        ],
        "bootstrap_reps": BOOTSTRAP_REPS,
        "bootstrap_seed": BOOTSTRAP_SEED + 2,
        "exclusions": exclusions,
        "boundary": "The chosen leaf value is scored against the eventual battle outcome; candidate values not chosen are not treated as counterfactual labels.",
    }


def leaf_markdown(row: dict) -> str:
    lo, hi = row["auc_bootstrap95"]
    return (
        "| Component | Decisions | Battles | Positive | Negative | AUC (95% CI) | "
        "Fallback decisions |\n"
        "|---|---:|---:|---:|---:|---:|---:|\n"
        f"| {row['component']} | {row['n_decisions']} | {row['n_battles']} | "
        f"{row['positive_decisions']} | {row['negative_decisions']} | "
        f"{row['auc']:.4f} [{lo:.4f}, {hi:.4f}] | "
        f"{row['exclusions']['fallback_decisions']} |"
    )


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


def heldout_markdown(rows: list[dict]) -> str:
    lines = [
        (
            "| Component | N | Alpha | Floor top-1 | Mixture top-1 (95% CI) | "
            "Paired Δ top-1 (95% CI) | Floor log-loss | Mixture log-loss (95% CI) | "
            "Paired Δ log-loss (95% CI) |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    def fmt(interval: list[float]) -> str:
        return f"[{interval[0]:.4f}, {interval[1]:.4f}]"

    for row in rows:
        floor = row["usage_floor"]
        lines.append(
            f"| {row['component']} | {row['n']} | "
            f"{row['arm'].rsplit('=', 1)[-1]} | {floor['top1']:.4f} | "
            f"{row['top1']:.4f} {fmt(row['top1_bootstrap95'])} | "
            f"{row['paired_top1_delta']:+.4f} "
            f"{fmt(row['paired_top1_delta_bootstrap95'])} | "
            f"{floor['logloss']:.4f} | {row['logloss']:.4f} "
            f"{fmt(row['logloss_bootstrap95'])} | "
            f"{row['paired_logloss_delta']:+.4f} "
            f"{fmt(row['paired_logloss_delta_bootstrap95'])} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-split", type=Path)
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--heldout", action="store_true")
    parser.add_argument("--leaf-dev", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.write_split:
        split = make_split()
    elif args.dev or args.heldout or args.leaf_dev:
        split = json.loads(SPLIT_PATH.read_text())
    else:
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
    if args.heldout:
        rows = score_stage_a_heldout(split)
        if args.json:
            print(json.dumps(rows, indent=2, sort_keys=True))
        else:
            print(heldout_markdown(rows))
    if args.leaf_dev:
        row = score_leaf_value(split)
        if args.json:
            print(json.dumps(row, indent=2, sort_keys=True))
        else:
            print(leaf_markdown(row))
    if not args.write_split and not args.dev and not args.heldout and not args.leaf_dev:
        print(json.dumps(split, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
