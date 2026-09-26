#!/usr/bin/env python3
"""Render the README measured-results table from committed receipts and scorers."""

from __future__ import annotations
import re

import argparse
import json
import subprocess
import sys
from pathlib import Path

START = "<!-- BEGIN GENERATED: measured-wins -->"
END = "<!-- END GENERATED: measured-wins -->"


def run_scorer(root: Path, script: str, *args: str) -> str:
    result = subprocess.run(
        [sys.executable, str(root / script), *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{script} exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout


def table_cells(output: str, label: str) -> list[str]:
    prefix = f"| {label} |"
    for line in output.splitlines():
        if line.startswith(prefix):
            return [cell.strip() for cell in line.strip().strip("|").split("|")]
    raise ValueError(f"scorer output has no row for {label!r}")


def banking77(root: Path) -> tuple[str, str]:
    output = run_scorer(
        root, "work/choice-banking77/score.py", "--set", "full-prompted"
    )
    jev = table_cells(output, "jev")
    haiku = table_cells(output, "haiku")
    return (
        f"Jev {jev[3]} ({jev[4]}) vs Haiku {haiku[3]} ({haiku[4]})",
        "Choice",
    )


def sst5(root: Path) -> tuple[str, str]:
    output = run_scorer(root, "work/score-sst5/score.py")
    jev = next(
        line
        for line in output.splitlines()
        if line.startswith("| Jev jev-1.13.0 (rounded expected)")
    )
    haiku = next(
        line
        for line in output.splitlines()
        if line.startswith("| Haiku 4.5 via adapter (rounded expected)")
    )
    jev_cells = [cell.strip() for cell in jev.strip().strip("|").split("|")]
    haiku_cells = [cell.strip() for cell in haiku.strip().strip("|").split("|")]
    return (
        f"Jev {jev_cells[1]}, MAE {jev_cells[4]} vs Haiku {haiku_cells[1]}, MAE {haiku_cells[4]}",
        "Score",
    )


def scifact(root: Path) -> tuple[str, str]:
    output = run_scorer(root, "work/noul-scifact/score.py")
    jev = table_cells(output, "Jev jev-1.13.0")
    haiku = table_cells(output, "Haiku 4.5 via adapter")
    return (
        f"Jev {jev[1]} ({jev[2]}, Brier {jev[5]}) vs Haiku {haiku[1]} ({haiku[2]}, Brier {haiku[5]})",
        "Noul",
    )


def miniwob(root: Path) -> tuple[str, str]:
    receipt = json.loads(
        (root / "work/miniwob-jev/live-20260925/receipt.json").read_text()
    )
    heldout = receipt["combined_heldout"]
    paired = heldout["mcnemar_vs_v1"]
    return (
        f"v3 {heldout['successes']}/{heldout['rows_written']} vs v1 {paired['v1_successes']}/625 "
        f"(McNemar p={paired['p_two_sided']:.4g}; spend ${heldout['estimated_spend_usd']:.6f})",
        "Computer-use",
    )


def webscreen(root: Path) -> tuple[str, str]:
    receipt = (root / "work/hermes-webscreen-repro/RECEIPT.md").read_text()
    caught = re.search(r"caught ([\d,]+)/([\d,]+) on arm A", receipt)
    clean = re.search(r"clean false positives 0/([\d,]+)", receipt)
    screenings = re.search(r"([\d,]+) screenings in [\d,]+ requests", receipt)
    spend = re.search(
        r"([\d,]+) input tokens x \$0\.042/M = \*\*\$([\d.]+)\*\*", receipt
    )
    if caught is None or clean is None or screenings is None or spend is None:
        raise ValueError("web-screen receipt is missing a measured result")
    caught_count, caught_total = caught.groups()
    clean_count = clean.group(1)
    screening_count = screenings.group(1)
    input_tokens, spend_usd = spend.groups()
    return (
        f"jev+local {caught_count}/{caught_total} arm A, "
        f"0/{clean_count} clean withheld, {screening_count} screenings, "
        f"{input_tokens} input tokens, ${spend_usd}",
        "Noul / web-screen",
    )


def omp_judge_usage(root: Path) -> tuple[str, str]:
    result = subprocess.run(
        ["git", "show", "b74704c9:EVAL.md"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    match = re.search(
        r"([\d,]+) calls, \$([\d.]+) total\. By `purpose`: `find` ([\d,]+).*?"
        r"`auto-thinking` ([\d,]+).*?`judge_batch` ([\d,]+), `judge` ([\d,]+)",
        result.stdout,
        re.DOTALL,
    )
    if not match:
        raise ValueError("EVAL b74704c9 has no OMP judge usage receipt")
    calls, dollars, find, auto_thinking, judge_batch, judge = match.groups()
    return (
        f"{calls} calls, ${dollars}; find {find}, auto-thinking {auto_thinking}, "
        f"judge_batch {judge_batch}, judge {judge}",
        "OMP judge usage",
    )


def render_table(root: Path) -> str:
    rows = [
        (
            "Banking77 intent classification",
            *banking77(root),
            "work/choice-banking77/score.py --set full-prompted",
        ),
        ("SST-5 sentiment scoring", *sst5(root), "work/score-sst5/score.py"),
        ("SciFact claim verification", *scifact(root), "work/noul-scifact/score.py"),
        (
            "Replicated web-screen",
            *webscreen(root),
            "work/hermes-webscreen-repro/RECEIPT.md; kerpopule/hermes-jev-skills@cf9e84c",
        ),
        (
            "MiniWoB v3 held-out",
            *miniwob(root),
            "work/miniwob-jev/live-20260925/receipt.json",
        ),
        (
            "OMP judge usage",
            *omp_judge_usage(root),
            "EVAL.md@b74704c9",
        ),
    ]
    lines = [
        "| Surface | Result | Shape | Evidence |",
        "|---|---|---|---|",
    ]
    for surface, result, shape, evidence in rows:
        lines.append(f"| {surface} | {result} | {shape} | `{evidence}` |")
    return "\n".join(lines)


def render_readme_text(readme: str, root: Path) -> str:
    table = render_table(root)
    start = readme.find(START)
    end = readme.find(END)
    if start < 0 or end < 0 or end < start:
        raise ValueError(f"README must contain {START!r} and {END!r}")
    before = readme[: start + len(START)]
    after = readme[end:]
    return f"{before}\n{table}\n{after}"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("readme", nargs="?", default="README.md")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = (root / args.readme).resolve()
    original = path.read_text()
    rendered = render_readme_text(original, root)
    if args.write:
        path.write_text(rendered)
        return 0
    if rendered != original:
        import difflib

        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            rendered.splitlines(keepends=True),
            fromfile=str(path),
            tofile=f"{path} (generated)",
        )
        sys.stderr.write("".join(diff))
        return 1
    print("README results table is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
