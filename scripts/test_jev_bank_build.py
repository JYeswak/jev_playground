"""Regression tests for the phase-0 decision-bank builder."""

import collections
import hashlib
import importlib.util
import json
import tempfile
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


class TemporaryTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.tmp_path = Path(self.tempdir.name)


class ReferenceTestCase(unittest.TestCase):
    def assistant_event(self, *content):
        return {"message": {"role": "assistant", "content": list(content)}}

    def text_block(self, text):
        return {"type": "text", "text": text}

    def tool_call_block(self, arguments):
        return {"type": "toolCall", "arguments": arguments}

    def referenced(self, source, events):
        return BUILDER.has_later_exact_reference(source, 10, iter(events))


class VerbatimReferenceTests(ReferenceTestCase):
    def test_minimum_span_length(self):
        source = "files already formatted"
        cases = (("files already forma", False), ("files already format", True))

        for span, expected in cases:
            with self.subTest(span=span):
                later = self.assistant_event(self.text_block(span))
                self.assertIs(self.referenced(source, [(11, later)]), expected)


class TokenReferenceTests(ReferenceTestCase):
    def test_later_tool_arguments_reuse_exact_path_and_identifier(self):
        cases = (
            (
                "The generated artifact is scripts/jev-bank-build.py.",
                {"path": "scripts/jev-bank-build.py"},
            ),
            (
                "The report names build_task_metadata as the serialization helper.",
                {"symbol": "build_task_metadata"},
            ),
        )

        for source, arguments in cases:
            with self.subTest(arguments=arguments):
                later = self.assistant_event(self.tool_call_block(arguments))
                self.assertTrue(self.referenced(source, [(11, later)]))


class ScopeReferenceTests(ReferenceTestCase):
    def test_thinking_content_is_not_relevant(self):
        source = "files already formatted"
        later = self.assistant_event(
            self.text_block("The unrelated status check completed."),
            {"type": "thinking", "text": "files already formatted"},
        )

        self.assertFalse(self.referenced(source, [(11, later)]))


class FullBankClassifierTests(TemporaryTestCase):
    def test_full_bank_classifier_ignores_user_and_tool_result_reuse(self):
        source = "session-specific-outcome-marker-" + "z" * 40
        events = [
            {"message": {"role": "toolResult", "content": source}},
            {"message": {"role": "toolResult", "content": source}},
            {"message": {"role": "user", "content": source}},
        ]
        path = self.tmp_path / "session.jsonl"
        path.write_text("".join(json.dumps(row) + "\n" for row in events))
        row = {
            "_line": 0,
            "_source_text": source,
            "censored": False,
            "unit_id": "unit",
        }

        BUILDER.classify_later_references(path, [row], collections.Counter())

        self.assertEqual(row["label"], "not-relevant")
        self.assertNotIn("_source_text", row)
        self.assertNotIn("_line", row)

    def test_full_bank_classifier_accepts_assistant_text_reference(self):
        source = "session-specific-outcome-marker-" + "y" * 40
        events = [
            {"message": {"role": "toolResult", "content": source}},
            {"message": {"role": "assistant", "content": source}},
        ]
        path = self.tmp_path / "session.jsonl"
        path.write_text("".join(json.dumps(row) + "\n" for row in events))
        row = {
            "_line": 0,
            "_source_text": source,
            "censored": False,
            "unit_id": "unit",
        }

        BUILDER.classify_later_references(path, [row], collections.Counter())

        self.assertEqual(row["label"], "relevant")
        self.assertNotIn("_source_text", row)
        self.assertNotIn("_line", row)


class DMechanicalAuditTests(unittest.TestCase):
    def test_d_mechanical_audit_matches_frozen_labels_and_rejects_drift(self):
        root = BUILDER.ROOT / "work" / "jev-bank"
        manifest = json.loads((root / "blind-sample-manifest.json").read_text())
        ids = manifest["tasks"]["D"]["ids"]
        labels = json.loads(
            (root / "vvkr-D-mechanical-labels-wildcarp.json").read_text()
        )
        rows = [{"unit_id": item, "label": labels[item]} for item in ids]

        audit = BUILDER.d_mechanical_label_audit(rows, root)

        self.assertEqual(audit["n"], 50)
        self.assertEqual(audit["matched"], 50)
        self.assertEqual(audit["counts"], {"not-relevant": 4, "relevant": 46})
        self.assertEqual(audit["status"], "MATCHED_TO_BUILDER")
        rows[0]["label"] = (
            "not-relevant" if rows[0]["label"] == "relevant" else "relevant"
        )
        with self.assertRaisesRegex(ValueError, "disagree with builder outcomes"):
            BUILDER.d_mechanical_label_audit(rows, root)


class TeacherBlindLabelTests(unittest.TestCase):
    def test_g_blind_double_label_matches_frozen_sample(self):
        root = BUILDER.ROOT / "work" / "jev-bank"
        manifest = json.loads((root / "blind-sample-manifest.json").read_text())
        ids = manifest["tasks"]["G"]["ids"]
        rows = [{"unit_id": item} for item in ids]

        summary = BUILDER.g_blind_double_label(rows, root)

        self.assertEqual(summary["n"], 50)
        self.assertEqual(summary["agree"], 35)
        self.assertAlmostEqual(summary["agreement"], 0.7)
        self.assertAlmostEqual(summary["cohen_kappa"], 0.3218806509945748)
        self.assertEqual(summary["status"], "COMPLETE")
        self.assertEqual(summary["labelers"], ["WildCarp", "HazySpring"])
        self.assertEqual(len(summary["sample_manifest_sha256"]), 64)
        self.assertEqual(len(summary["label_files_sha256"]), 2)

    def test_g_blind_double_label_rejects_missing_candidate_id(self):
        root = BUILDER.ROOT / "work" / "jev-bank"
        manifest = json.loads((root / "blind-sample-manifest.json").read_text())
        rows = [{"unit_id": item} for item in manifest["tasks"]["G"]["ids"][:-1]]

        with self.assertRaisesRegex(ValueError, "not in candidate rows"):
            BUILDER.g_blind_double_label(rows, root)


class SourceManifestTests(unittest.TestCase):
    def test_source_manifest_digest_is_order_independent(self):
        sources = [("b", "2"), ("a", "1")]

        digest = BUILDER.source_manifest_digest(sources)

        expected = hashlib.sha256(b"a\x001\nb\x002\n").hexdigest()
        self.assertEqual(digest, expected)
        self.assertEqual(
            BUILDER.source_manifest_digest(list(reversed(sources))), expected
        )

    def test_read_rows_hashes_exact_source_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.jsonl"
            raw = b'{"row":1}\n{"row":2}\n'
            path.write_bytes(raw)
            digest = hashlib.sha256()

            rows = BUILDER.read_rows(path, digest)

        self.assertEqual(rows, [{"row": 1}, {"row": 2}])
        self.assertEqual(digest.hexdigest(), hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    unittest.main()
