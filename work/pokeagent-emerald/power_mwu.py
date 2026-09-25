#!/usr/bin/env python3
"""Bootstrap Mann-Whitney power from a committed baseline policy."""

from __future__ import annotations

import argparse
import hashlib
import json
from importlib import import_module
from pathlib import Path


def load_policy(path: Path, policy: str, cap: int) -> list[tuple[int, bool]]:
    """Load scored macro counts for one policy, capping only genuine goal failures."""
    values = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("policy") != policy:
            continue
        if row.get("child_error") is not None or row.get("final") is None:
            raise ValueError(f"{path} row {line_number} is not scored")
        if not row.get("scored", True):
            raise ValueError(f"{path} row {line_number} is marked unscored")
        reached = bool(row["goal_reached"])
        values.append((cap if not reached else int(row["macros_after_start"]), reached))
    if not values:
        raise ValueError(f"baseline has no rows for policy {policy!r}")
    return values


def power(
    control_values: list[tuple[int, bool]],
    n: int,
    shift: int,
    simulations: int,
    seed: int,
    cap: int,
    capped_stay: bool,
    fixed_control: bool,
) -> float:
    np = import_module("numpy")
    mannwhitneyu = import_module("scipy.stats").mannwhitneyu
    rng = np.random.default_rng(seed)
    rejections = 0
    control_fixed = np.array([value for value, _ in control_values])
    for _ in range(simulations):
        if fixed_control:
            control = control_fixed
        else:
            control_idx = rng.integers(0, len(control_values), size=n)
            control = np.array([control_values[i][0] for i in control_idx])
        treatment_idx = rng.integers(0, len(control_values), size=n)
        treatment = np.array([control_values[i][0] for i in treatment_idx])
        if capped_stay:
            treatment = np.where(
                np.array([control_values[i][1] for i in treatment_idx]),
                np.maximum(1, treatment - shift),
                cap,
            )
        else:
            treatment = np.maximum(1, treatment - shift)
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
    parser.add_argument("--control-policy", default="random")
    parser.add_argument("--cap", type=int, default=500)
    parser.add_argument("--n", type=int, default=80)
    parser.add_argument("--simulations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--shifts", type=int, nargs="+", default=[2, 5, 10])
    parser.add_argument("--capped-stay", action="store_true")
    parser.add_argument(
        "--fixed-control",
        action="store_true",
        help="Use the committed control rows as the fixed control arm",
    )
    args = parser.parse_args()

    rows_path = Path(args.rows)
    values = load_policy(rows_path, args.control_policy, args.cap)
    receipt = {
        "rows_sha256": hashlib.sha256(rows_path.read_bytes()).hexdigest(),
        "control_policy": args.control_policy,
        "control_n": len(values),
        "n_per_treatment_arm": args.n,
        "cap": args.cap,
        "simulations": args.simulations,
        "seed": args.seed,
        "alpha": 0.05,
        "capped_stay": args.capped_stay,
        "fixed_control": args.fixed_control,
        "alternative": "treatment macro count lower than control",
        "power_by_shift": {
            str(shift): power(
                values,
                args.n,
                shift,
                args.simulations,
                args.seed + shift,
                args.cap,
                args.capped_stay,
                args.fixed_control,
            )
            for shift in args.shifts
        },
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
