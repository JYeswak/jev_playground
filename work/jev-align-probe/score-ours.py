#!/usr/bin/env python3
"""Score a saved jev-align AI Function against the committed omp-jev-failure gold set.

jev-align's own report only covers the rows a human labeled (6 of 11 here). This
scores the ACCEPTED function over EVERY row, which is the number that can be
compared with work/omp-jev-failure/measure.mjs.

  infisical run --projectId=... -- python score-ours.py RUN_DIR CSV GOLD_JSON
"""

from __future__ import annotations

import csv
import json
import re
import sys

from jev_align import AIFunction

NORMALIZE = re.compile(r"[│┃╭╮╰╯━─┏┓┗┛┡┩╇┳┻╋]")


def flatten(value: str) -> str:
    return re.sub(r"\s+", " ", NORMALIZE.sub(" ", value)).strip()


def main() -> int:
    run_dir, csv_path, gold_path = sys.argv[1], sys.argv[2], sys.argv[3]
    gold = json.load(open(gold_path, encoding="utf-8"))
    with open(csv_path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    function = AIFunction.load(run_dir)
    correct = 0
    adversarial_correct = 0
    adversarial_total = 0
    per_class: dict[str, list[int]] = {}
    lines = []

    for row in rows:
        flat = flatten(row["failure"])
        matches = [g for g in gold if g["needle"] in flat]
        if len(matches) != 1:
            raise SystemExit(f"gold match failed ({len(matches)}) for: {flat[:80]}")
        expected = matches[0]["label"]
        name = matches[0]["name"]
        prediction = function(**row)
        got = prediction.choice
        hit = got == expected
        correct += hit
        bucket = per_class.setdefault(expected, [0, 0])
        bucket[0] += hit
        bucket[1] += 1
        if name.startswith("adv-"):
            adversarial_total += 1
            adversarial_correct += hit
        lines.append(
            f"{'PASS' if hit else 'FAIL'}  {name:<32} expected={expected:<9} "
            f"got={got:<9} confidence={prediction.confidence:.3f}"
        )

    print("\n".join(lines))
    print(f"\nAI Function accuracy vs committed gold: {correct}/{len(rows)}")
    for label, (hit, total) in sorted(per_class.items()):
        print(f"  {label:<10} {hit}/{total}")
    print(f"  adversarial arms {adversarial_correct}/{adversarial_total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
