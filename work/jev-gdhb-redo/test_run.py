from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Self
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run


class StubResponse:
    def __init__(self, body: bytes, headers: dict[str, str]) -> None:
        self.body = body
        self.headers = headers

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def geturl(self) -> str:
        return run.CLEF_ENDPOINT_URL

    def read(self) -> bytes:
        return self.body


class StubOpener:
    def __init__(self, response: StubResponse) -> None:
        self.response = response

    def open(self, _request: object, timeout: int) -> StubResponse:
        return self.response


class ClefMassiveTests(unittest.TestCase):
    def test_spec_pins_only_local_clef_and_marks_jev_not_run(self) -> None:
        rows = run.load_jsonl(run.CORPUS)
        prior_hashes, _ = run.collect_prior_texts()
        spec = run.build_spec(rows, run.sha256_file(run.CORPUS), prior_hashes)

        self.assertEqual(
            spec["models"],
            {
                "clef": "clef-flash",
                "endpoint": "http://127.0.0.1:11300/jev/clef-flash/classify",
                "jev_arm": "NOT_RUN",
            },
        )
        self.assertEqual(spec["execution"], {"concurrency": 1, "retries": 0})
        self.assertEqual(spec["cost_usd"], 0.0)
        self.assertEqual(spec["sample"]["row_count"], 954)
        self.assertIn("model id is exactly clef-flash", spec["response_validation"])
        self.assertEqual(
            spec["question"]["criteria_description_rule"],
            "replace each choice label underscore with a space",
        )

    def test_request_uses_all_labels_and_original_utterance(self) -> None:
        source = run.load_jsonl(run.CORPUS)
        labels = sorted({row["gold"] for row in source})
        utterance = source[0]["text"]

        payload = run.build_request_payload(utterance, labels)

        self.assertEqual(payload["model"], "clef-flash")
        self.assertEqual(payload["state"], {"customer_message": utterance})
        self.assertEqual(
            payload["questions"]["intent"]["criteria"],
            {label: label.replace("_", " ") for label in labels},
        )
        self.assertNotIn("options", payload["questions"]["intent"])

    def test_request_refuses_malformed_json(self) -> None:
        response = StubResponse(
            b"{",
            {run.LOCALBENCH_REQUEST_ID_HEADER: "localbench-test"},
        )
        with (
            patch.object(run, "LOCAL_OPENER", StubOpener(response)),
            self.assertRaises(run.RunStop) as caught,
        ):
            run.request_local(run.load_jsonl(run.CORPUS)[0]["text"])

        self.assertEqual(str(caught.exception), "local Clef response is not valid JSON")

    def test_request_refuses_missing_localbench_request_id(self) -> None:
        response = StubResponse(b"{}", {})
        with (
            patch.object(run, "LOCAL_OPENER", StubOpener(response)),
            self.assertRaises(run.RunStop) as caught,
        ):
            run.request_local(run.load_jsonl(run.CORPUS)[0]["text"])

        self.assertEqual(str(caught.exception), "response lacks localbench guard request id")

    def test_request_refuses_missing_model_identity(self) -> None:
        labels = sorted({row["gold"] for row in run.load_jsonl(run.CORPUS)})
        probabilities = {label: 0.0 for label in labels}
        probabilities[labels[0]] = 1.0
        response_body = json.dumps(
            {
                "answers": {
                    run.QUESTION_NAME: {
                        "choice": labels[0],
                        "probabilities": probabilities,
                        "confidence": 1.0,
                    }
                }
            }
        ).encode()
        response = StubResponse(
            response_body,
            {run.LOCALBENCH_REQUEST_ID_HEADER: "localbench-test"},
        )
        with (
            patch.object(run, "LOCAL_OPENER", StubOpener(response)),
            self.assertRaises(TypeError) as caught,
        ):
            run.request_local(run.load_jsonl(run.CORPUS)[0]["text"])

        self.assertEqual(str(caught.exception), "Clef response model id is missing or not a string")

    def test_prediction_loop_serializes_calls_and_stops_on_first_error(self) -> None:
        source = run.load_jsonl(run.CORPUS)
        labels = sorted({row["gold"] for row in source})[:3]
        rows = [
            {"id": f"row-{index}", "gold": labels[index], "text": source[index]["text"]}
            for index in range(3)
        ]
        failed_utterance = rows[1]["text"]
        probabilities = {label: 0.0 for label in labels}
        probabilities[labels[0]] = 1.0
        active = 0
        max_active = 0
        calls = 0

        def transport(utterance: str) -> dict[str, object]:
            nonlocal active, max_active, calls
            calls += 1
            active += 1
            max_active = max(max_active, active)
            try:
                if utterance == failed_utterance:
                    raise ConnectionError("Clef unavailable")
                return {
                    "choice": labels[0],
                    "probabilities": probabilities,
                    "latency_ms": 1,
                    "model": "clef-flash",
                }
            finally:
                active -= 1

        with tempfile.TemporaryDirectory() as directory:
            results_path = Path(directory) / "rows.jsonl"
            predictions = run.run_predictions(rows, transport, results_path=results_path)
            persisted = run.load_jsonl(results_path)

        self.assertEqual(calls, 2)
        self.assertEqual(max_active, 1)
        self.assertEqual([row["status"] for row in predictions], ["scored", "ERROR"])
        self.assertNotIn("text", predictions[0])
        self.assertEqual(predictions[1]["error_class"], "ConnectionError")
        self.assertEqual(persisted, predictions)
        expected_hash = run.sha256_file(Path(run.__file__))
        for record in persisted:
            self.assertEqual(record["run_py_sha256"], expected_hash)
            timestamp = record["row_started_at_utc"]
            self.assertIsInstance(timestamp, str)
            self.assertTrue(timestamp.endswith("Z"))
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            self.assertEqual(parsed.utcoffset(), timezone.utc.utcoffset(None))

    def test_prediction_loop_refuses_wrong_model(self) -> None:
        corpus = run.load_jsonl(run.CORPUS)
        row = corpus[0]
        labels = sorted({item["gold"] for item in corpus})
        probabilities = {label: 0.0 for label in labels}
        probabilities[labels[0]] = 1.0
        predictions = run.run_predictions(
            [row],
            lambda _utterance: {
                "model": "wrong-model",
                "choice": labels[0],
                "probabilities": probabilities,
                "confidence": 1.0,
            },
        )

        self.assertEqual(predictions[0]["status"], "ERROR")
        self.assertEqual(predictions[0]["error_class"], "RunStop")

    def test_valid_choice_must_be_offered_and_probability_maximum(self) -> None:
        all_labels = sorted({row["gold"] for row in run.load_jsonl(run.CORPUS)})
        labels = all_labels[:2]
        valid = {labels[0]: 0.8, labels[1]: 0.2}

        self.assertIsNone(run.validate_answer(labels[0], valid, labels))
        self.assertEqual(
            run.validate_answer(labels[1], valid, labels),
            "choice_not_probability_maximum",
        )
        self.assertEqual(
            run.validate_answer(all_labels[2], valid, labels),
            "choice_not_offered",
        )

    def test_score_uses_only_complete_clef_rows_and_keeps_jev_not_run(self) -> None:
        corpus = run.load_jsonl(run.CORPUS)
        labels = sorted({row["gold"] for row in corpus})
        rows = [
            {"id": row["id"], "gold": row["gold"]}
            for row in corpus[:20]
        ]
        predictions = []
        for index, row in enumerate(rows):
            if index == 19:
                predictions.append(
                    {"row_id": row["id"], "status": "invalid", "choice": None}
                )
            else:
                choice = (
                    row["gold"]
                    if index < 10
                    else next(
                        label for label in labels if label != row["gold"]
                    )
                )
                predictions.append(
                    {"row_id": row["id"], "status": "scored", "choice": choice}
                )

        metrics = run.score_completed(rows, predictions)

        self.assertEqual(metrics["outcome"], "CLEF_ONLY_MEASURED")
        self.assertEqual(metrics["clef_correct"], 10)
        self.assertEqual(metrics["clef_accuracy"], 0.5)
        self.assertEqual(metrics["invalid_answers"], 1)
        self.assertEqual(metrics["jev_arm_status"], "NOT_RUN")
        self.assertNotIn("mcnemar_two_sided_exact_p", metrics)
        with self.assertRaises(run.RunStop):
            run.score_completed(rows, predictions[:-1])




if __name__ == "__main__":
    unittest.main()
