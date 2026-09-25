"""Compute oracle@N and frozen floors from official result.txt rows.

The only member bytes read are result.txt, traj.jsonl, and runtime.log. Raw member
text is never printed or written. floor_receipt.json contains task keys and
candidate IDs/counts only.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from range_zip import (
    archive_score,
    open_remote_zip,
    read_member_bytes,
    result_members,
    task_key,
)

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
            key = task_key(name)
            out.setdefault(key, {})["result"] = name
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


def read_result(archive, member: str, remote=None) -> float:
    source = (
        read_member_bytes(archive, remote, member)
        if remote is not None
        else archive.read(member)
    )
    value = source.decode("utf-8", "replace").strip()
    try:
        numeric = float(value)
    except ValueError as exc:
        raise ValueError(f"{member}: unexpected result {value!r}") from exc
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{member}: unexpected result {value!r}")
    return numeric


def main() -> None:
    pool = json.loads(POOL.read_text())
    selected = [row["archive"] for row in pool["selected"]]
    runs: dict[str, dict[str, Any]] = {}
    for archive_name in selected:
        url = next(
            row["url"] for row in pool["selected"] if row["archive"] == archive_name
        )
        archive, remote = open_remote_zip(url)
        try:
            members = member_map(archive)
            rows = {
                task: read_result(archive, info["result"], remote)
                for task, info in members.items()
                if "result" in info
            }
            runs[archive_name] = {
                "url": url,
                "rows": rows,
                "members": members,
                "fetched_bytes": remote.fetched_bytes,
                "archive": archive,
            }
        except Exception:
            archive.close()
            raise

    tasks = sorted(set.intersection(*(set(run["rows"]) for run in runs.values())))
    candidate_names = sorted(runs)
    picks: dict[str, dict[str, str | None]] = {}
    metadata: dict[str, dict[str, Any]] = {
        name: {"traj_steps": {}, "claims_success": {}} for name in candidate_names
    }
    for task in tasks:
        candidates = []
        for name in candidate_names:
            info = runs[name]["members"][task]
            traj = (
                runs[name]["archive"].read(info["traj"]).decode("utf-8", "replace")
                if "traj" in info
                else ""
            )
            runtime = (
                runs[name]["archive"].read(info["runtime"]).decode("utf-8", "replace")
                if "runtime" in info
                else ""
            )
            steps = len(traj.splitlines())
            claims = bool(SUCCESS_RE.search(runtime[-12000:]))
            metadata[name]["traj_steps"][task] = steps
            metadata[name]["claims_success"][task] = claims
            candidates.append((name, runs[name]["rows"][task], steps, claims))
        shortest = min(candidates, key=lambda x: (x[2], x[0]))[0]
        claims = sorted(
            name for name, _result, _steps, has_claim in candidates if has_claim
        )
        claims_pick = claims[0] if claims else candidate_names[0]
        random_pick = candidate_names[stable_index(task, len(candidate_names))]
        picks[task] = {
            "random": random_pick,
            "shortest": shortest,
            "claims_success": claims_pick,
            "claims_success_candidates": ",".join(claims),
        }

    def rate(pick_key: str) -> float:
        return sum(runs[picks[t][pick_key]]["rows"][t] for t in tasks) / len(tasks)

    oracle_success = sum(
        max(runs[name]["rows"][task] for name in candidate_names) for task in tasks
    )
    best_name = max(
        candidate_names,
        key=lambda name: (sum(runs[name]["rows"][task] for task in tasks), name),
    )
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
        "oracle_successes": oracle_success,
        "oracle_rate": oracle_success / len(tasks),
        "best_single_archive": best_name,
        "best_single_successes": sum(runs[best_name]["rows"][task] for task in tasks),
        "best_single_rate": rate(best_name)
        if False
        else sum(runs[best_name]["rows"][task] for task in tasks) / len(tasks),
        "floors": {
            key: {
                "successes": sum(runs[picks[t][key]]["rows"][t] for t in tasks),
                "rate": rate(key),
            }
            for key in ["random", "shortest", "claims_success"]
        },
        "claims_success_no_match_tasks": sum(
            not picks[t]["claims_success_candidates"] for t in tasks
        ),
        "results_by_task": {
            task: {name: runs[name]["rows"][task] for name in candidate_names}
            for task in tasks
        },
        "picks": picks,
        "trajectory_step_counts": {
            name: metadata[name]["traj_steps"] for name in candidate_names
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
                k: receipt[k]
                for k in [
                    "n",
                    "tasks",
                    "selected_scores",
                    "oracle_successes",
                    "best_single_archive",
                    "best_single_successes",
                    "floors",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
