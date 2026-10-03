"""Regression tests for the phase-0 decision-bank builder."""

import importlib.util
import json
import time
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


class RegexSafetyTests(unittest.TestCase):
    def test_token_regex_forms_and_identifier_boundaries(self):
        self.assertEqual(
            BUILDER.PATH_TOKEN_RE.findall("/workspace/archive.tar.gz"),
            ["/workspace/archive.tar.gz"],
        )
        self.assertIsNone(BUILDER.PATH_TOKEN_RE.search("x/workspace/file.txt/"))
        self.assertEqual(
            BUILDER.BACKTICK_TOKEN_RE.findall("`cache_index_42`"),
            ["cache_index_42"],
        )
        self.assertEqual(BUILDER.BACKTICK_TOKEN_RE.findall("`two words`"), [])
        self.assertEqual(
            BUILDER.QUALIFIED_IDENTIFIER_RE.findall("pkg::CacheIndex42"),
            ["pkg::CacheIndex42"],
        )
        self.assertNotIn(
            "Pkg::CacheIndex42",
            BUILDER.QUALIFIED_IDENTIFIER_RE.findall("xPkg::CacheIndex42Suffix"),
        )
        self.assertEqual(
            BUILDER.IDENTIFIER_RE.findall("cache_index_42"), ["cache_index_42"]
        )
        self.assertNotIn(
            "cache_index_42",
            BUILDER.IDENTIFIER_RE.findall("notcache_index_42x"),
        )

    def test_path_token_strips_sentence_final_period(self):
        self.assertIn("/x/abc", BUILDER.reference_tokens("Result path: /x/abc."))

    def test_short_path_reuse_ignores_sentence_final_period(self):
        source = "Result path: /x/abc."
        later = {
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "toolCall", "arguments": {"path": "/x/abc"}},
                ],
            }
        }

        self.assertTrue(
            BUILDER.has_later_exact_reference(source, 10, iter([(11, later)]))
        )

    def test_different_multi_extension_path_is_not_a_reuse(self):
        source = "The output is /x/archive.tar.gz"
        later = {
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "toolCall",
                        "arguments": {"path": "/x/archive.tar.backup"},
                    }
                ],
            }
        }

        self.assertFalse(
            BUILDER.has_later_exact_reference(source, 10, iter([(11, later)]))
        )

    def test_regex_near_misses_are_bounded_at_doubled_lengths(self):
        for pattern, prefix, suffix in (
            (BUILDER.PATH_TOKEN_RE, "", "/"),
            (BUILDER.BACKTICK_TOKEN_RE, "`", ""),
            (BUILDER.QUALIFIED_IDENTIFIER_RE, "", "::"),
        ):
            for size in (2048, 4096, 8192):
                near_miss = prefix + "a" * size + suffix
                started = time.perf_counter()
                match = pattern.search(near_miss)
                elapsed = time.perf_counter() - started

                self.assertIsNone(match)
                self.assertLess(
                    elapsed,
                    1.0,
                    f"{pattern.pattern!r} n={len(near_miss)} elapsed={elapsed:.3f}s",
                )


class MechanicalOutcomeTests(unittest.TestCase):
    def referenced(self, source, events):
        return BUILDER.has_later_exact_reference(source, 10, iter(events))

    def test_20_character_later_verbatim_span_is_relevant(self):
        source = "prefix silver lanterns glow suffix"
        earlier = {
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "silver lanterns glow"}],
            }
        }
        later = {
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "silver lanterns glow"}],
            }
        }

        self.assertTrue(self.referenced(source, [(9, earlier), (11, later)]))

    def test_19_character_span_is_not_relevant(self):
        source = "silver lanterns glo"
        later = {
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "silver lanterns glo"}],
            }
        }

        self.assertFalse(self.referenced(source, [(11, later)]))

    def test_later_tool_argument_with_exact_path_is_relevant(self):
        source = "The generated artifact is /workspace/src/engine/route_index.py."
        later = {
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "toolCall",
                        "arguments": {"path": "/workspace/src/engine/route_index.py"},
                    }
                ],
            }
        }

        self.assertTrue(self.referenced(source, [(11, later)]))

    def test_later_tool_argument_with_exact_identifier_is_relevant(self):
        source = "The report names cache_index_42 as the retry sentinel."
        later = {
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "toolCall",
                        "arguments": {"symbol": "cache_index_42"},
                    }
                ],
            }
        }

        self.assertTrue(self.referenced(source, [(11, later)]))

    def test_unrelated_assistant_text_is_not_relevant(self):
        source = "prefix silver lanterns glow suffix"
        later = {
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "The unrelated status check completed."},
                    {"type": "thinking", "text": "silver lanterns glow"},
                ],
            }
        }

        self.assertFalse(self.referenced(source, [(11, later)]))


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
