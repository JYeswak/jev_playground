from __future__ import annotations

import copy
import hashlib
import io
from contextlib import redirect_stdout
import json
import tempfile
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MINER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MINER_DIR))

import miner

try:
    TASK = json.loads((MINER_DIR / "task.json").read_text(encoding="utf-8"))
    FIXTURE = MINER_DIR / TASK["fixture"]
    AS_OF = TASK["as_of"]
except (OSError, json.JSONDecodeError) as error:
    raise RuntimeError("invalid fleet-miner task or fixture path") from error


def fixture_rows():
    rows = []
    for line_number, line in enumerate(FIXTURE.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise AssertionError(f"invalid fixture JSON at line {line_number}") from error
    return rows


def fixture_metrics(rows=None):
    cutoff = miner._timestamp(AS_OF)
    metrics = miner.Metrics(cutoff - miner.timedelta(days=TASK["window_days"]), cutoff)
    for row in fixture_rows() if rows is None else rows:
        metrics.process(row, str(FIXTURE))
    metrics.finish()
    return metrics


class MinerLabelsTest(unittest.TestCase):
    def test_result_readback_join_is_scoped_to_session_and_hash_only(self):
        rows = miner.extract_result_labels(fixture_rows(), AS_OF)

        self.assertEqual([row["label"] for row in rows], ["read_back", "not_read_back"])
        for row in rows:
            self.assertIsInstance(row["session_id_sha256"], str)
            self.assertEqual(len(row["session_id_sha256"]), 64)
            self.assertIsInstance(row["call_index"], int)
            self.assertEqual(
                set(row),
                {"session_id_sha256", "call_index", "artifact_sha256", "event_sha256", "label"},
            )

    def test_reused_tool_call_ids_never_join_across_sessions(self):
        rows = copy.deepcopy(fixture_rows())
        for row in rows:
            if row.get("id") == "m07":
                row["message"]["content"][0]["id"] = "c01"
            elif row.get("id") == "m08":
                row["message"]["toolCallId"] = "c01"

        expected = [
            (hashlib.sha256(b"synthetic-session-a").hexdigest(), 1, "read_back"),
            (hashlib.sha256(b"synthetic-session-a").hexdigest(), 3, "not_read_back"),
        ]
        for emitted in (
            miner.extract_result_labels(rows, AS_OF),
            [row for row in fixture_metrics(rows).label_rows("result") if "artifact_sha256" in row],
        ):
            self.assertEqual(
                [(row["session_id_sha256"], row["call_index"], row["label"]) for row in emitted],
                expected,
            )

    def test_label_emitters_exclude_events_before_the_fourteen_day_window(self):
        rows = []
        for row in fixture_rows():
            older = dict(row)
            older["timestamp"] = "2026-09-19T00:40:00Z"
            rows.append(older)

        self.assertEqual(miner.extract_result_labels(rows, AS_OF), [])
        self.assertEqual(miner.extract_reread_events(rows, AS_OF), [])

    def test_as_of_drops_every_later_tool_call(self):
        calls = miner.tool_calls(fixture_rows(), AS_OF)

        self.assertFalse(any(call.path == "/fixture/after-cutoff.py" for call in calls))

    def test_reread_emits_raw_refetch_metadata_without_harm_or_label(self):
        rows = miner.extract_reread_events(fixture_rows(), AS_OF)

        self.assertEqual(len(rows), 3)
        self.assertEqual([row["calls_since_prior_read"] for row in rows], [1, 0, 1])
        self.assertEqual([row["line_range"] for row in rows], ["1-10", "11-20:raw", "11-20:raw"])
        self.assertEqual(fixture_metrics().label_rows("reread"), rows)
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "session_id_sha256",
                    "call_index",
                    "path_sha256",
                    "line_range",
                    "fetch_tool",
                    "calls_since_prior_read",
                },
            )

    def test_sed_in_place_write_invalidates_repeat_read_candidate(self):
        repeats = miner.classify_repeat_reads(fixture_rows(), AS_OF)

        self.assertEqual([row["is_redundant"] for row in repeats], [False, True, True])

    def test_missing_joined_outcome_is_emitted_not_counted_despite_positive_hint(self):
        metrics = fixture_metrics()
        missing = [
            row for row in metrics.label_rows("delegate")
            if row["session_id_sha256"] == hashlib.sha256(b"synthetic-session-proxies").hexdigest()
            and row["call_index"] == 7
        ]

        self.assertTrue(missing)
        for row in missing:
            self.assertIsNone(row["label"])
            self.assertEqual(row["status"], "NOT_COUNTED")

    def test_same_command_rerun_exposes_distance_without_inventing_k(self):
        metrics = fixture_metrics()
        session_hash = hashlib.sha256(b"synthetic-session-proxies").hexdigest()
        reruns = [row for row in metrics.result_reruns if row["session_id_sha256"] == session_hash]

        self.assertEqual(len(reruns), 1)
        self.assertEqual(reruns[0]["calls_until_repeat"], 1)
        self.assertEqual(reruns[0]["calls_since_result"], 1)
        self.assertIsNone(reruns[0]["rerun_window_calls"])
        self.assertIsNone(reruns[0]["label"])
        self.assertEqual(reruns[0]["status"], "NOT_COUNTED")
        self.assertIn(reruns[0], metrics.label_rows("result"))

    def test_organic_family_rows_use_closed_private_proxy_envelope(self):
        metrics = fixture_metrics()
        base = {
            "schema_version", "family", "session_id_sha256", "call_index",
            "event_sha256", "label", "status", "source_kind",
        }
        for family in ("route", "nudge", "recover", "land", "outcome", "pin", "delegate"):
            rows = metrics.label_rows(family)
            with self.subTest(family=family):
                self.assertTrue(rows)
            for row in rows:
                with self.subTest(family=family, source=row["source_kind"]):
                    self.assertTrue(base <= set(row))
                    self.assertEqual(row["schema_version"], 1)
                    self.assertEqual(row["family"], family)
                    for key, value in row.items():
                        if key.endswith("_sha256"):
                            self.assertRegex(value, r"^[0-9a-f]{64}$")
                        elif key not in base:
                            self.assertIsInstance(value, (int, type(None)))
                    self.assertIsInstance(row["call_index"], (int, type(None)))
                    self.assertEqual(row["status"], "COUNTED" if row["label"] is not None else "NOT_COUNTED")
                    serialized = json.dumps(row)
                    for private in ("/fixture", "synthetic-session", "printf repeated", "Synthetic fixture"):
                        self.assertNotIn(private, serialized)
                    self.assertNotIn("harm", row)
                    self.assertNotIn("accepted", row)

    def test_family_outcomes_remain_source_defined_proxies(self):
        rows = fixture_rows()
        metrics = fixture_metrics(rows)
        by_id = {row["id"]: row for row in rows if "id" in row}
        cases = [
            # Family, source proxy, origin event, originating/followup call, session, observed label.
            ("route", "locate_find", "m17", 5, "synthetic-session-c", None),
            ("route", "find_next_call", "m17", 5, "synthetic-session-c", "next_read"),
            ("route", "ask_result", "proxy05", 3, "synthetic-session-proxies", "error"),
            ("nudge", "todo_nudge", "n01", 7, "synthetic-session-c", "followed"),
            ("nudge", "kit_guard", "kit01", 1, "synthetic-session-kit-guard", "reread_agents"),
            ("nudge", "todo_nudge", "nudge-unjoined", None, "synthetic-session-proxies", None),
            ("recover", "bash_error", "m24", 8, "synthetic-session-c", "changed_command:ok"),
            ("recover", "bash_error", "proxy08", 4, "synthetic-session-proxies", "changed_command:err"),
            ("recover", "bash_error", "proxy10", 5, "synthetic-session-proxies", None),
            ("land", "git_commit_result", "proxy07", 4, "synthetic-session-proxies", "error"),
            ("land", "git_commit_hook_reject", "proxy07", 4, "synthetic-session-proxies", "hook_reject"),
            ("land", "br_close_result", "proxy09", 5, "synthetic-session-proxies", "error"),
            ("land", "br_close_refused", "proxy09", 5, "synthetic-session-proxies", "refused_or_error"),
            ("outcome", "correction_after_final", "m31", None, "synthetic-session-c", "correction"),
            ("outcome", "correction_after_final", "proxy13", None, "synthetic-session-proxies", "no_correction_observed"),
            ("pin", "compaction", "k01", 10, "synthetic-session-c", "reread_prior_file"),
            ("delegate", "task_spawn", "m29", 11, "synthetic-session-c", None),
            ("delegate", "task_agent", "m29", 11, "synthetic-session-c", "error"),
            ("delegate", "task_model", "m29", 11, "synthetic-session-c", None),
            ("delegate", "task_spawn", "proxy11", 6, "synthetic-session-proxies", None),
            ("delegate", "task_agent", "proxy11", 6, "synthetic-session-proxies", "ok"),
            ("delegate", "task_model", "proxy11", 6, "synthetic-session-proxies", None),
            ("delegate", "task_spawn", "proxy15", 7, "synthetic-session-proxies", None),
            ("delegate", "task_agent", "proxy15", 7, "synthetic-session-proxies", None),
            ("delegate", "task_model", "proxy15", 7, "synthetic-session-proxies", None),
        ]
        for family, source_kind, event_id, call_index, session_id, expected_label in cases:
            event_hash = hashlib.sha256(
                json.dumps(by_id[event_id], sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            session_hash = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
            with self.subTest(family=family, source=source_kind, event=event_id):
                emitted = [
                    row for row in metrics.label_rows(family)
                    if row["source_kind"] == source_kind
                    and row["event_sha256"] == event_hash
                    and row["session_id_sha256"] == session_hash
                    and row["call_index"] == call_index
                ]
                self.assertEqual(len(emitted), 1)
                self.assertEqual(emitted[0]["label"], expected_label)
                self.assertEqual(emitted[0]["status"], "NOT_COUNTED" if expected_label is None else "COUNTED")

    def test_nudge_followup_in_another_session_does_not_label_origin(self):
        rows = fixture_rows()
        origin = next(row for row in rows if row.get("id") == "nudge-unjoined")
        later_session = {
            "type": "session", "id": "synthetic-later-session",
            "timestamp": origin["timestamp"],
        }
        later_todo = copy.deepcopy(next(row for row in rows if row.get("id") == "m21"))
        later_todo["timestamp"] = origin["timestamp"]
        metrics = fixture_metrics([
            {"type": "session", "id": "synthetic-origin-session", "timestamp": origin["timestamp"]},
            origin, later_session, later_todo,
        ])

        origin_rows = [
            row for row in metrics.label_rows("nudge")
            if row["session_id_sha256"] == hashlib.sha256(b"synthetic-origin-session").hexdigest()
        ]
        self.assertTrue(origin_rows)
        self.assertTrue(all(row["label"] is None and row["status"] == "NOT_COUNTED" for row in origin_rows))

    def test_ca37_rows_reproduce_observed_label_counts(self):
        counts = miner.ca37_candidate_counts(ROOT / "work" / "jev-census" / "candidates.json")

        self.assertEqual(
            counts,
            {
                "vendor_paste": (0, 39),
                "skill_veto": (53, 200),
                "gate_cascade": (4, 102),
                "memory_filter": (75, 100),
            },
        )

    def test_decision_log_scalar_counts_accumulate_as_integer_values(self):
        stamp = "2026-10-05T14:56:20.781Z"
        metrics = miner.Metrics(miner._timestamp(stamp), miner._timestamp(stamp))

        metrics.process(
            {"ts": stamp, "status": "scored", "flag": False, "latencyMs": 858, "model": "nimble:latest"},
            "/fixture/.local/state/jev/gate-observe.jsonl",
        )

        self.assertEqual(miner._source_count("dl:gate-observe.jsonl:status=scored", metrics), 1)

    def test_rank_labels_count_touched_hit_rows_not_hit_entries(self):
        stamp = "2026-09-27T03:32:28.259Z"
        metrics = miner.Metrics(miner._timestamp("2026-09-20T00:48:27Z"), miner._timestamp(AS_OF))
        observed_hit_sha256 = "780bc12cbd4e805bf40a03d309f29f31d86a5eb0d8c58ceeb715636d40360ba8"

        metrics.process(
            {
                "schema": "jev-find-rank.v1",
                "ts": stamp,
                "session": "synthetic-rank-session",
                "hits": [observed_hit_sha256],
                "count": 1,
                "nextToolCalls": [
                    {"ordinal": 5, "tool": "read", "touched": [observed_hit_sha256]},
                    {"ordinal": 6, "tool": "read", "touched": [observed_hit_sha256]},
                ],
                "complete": False,
            },
            "/fixture/.local/state/jev/find-rank.jsonl",
        )

        source = "k:421:find-rank.jsonl rows whose next calls touched a returned hit"
        self.assertEqual(miner._source_count(source, metrics), 1)

        emitted = metrics.label_rows("rank")
        self.assertEqual(len(emitted), 1)
        self.assertEqual(emitted[0]["source_kind"], "find_rank")
        self.assertEqual(
            emitted[0]["session_id_sha256"],
            hashlib.sha256(b"synthetic-rank-session").hexdigest(),
        )
        self.assertIsNone(emitted[0]["call_index"])
        self.assertEqual(emitted[0]["label"], "touched_shown_hit")
        self.assertEqual(emitted[0]["status"], "COUNTED")
        # The recorded outcome is known even though its transcript index is not.

    def test_rank_ignores_unshown_hits_and_requires_complete_negative_window(self):
        observed_hit = "780bc12cbd4e805bf40a03d309f29f31d86a5eb0d8c58ceeb715636d40360ba8"
        row = {
            "schema": "jev-find-rank.v1", "ts": "2026-09-27T03:32:28.259Z",
            "session": "synthetic-rank-session", "hits": [observed_hit], "count": 1,
            "nextToolCalls": [{"ordinal": 5, "tool": "read", "touched": ["unshown-hit"]}],
            "complete": False,
        }
        metrics = fixture_metrics([])
        metrics.process(row, "/fixture/.local/state/jev/find-rank.jsonl")
        self.assertEqual(metrics.find_rank_touched, 0)
        self.assertEqual(metrics.label_rows("rank")[0]["status"], "NOT_COUNTED")
        row["complete"] = True
        metrics.process(row, "/fixture/.local/state/jev/find-rank.jsonl")
        self.assertEqual(metrics.label_rows("rank")[-1]["label"], "no_shown_hit_touched")
        self.assertIsNone(metrics.label_rows("rank")[-1]["call_index"])

    def test_missing_golden_provenance_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            family = Path(directory) / "result"
            family.mkdir()
            (family / "labels.jsonl").write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "PROVENANCE.md"):
                miner.validate_golden_provenance(family)

    def test_golden_writer_records_and_checks_hash_only_rows(self):
        row = miner.extract_result_labels(fixture_rows(), AS_OF)[0]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result"
            with patch.dict("os.environ", {"UPDATE_GOLDENS": "1"}), patch.object(
                miner, "_miner_commit", return_value="f" * 40
            ):
                miner._write_labels([row], "result", AS_OF, target)

            miner.validate_golden_provenance(target)
            saved = json.loads((target / "labels.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(saved, row)
            self.assertEqual(
                set(saved),
                {"session_id_sha256", "call_index", "artifact_sha256", "event_sha256", "label"},
            )
            (target / "labels.jsonl").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "sha256"):
                miner.validate_golden_provenance(target)

    def test_provenance_refuses_running_source_and_input_invocation_mismatch(self):
        row = miner.extract_result_labels(fixture_rows(), AS_OF)[0]
        command = f"UPDATE_GOLDENS=1 python3 work/fleet-schema/miner.py --labels result --as-of {AS_OF} --input {FIXTURE} --json"
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result"
            with patch.dict("os.environ", {"UPDATE_GOLDENS": "1"}), patch.object(
                miner, "_miner_commit", return_value="f" * 40
            ):
                miner._write_labels([row], "result", AS_OF, target, command=command)
            source_hash = hashlib.sha256(Path(miner.__file__).read_bytes()).hexdigest()
            miner.validate_golden_provenance(
                target, expected_miner_source_sha256=source_hash, expected_command=command
            )
            with self.assertRaisesRegex(ValueError, "source"):
                miner.validate_golden_provenance(target, expected_miner_source_sha256="0" * 64)
            with self.assertRaisesRegex(ValueError, "command"):
                miner.validate_golden_provenance(
                    target, expected_command=command.replace(str(FIXTURE), "/fixture/different-input.jsonl")
                )



    def test_golden_writer_refuses_uncommitted_running_source_before_writing(self):
        row = miner.extract_result_labels(fixture_rows(), AS_OF)[0]
        git_results = [
            miner.subprocess.CompletedProcess([], 0, stdout="f" * 40 + "\n"),
            miner.subprocess.CompletedProcess([], 0, stdout=b"different committed miner source\n"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result"
            with patch.dict("os.environ", {"UPDATE_GOLDENS": "1"}), patch.object(
                miner.subprocess, "run", side_effect=git_results
            ), self.assertRaisesRegex(ValueError, "running miner source differs"):
                miner._write_labels([row], "result", AS_OF, target)
            self.assertFalse(target.exists())


class MinerSafetyTest(unittest.TestCase):
    def test_empty_scan_set_fails_closed(self):
        result = miner.scan_files(
            [],
            AS_OF,
            load_average=lambda: 0.0,
            clock=lambda: 0.0,
        )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.complete_counts, {})
        self.assertEqual(result.counts, {"empty_input": 1})

    def test_load_above_80_defers_without_reading(self):
        result = miner.scan_files(
            [FIXTURE],
            AS_OF,
            load_average=lambda: 81.0,
            clock=lambda: 0.0,
            budget_seconds=3000.0,
        )

        self.assertEqual(result.verdict, "DEFERRED")
        self.assertEqual(result.files_read, ())
        self.assertEqual(result.files_not_read, (str(FIXTURE),))
        self.assertEqual(result.complete_counts, {})

    def test_load_crossing_limit_mid_file_stops_with_partial_verdict(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.jsonl"
            row = '{"timestamp":"2026-10-04T00:40:00Z","type":"observed"}\n'
            path.write_text(row * 16384, encoding="utf-8")
            loads = iter((0.0, 81.0))
            result = miner.scan_files(
                [path],
                AS_OF,
                load_average=lambda: next(loads),
                clock=lambda: 0.0,
            )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.files_read, ())
        self.assertEqual(result.files_not_read, (str(path),))
        self.assertNotIn("complete", result.counts)

    def test_budget_overrun_is_partial_and_names_unread_files(self):
        times = iter((0.0, 0.0, 1.1))
        result = miner.scan_files(
            [FIXTURE, FIXTURE],
            AS_OF,
            load_average=lambda: 0.0,
            clock=lambda: next(times),
            budget_seconds=1.0,
        )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.files_read, (str(FIXTURE),))
        self.assertEqual(result.files_not_read, (str(FIXTURE),))
        self.assertNotIn("complete", result.counts)

    def test_budget_above_cap_is_rejected_by_scanner_and_cli(self):
        with self.assertRaisesRegex(ValueError, "budget must be"):
            miner.scan_files(
                [FIXTURE],
                AS_OF,
                load_average=lambda: 0.0,
                clock=lambda: 0.0,
                budget_seconds=3000.1,
            )

        with self.assertRaises(SystemExit) as caught:
            miner._main([
                "--labels", "result",
                "--as-of", AS_OF,
                "--input", str(FIXTURE),
                "--budget-seconds", "3001",
            ])
        self.assertEqual(caught.exception.code, 2)

    def test_unreadable_file_makes_scan_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.jsonl"
            result = miner.scan_files(
                [FIXTURE, missing],
                AS_OF,
                load_average=lambda: 0.0,
                clock=lambda: 0.0,
            )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.files_read, (str(FIXTURE),))
        self.assertEqual(result.files_not_read, (str(missing),))
        self.assertNotIn("complete", result.counts)

    def test_invalid_json_never_yields_complete_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "malformed.jsonl"
            observed_session_row = FIXTURE.read_text(encoding="utf-8").splitlines()[0]
            path.write_text(observed_session_row + "\n{malformed\n", encoding="utf-8")
            result = miner.scan_files(
                [path],
                AS_OF,
                load_average=lambda: 0.0,
                clock=lambda: 0.0,
            )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.files_read, ())
        self.assertEqual(result.files_not_read, (str(path),))
        self.assertEqual(result.counts.get("invalid_json"), 1)

    def test_rank_reopens_at_thirty_positive_labels(self):
        current = {"outcome": {"occurrences": 10, "labels": 100, "positives": 30}}
        baseline = {"outcome": {"occurrences": 10, "labels": 100, "positives": 29}}

        self.assertIn("outcome", miner.rank_reopen_reasons(current, baseline))
        self.assertIn("positive_threshold", miner.rank_reopen_reasons(current, baseline)["outcome"])

    def test_rank_does_not_substitute_total_labels_for_positives(self):
        current = {"outcome": {"occurrences": 10, "labels": 100, "positives": 29}}
        baseline = {"outcome": {"occurrences": 10, "labels": 29, "positives": 29}}

        self.assertNotIn("outcome", miner.rank_reopen_reasons(current, baseline))

    def test_rank_json_reopens_at_positive_thirty_with_constant_total_labels(self):
        fixture = fixture_rows()
        final = next(row for row in fixture if row.get("id") == "m31")
        correction = next(row for row in fixture if row.get("id") == "m32")
        neutral = next(row for row in fixture if row.get("id") == "proxy14")
        points = [
            json.loads(line) for line in miner.PLAN_POINTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        points[4]["occurrences_14d"] = 100
        points[4]["label_count"] = 29
        points[4]["count_source"]["labels"] = ["c:user_after_final_answer"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "decision-points.jsonl"
            registry.write_text("".join(json.dumps(row) + "\n" for row in points), encoding="utf-8")
            input_path = root / "sessions.jsonl"
            report_path = root / "rank.txt"
            for positives in (29, 30):
                rows = [fixture[0]]
                for index in range(100):
                    rows.extend([final, correction if index < positives else neutral])
                input_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
                output = io.StringIO()
                with patch.object(miner, "PLAN_POINTS", registry), patch.object(
                    miner, "_ensure_nice"
                ), patch.object(miner, "_load_average", return_value=0.0), patch.dict(
                    "os.environ", {"UPDATE_GOLDENS": "0"}
                ), redirect_stdout(output):
                    status = miner._main([
                        "--rank", "--as-of", AS_OF, "--json", "--input", str(input_path),
                        "--rank-output", str(report_path),
                    ])
                with self.subTest(positives=positives):
                    self.assertEqual(status, 0)
                    payload = json.loads(output.getvalue())
                    self.assertEqual(payload["verdict"], "COMPLETE")
                    self.assertEqual(payload["families"]["outcome"], {
                        "occurrences": 100, "labels": 100, "positives": positives,
                    })
                    self.assertEqual(payload["plan_counts"]["outcome"]["positives"], 29)
                    if positives == 29:
                        self.assertNotIn("outcome", payload["reopen"])
                    else:
                        self.assertIn("positive_threshold", payload["reopen"]["outcome"])
                        self.assertIn("REOPEN", report_path.read_text(encoding="utf-8"))



if __name__ == "__main__":
    unittest.main()
