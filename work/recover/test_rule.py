"""Tests for work/recover/rule.py (jev-n4-recover-error-rule-1grh).

Hermetic: synthetic rows only, no fleet reads, no model calls, no network.
Follows the bead's planted negatives: timeout-identical-retry is not flagged,
not-found-identical-retry is flagged, and imputed outcomes refuse as
NOT_IDENTIFIABLE.
"""

import unittest

from work.recover.rule import (
    Refused,
    classify_bash_error,
    classify_edit_error,
    estimate_effect,
    flag_violation,
    load_task,
    next_action_kind,
    prescribed_action,
    score_rows,
    split_sessions,
    summarize,
    wilson_interval,
)


def bash_call(command):
    return {"name": "bash", "arguments": {"command": command}}


def err_result(text):
    return {"is_error": True, "text": text}


def ok_result():
    return {"is_error": False, "text": "[]"}


def episode_rows(fail_command, fail_text, next_command):
    # Real fixture schema: tool calls arrive as content parts, results at
    # message level (role toolResult with toolCallId/isError/content).
    return [
        {"type": "message", "message": {"role": "assistant", "content": [
            {"type": "toolCall", "id": "c1", "name": "bash", "arguments": {"command": fail_command}}]}},
        {"type": "message", "message": {"role": "toolResult", "toolCallId": "c1", "toolName": "bash",
                                        "isError": True, "content": [{"type": "text", "text": fail_text}]}},
        {"type": "message", "message": {"role": "assistant", "content": [
            {"type": "toolCall", "id": "c2", "name": "bash", "arguments": {"command": next_command}}]}},
        {"type": "message", "message": {"role": "toolResult", "toolCallId": "c2", "toolName": "bash",
                                        "isError": False, "content": []}},
    ]


class ClassifyBashTest(unittest.TestCase):
    def test_timeout_class(self):
        for text in ("curl: (28) timed out after 30000ms", "deadline exceeded", "lock timeout"):
            with self.subTest(text=text):
                self.assertIn(classify_bash_error(text), ("timeout", "lock"))

    def test_timeout_word_alone(self):
        self.assertEqual(classify_bash_error("operation timeout"), "timeout")

    def test_network_class(self):
        self.assertEqual(classify_bash_error("curl: (7) Failed to connect: No route to host network unreachable"), "network")

    def test_lock_class(self):
        self.assertEqual(classify_bash_error("resource busy, try again"), "lock")

    def test_syntax_class(self):
        self.assertEqual(classify_bash_error("syntax error near unexpected token"), "syntax")

    def test_not_found_class(self):
        for text in ("bash: syk: command not found", "ENOENT: no such file"):
            with self.subTest(text=text):
                self.assertEqual(classify_bash_error(text), "not-found")

    def test_permission_class(self):
        self.assertEqual(classify_bash_error("permission denied"), "permission")

    def test_generic_exit_unclassified(self):
        self.assertIsNone(classify_bash_error("exit code 1"))


class ClassifyEditTest(unittest.TestCase):
    def test_stale_tag(self):
        self.assertEqual(classify_edit_error({"tag": "stale_tag", "path": "a.ts"}), "stale-tag")

    def test_ordinary_edit_unclassified(self):
        self.assertIsNone(classify_edit_error({"path": "a.ts", "edits": []}))


class PrescriptionTest(unittest.TestCase):
    def test_retry_classes(self):
        for klass in ("timeout", "network", "lock"):
            self.assertEqual(prescribed_action("bash", klass), "retry")

    def test_change_classes(self):
        for klass in ("syntax", "not-found", "permission"):
            self.assertEqual(prescribed_action("bash", klass), "change")

    def test_edit_stale_tag(self):
        self.assertEqual(prescribed_action("edit", "stale-tag"), "re-read")

    def test_silent_when_rule_has_no_class(self):
        self.assertIsNone(prescribed_action("bash", None))
        self.assertIsNone(prescribed_action("task", None))


class ViolationFlagTest(unittest.TestCase):
    def test_identical_retry_after_timeout_is_not_flagged(self):
        self.assertFalse(flag_violation("bash", "timeout", "retry"))

    def test_identical_retry_after_not_found_is_flagged(self):
        self.assertTrue(flag_violation("bash", "not-found", "retry"))

    def test_matching_change_is_not_flagged(self):
        self.assertFalse(flag_violation("bash", "syntax", "change"))

    def test_unknown_class_never_flagged(self):
        self.assertFalse(flag_violation("bash", None, "retry"))
        self.assertFalse(flag_violation("bash", "timeout", None))


class ImputationRefusalTest(unittest.TestCase):
    def test_estimate_effect_refuses_not_identifiable(self):
        with self.assertRaises(Refused) as ctx:
            estimate_effect([{"agree": True, "next_ok": True}])
        self.assertIn("NOT_IDENTIFIABLE", str(ctx.exception))


class CohortJoinTest(unittest.TestCase):
    def test_timeout_retry_then_success_joins_agree(self):
        rows = episode_rows("curl slow", "timed out", "curl slow")
        scored = score_rows(rows)
        self.assertEqual(len(scored["episodes"]), 1)
        ep = scored["episodes"][0]
        self.assertEqual((ep["tool"], ep["class"], ep["action"]), ("bash", "timeout", "retry"))
        self.assertTrue(ep["agree"])
        self.assertTrue(ep["next_ok"])

    def test_not_found_retry_joins_disagree(self):
        rows = episode_rows("syk", "syk: command not found", "syk")
        ep = score_rows(rows)["episodes"][0]
        self.assertEqual((ep["tool"], ep["class"], ep["action"]), ("bash", "not-found", "retry"))
        self.assertFalse(ep["agree"])

    def test_different_next_call_is_change(self):
        self.assertEqual(next_action_kind(bash_call("a"), bash_call("b")), "change")
        self.assertIsNone(next_action_kind(bash_call("a"), None))


class SummarizeTest(unittest.TestCase):
    def test_small_n_reports_not_powered(self):
        out = summarize([{"class": "timeout", "agree": True, "next_ok": True}])
        self.assertEqual(out["timeout"]["status"], "NOT_POWERED")

    def test_wilson_bounds(self):
        lo, hi = wilson_interval(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)
        lo, hi = wilson_interval(10, 10)
        self.assertEqual(hi, 1.0)


class TaskContractTest(unittest.TestCase):
    def test_missing_task_file_refuses(self):
        with self.assertRaises(SystemExit):
            load_task("work/recover/does-not-exist-task.json")

    def test_task_resolves_fixture_from_envelope(self):
        _, rows, identity = load_task("work/fleet-schema/task.json")
        self.assertEqual(identity["as_of"], "2026-10-04T00:48:27Z")
        self.assertEqual(identity["window_days"], 14)
        self.assertTrue(len(rows) > 0)
        self.assertRegex(identity["fixture_sha256"], r"^[0-9a-f]{64}$")


class SplitTest(unittest.TestCase):
    def test_dev_held_split_is_deterministic(self):
        rows = [
            {"type": "session", "id": "b", "timestamp": "2026-10-04T00:41:00Z"},
            {"type": "session", "id": "a", "timestamp": "2026-10-04T00:40:00Z"},
            {"type": "session", "id": "c", "timestamp": "2026-10-04T00:42:00Z"},
        ]
        dev, held = split_sessions(rows)
        self.assertEqual(dev, {"a", "b"})
        self.assertEqual(held, {"c"})

if __name__ == "__main__":
    unittest.main()
