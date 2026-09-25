"""Build compact untracked live states from allowed OSWorld members.

Output defaults to /tmp so raw trajectory text is never committed. Only traj.jsonl,
runtime.log and result.txt members are touched; result.txt is used for joining and
is not included in the live state.
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from range_zip import open_remote_zip, read_member_bytes, task_key


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
    opened: dict[str, tuple[object, object, dict[str, dict[str, str]]]] = {}
    try:
        for candidate in selected:
            archive, remote = open_remote_zip(candidate["url"])
            opened[candidate["archive"]] = (archive, remote, member_map(archive))
        tasks = sorted(
            set.intersection(
                *(set(members) for _archive, _remote, members in opened.values())
            )
        )

        def read_one(item: tuple[str, str]) -> tuple[str, str, dict[str, object]]:
            name, task = item
            archive, remote, members = opened[name]
            info = members[task]
            traj = compact_traj(read_member_bytes(archive, remote, info["traj"]))
            runtime = read_member_bytes(archive, remote, info["runtime"]).decode(
                "utf-8", "replace"
            )
            return (
                name,
                task,
                {"actions": traj, "runtime_tail": runtime[-args.runtime_tail :]},
            )

        states: dict[str, dict[str, object]] = {}
        requests = [
            (candidate["archive"], task) for task in tasks for candidate in selected
        ]
        with ThreadPoolExecutor(max_workers=64) as executor:
            for name, task, evidence in executor.map(read_one, requests):
                states.setdefault(task, {})[name] = evidence

        with Path(args.out).open("w", encoding="utf-8") as output:
            for task in tasks:
                candidates = [
                    {
                        "id": f"c{index}",
                        "archive": candidate["archive"],
                        **states[task][candidate["archive"]],
                    }
                    for index, candidate in enumerate(selected)
                ]
                output.write(
                    json.dumps(
                        {"task": task, "candidates": candidates}, ensure_ascii=False
                    )
                    + "\n"
                )
    finally:
        for archive, _remote, _members in opened.values():
            archive.close()
    print(
        json.dumps({"tasks": len(tasks), "out": args.out, "raw_text_committed": False})
    )


if __name__ == "__main__":
    main()
