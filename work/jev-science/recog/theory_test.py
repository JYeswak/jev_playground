#!/usr/bin/env python3
"""Statistical calculation tests and an explicit local analysis report.

The registered unittest path reads committed inputs only. `--report` reads the
optional local work/jev-science/table_draft.json and committed CSV files.
"""

import argparse
import csv
import json
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def load_report_inputs(draft_path=None):
    codes = {}
    with open(os.path.join(HERE, "codes.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            codes[row["id"]] = row["code"]
    if draft_path is None:
        draft_path = os.path.join(ROOT, "work", "jev-science", "table_draft.json")
    try:
        with open(draft_path, encoding="utf-8") as fh:
            table = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read report draft {draft_path}: {exc}") from exc
    verdict = {x["id"]: x["verdict"] for x in table}
    with open(os.path.join(HERE, "new_verdicts.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            verdict[row["id"]] = row["verdict"]
    if set(codes) != set(verdict):
        raise ValueError(f"coding/verdict ID mismatch: {set(codes) ^ set(verdict)}")
    return codes, verdict, table


def fisher(a, b, c, d):
    # two-sided Fisher on [[a,b],[c,d]] via hypergeometric doubling
    n1, n2, m1 = a + b, c + d, a + c
    n = n1 + n2

    def hg(k):
        return math.comb(n1, k) * math.comb(n2, m1 - k) / math.comb(n, m1)

    p_obs = hg(a)
    return sum(
        hg(k) for k in range(max(0, m1 - n2), min(n1, m1) + 1) if hg(k) <= p_obs + 1e-12
    )


def or_haldane(a, b, c, d):
    a1, b1, c1, d1 = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    OR = (a1 * d1) / (b1 * c1)
    se = math.sqrt(1 / a1 + 1 / b1 + 1 / c1 + 1 / d1)
    lo = math.exp(math.log(OR) - 1.96 * se)
    hi = math.exp(math.log(OR) + 1.96 * se)
    return OR, lo, hi


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0, (c - m) / den), min(1, (c + m) / den))


def newcombe(a, n1, c, n2):
    p1, p2 = a / n1, c / n2
    l1, u1 = wilson(a, n1)
    l2, u2 = wilson(c, n2)
    rd = p1 - p2
    lo = rd - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = rd + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return rd, lo, hi


def report(name, pos, codes, verdict):
    # pos(id) True means event; rows R/F
    a = sum(1 for i in codes if codes[i] == "R" and pos(i))
    b = sum(1 for i in codes if codes[i] == "R" and not pos(i))
    c = sum(1 for i in codes if codes[i] == "F" and pos(i))
    d = sum(1 for i in codes if codes[i] == "F" and not pos(i))
    p = fisher(a, b, c, d)
    OR, olo, ohi = or_haldane(a, b, c, d)
    rd, rlo, rhi = newcombe(a, a + b, c, c + d)
    print(
        f"{name} 2x2 [[R-event {a}, R-no {b}],[F-event {c}, F-no {d}]] p={p:.4f} OR={OR:.2f} [{olo:.2f},{ohi:.2f}] RD={rd:.3f} [{rlo:.3f},{rhi:.3f}]"
    )


def run_report(draft_path=None):
    codes, verdict, table = load_report_inputs(draft_path)
    agree = sum(
        1
        for row in table
        if ((codes[row["id"]] == "F") == bool(row.get("future_counterfactual")))
    )
    print(f"n={len(codes)} agree-with-table-flag={agree}/{len(table)}")
    print(
        "disagreements:",
        [
            row["id"]
            for row in table
            if (codes[row["id"]] == "F") != bool(row.get("future_counterfactual"))
        ],
    )
    report("PRIMARY win-vs-nonwin  ", lambda i: verdict[i] == "win", codes, verdict)
    report("SECONDARY loss-vs-rest ", lambda i: verdict[i] == "loss", codes, verdict)
    report(
        "SECONDARY winTie-vs-loss",
        lambda i: verdict[i] in ("win", "tie"),
        codes,
        verdict,
    )
    own = {i for i in codes if i not in ("R86b", "R89b", "R90b")}
    sub = {i: codes[i] for i in own}
    a = sum(1 for i in sub if sub[i] == "R" and verdict[i] == "win")
    b = sum(1 for i in sub if sub[i] == "R" and verdict[i] != "win")
    c = sum(1 for i in sub if sub[i] == "F" and verdict[i] == "win")
    d = sum(1 for i in sub if sub[i] == "F" and verdict[i] != "win")
    p = fisher(a, b, c, d)
    print(f"SENSITIVITY own-vein-only win-vs-nonwin [[{a},{b}],[{c},{d}]] p={p:.4f}")


class TestStatistics(unittest.TestCase):
    def test_fisher_two_sided_known_table(self):
        self.assertAlmostEqual(
            fisher(1, 9, 11, 3),
            0.0027594561852200836,
            places=12,
        )

    def test_haldane_correction_handles_zero_cells(self):
        odds_ratio, lower, upper = or_haldane(0, 3, 4, 0)
        self.assertAlmostEqual(odds_ratio, 1 / 63)
        self.assertTrue(
            all(math.isfinite(value) for value in (odds_ratio, lower, upper))
        )
        self.assertLess(lower, odds_ratio)
        self.assertGreater(upper, odds_ratio)

    def test_newcombe_interval_contains_risk_difference(self):
        difference, lower, upper = newcombe(7, 12, 2, 10)
        self.assertAlmostEqual(difference, 7 / 12 - 2 / 10)
        self.assertLessEqual(lower, difference)
        self.assertGreaterEqual(upper, difference)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        action="store_true",
        help="recompute the local analysis from table_draft.json",
    )
    parser.add_argument("--draft", help="path to a table_draft.json for --report")
    args, unittest_args = parser.parse_known_args()
    if args.report:
        run_report(args.draft)
    else:
        unittest.main(argv=[sys.argv[0], *unittest_args])


if __name__ == "__main__":
    main()
