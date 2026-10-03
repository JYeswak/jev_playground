import json
import os
import unittest
import traffic


class TrafficContractTests(unittest.TestCase):
    def test_cascade_denominator_includes_cleared_and_paid_rows(self):
        opportunities, paid, days, provenance = traffic.facg_window()
        self.assertEqual((opportunities, paid), (102, 4))
        self.assertEqual(days, 1.0 / 24)
        self.assertIn("98 nimble-cleared + 4 paid", provenance)

    def test_unlabeled_traffic_is_explicitly_not_counted(self):
        self.assertEqual(traffic.counting_status(None), "NOT_COUNTED")
        self.assertEqual(traffic.counting_status(0), "COUNTED")

    def test_candidates_mark_unlabeled_rows_and_report_paid_share(self):
        path = os.path.join(os.path.dirname(__file__), "candidates.json")
        with open(path, encoding="utf-8") as fh:
            candidates = json.load(fh)["candidates"]
        cascade = candidates["gate_cascade"]
        self.assertEqual(cascade["opportunities"], 102)
        self.assertEqual(cascade["positives"], 4)
        self.assertAlmostEqual(cascade["paid_share"], 4 / 102)
        for name in ("injection_reads", "webscreen"):
            row = candidates[name]
            self.assertIsNone(row["positives"])
            self.assertEqual(row["status"], "NOT_COUNTED")
            self.assertEqual(row["traffic"]["status"], "NOT_COUNTED")


if __name__ == "__main__":
    unittest.main()
