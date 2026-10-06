#!/usr/bin/env python3
"""Measure marginal classifier-family cost from committed contract to ship verdict."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from telemetry import HOME, MeasurementError, _bead_ids
from telemetry import session_metrics as _session_metrics

ROOT = Path(__file__).resolve().parents[2]
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
AXES = (
    "wall_seconds",
    "files_touched",
    "commits",
    "agent_turns",
    "model_calls",
    "spend_usd",
)


def _git(root: Path, *args: str, check: bool = True) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MeasurementError(f"git {' '.join(args)} failed: {exc}") from exc
    if check and result.returncode:
        detail = result.stderr.strip()
        raise MeasurementError(
            f"git {' '.join(args)} failed: {detail or result.returncode}"
        )
    return result.stdout


def _commits_for_path(root: Path, path: str) -> list[tuple[str, int]]:
    output = _git(
        root, "log", "--first-parent", "--reverse", "--format=%H%x09%ct", "--", path
    )
    result: list[tuple[str, int]] = []
    for line in output.splitlines():
        sha, sep, epoch = line.partition("\t")
        if not sep:
            raise MeasurementError(f"invalid git log row for {path}")
        result.append((sha, int(epoch)))
    return result


def _first_parent_order(root: Path) -> dict[str, int]:
    commits = _git(root, "rev-list", "--first-parent", "--reverse", "HEAD").splitlines()
    return {commit: position for position, commit in enumerate(commits)}


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=root,
            capture_output=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MeasurementError(f"cannot verify commit order: {exc}") from exc
    if result.returncode not in (0, 1):
        raise MeasurementError(
            result.stderr.decode("utf-8", errors="replace").strip()
            or "git ancestry check failed"
        )
    return result.returncode == 0


def _family_candidates(root: Path) -> list[dict[str, Any]]:
    contracts = sorted(
        path
        for path in (root / "kit" / "contracts").glob("*.json")
        if path.stem != "schema"
    )
    candidates: list[dict[str, Any]] = []
    for contract in contracts:
        contract_rel = contract.relative_to(root).as_posix()
        ship_rel = f"work/ship/{contract.stem}/SHIP.md"
        start_commits = _commits_for_path(root, contract_rel)
        end_commits = _commits_for_path(root, ship_rel)
        if not start_commits:
            raise MeasurementError(
                f"family {contract.stem}: contract start commit missing ({contract_rel})"
            )
        if not end_commits:
            continue
        start_sha, start_epoch = start_commits[0]
        end_sha, end_epoch = end_commits[0]
        if not _is_ancestor(root, start_sha, end_sha):
            raise MeasurementError(
                f"family {contract.stem}: ship verdict is not descended from contract commit"
            )
        ship_text = _git(root, "show", f"{end_sha}:{ship_rel}")
        beads = _bead_ids(ship_text)
        if not beads:
            raise MeasurementError(
                f"family {contract.stem}: SHIP.md must cite its family bead IDs"
            )
        candidates.append(
            {
                "family": contract.stem,
                "contract_path": contract_rel,
                "ship_path": ship_rel,
                "start_sha": start_sha,
                "start_epoch": start_epoch,
                "end_sha": end_sha,
                "end_epoch": end_epoch,
                "beads": beads,
            }
        )
    history_order = _first_parent_order(root) if candidates else {}
    return sorted(
        candidates, key=lambda item: (history_order[item["end_sha"]], item["family"])
    )


def _verify_prereg(root: Path, candidates: list[dict[str, Any]]) -> tuple[str, str]:
    prereg_path = "work/next-family-cost/PREREG.md"
    commits = _commits_for_path(root, prereg_path)
    if not commits:
        raise MeasurementError("PREREG.md has no committed history")
    if len(candidates) < 2:
        raise MeasurementError(
            "second family ship verdict is missing; chronology cannot yet be verified"
        )
    prereg_sha = commits[-1][0]
    second = candidates[1]
    second_sha = second["start_sha"]
    if not _is_ancestor(root, prereg_sha, second_sha):
        raise MeasurementError(
            "PREREG.md was committed after the second family's contract commit"
        )
    return prereg_sha, second_sha


def _git_metrics(root: Path, item: dict[str, Any]) -> dict[str, Any]:
    start_parent = _git(root, "rev-parse", f"{item['start_sha']}^", check=False).strip()
    revision_range = (
        f"{start_parent}..{item['end_sha']}" if start_parent else item["end_sha"]
    )
    commits = _git(
        root, "rev-list", "--first-parent", "--reverse", revision_range
    ).splitlines()
    family_beads = set(item["beads"])
    attributed_commits: list[str] = []
    changed_paths: set[str] = set()
    for commit in commits:
        message = _git(root, "show", "-s", "--format=%B", commit)
        if not family_beads.intersection(_bead_ids(message)):
            continue
        attributed_commits.append(commit)
        parent = _git(root, "rev-parse", f"{commit}^1", check=False).strip()
        base = parent if parent else EMPTY_TREE
        changed_paths.update(
            _git(root, "diff", "--name-only", base, commit).splitlines()
        )
    if not attributed_commits:
        raise MeasurementError(
            f"family {item['family']}: no span commits cite its bead IDs"
        )
    wall_seconds = item["end_epoch"] - item["start_epoch"]
    if wall_seconds < 0:
        raise MeasurementError(
            f"family {item['family']}: ship verdict timestamp precedes contract commit"
        )
    bead_source = {"beads": item["beads"], "commits": attributed_commits}
    return {
        "wall_seconds": wall_seconds,
        "files_touched": len(changed_paths),
        "commits": len(attributed_commits),
        "wall_source": {
            "start_commit": item["start_sha"],
            "end_commit": item["end_sha"],
        },
        "files_source": bead_source,
        "commits_source": bead_source,
    }


def measure(
    root: Path = ROOT, *, families: int = 3, home: Path = HOME
) -> dict[str, Any]:
    if families != 3:
        raise MeasurementError(
            "the preregistered comparison requires exactly three families"
        )
    candidates = _family_candidates(root)
    if len(candidates) < families:
        raise MeasurementError(
            f"only {len(candidates)} committed family ship verdicts found; need {families}"
        )
    candidates = candidates[:families]
    prereg_sha, second_contract_sha = _verify_prereg(root, candidates)
    for index, item in enumerate(candidates):
        if index > 0 and not _is_ancestor(root, prereg_sha, item["start_sha"]):
            raise MeasurementError(
                f"PREREG.md is not committed before {item['family']} contract"
            )
    results: list[dict[str, Any]] = []
    for item in candidates:
        metrics = _git_metrics(root, item)
        turns, calls, spend, session_sources = _session_metrics(
            item["beads"], item["start_epoch"], item["end_epoch"], root=root, home=home
        )
        metrics.update(
            {
                "family": item["family"],
                "contract_commit": item["start_sha"],
                "ship_commit": item["end_sha"],
                "beads": item["beads"],
                "agent_turns": turns,
                "agent_turns_source": session_sources,
                "model_calls": calls,
                "model_calls_source": session_sources,
                "spend_usd": round(spend, 8),
                "spend_source": session_sources,
            }
        )
        results.append(metrics)

    baseline = results[0]
    ratios: list[dict[str, Any]] = []
    for result in results[1:]:
        ratio_row: dict[str, Any] = {"family": result["family"], "axes": {}}
        for axis in AXES:
            base = baseline[axis]
            if base <= 0:
                raise MeasurementError(
                    f"family 1 has a zero {axis} baseline; ratio is undefined"
                )
            ratio_row["axes"][axis] = {
                "ratio": round(result[axis] / base, 6),
                "ceiling": 1.0,
                "pass": result[axis] / base <= 1.0,
                "baseline_source": baseline.get(
                    f"{axis}_source", baseline["contract_commit"]
                ),
                "family_source": result.get(
                    f"{axis}_source", result["contract_commit"]
                ),
            }
        ratios.append(ratio_row)
    passed = all(axis["pass"] for row in ratios for axis in row["axes"].values())
    return {
        "schema": "next-family-cost.v1",
        "status": "PASS" if passed else "FAIL",
        "clause_met": passed,
        "prereg_commit": prereg_sha,
        "second_contract_commit": second_contract_sha,
        "ceiling": "each axis for families 2 and 3 <= 1.00x family 1",
        "families": results,
        "ratios": ratios,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--families", type=int, required=True)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)
    try:
        result = measure(families=args.families)
    except MeasurementError as exc:
        envelope = {
            "schema": "next-family-cost.v1",
            "status": "ERROR",
            "clause_met": False,
            "error": str(exc),
        }
        print(
            json.dumps(envelope, sort_keys=True)
            if args.json_output
            else f"ERROR: {exc}"
        )
        return 1
    print(
        json.dumps(result, sort_keys=True, indent=2)
        if args.json_output
        else result["status"]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
