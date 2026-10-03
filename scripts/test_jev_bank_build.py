"""Regression tests for the phase-0 decision-bank builder."""

import importlib.util
import json
import unittest
from pathlib import Path

BUILDER_PATH = Path(__file__).with_name("jev-bank-build.py")
SPEC = importlib.util.spec_from_file_location("jev_bank_build", BUILDER_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load builder from {BUILDER_PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class SecretScrubTests(unittest.TestCase):
    def test_redacts_standalone_typesafe_key_shape(self):
        token = f"apikey_fakefake{'a' * 27}_{'b' * 64}"

        scrubbed = BUILDER.scrub(f"tool result included {token}")

        self.assertNotIn(token, scrubbed)
        self.assertIn("[REDACTED]", scrubbed)

    def test_redacts_long_apikey_token(self):
        token = f"apikey_fakefake{'c' * 12}"

        scrubbed = BUILDER.scrub(f"tool result included {token}")

        self.assertNotIn(token, scrubbed)
        self.assertIn("[REDACTED]", scrubbed)

    def test_leaves_incomplete_key_shape_unchanged(self):
        text = "tool result referenced apikey_not-a-secret"

        self.assertEqual(BUILDER.scrub(text), text)

    def test_redacts_answer_payloads_from_every_sheet_text_field(self):
        jev_output = json.dumps(
            {
                "jev": {
                    "raw_score": 0.75,
                    "probabilities": {"low": 0.25, "high": 0.75},
                    "model": "jev-1.13.0",
                }
            }
        )
        system_one_output = json.dumps(
            {"answers": {"relevance": {"noul": 0.9, "confidence": 0.8}}}
        )
        choice_output = json.dumps(
            {
                "answers": {
                    "triage": {
                        "choice": "drop",
                        "probabilities": {"keep": 0.1, "drop": 0.9},
                    }
                }
            }
        )
        unwrapped_output = json.dumps({"raw_score": None, "probabilities": {}})
        sheet_row = {
            "state": {
                "task": "safe context",
                "result_head": jev_output,
                "result_tail": unwrapped_output,
            },
            "outcome_window": [{"text": system_one_output}, {"text": choice_output}],
        }

        scrubbed = BUILDER.redact_blind_sheet_value(sheet_row)

        self.assertEqual(scrubbed["state"]["result_head"], "[MODEL_ANSWER_REDACTED]")
        self.assertEqual(scrubbed["state"]["result_tail"], "[MODEL_ANSWER_REDACTED]")
        self.assertEqual(
            scrubbed["outcome_window"][0]["text"], "[MODEL_ANSWER_REDACTED]"
        )
        self.assertEqual(
            scrubbed["outcome_window"][1]["text"], "[MODEL_ANSWER_REDACTED]"
        )
        self.assertEqual(scrubbed["state"]["task"], "safe context")
        self.assertFalse(BUILDER.contains_jev_answer_shape(json.dumps(scrubbed)))
        self.assertNotRegex(
            json.dumps(scrubbed),
            r'"(?:noul|choice|probabilities|raw_score)"\s*:',
        )

    def test_redacts_escaped_answer_payload_in_truncated_sheet_text(self):
        escaped = json.dumps(
            json.dumps(
                {
                    "answers": {
                        "relevance": {
                            "noul": 0.9,
                            "confidence": 0.8,
                            "model": "jev-1.13.0",
                        }
                    }
                }
            )
        )[1:-1]
        truncated = escaped[: escaped.index("confidence")]

        scrubbed = BUILDER.redact_blind_sheet_value(
            {"state": {"result_head": truncated}}
        )

        self.assertEqual(scrubbed["state"]["result_head"], "[MODEL_ANSWER_REDACTED]")


class TaskMetadataTests(unittest.TestCase):
    def test_tool_result_metadata_keeps_source_and_exclusion_counts(self):
        summary = {
            "source_files": 7,
            "source_hashed_files": 6,
            "source_manifest_sha256": "a" * 64,
            "censor_as_of_utc": "2026-10-03T02:05:37Z",
            "dropped_over_32k": 2,
            "duplicate_state": 3,
            "conflicting_state": 4,
            "skipped_few_probe_words": 5,
        }

        metadata = BUILDER.build_task_metadata(
            "tool-result", summary, "units-sha", "candidate-sha"
        )

        self.assertEqual(metadata["source_files"], 7)
        self.assertEqual(metadata["source_hashed_files"], 6)
        self.assertEqual(metadata["source_manifest_sha256"], "a" * 64)
        self.assertEqual(metadata["censor_as_of_utc"], "2026-10-03T02:05:37Z")
        self.assertEqual(metadata["dropped_over_32k"], 2)
        self.assertEqual(metadata["duplicate_state"], 3)
        self.assertEqual(metadata["conflicting_state"], 4)
        self.assertEqual(metadata["skipped_few_probe_words"], 5)


if __name__ == "__main__":
    unittest.main()
