from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from collect_timewindow import (
    write_corpus,
)
from score_timewindow import (
    receipt_text,
    score_data,
    score_files,
    write_receipt,
)

OLD_CORPUS = HERE / "corpus.json"
TIMEWINDOW_ROWS = HERE / "timewindow-rows.jsonl"
TIMEWINDOW_CORPUS = HERE / "timewindow-corpus.json"

# Metadata only; these are real, distinct-source observations from the frozen
# 2026-10-02..04 corpus. The reference rows share size/tool, while the unref row
# is a real non-content tool. No result text is checked into this fixture.
HELD_REFERENCE_A = {
    "sample_id": "h-ref-a",
    "ref": True,
    "tool": "bash",
    "size": 51353,
    "source_path_sha256": "ed0cb9116cae2458b6054f3ac58747c76a0c2f995c2e6cbc10b63fad80768451",
}
HELD_REFERENCE_B = {
    "sample_id": "h-ref-b",
    "ref": True,
    "tool": "bash",
    "size": 51353,
    "source_path_sha256": "46152481ea891b885cb906552e64968014b5915d4ab801a687c5e490184ee40a",
}
HELD_UNREFERENCED = {
    "sample_id": "h-unref",
    "ref": False,
    "tool": "write",
    "size": 10612,
    "source_path_sha256": "ffc9ed04813eeb38a0dd443de66c65695869770a9e1919eb045b409a896518ae",
}


def prior_dev_rows() -> tuple[dict[str, object], dict[str, object]]:
    prior = json.loads(  # ubs:ignore — malformed committed fixture should fail this test
        OLD_CORPUS.read_text(encoding="utf-8")
    )
    rows = prior["dev"] + prior["held"]
    content_tools = {
        "read",
        "bash",
        "eval",
        "grep",
        "glob",
        "find",
        "web_search",
        "web_extract",
        "fetch",
    }
    referenced = next(
        row for row in rows if row["ref"] and row["tool"] in content_tools
    )
    unreferenced = next(row for row in rows if not row["ref"])

    def to_sample(sample_id: str, row: dict[str, object]) -> dict[str, object]:
        path = Path(str(row["file"])).expanduser().resolve().as_posix()
        return {
            "sample_id": sample_id,
            "ref": row["ref"],
            "tool": row["tool"],
            "size": row["size"],
            "source_path_sha256": hashlib.sha256(path.encode("utf-8")).hexdigest(),
        }
    return to_sample("d-ref", referenced), to_sample("d-unref", unreferenced)


def result_rows(
    samples: list[dict[str, object]], choices: dict[str, str]
) -> list[dict[str, object]]:
    return [
        {
            "sample_id": str(sample["sample_id"]),
            "model": "jev-1.13.0",
            "status": "scored",
            "choice": choices[str(sample["sample_id"])],
        }
        for sample in samples
    ]


class TimewindowScorerTests(unittest.TestCase):
    def test_later_reread_drop_is_counted_as_a_held_miss(self) -> None:
        dev = list(prior_dev_rows())
        held = [dict(HELD_REFERENCE_A), dict(HELD_UNREFERENCED)]
        corpus = {
            "status": "READY",
            "dev": dev,
            "held": held,
            "weekly_volume_estimate": 100,
        }
        samples = dev + held
        choices = {
            "d-ref": "keep",
            "d-unref": "keep",
            "h-ref-a": "drop",
            "h-unref": "keep",
        }

        report = score_data(corpus, result_rows(samples, choices))

        self.assertEqual(report.jev.reference_drops, 1)
        self.assertEqual(report.held_matched.reference_drops, 1)
        self.assertFalse(report.primary_advantage)

    def test_zero_drop_comparator_is_refused_when_jev_has_misses(self) -> None:
        dev = list(prior_dev_rows())
        held = [
            dict(HELD_REFERENCE_A),
            dict(HELD_REFERENCE_B),
            dict(HELD_UNREFERENCED),
        ]
        corpus = {
            "status": "READY",
            "dev": dev,
            "held": held,
            "weekly_volume_estimate": 100,
        }
        samples = dev + held
        choices = {
            "d-ref": "keep",
            "d-unref": "keep",
            "h-ref-a": "drop",
            "h-ref-b": "keep",
            "h-unref": "keep",
        }

        with self.assertRaisesRegex(ValueError, "zero-drop baseline"):
            score_data(corpus, result_rows(samples, choices))

    def test_insufficient_corpus_receipt_states_no_calls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            corpus_path = directory / "corpus.json"
            rows_path = directory / "rows.jsonl"
            corpus_path.write_text(
                json.dumps({"status": "NOT ENOUGH DATA", "counts": {"labelable": 12}}),
                encoding="utf-8",
            )
            rows_path.write_text("", encoding="utf-8")

            report = score_files(corpus_path, rows_path)
            receipt = receipt_text(report, corpus_path, rows_path)

        self.assertEqual(report["live_calls"], 0)
        self.assertIn("No Jev calls were run.", receipt)


    def test_scorer_rejects_rows_bound_to_different_result_hashes(self) -> None:
        records = [
            json.loads(line)  # ubs:ignore — malformed committed JSONL should fail this test
            for line in TIMEWINDOW_ROWS.read_text(encoding="utf-8").splitlines()
            if line
        ]
        changed = dict(records[0])
        digest = str(changed["full_result_sha256"])
        changed["full_result_sha256"] = ("0" if digest[0] != "0" else "1") + digest[1:]
        records[0] = changed

        with tempfile.TemporaryDirectory() as temporary:
            rows_path = Path(temporary) / "rows.jsonl"
            rows_path.write_text(
                "".join(f"{json.dumps(row)}\n" for row in records),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "corpus hashes"):
                score_files(TIMEWINDOW_CORPUS, rows_path)

    def test_old_excluded_corpus_is_never_a_write_target(self) -> None:
        before = hashlib.sha256(OLD_CORPUS.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, "excluded prior corpus"):
            write_corpus(OLD_CORPUS, {"dev": [], "held": []})
        with self.assertRaisesRegex(ValueError, "excluded prior corpus"):
            write_receipt(OLD_CORPUS, "must not replace the old corpus")
        self.assertEqual(hashlib.sha256(OLD_CORPUS.read_bytes()).hexdigest(), before)

    def test_committed_sample_is_disjoint_and_has_no_full_result_text(self) -> None:
        corpus = json.loads(  # ubs:ignore — malformed committed fixture should fail this test
            TIMEWINDOW_CORPUS.read_text(encoding="utf-8")
        )
        dev = corpus["dev"]
        held = corpus["held"]
        start = dt.datetime.fromisoformat(corpus["window_start"].replace("Z", "+00:00"))
        end = dt.datetime.fromisoformat(corpus["window_end_exclusive"].replace("Z", "+00:00"))
        for row in dev + held:
            timestamp = dt.datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            self.assertLessEqual(start, timestamp)
            self.assertLess(timestamp, end)
        self.assertEqual((len(dev), len(held)), (100, 100))
        dev_sources = {row["source_path_sha256"] for row in dev}
        held_sources = {row["source_path_sha256"] for row in held}
        self.assertFalse(dev_sources & held_sources)
        self.assertGreaterEqual(sum(row["ref"] for row in held), 20)
        self.assertGreaterEqual(sum(not row["ref"] for row in held), 20)
        prior_sources: set[str] = set()
        prior_result_prefixes: set[str] = set()
        for prior_path in (ROOT / "work/longres/corpus.json", OLD_CORPUS, ROOT / "work/longres/corpus2.json"):
            prior = json.loads(  # ubs:ignore — malformed historical fixture should fail this test
                prior_path.read_text(encoding="utf-8")
            )
            for prior_row in prior["dev"] + prior["held"]:
                canonical = Path(prior_row["file"]).expanduser().resolve().as_posix()
                prior_sources.add(hashlib.sha256(canonical.encode("utf-8")).hexdigest())
                prior_result_prefixes.add(str(prior_row["win_sha"]).lower())
        self.assertFalse((dev_sources | held_sources) & prior_sources)
        for row in dev + held:
            self.assertEqual(len(row["source_path_sha256"]), 64)
            self.assertEqual(len(row["full_result_sha256"]), 64)
            self.assertFalse(any(row["full_result_sha256"].startswith(prefix) for prefix in prior_result_prefixes))
            self.assertGreaterEqual(row["size"], 10_000)
            self.assertLessEqual(len(row["head"]), 350)
            self.assertLessEqual(len(row["tail"]), 350)
            self.assertLess(len(row["head"]) + len(row["tail"]), row["size"])
            self.assertNotIn("result_text", row)
            self.assertNotIn("file", row)


if __name__ == "__main__":
    unittest.main()
