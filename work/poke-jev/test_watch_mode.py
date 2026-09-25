"""Keyless regression tests for the public challenge owner filter."""

import sys
import unittest


def require_prerequisites() -> None:
    if sys.version_info < (3, 12):
        print("SKIP (missing prerequisite: Python >= 3.12)")
        raise SystemExit(8)


require_prerequisites()

from watch_mode import accepts_challenge  # noqa: E402


class OwnerFilter(unittest.TestCase):
    def test_exact_username_is_accepted(self):
        self.assertTrue(accepts_challenge("JoshuaBot", "JoshuaBot"))

    def test_spaces_are_normalized(self):
        self.assertTrue(accepts_challenge("Joshua Bot", "joshua_bot"))

    def test_hyphens_are_normalized(self):
        self.assertTrue(accepts_challenge("Joshua-Bot", "joshuabot"))

    def test_empty_owner_rejects_every_challenge(self):
        self.assertFalse(accepts_challenge("JoshuaBot", ""))

    def test_spaces_only_owner_rejects_every_challenge(self):
        self.assertFalse(accepts_challenge("", "   "))

    def test_near_miss_username_is_rejected(self):
        self.assertFalse(accepts_challenge("JoshuaBot2", "JoshuaBot"))


if __name__ == "__main__":
    unittest.main()
