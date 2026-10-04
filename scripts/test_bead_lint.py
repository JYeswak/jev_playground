"""Tests for scripts/bead-lint.py: a bead is dispatchable only if a fresh agent can work it alone."""

import importlib.util
import pathlib
import unittest

SPEC = importlib.util.spec_from_file_location(
    "bead_lint", pathlib.Path(__file__).with_name("bead-lint.py")
)
assert SPEC is not None and SPEC.loader is not None
bead_lint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bead_lint)

COMPLETE = {
    "id": "jev-x.1",
    "title": "classifier measurement core",
    "issue_type": "feature",
    "status": "open",
    "description": (
        "WHAT: a zero-dependency module. WHY: the audit overturned three claims "
        "(work/plan-20261004/specs/advanced-mathops.md:41; arXiv:1706.04599). "
        "SOURCE: work/plan-20261004/PRODUCT.md"
    ),
    "acceptance_criteria": (
        "creates: scripts/test_x.py. "
        "Failing-first test: `python3 -m unittest scripts/test_x.py` reproduces ECE .028. "
        "Planted negative: a coin-flip backend fails eval. NO-CLAIM: no live quality claim."
    ),
}
HOLLOW = {
    "id": "jev-x.2",
    "title": "make it better",
    "issue_type": "task",
    "status": "open",
    "description": "improve things",
    "acceptance_criteria": "",
}


class BeadLint(unittest.TestCase):
    def codes(self, bead, ids=(), deps=()):
        return {f["code"] for f in bead_lint.lint_bead(bead, set(ids), deps)}

    def test_complete_bead_has_no_findings(self):
        self.assertEqual(self.codes(COMPLETE, {"jev-x.1"}), set())

    def test_hollow_bead_fails_every_self_containment_check(self):
        self.assertTrue(
            {
                "no-what",
                "no-why",
                "no-acceptance",
                "no-command",
                "no-negative",
                "no-source",
            }
            <= self.codes(HOLLOW)
        )

    def test_dependency_on_missing_bead_is_flagged(self):
        self.assertIn(
            "dangling-dep", self.codes(COMPLETE, {"jev-x.1"}, [("jev-x.1", "jev-gone")])
        )

    def test_epic_is_exempt_from_command_and_negative(self):
        epic = dict(
            HOLLOW,
            issue_type="epic",
            description="WHAT: product. WHY: Joshua asked (work/plan/PRODUCT.md)",
            acceptance_criteria="all children closed",
        )
        self.assertFalse({"no-command", "no-negative"} & self.codes(epic))

    def test_arxiv_id_alone_counts_as_a_source(self):
        bead = dict(
            COMPLETE, description="WHAT: x. WHY: conformal sets (arXiv:2107.07511)."
        )
        self.assertNotIn("no-source", self.codes(bead, {"jev-x.1"}))

    def test_imperative_plant_counts_as_a_negative(self):
        # jev-b35c.16 (2026-10-04) wrote "Plant out-of-scope route ..." and was flagged no-negative.
        bead = dict(
            COMPLETE,
            acceptance_criteria="`node --test x.mjs` passes. Plant a bad fixture; assert the safe side.",
        )
        self.assertNotIn("no-negative", self.codes(bead, {"jev-x.1"}))

    def test_acceptance_path_that_does_not_exist_and_is_not_created_is_flagged(self):
        # jev-z885 (2026-10-04) cited `work/jev-qpv2` tests that do not exist; lint passed it.
        bead = dict(
            COMPLETE,
            acceptance_criteria="`python3 work/nowhere/ope.py` passes. Planted negative: shuffled labels fail.",
        )
        self.assertIn("missing-path", self.codes(bead, {"jev-x.1"}))

    def test_declared_created_path_is_not_missing(self):
        bead = dict(
            COMPLETE,
            acceptance_criteria="creates: work/nowhere/ope.py. `python3 work/nowhere/ope.py` passes. Plant a bad row.",
        )
        self.assertNotIn("missing-path", self.codes(bead, {"jev-x.1"}))

    def test_existing_repo_path_is_not_missing(self):
        bead = dict(
            COMPLETE,
            acceptance_criteria="`python3 scripts/bead-lint.py --all-open` exits 0. Plant a hollow bead.",
        )
        self.assertNotIn("missing-path", self.codes(bead, {"jev-x.1"}))

    def test_angle_bracket_placeholder_is_flagged(self):
        # jev-mvvh (2026-10-04): `python3 <ledger script> --days 7` passed lint.
        bead = dict(
            COMPLETE,
            acceptance_criteria="Run: `python3 <ledger script> --days 7 --json`. Planted: a missing input exits non-zero.",
        )
        self.assertIn("placeholder", self.codes(bead, {"jev-x.1"}))

    def test_placeholder_outside_a_command_is_allowed(self):
        bead = dict(
            COMPLETE,
            acceptance_criteria="creates: scripts/test_x.py. `python3 -m unittest scripts/test_x.py` passes. "
            "Close with commit:<sha>. Plant a bad row.",
        )
        self.assertNotIn("placeholder", self.codes(bead, {"jev-x.1"}))

    def test_one_word_slot_in_a_command_is_a_parameter_not_a_placeholder(self):
        bead = dict(
            COMPLETE,
            acceptance_criteria="`br dep list <id> --json` shows every prerequisite closed. Plant an open leaf.",
        )
        self.assertNotIn("placeholder", self.codes(bead, {"jev-x.1"}))

    def test_comparison_operators_in_a_jq_filter_are_not_a_placeholder(self):
        # jev-6pjh (2026-10-04): `select(.ts >= $start and .ts < $end)` was misread as a slot.
        bead = dict(
            COMPLETE,
            acceptance_criteria="`jq -s '[.[] | select(.ts >= $start and .ts < $end)] | length' log.jsonl` is 0. Plant a stale row.",
        )
        self.assertNotIn("placeholder", self.codes(bead, {"jev-x.1"}))

    def test_overlong_path_is_missing_not_a_crash(self):
        # A 50k-char path raised OSError(63) from exists() (2026-10-04 adversarial run).
        bead = dict(
            COMPLETE,
            acceptance_criteria="`python3 "
            + "x/" * 25000
            + "t.py` passes. Plant a bad row.",
        )
        self.assertIn("missing-path", self.codes(bead, {"jev-x.1"}))


if __name__ == "__main__":
    unittest.main()
