from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import LedgerInputError, memory_metrics, read_jsonl
from extract_window import extract_window
from ledger import (
    expand_memory_surfaces,
    load_approved_harm_costs,
    load_expected,
    main,
    validate_harm_cost_coverage,
    verify_cost_commit_order,
)
from policy import (
    classify_memory_cap3_harm,
    classify_surface,
    screen_rows,
    strict_failures,
    switch_recommendation,
    validate_screen_attribution,
)
from report import _metrics, assemble_report, native_usage

# Sanitized metadata fields captured from memory-filter JSONL; memory text is omitted.
CAPTURED_ENFORCED = {
    "schema": "jev-memory-filter.v1",
    "model": "jev-1.13.0",
    "ts": "2026-10-03T22:20:03.651Z",
    "instance": "a30b9f04",
    "status": "enforced",
    "promptHash": "6737fffb81b7e366abf427ae86c748bd104a107af0dd4e6a48f9d7f13a49ad8d",
    "decision": "prune",
    "tokensSaved": 0,
    "inputTokens": None,
    "latencyMs": None,
    "repo": "/Users/josh/Developer/uds",
}
CAPTURED_DROP = {
    "schema": "jev-memory-filter.v1",
    "model": "jev-1.13.0",
    "ts": "2026-10-03T22:20:03.462Z",
    "instance": "a30b9f04",
    "status": "scored",
    "promptHash": "6737fffb81b7e366abf427ae86c748bd104a107af0dd4e6a48f9d7f13a49ad8d",
    "decision": "drop",
    "tokensSaved": 74,
    "inputTokens": 431,
    "latencyMs": 174,
    "repo": "/Users/josh/Developer/uds",
}
CAPTURED_CAP3 = {
    "schema": "jev-memory-filter.v1",
    "model": "jev-1.13.0",
    "ts": "2026-10-03T22:15:40.113Z",
    "instance": "a30b9f04",
    "status": "cap3-pruned",
    "promptHash": "3e962eb617881a70361ded7b98d633d9ddbac4d404e59150d6b1940fe5113274",
    "decision": "prune",
    "tokensSaved": 58,
    "repo": "/Users/josh/Developer/uds",
}
CAPTURED_LATE_IGNORED = {
    "schema": "jev-memory-filter.v1",
    "model": "jev-1.13.0",
    "ts": "2026-10-05T16:41:19.348Z",
    "instance": "7c59c23d",
    "status": "late-ignored",
    "promptHash": "4d6dbc18e5e6531b41e59da0f4c5672a857a85a8a6a8822193dca129cf875a49",
    "decision": "keep",
    "tokensSaved": 0,
    "inputTokens": 417,
    "latencyMs": 443,
    "repo": "/Users/josh/Developer/jev",
}


class LedgerTests(unittest.TestCase):
    def tempdir(self) -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))

    def test_window_is_start_inclusive_end_exclusive_and_hashes_exact_bytes(
        self,
    ) -> None:
        with self.tempdir() as temp:
            root = Path(temp)
            source = root / "source.jsonl"
            output = root / "window.jsonl"
            before = copy.deepcopy(CAPTURED_DROP)
            before["ts"] = "2026-10-03T22:14:59.999Z"
            at_start = copy.deepcopy(CAPTURED_DROP)
            at_start["ts"] = "2026-10-03T22:15:00.000Z"
            at_end = copy.deepcopy(CAPTURED_CAP3)
            at_end["ts"] = "2026-10-04T22:15:00.000Z"
            source_bytes = b"".join(
                (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()
                for row in (before, at_start, at_end)
            )
            source.write_bytes(source_bytes)

            result = extract_window(
                source,
                output,
                datetime(2026, 10, 3, 22, 15, tzinfo=timezone.utc),
                datetime(2026, 10, 4, 22, 15, tzinfo=timezone.utc),
            )

            expected = (
                json.dumps(at_start, sort_keys=True, separators=(",", ":")) + "\n"
            ).encode()
            self.assertEqual(result.rows, 1)
            self.assertEqual(output.read_bytes(), expected)
            self.assertEqual(result.sha256, hashlib.sha256(expected).hexdigest())
            receipt = output.with_suffix(".sha256")
            self.assertEqual(
                receipt.read_text(encoding="utf-8"),
                f"{result.sha256}  {output.name}\n",
            )

    def test_window_rerun_reproduces_identical_receipt(self) -> None:
        with self.tempdir() as temp:
            root = Path(temp)
            source = root / "source.jsonl"
            output = root / "window.jsonl"
            source.write_text(json.dumps(CAPTURED_DROP) + "\n", encoding="utf-8")
            start = datetime(2026, 10, 3, 22, 15, tzinfo=timezone.utc)
            end = datetime(2026, 10, 4, 22, 15, tzinfo=timezone.utc)

            first = extract_window(source, output, start, end)
            second = extract_window(source, output, start, end)

            self.assertEqual(first, second)

    def test_window_refuses_missing_input(self) -> None:
        with self.tempdir() as temp:
            root = Path(temp)
            with self.assertRaises(FileNotFoundError):
                extract_window(
                    root / "missing.jsonl",
                    root / "window.jsonl",
                    datetime(2026, 10, 3, 22, 15, tzinfo=timezone.utc),
                    datetime(2026, 10, 4, 22, 15, tzinfo=timezone.utc),
                )

    def test_window_refuses_malformed_rows_instead_of_silently_dropping_them(
        self,
    ) -> None:
        with self.tempdir() as temp:
            root = Path(temp)
            source = root / "source.jsonl"
            source.write_text("not-json\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                extract_window(
                    source,
                    root / "window.jsonl",
                    datetime(2026, 10, 3, 22, 15, tzinfo=timezone.utc),
                    datetime(2026, 10, 4, 22, 15, tzinfo=timezone.utc),
                )

    def test_memory_jev_joins_only_drop_rows_to_the_same_enforced_turn(self) -> None:
        unrelated = copy.deepcopy(CAPTURED_DROP)
        unrelated["promptHash"] = "different-prompt"
        kept = copy.deepcopy(CAPTURED_DROP)
        kept["decision"] = "keep"
        metrics = memory_metrics(
            [CAPTURED_ENFORCED, CAPTURED_DROP, unrelated, kept, CAPTURED_CAP3]
        )
        self.assertEqual(metrics["memory_jev_tokens"], 74)
        self.assertEqual(metrics["memory_jev_drop_rows"], 1)

    def test_memory_cap3_is_reported_separately_from_jev_drops(self) -> None:
        metrics = memory_metrics([CAPTURED_ENFORCED, CAPTURED_DROP, CAPTURED_CAP3])
        self.assertEqual(metrics["memory_cap3_tokens"], 58)
        self.assertEqual(metrics["memory_cap3_rows"], 1)
        self.assertNotEqual(metrics["memory_cap3_tokens"], metrics["memory_jev_tokens"])

    def test_memory_cost_uses_recorded_input_tokens_and_latency(self) -> None:
        metrics = memory_metrics([CAPTURED_ENFORCED, CAPTURED_DROP])
        self.assertEqual(metrics["memory_jev_input_tokens"], 431)
        self.assertAlmostEqual(metrics["memory_jev_spend_usd"], 0.000018102)
        self.assertEqual(metrics["memory_jev_latency_ms_p50"], 174)
        self.assertEqual(metrics["memory_jev_latency_ms_p95"], 174)

    def test_cap3_without_x8_harm_bound_is_unmeasured(self) -> None:
        self.assertEqual(
            classify_memory_cap3_harm(None)["verdict"],
            "UNMEASURED",
        )

    def test_cap3_bound_above_five_percent_is_kill(self) -> None:
        self.assertEqual(classify_memory_cap3_harm(0.051)["verdict"], "KILL")

    def test_promote_requires_bar_commit_before_data(self) -> None:
        expected = [{"id": "surface", "expect": "on"}]
        bad = [
            {
                "id": "surface",
                "live": "on",
                "verdict": "PROMOTE",
                "bar_commit_epoch": 100,
                "data_start_epoch": 100,
            }
        ]
        good = [
            {
                "id": "surface",
                "live": "on",
                "verdict": "PROMOTE",
                "bar_commit_epoch": 99,
                "data_start_epoch": 100,
            }
        ]
        self.assertTrue(strict_failures(expected, bad))
        self.assertEqual(strict_failures(expected, good), [])

    def test_missing_value_or_cost_is_unmeasured_not_a_zero_value(self) -> None:
        result = classify_surface(value_usd=None, cost_usd=0.001)
        self.assertEqual(result["verdict"], "UNMEASURED")
        self.assertIsNone(result["net_usd"])

    def test_negative_net_value_is_kill_without_applying_a_switch(self) -> None:
        result = classify_surface(value_usd=0.000021, cost_usd=0.000021672)
        self.assertEqual(result["verdict"], "KILL")
        self.assertLess(result["net_usd"], 0)
        self.assertIsNone(result["applied_action"])

    def test_strict_gate_rejects_an_unmeasured_claimed_on_surface(self) -> None:
        expected = [{"id": "smart-stop", "expect": "on"}]
        rows = [{"id": "smart-stop", "live": "on", "verdict": "UNMEASURED"}]
        self.assertTrue(strict_failures(expected, rows))

    def test_strict_gate_rejects_kill_surface_still_live(self) -> None:
        expected = [{"id": "vendor-shadow", "expect": "on"}]
        rows = [{"id": "vendor-shadow", "live": "on", "verdict": "KILL"}]
        self.assertTrue(strict_failures(expected, rows))

    def test_strict_gate_allows_measured_kill_only_when_live_off(self) -> None:
        expected = [{"id": "vendor-shadow", "expect": "on"}]
        rows = [
            {
                "id": "vendor-shadow",
                "live": "off",
                "verdict": "KILL",
                "switch_verified_off": True,
                "fresh_session_rows": 0,
            }
        ]
        self.assertEqual(strict_failures(expected, rows), [])

    def test_strict_gate_rejects_missing_claimed_on_surface_row(self) -> None:
        expected = [{"id": "find", "expect": "on"}]
        self.assertTrue(strict_failures(expected, []))

    def test_strict_gate_rejects_kill_surface_with_fresh_session_rows(self) -> None:
        expected = [{"id": "vendor-shadow", "expect": "on"}]
        rows = [
            {
                "id": "vendor-shadow",
                "live": "off",
                "verdict": "KILL",
                "switch_verified_off": True,
                "fresh_session_rows": 1,
            }
        ]
        self.assertTrue(strict_failures(expected, rows))

    def test_screen_rows_without_repo_or_session_are_refused(self) -> None:
        with self.assertRaises(LedgerInputError):
            validate_screen_attribution([{"repo": "/repo"}])

    def test_missing_log_input_is_not_interpreted_as_zero(self) -> None:
        with self.tempdir() as temp, self.assertRaises(FileNotFoundError):
            read_jsonl(Path(temp) / "missing.jsonl")

    def test_missing_harm_cost_table_blocks_ledger(self) -> None:
        with self.tempdir() as temp, self.assertRaises(LedgerInputError):
            load_approved_harm_costs(Path(temp) / "harm-costs.json")

    def test_harm_cost_table_requires_all_enabled_gate_and_screen_surfaces(
        self,
    ) -> None:
        expected = [
            {"id": "gate-observe", "group": "hook", "expect": "on"},
            {"id": "webscreen-global", "group": "global", "expect": "on"},
            {"id": "memory-filter", "group": "extension", "expect": "on"},
        ]
        harm_costs = {"surfaces": {"gate-observe": {"usd_per_prevented_harm": 1.0}}}
        with self.assertRaises(LedgerInputError) as caught:
            validate_harm_cost_coverage(expected, harm_costs)
        self.assertIn("webscreen-global", str(caught.exception))

    def test_harm_cost_table_accepts_complete_gate_and_screen_coverage(self) -> None:
        expected = [
            {"id": "gate-observe", "group": "hook", "expect": "on"},
            {"id": "webscreen-global", "group": "global", "expect": "on"},
            {"id": "memory-filter", "group": "extension", "expect": "on"},
        ]
        harm_costs = {
            "surfaces": {
                "gate-observe": {"usd_per_prevented_harm": 1.0},
                "webscreen-global": {"usd_per_prevented_harm": 2.0},
            }
        }
        self.assertIsNone(validate_harm_cost_coverage(expected, harm_costs))

    def test_harm_costs_committed_after_first_output_are_refused(self) -> None:
        with self.assertRaises(LedgerInputError):
            verify_cost_commit_order(
                cost_commit_epoch=200, first_output_commit_epoch=100
            )

    def test_negative_recommendation_names_switch_without_applying_it(self) -> None:
        surface = {
            "switch_file": "~/.local/state/jev/vendor-shadow-off",
            "switch_polarity": "presence-ON",
        }
        result = switch_recommendation(surface, "KILL")
        self.assertEqual(
            result,
            {
                "action": "turn-off",
                "file": "~/.local/state/jev/vendor-shadow-off",
                "polarity": "presence-ON",
                "applied": False,
            },
        )

    def test_inventory_memory_surface_expands_into_two_rows(self) -> None:
        rows = expand_memory_surfaces([{"id": "memory-filter", "expect": "on"}])
        self.assertEqual([row["id"] for row in rows], ["memory-jev", "memory-cap3"])

    def test_native_usage_parses_recorded_purpose_and_session_owner(self) -> None:
        with self.tempdir() as temp:
            home = Path(temp) / "home"
            session_file = (
                home / ".omp" / "agent" / "sessions" / "repo" / "session.jsonl"
            )
            session_file.parent.mkdir(parents=True)
            rows = [
                {
                    "type": "session",
                    "id": "01a10c83-b368-74a9-b172-89927ada3baf",
                    "cwd": "/Users/josh/Developer/jev",
                },
                {
                    "type": "model_usage",
                    "timestamp": "2026-10-05T15:27:37.824Z",
                    "purpose": "find",
                    "provider": "typesafe",
                    "model": "jev-latest",
                    "usage": {"input": 6543, "cost": {"total": 0.000274806}},
                },
            ]
            session_file.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
            with patch("report.HOME", home):
                usage, sessions = native_usage(
                    datetime(2026, 10, 5, 15, 27, tzinfo=timezone.utc),
                    datetime(2026, 10, 5, 15, 28, tzinfo=timezone.utc),
                )
            self.assertEqual(
                sessions["01a10c83-b368-74a9-b172-89927ada3baf"],
                "/Users/josh/Developer/jev",
            )
            self.assertEqual(len(usage["find"]), 1)
            self.assertEqual(usage["find"][0]["usage"]["input"], 6543)

    def test_screen_session_join_supplies_repo_from_session_metadata(self) -> None:
        rows, errors = screen_rows(
            [{"session": "session-1"}], {"session-1": "/Users/josh/Developer/jev"}
        )
        self.assertEqual(errors, [])
        self.assertEqual(rows[0]["repo"], "/Users/josh/Developer/jev")

    def test_missing_token_usage_stays_unmeasured_not_zero(self) -> None:
        metrics = _metrics([{"input_tokens": None}], lambda row: row["input_tokens"])
        self.assertEqual(metrics["calls"], 1)
        self.assertIsNone(metrics["input_tokens"])
        self.assertIsNone(metrics["jev_spend_usd"])

    def test_native_percentiles_are_unmeasured_when_any_call_lacks_latency(
        self,
    ) -> None:
        metrics = _metrics(
            [{"input": 5, "latency": 10}, {"input": 8, "latency": None}],
            lambda row: row["input"],
            lambda row: row["latency"],
        )
        self.assertEqual(metrics["calls"], 2)
        self.assertIsNone(metrics["latency_ms_p50"])
        self.assertIsNone(metrics["latency_ms_p95"])

    def test_memory_percentiles_are_unmeasured_when_any_call_lacks_latency(
        self,
    ) -> None:
        incomplete = dict(CAPTURED_DROP)
        incomplete["promptHash"] = "turn-without-latency"
        incomplete["latencyMs"] = None
        metrics = memory_metrics([CAPTURED_ENFORCED, CAPTURED_DROP, incomplete])
        self.assertFalse(metrics["memory_jev_latency_complete"])
        self.assertIsNone(metrics["memory_jev_latency_ms_p50"])
        self.assertIsNone(metrics["memory_jev_latency_ms_p95"])

    def test_smart_stop_usage_is_costed_when_value_remains_unmeasured(self) -> None:
        with self.tempdir() as temp:
            root = Path(temp)
            memory_log = root / "memory-filter.jsonl"
            memory_log.write_text("", encoding="utf-8")
            event = {
                "type": "model_usage",
                "timestamp": "2026-10-05T14:56:15.509Z",
                "purpose": "unexpected-stop",
                "provider": "typesafe",
                "model": "jev-latest",
                "usage": {"input": 825, "cost": {"total": 0.00003465}},
            }
            surface = {
                "id": "smart-stop",
                "group": "native",
                "expect": "on",
                "purpose": "unexpected-stop",
                "name": "smart stop",
                "evidence": "no measured continuation benefit",
                "saving": "none",
            }
            with (
                patch(
                    "report.native_usage",
                    return_value=({"unexpected-stop": [event]}, {}),
                ),
                patch("report.MEMORY_LOG", memory_log),
            ):
                report = assemble_report(
                    [surface],
                    {"surfaces": {}, "_sha256": "0" * 64},
                    days=1,
                    end=datetime(2026, 10, 5, 15, 0, tzinfo=timezone.utc),
                    history=root / "history.jsonl",
                )
            row = report["rows"][0]
            self.assertEqual(row["calls"], 1)
            self.assertEqual(row["input_tokens"], 825)
            self.assertAlmostEqual(row["jev_spend_usd"], 0.00003465)
            self.assertIsNone(row["value_usd"])
            self.assertEqual(row["verdict"], "UNMEASURED")

    def test_memory_report_includes_late_ignored_call_cost(self) -> None:
        with self.tempdir() as temp:
            root = Path(temp)
            memory_log = root / "memory-filter.jsonl"
            state = root / "state"
            state.mkdir()
            drop = copy.deepcopy(CAPTURED_DROP)
            drop["ts"] = "2026-10-03T22:20:03.462Z"
            enforced = copy.deepcopy(CAPTURED_ENFORCED)
            enforced["ts"] = "2026-10-03T22:20:03.651Z"
            memory_log.write_text(
                "\n".join(
                    json.dumps(row) for row in (drop, enforced, CAPTURED_LATE_IGNORED)
                )
                + "\n",
                encoding="utf-8",
            )
            surface = {
                "id": "memory-filter",
                "group": "extension",
                "expect": "on",
                "name": "memory relevance filter",
                "evidence": "captured fixture",
                "saving": "tokens removed",
            }
            with (
                patch("report.native_usage", return_value=({}, {})),
                patch("report.MEMORY_LOG", memory_log),
                patch("report.STATE", state),
            ):
                report = assemble_report(
                    expand_memory_surfaces([surface]),
                    {"surfaces": {}, "_sha256": "0" * 64},
                    days=7,
                    end=datetime(2026, 10, 5, 17, 0, tzinfo=timezone.utc),
                    history=root / "history.jsonl",
                )
            memory_row = next(
                row for row in report["rows"] if row["id"] == "memory-jev"
            )
            self.assertEqual(
                memory_row["value_measure"], {"tokens_saved": 74, "drop_rows": 1}
            )
            self.assertEqual(memory_row["calls"], 2)
            self.assertEqual(memory_row["input_tokens"], 848)
            self.assertAlmostEqual(memory_row["jev_spend_usd"], 0.000035616)
            self.assertEqual(memory_row["latency_ms_p95"], 443)

    def test_report_uses_requested_frozen_memory_source_and_window(self) -> None:
        with self.tempdir() as temp:
            root = Path(temp)
            state = root / "state"
            state.mkdir()
            frozen = root / "frozen.jsonl"
            rolling = root / "rolling.jsonl"
            drop = copy.deepcopy(CAPTURED_DROP)
            drop["ts"] = "2026-10-03T18:55:00.000Z"
            enforced = copy.deepcopy(CAPTURED_ENFORCED)
            enforced["ts"] = "2026-10-03T18:55:01.000Z"
            cap3 = copy.deepcopy(CAPTURED_CAP3)
            cap3["ts"] = "2026-10-03T19:00:00.000Z"
            frozen.write_text(
                "\n".join(json.dumps(row) for row in (drop, enforced, cap3)) + "\n",
                encoding="utf-8",
            )
            rolling_cap3 = dict(cap3)
            rolling_cap3["tokensSaved"] = 999
            rolling.write_text(json.dumps(rolling_cap3) + "\n", encoding="utf-8")
            surface = {
                "id": "memory-filter",
                "group": "extension",
                "expect": "on",
                "name": "memory relevance filter",
                "evidence": "captured fixture",
                "saving": "tokens removed",
            }
            with (
                patch("report.native_usage", return_value=({}, {})),
                patch("report.MEMORY_LOG", rolling),
                patch("report.STATE", state),
            ):
                report = assemble_report(
                    expand_memory_surfaces([surface]),
                    {"surfaces": {}, "_sha256": "0" * 64},
                    days=1,
                    end=datetime(2026, 10, 3, 20, 0, tzinfo=timezone.utc),
                    history=root / "history.jsonl",
                    memory_path=frozen,
                )
            rows = {row["id"]: row for row in report["rows"]}
            self.assertEqual(rows["memory-jev"]["value_measure"]["tokens_saved"], 74)
            self.assertEqual(rows["memory-cap3"]["value_measure"]["tokens_saved"], 58)
            self.assertEqual(report["window"]["start"], "2026-10-02T20:00:00+00:00")
            self.assertEqual(report["window"]["end"], "2026-10-03T20:00:00+00:00")

    def test_committed_memory_window_reproduces_token_totals(self) -> None:
        artifact = Path(__file__).with_name("window-20261002.jsonl")
        checksum = Path(__file__).with_name("window-20261002.sha256")
        expected_hash = checksum.read_text(encoding="utf-8").split()[0]
        self.assertEqual(
            hashlib.sha256(artifact.read_bytes()).hexdigest(), expected_hash
        )

        start = datetime(2026, 10, 2, 20, 0, tzinfo=timezone.utc)
        end = datetime(2026, 10, 3, 20, 0, tzinfo=timezone.utc)
        metrics = memory_metrics(read_jsonl(artifact, start, end))
        self.assertEqual(metrics["memory_jev_tokens"], 33_884)
        self.assertEqual(metrics["memory_cap3_tokens"], 108_270)

    def test_gate_emits_unmeasured_verdicts_and_fails_when_harm_costs_are_missing(
        self,
    ) -> None:
        with self.tempdir() as temp:
            root = Path(temp)
            expected = root / "expected.json"
            find_surface = next(
                surface for surface in load_expected() if surface["id"] == "find"
            )
            expected.write_text(
                json.dumps({"surfaces": [find_surface]}), encoding="utf-8"
            )
            memory_input = root / "memory-filter.jsonl"
            memory_input.write_text("", encoding="utf-8")
            missing_costs = root / "harm-costs.json"
            output = io.StringIO()
            with (
                patch("report.native_usage", return_value=({}, [])),
                contextlib.redirect_stdout(output),
            ):
                status = main(
                    [
                        "--gate",
                        "--days",
                        "7",
                        "--expected",
                        str(expected),
                        "--harm-costs",
                        str(missing_costs),
                        "--memory-input",
                        str(memory_input),
                        "--history",
                        str(root / "ledger-history.jsonl"),
                    ]
                )

            try:
                result = json.loads(output.getvalue())
            except json.JSONDecodeError as exc:
                self.fail(f"--gate did not emit valid JSON: {exc}")
            self.assertEqual(status, 1)
            self.assertIsNone(result["harm_costs_sha256"])
            row = next(row for row in result["rows"] if row["id"] == "find")
            self.assertEqual(row["verdict"], "UNMEASURED")
            self.assertIsNone(row["value_usd"])
            self.assertIn("find", "\n".join(result["strict_failures"]))


if __name__ == "__main__":
    unittest.main()
