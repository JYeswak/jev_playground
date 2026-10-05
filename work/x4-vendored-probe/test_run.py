"""Planted negatives for work/x4-vendored-probe/run.py (offline, no model calls).

Rows are taken from the committed frozen sample, not typed by hand.
Run: python3 -m unittest work/x4-vendored-probe/test_run.py -v   (needs scikit-learn; see RECEIPT.md)
"""

import importlib.util
import json
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("x4_run", HERE / "run.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
SAMPLE = json.loads(run.SAMPLE.read_text())


class DevOnlyFit(unittest.TestCase):
    def test_refit_including_held_rows_is_refused(self):
        held_ids = {r["sample_id"] for r in SAMPLE["held"]}
        with self.assertRaisesRegex(ValueError, "held rows in training set"):
            run.fit_probe(SAMPLE["dev"] + SAMPLE["held"][:5], held_ids)

    def test_dev_only_fit_is_accepted(self):
        held_ids = {r["sample_id"] for r in SAMPLE["held"]}
        score, _, _ = run.fit_probe(SAMPLE["dev"], held_ids)
        self.assertEqual(len(score(SAMPLE["held"][:4])), 4)


class ClusterBootstrapUnit(unittest.TestCase):
    def setUp(self):
        self.held = SAMPLE["held"]
        self.labels = np.asarray([int(r["label"] == "pos") for r in self.held])

    def test_window_level_resampling_is_refused(self):
        window_ids = [r["sample_id"] for r in self.held]
        with self.assertRaisesRegex(ValueError, "window resampling"):
            run.cluster_bootstrap(lambda idx: 0.0, self.labels, window_ids, b=10)

    def test_source_group_resampling_uses_53_units(self):
        groups = [run.source_group(r) for r in self.held]
        out = run.cluster_bootstrap(
            lambda idx: float(self.labels[idx].mean()), self.labels, groups, b=50
        )
        self.assertEqual(out["units"], 53)


if __name__ == "__main__":
    unittest.main()
