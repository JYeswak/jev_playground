"""Build compact untracked live states from only traj.jsonl/runtime.log/result.txt members.

Output defaults to /tmp so raw trajectory text is never committed. Official result.txt
is read only for joining and is deliberately excluded from the live state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from range_zip import open_remote_zip, task_key


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


def compact_traj(raw: bytes) -> list[str]:
    out: list[str] = []
    for line in raw.decode("utf-8", "replace").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        action = row.get("action") or {}
        if not isinstance(action, dict):
            action = {"raw": str(action)}
        item = {
            "step": row.get("step_num"),
            "name": action.get("name"),
            "type": action.get("action_type"),
            "input": action.get("input"),
            "command": str(action.get("command", ""))[:240],
        }
        out.append(json.dumps(item, sort_keys=True, ensure_ascii=False))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", default="work/osw-bestofn/pool.json")
    parser.add_argument("--out", default="/tmp/jev-osw-bestofn-states.jsonl")
    parser.add_argument("--runtime-tail", type=int, default=1200)
    args = parser.parse_args()
    pool = json.loads(Path(args.pool).read_text())
    selected = pool["selected"]
    by_archive: dict[str, tuple[object, dict[str, dict[str, str]]]] = {}
    try:
        for candidate in selected:
            archive, _remote = open_remote_zip(candidate["url"])
            by_archive[candidate["archive"]] = (archive, member_map(archive))
        tasks = sorted(
            set.intersection(
                *(set(members) for _archive, members in by_archive.values())
            )
        )
        with Path(args.out).open("w", encoding="utf-8") as output:
            for task in tasks:
                candidates = []
                for index, candidate in enumerate(selected):
                    archive, members = by_archive[candidate["archive"]]
                    info = members[task]
                    traj = (
                        compact_traj(archive.read(info["traj"]))
                        if "traj" in info
                        else []
                    )
                    runtime = (
                        archive.read(info["runtime"]).decode("utf-8", "replace")
                        if "runtime" in info
                        else ""
                    )
                    candidates.append(
                        {
                            "id": f"c{index}",
                            "archive": candidate["archive"],
                            "actions": traj,
                            "runtime_tail": runtime[-args.runtime_tail :],
                        }
                    )
                output.write(
                    json.dumps(
                        {"task": task, "candidates": candidates}, ensure_ascii=False
                    )
                    + "\n"
                )
    finally:
        for archive, _members in by_archive.values():
            archive.close()
    print(
        json.dumps({"tasks": len(tasks), "out": args.out, "raw_text_committed": False})
    )


if __name__ == "__main__":
    main()
