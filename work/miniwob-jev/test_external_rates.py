"""Keyless tests for the committed Table 3 extraction and external-rate projection."""

from __future__ import annotations

import csv
import io
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXTRACT = HERE / "external-rates-table3.tsv"
RATES = HERE / "external-rates.tsv"
FIELDS = (
    "human_success_rate",
    "cc_net_mean_score",
    "aggregated_sota_bc_rl",
    "aggregated_sota_augmented",
)
EXPECTED_URL = "https://proceedings.mlr.press/v162/humphreys22a/humphreys22a.pdf"
EXPECTED_SHA256 = "ba2a9a0a5e46aa5f34cfc720ac08049253917407e2fbd4a8cdbd2c8ca3ec8455"


def _extract_rows(text: str) -> list[dict[str, str]]:
    lines = [line for line in text.splitlines() if line and not line.startswith("#")]
    return list(csv.DictReader(io.StringIO("\n".join(lines)), delimiter="\t"))


def _rates_rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def _normalized(value: str) -> str:
    return "" if value == "n/a" else value


class Table3Projection(unittest.TestCase):
    def assert_projection_matches(self, rates_text: str) -> None:
        extracted = {
            row["task"]: row
            for row in _extract_rows(EXTRACT.read_text(encoding="utf-8"))
        }
        all_rates = _rates_rows(rates_text)
        rates = {row["task"]: row for row in all_rates if row["human_success_rate"]}
        self.assertEqual(set(rates), set(extracted))
        for task, source in extracted.items():
            self.assertIn(task, rates)
            for field in FIELDS:
                self.assertEqual(
                    rates[task][field],
                    _normalized(source[field]),
                    f"{task}: {field}",
                )

    def test_header_and_all_projected_values_match_extraction(self) -> None:
        header = EXTRACT.read_text(encoding="utf-8").splitlines()[:3]
        self.assertEqual(header[0], f"# source_url: {EXPECTED_URL}")
        self.assertEqual(header[1], f"# source_sha256: {EXPECTED_SHA256}")
        self.assertIn("# table: 3", header[2])
        self.assert_projection_matches(RATES.read_text(encoding="utf-8"))

    def test_one_planted_rate_mismatch_fails_projection(self) -> None:
        original = RATES.read_text(encoding="utf-8")
        planted = original.replace(
            "book-flight\t0.87\t0.87\t0.00\t1.00",
            "book-flight\t0.87\t0.87\t0.00\t0.99",
            1,
        )
        self.assertNotEqual(planted, original)
        with self.assertRaises(AssertionError):
            self.assert_projection_matches(planted)


if __name__ == "__main__":
    unittest.main()
