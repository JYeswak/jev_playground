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


if __name__ == "__main__":
    unittest.main()
