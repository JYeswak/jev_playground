#!/usr/bin/env python3
"""Offline tests for the receipt-backed README results generator."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "render_results", ROOT / "scripts" / "render-results.py"
)
assert SPEC and SPEC.loader
render_results = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_results)


class RenderResultsTest(unittest.TestCase):
    def test_render_is_idempotent_against_committed_readme(self):
        readme = (ROOT / "README.md").read_text()
        rendered = render_results.render_readme_text(readme, ROOT)
        self.assertEqual(rendered, readme)

    def test_planted_table_drift_is_detected(self):
        readme = (ROOT / "README.md").read_text()
        planted = readme.replace("2467/3080", "2466/3080", 1)
        self.assertNotEqual(render_results.render_readme_text(planted, ROOT), planted)

    def test_generated_table_has_receipt_backed_surfaces(self):
        table = render_results.render_table(ROOT)
        for surface in (
            "Banking77 intent classification",
            "SST-5 sentiment scoring",
            "SciFact claim verification",
            "BEIR SciFact reranking",
            "MiniWoB v3 held-out",
            "OMP judge usage",
        ):
            self.assertIn(surface, table)


if __name__ == "__main__":
    unittest.main()
