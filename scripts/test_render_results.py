#!/usr/bin/env python3
"""Offline tests for the receipt-backed README results generator."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_nfcorpus_failed_joint_bar_discloses_both_payers(self):
        receipt = json.loads(
            (ROOT / "work/rerank-scifact/receipt-nfcorpus-v2.json").read_text()
        )
        result, _ = render_results.nfcorpus_rerank(ROOT)
        self.assertFalse(receipt["bar"]["pass"])
        self.assertIn("joint bar FAIL:", result)
        self.assertIn("nDCG@10 +0.027 missed +0.05", result)
        self.assertIn("free LLM p50 25.9s, $0 by unchanged usage", result)
        self.assertIn(
            f"Jev eligible run ${receipt['usage']['jev_input_cost_usd']:.4f} "
            f"(${receipt['spend']['total_input_cost_usd']:.4f} including discarded run)",
            result,
        )

    def test_nfcorpus_inconsistent_pass_refused(self):
        original_read_text = Path.read_text

        def planted_read_text(path, *args, **kwargs):
            text = original_read_text(path, *args, **kwargs)
            if path.name == "receipt-nfcorpus-v2.json":
                receipt = json.loads(text)
                receipt["bar"]["pass"] = True
                return json.dumps(receipt)
            return text

        with (
            patch.object(Path, "read_text", planted_read_text),
            self.assertRaisesRegex(ValueError, "bar disagrees"),
        ):
            render_results.nfcorpus_rerank(ROOT)


if __name__ == "__main__":
    unittest.main()
