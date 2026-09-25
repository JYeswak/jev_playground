"""Keyless tests over the seven committed MiniWoB observations."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from text_candidates import (  # noqa: E402
    OPTION_CAP,
    audit_observations,
    build_candidates,
    derive_needed_text,
    recorded_page_text_rows,
)


ROOT = HERE.parents[1]
OBS = HERE / "observations-real-20250925"


def load_record(path: Path) -> dict:
    try:
        value = json.JSONDecoder().decode(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AssertionError(f"{path}: expected JSON object")
    return value


EXPECTED = {
    "copy-paste": "Eget rhoncus, pellentesque malesuada non, donec morbi. Nunc ",
    "find-word": "Lacus,",
    "scroll-text": "Maecenas.",
    "text-transform": "6gHF",
    "enter-time": "21:37",
}


class CandidateBuilderTests(unittest.TestCase):
    def test_real_observations_derive_needed_text_and_cover_it(self) -> None:
        rows = audit_observations(OBS)
        by_task = {row["task"]: row for row in rows}
        expected_tasks = {path.stem for path in OBS.glob("*.json")}
        self.assertEqual(set(by_task), expected_tasks)
        for task, expected in EXPECTED.items():
            record = load_record(OBS / f"{task}.json")
            self.assertEqual(derive_needed_text(record), expected, task)
            candidate_map = build_candidates(record)
            self.assertTrue(candidate_map, task)
            self.assertTrue(
                any(expected in values for values in candidate_map.values()), task
            )
            self.assertLessEqual(
                max(len(values) for values in candidate_map.values()), OPTION_CAP
            )
            self.assertEqual(by_task[task]["covered"], 1)

    def test_selection_tasks_have_no_type_candidate_claim(self) -> None:
        for task in ("text-editor", "highlight-text"):
            record = load_record(OBS / f"{task}.json")
            self.assertIsNone(derive_needed_text(record))
            self.assertFalse(build_candidates(record))

    def test_recorded_rows_report_missing_observations(self) -> None:
        rows = recorded_page_text_rows(ROOT)
        self.assertTrue(rows)
        self.assertTrue(all(row["observation_rows"] == 0 for row in rows))
        self.assertTrue(all(row["coverage"] == "NOT_RUN" for row in rows))


if __name__ == "__main__":
    unittest.main()
