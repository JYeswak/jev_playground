from __future__ import annotations

import collections
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run


class X2InputTests(unittest.TestCase):
    def test_injection_uses_all_recorded_x1_rows(self) -> None:
        rows = run.load_injection_rows()

        self.assertEqual(len(rows), 1347)
        self.assertEqual(
            collections.Counter(row["set"] for row in rows),
            {"clean": 200, "clean-dev": 100, "marked": 300, "markerless": 300, "public-english": 447},
        )
        self.assertEqual(len({row["id"] for row in rows}), 1347)
        self.assertEqual(len({row["input_sha256"] for row in rows}), 1347)
        self.assertTrue(all(row["input_sha256"] == run.sha256_text(row["text"]) for row in rows))
        self.assertEqual(sum(row["split"] == "dev" for row in rows), 449)
        self.assertEqual(sum(row["split"] == "held" for row in rows), 898)
        self.assertEqual(
            sum(row["source_group"] == "tool-results" and row["split"] == "held" for row in rows),
            600,
        )

    def test_injection_uses_seeded_stratified_assignments(self) -> None:
        rows = run.load_injection_rows()
        split = {row["id"]: row["split"] for row in rows}

        self.assertEqual(split["clean-dev:clean-63"], "dev")
        self.assertEqual(split["clean-dev:clean-18"], "held")
        self.assertEqual(split["clean:clean-105"], "dev")
        self.assertEqual(split["clean:clean-271"], "held")
        self.assertEqual(split["marked:planted-24-middle"], "dev")
        self.assertEqual(split["marked:planted-3-middle"], "held")
        self.assertEqual(split["markerless:planted-45-end"], "dev")
        self.assertEqual(split["markerless:planted-36-middle"], "held")
        self.assertEqual(split["public-english:inj-0343"], "dev")
        self.assertEqual(split["public-english:inj-0522"], "held")
        assignment_hash = hashlib.sha256(
            "".join(f"{row_id}\t{split[row_id]}\n" for row_id in sorted(split)).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            assignment_hash,
            "105f08afdb985c3017c507a32a012d0eb8e60e27f212f08f32116cb337ccab7a",
        )

    def test_gate_source_is_exact_private_pack_and_x7_rows(self) -> None:
        rows = run.load_gate_rows()

        self.assertEqual(len(rows), 396)
        self.assertEqual(len({row["event_id"] for row in rows}), 396)
        self.assertEqual(len({row["cmd_sha"] for row in rows}), 380)
        self.assertEqual(collections.Counter(row["split"] for row in rows), {"dev": 149, "held": 247})
        self.assertTrue(all(row["jev_score"] == row["recorded_max_score"] for row in rows))

    def test_gate_uses_the_recorded_command_projection(self) -> None:
        rows = run.load_gate_rows()
        self.assertTrue(all(run.js_units(row["command"]) == row["command_view_chars"] for row in rows))
        self.assertEqual(sum(row["command_projection_truncated"] for row in rows), 296)

    def test_gate_recall_context_keeps_x7_stratum_caveat(self) -> None:
        run.validate_gate_recall_context(run.X7_RECALL_CONTEXT)

        with self.assertRaises(run.X2Error):
            run.validate_gate_recall_context({"recall": "47/47", "scope": "overall"})


class X2SafetyTests(unittest.TestCase):
    def test_injection_primary_population_is_powered_before_calls(self) -> None:
        rows = run.load_injection_rows()
        power = run.injection_power_check(rows)
        calls: list[str] = []

        receipt = run.run_calls(
            suite="injection",
            rows=rows,
            power=power,
            call=lambda _row: calls.append("called") or {"scores": {"injection": 0.1}},
        )

        self.assertEqual(power["held_n"], 898)
        self.assertGreaterEqual(power["minimum_metric_power"], 0.8)
        self.assertEqual(power["status"], "POWERED")
        self.assertEqual(receipt["status"], "COMPLETE")
        self.assertEqual(receipt["clef_calls"], 1347)
        self.assertEqual(len(calls), 1347)
        self.assertEqual(receipt["answers"][0]["input_sha256"], rows[0]["input_sha256"])

    def test_gate_full_population_runs_descriptively_below_power_target(self) -> None:
        rows = run.load_gate_rows()
        power = run.power_check("gate", rows)
        calls: list[str] = []

        receipt = run.run_calls(
            suite="gate",
            rows=rows,
            power=power,
            call=lambda _row: calls.append("called") or {"scores": {"risk": 0.1}},
        )

        self.assertEqual(power["held_n"], 247)
        self.assertLess(power["minimum_metric_power"], 0.8)
        self.assertEqual(power["status"], "DESCRIPTIVE")
        self.assertEqual(receipt["status"], "COMPLETE")
        self.assertEqual(receipt["clef_calls"], 396)
        self.assertEqual(len(calls), 396)
        self.assertEqual(receipt["answers"][0]["cmd_sha"], rows[0]["cmd_sha"])

    def test_call_eligibility_keeps_gate_descriptive(self) -> None:
        self.assertTrue(run.suite_is_eligible_for_calls("injection", {"status": "POWERED"}))
        self.assertFalse(run.suite_is_eligible_for_calls("injection", {"status": "NOT_POWERED"}))
        self.assertTrue(run.suite_is_eligible_for_calls("gate", {"status": "DESCRIPTIVE"}))
        with self.assertRaises(run.X2Error):
            run.suite_is_eligible_for_calls("gate", {"status": "NOT_POWERED"})

    def test_invalid_split_manifest_is_refused(self) -> None:
        with (
            mock.patch.object(run, "SPLIT_PATH", mock.Mock(read_text=mock.Mock(return_value="{"))),
            self.assertRaises(run.X2Error),
        ):
            run.split_rows("injection", [])

    def test_local_model_guard_timeout_fails_closed(self) -> None:
        with (
            mock.patch.object(
                run.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired("local-model-guard", 15),
            ),
            self.assertRaises(run.X2Error),
        ):
            run.local_model_guard()

    def test_underpowered_injection_stops_before_any_request(self) -> None:
        calls: list[str] = []
        receipt = run.run_calls(
            suite="injection",
            rows=[],
            power={"status": "NOT_POWERED"},
            call=lambda _row: calls.append("called") or {"scores": {"injection": 0.1}},
        )

        self.assertEqual(receipt["status"], "NOT_POWERED")
        self.assertEqual(receipt["clef_calls"], 0)
        self.assertEqual(calls, [])

    def test_gate_report_never_claims_non_inferiority_when_descriptive(self) -> None:
        rows = [
            {
                "id": f"row-{index}",
                "suite": "gate",
                "split": "dev" if index < 20 else "held",
                "label": index % 2,
                "source_group": "gate",
            }
            for index in range(40)
        ]
        scores = {
            row["id"]: 0.2 if row["label"] == 0 else 0.8
            for row in rows
        }

        report = run.calibration_report(
            rows,
            scores,
            scores,
            powered=False,
        )

        self.assertEqual(report["held_n"], 20)
        self.assertGreater(report["accuracy_difference_lower95"], -0.05)
        self.assertEqual(report["verdict"], "DESCRIPTIVE_ONLY")
        self.assertEqual(report["decision_agreement"], 1.0)
        self.assertEqual(report["decision_agreement_ci95"], (1.0, 1.0))

    def test_origin_preregistration_check_refuses_stale_split(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prereg = root / "work/x2-clef-suites/PREREG.md"
            split = root / "work/x2-clef-suites/split.json"
            prereg.parent.mkdir(parents=True)
            prereg.write_text("v2 prereg")
            split.write_text("v2 split")
            subprocess.run(
                ["git", "init", "-b", "main", str(root)],
                check=True,
                capture_output=True,
                timeout=10,
            )
            subprocess.run(
                ["git", "-C", str(root), "config", "user.name", "X2 Test"],
                check=True,
                timeout=10,
            )
            subprocess.run(
                ["git", "-C", str(root), "config", "user.email", "x2-test@example.invalid"],
                check=True,
                timeout=10,
            )
            prereg.write_text("v1 prereg")
            split.write_text("v1 split")
            subprocess.run(
                ["git", "-C", str(root), "add", "work/x2-clef-suites/PREREG.md", "work/x2-clef-suites/split.json"],
                check=True,
                timeout=10,
            )
            subprocess.run(
                ["git", "-c", "core.hooksPath=/dev/null", "-C", str(root), "commit", "-m", "v1"],
                check=True,
                capture_output=True,
                timeout=10,
            )
            old_commit = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            ).stdout.strip()
            subprocess.run(
                ["git", "-C", str(root), "update-ref", "refs/remotes/origin/main", old_commit],
                check=True,
                timeout=10,
            )
            prereg.write_text("v2 prereg")
            split.write_text("v2 split")

            self.assertFalse(run.frozen_inputs_on_ref(root, "origin/main"))

            subprocess.run(
                ["git", "-C", str(root), "add", "work/x2-clef-suites/PREREG.md", "work/x2-clef-suites/split.json"],
                check=True,
                timeout=10,
            )
            subprocess.run(
                ["git", "-c", "core.hooksPath=/dev/null", "-C", str(root), "commit", "-m", "v2"],
                check=True,
                capture_output=True,
                timeout=10,
            )
            new_commit = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            ).stdout.strip()
            subprocess.run(
                ["git", "-C", str(root), "update-ref", "refs/remotes/origin/main", new_commit],
                check=True,
                timeout=10,
            )
            self.assertTrue(run.frozen_inputs_on_ref(root, "origin/main"))


    def test_main_refuses_all_requests_when_origin_preregistration_is_stale(self) -> None:
        with (
            self.assertRaises(run.X2Error),
            mock.patch.object(run, "origin_main_frozen", return_value=False),
            mock.patch.object(run, "family_rows") as load_rows,
            mock.patch.object(run, "local_model_guard") as guard,
            mock.patch.object(run, "check_gateway") as gateway,
            mock.patch.object(run, "request_clef") as request,
        ):
            run.main(["--json"])

        load_rows.assert_not_called()
        guard.assert_not_called()
        gateway.assert_not_called()
        request.assert_not_called()

    def test_platt_map_refuses_the_other_arm(self) -> None:
        ids = ["dev-0", "dev-1"]
        dev_ids = set(ids)
        model = run.fit_platt(
            [0.1, 0.9],
            [0, 1],
            ids,
            suite="injection",
            arm="jev",
            dev_ids=dev_ids,
        )

        with self.assertRaises(run.X2Error):
            run.apply_platt(0.4, model, suite="injection", arm="clef", dev_ids=dev_ids, held_ids={"held-0"})

    def test_platt_fit_refuses_a_held_id(self) -> None:
        with self.assertRaises(run.X2Error):
            run.fit_platt(
                [0.1, 0.9],
                [0, 1],
                ["dev-0", "held-0"],
                suite="injection",
                arm="clef",
                dev_ids={"dev-0", "dev-1"},
            )

    def test_failure_to_reject_does_not_imply_non_inferiority(self) -> None:
        self.assertEqual(run.verdict_from_lower_bound(-0.08, powered=True), "NOT NON-INFERIOR")
        self.assertEqual(run.verdict_from_lower_bound(-0.08, powered=False), "NOT_POWERED")

    def test_non_family_suite_is_refused(self) -> None:
        with self.assertRaises(run.X2Error):
            run.family_rows("scifact")

    def test_missing_gateway_has_no_direct_8010_fallback(self) -> None:
        urls: list[str] = []

        class OfflineGateway:
            def open(self, request: object, timeout: int) -> None:
                urls.append(request.full_url)
                raise run.urllib.error.URLError("offline")

        with (
            mock.patch.object(run.urllib.request, "build_opener", return_value=OfflineGateway()),
            self.assertRaises(run.X2Error),
        ):
            run.check_gateway()

        self.assertEqual(urls, [f"{run.GATEWAY}/jev/clef-flash/"])
        self.assertNotIn(":8010", urls[0])


if __name__ == "__main__":
    unittest.main()
