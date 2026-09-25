"""Compute oracle@N and frozen floors from official result.txt rows.

Only result.txt, traj.jsonl and runtime.log members are read. Raw member text is never printed
or written to the repository; the receipt contains candidate IDs, scores and counts only.
"""

from __future__ import annotations

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from range_zip import open_remote_zip, read_member_bytes, task_key

ROOT = Path(__file__).resolve().parent
POOL = ROOT / "pool.json"
OUT = ROOT / "floor_receipt.json"
SEED = 20250925
SUCCESS_RE = re.compile(
    r"(?:task\s+)?(?:completed|succeeded|success(?:ful|fully)?)", re.IGNORECASE
)


def member_map(archive) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for name in archive.namelist():
        if name.endswith("/result.txt"):
            out.setdefault(task_key(name), {})["result"] = name
        elif name.endswith("/traj.jsonl"):
            out.setdefault(task_key(name.replace("/traj.jsonl", "/result.txt")), {})[
                "traj"
            ] = name
        elif name.endswith("/runtime.log"):
            out.setdefault(task_key(name.replace("/runtime.log", "/result.txt")), {})[
                "runtime"
            ] = name
    return out


def stable_index(task: str, count: int) -> int:
    digest = hashlib.sha256(f"{SEED}:{task}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % count


def read_result(archive, remote, member: str) -> float:
    value = (
        read_member_bytes(archive, remote, member).decode("utf-8", "replace").strip()
    )
    try:
        numeric = float(value)
    except ValueError as exc:
        raise ValueError(f"{member}: unexpected result {value!r}") from exc
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{member}: unexpected result {value!r}")
    return numeric


def main() -> None:
    pool = json.loads(POOL.read_text())
    selected = pool["selected"]
    runs: dict[str, dict[str, Any]] = {}
    for candidate in selected:
        archive, remote = open_remote_zip(candidate["url"])
        members = member_map(archive)
        rows = {
            task: read_result(archive, remote, info["result"])
            for task, info in members.items()
            if "result" in info
        }
        runs[candidate["archive"]] = {
            "url": candidate["url"],
            "rows": rows,
            "members": members,
            "remote": remote,
            "archive": archive,
        }

    candidate_names = [str(row["archive"]) for row in selected]
    tasks = sorted(set.intersection(*(set(run["rows"]) for run in runs.values())))
    if len(tasks) != 361:
        raise SystemExit(f"joined tasks={len(tasks)}, expected 361")

    def read_attributes(item: tuple[str, str]) -> tuple[str, str, int, bool]:
        name, task = item
        run = runs[name]
        info = run["members"][task]
        traj = read_member_bytes(run["archive"], run["remote"], info["traj"])
        runtime = read_member_bytes(run["archive"], run["remote"], info["runtime"])
        return (
            name,
            task,
            len(traj.decode("utf-8", "replace").splitlines()),
            bool(SUCCESS_RE.search(runtime[-12000:].decode("utf-8", "replace"))),
        )

    attributes: dict[tuple[str, str], tuple[int, bool]] = {}
    requests = [(name, task) for name in candidate_names for task in tasks]
    with ThreadPoolExecutor(max_workers=64) as executor:
        for name, task, steps, claims in executor.map(read_attributes, requests):
            attributes[(name, task)] = (steps, claims)

    picks: dict[str, dict[str, str]] = {}
    for task in tasks:
        candidates = [
            (name, runs[name]["rows"][task], *attributes[(name, task)])
            for name in candidate_names
        ]
        shortest = min(candidates, key=lambda row: (row[2], row[0]))[0]
        claims = sorted(row[0] for row in candidates if row[3])
        claims_pick = claims[0] if claims else candidate_names[0]
        picks[task] = {
            "random": candidate_names[stable_index(task, len(candidate_names))],
            "shortest": shortest,
            "claims_success": claims_pick,
            "claims_success_candidates": ",".join(claims),
        }

    def floor_stats(pick_key: str) -> dict[str, float]:
        total = sum(runs[picks[task][pick_key]]["rows"][task] for task in tasks)
        exact = sum(runs[picks[task][pick_key]]["rows"][task] >= 1.0 for task in tasks)
        return {
            "reward_sum": total,
            "mean_reward": total / len(tasks),
            "exact_tasks": exact,
        }

    per_task_oracle = {
        task: max(runs[name]["rows"][task] for name in candidate_names)
        for task in tasks
    }
    oracle_sum = sum(per_task_oracle.values())
    best_name = max(
        candidate_names,
        key=lambda name: (sum(runs[name]["rows"][task] for task in tasks), name),
    )
    best_sum = sum(runs[best_name]["rows"][task] for task in tasks)
    receipt = {
        "source": "xlangai/ubuntu_osworld_verified_trajs",
        "n": len(candidate_names),
        "tasks": len(tasks),
        "random_seed": SEED,
        "selected_archives": candidate_names,
        "selected_scores": {
            name: sum(runs[name]["rows"][task] for task in tasks)
            for name in candidate_names
        },
        "oracle_reward_sum": oracle_sum,
        "oracle_mean_reward": oracle_sum / len(tasks),
        "oracle_exact_tasks": sum(value >= 1.0 for value in per_task_oracle.values()),
        "best_single_archive": best_name,
        "best_single_reward_sum": best_sum,
        "best_single_mean_reward": best_sum / len(tasks),
        "best_single_exact_tasks": sum(
            runs[best_name]["rows"][task] >= 1.0 for task in tasks
        ),
        "floors": {
            key: floor_stats(key) for key in ["random", "shortest", "claims_success"]
        },
        "claims_success_no_match_tasks": sum(
            not picks[task]["claims_success_candidates"] for task in tasks
        ),
        "results_by_task": {
            task: {name: runs[name]["rows"][task] for name in candidate_names}
            for task in tasks
        },
        "picks": picks,
        "trajectory_step_counts": {
            name: {task: attributes[(name, task)][0] for task in tasks}
            for name in candidate_names
        },
        "read_boundary": ["traj.jsonl", "runtime.log", "result.txt"],
        "raw_text_committed": False,
        "network": "range GET only; no screenshot or other ZIP member read",
    }
    for run in runs.values():
        run["archive"].close()
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "n": receipt["n"],
                "tasks": receipt["tasks"],
                "selected_archives": candidate_names,
                "oracle_mean_reward": receipt["oracle_mean_reward"],
                "best_single": {
                    "archive": best_name,
                    "mean_reward": receipt["best_single_mean_reward"],
                    "exact_tasks": receipt["best_single_exact_tasks"],
                },
                "floors": receipt["floors"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
