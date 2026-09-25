#!/usr/bin/env python3
"""Bootstrap Mann-Whitney power from the committed random baseline rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from importlib import import_module
from pathlib import Path

np = import_module("numpy")
mannwhitneyu = import_module("scipy.stats").mannwhitneyu


def load_random(path: Path) -> list[int]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    values = [
        500 if not row["goal_reached"] else int(row["macros_after_start"])
        for row in rows
        if row["policy"] == "random"
    ]
    if not values:
        raise ValueError("baseline has no random rows")
    return values


def power(
    random_values: list[int], n: int, shift: int, simulations: int, seed: int
) -> float:
    rng = np.random.default_rng(seed)
    rejections = 0
    for _ in range(simulations):
        control = rng.choice(random_values, n, replace=True)
        treatment = np.maximum(1, rng.choice(random_values, n, replace=True) - shift)
        p_value = mannwhitneyu(
            treatment, control, alternative="less", method="asymptotic"
        ).pvalue
        rejections += p_value < 0.05
    return rejections / simulations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rows", default="work/pokeagent-emerald/baseline-results.jsonl"
    )
    parser.add_argument("--n", type=int, default=38)
    parser.add_argument("--simulations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--shifts", type=int, nargs="+", default=[50, 75])
    args = parser.parse_args()

    rows_path = Path(args.rows)
    values = load_random(rows_path)
    receipt = {
        "rows_sha256": hashlib.sha256(rows_path.read_bytes()).hexdigest(),
        "random_n": len(values),
        "random_values": values,
        "n_per_arm": args.n,
        "simulations": args.simulations,
        "seed": args.seed,
        "alpha": 0.05,
        "alternative": "treatment macro count lower than random",
        "power_by_shift": {
            str(shift): power(
                values, args.n, shift, args.simulations, args.seed + shift
            )
            for shift in args.shifts
        },
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
