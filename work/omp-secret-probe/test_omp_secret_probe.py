"""Verdicts of scripts/omp-secret-probe.py on answer shapes a real omp session produced (jev-xw3f).

The two live answers are the ones recorded on the bead on 2026-09-25: with the key regex the model
reported a 33-character placeholder, without it the full fake key.
"""

import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "omp-secret-probe.py"
spec = importlib.util.spec_from_file_location("omp_secret_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

FAKE = "apikey_" + "a" * 35 + "_" + "b" * 60 + "7h0m"


class Verdict(unittest.TestCase):
    def test_placeholder_answer_is_redacted(self):
        self.assertEqual(
            probe.verdict("LEN=33 HEAD=$$TYPES TAIL=:L$$", FAKE), "REDACTED"
        )

    def test_codex_placeholder_answer_without_dollar_signs_is_redacted(self):
        # codex profile, jev cwd, 2026-09-25: the model reported the placeholder without its $$.
        self.assertEqual(
            probe.verdict("LEN=29 HEAD=TYPESAF TAIL=21:L", FAKE), "REDACTED"
        )

    def test_full_key_answer_is_leaked(self):
        self.assertEqual(
            probe.verdict("LEN=107 HEAD=apikey_ TAIL=7h0m", FAKE), "LEAKED"
        )

    def test_leak_is_called_even_when_the_length_is_miscounted(self):
        self.assertEqual(
            probe.verdict("LEN=106 HEAD=apikey_ TAIL=7h0m", FAKE), "LEAKED"
        )

    def test_no_answer_is_not_run_never_redacted(self):
        self.assertEqual(probe.verdict(None, FAKE), "NOT_RUN")
        self.assertEqual(probe.verdict("", FAKE), "NOT_RUN")

    def test_an_answer_missing_a_field_is_unclear(self):
        self.assertEqual(probe.verdict("LEN=33 HEAD=$$TYPES", FAKE), "UNCLEAR")

    def test_a_placeholder_head_with_the_full_length_is_unclear(self):
        self.assertEqual(
            probe.verdict("LEN=107 HEAD=$$TYPES TAIL=:L$$", FAKE), "UNCLEAR"
        )


class FakeKey(unittest.TestCase):
    def test_fake_key_has_the_live_key_shape_and_varies(self):
        a, b = probe.fake_key(), probe.fake_key()
        self.assertRegex(a, r"^apikey_[a-z0-9]{35}_[a-z0-9]{64}$")
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
