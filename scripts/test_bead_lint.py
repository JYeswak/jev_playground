"""Tests for scripts/bead-lint.py: a bead is dispatchable only if a fresh agent can work it alone."""

import importlib.util
import json
import pathlib
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

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

    def test_bare_interpreter_command_is_a_placeholder(self):
        # WildCarp converge r1 L3: "`python3` over the committed rows" named no script.
        bead = dict(
            COMPLETE,
            acceptance_criteria="`python3` over the committed rows recomputes 0.906. Plant a bad row.",
        )
        self.assertIn("placeholder", self.codes(bead, {"jev-x.1"}))


    def test_unreachable_pillar_live_is_reported_but_none_and_in_review_are_ignored(self):
        # Observed IDs/labels: jev-q3q8 and jev-b35c.16 (live); jev-sk29 (none);
        # jev-9cqw (live). The root edge to jev-b35c.16 is removed to plant the failure.
        beads = [
            {"id": "jev-q3q8", "status": "open", "issue_type": "epic", "labels": []},
            {"id": "jev-b35c.16", "status": "open", "issue_type": "feature", "labels": ["pillar:live"]},
            {"id": "jev-sk29", "status": "open", "issue_type": "task", "labels": ["pillar:none"]},
            {"id": "jev-9cqw", "status": "in_review", "issue_type": "task", "labels": ["pillar:live"]},
        ]
        findings = bead_lint.lint_graph(beads, [], [])
        codes = {(finding["id"], finding["code"]) for finding in findings}
        self.assertIn(("jev-b35c.16", "unreachable-from-root"), codes)
        self.assertNotIn(("jev-sk29", "unreachable-from-root"), codes)
        self.assertNotIn(("jev-9cqw", "unreachable-from-root"), codes)

    def test_pillar_live_reachable_from_mission_root_is_not_reported(self):
        beads = [
            {"id": "jev-q3q8", "status": "open", "issue_type": "epic", "labels": []},
            {"id": "jev-b35c.16", "status": "open", "issue_type": "feature", "labels": ["pillar:live"]},
        ]
        self.assertEqual(
            bead_lint.lint_graph(beads, [("jev-q3q8", "jev-b35c.16")], []),
            [],
        )

    def test_in_progress_with_open_prerequisite_is_reported(self):
        beads = [
            {"id": "jev-q3q8", "status": "in_progress", "issue_type": "epic", "labels": []},
            {"id": "jev-b35c.16", "status": "open", "issue_type": "feature", "labels": []},
        ]
        findings = bead_lint.lint_graph(
            beads, [("jev-q3q8", "jev-b35c.16")], []
        )
        self.assertIn(
            ("jev-q3q8", "blocked-in-progress"),
            {(finding["id"], finding["code"]) for finding in findings},
        )

    def test_closed_prerequisite_does_not_block_in_progress_bead(self):
        beads = [
            {"id": "jev-q3q8", "status": "in_progress", "issue_type": "epic", "labels": []},
            {"id": "jev-b35c.16", "status": "closed", "issue_type": "feature", "labels": []},
        ]
        findings = bead_lint.lint_graph(
            beads, [("jev-q3q8", "jev-b35c.16")], []
        )
        self.assertNotIn(
            ("jev-q3q8", "blocked-in-progress"),
            {(finding["id"], finding["code"]) for finding in findings},
        )

    def test_epic_blocked_by_its_own_child_is_reported(self):
        beads = [
            {"id": "jev-q3q8", "status": "open", "issue_type": "epic", "labels": []},
            {"id": "jev-b35c", "status": "open", "issue_type": "epic", "labels": []},
            {"id": "jev-b35c.16", "status": "open", "issue_type": "feature", "labels": ["pillar:live"]},
        ]
        findings = bead_lint.lint_graph(
            beads,
            [("jev-q3q8", "jev-b35c"), ("jev-b35c", "jev-b35c.16")],
            [("jev-b35c.16", "jev-b35c")],
        )
        self.assertIn(
            ("jev-b35c", "epic-blocks-own-child"),
            {(finding["id"], finding["code"]) for finding in findings},
        )

    def test_epic_parent_child_edge_alone_is_not_a_blocker(self):
        beads = [
            {"id": "jev-q3q8", "status": "open", "issue_type": "epic", "labels": []},
            {"id": "jev-b35c", "status": "open", "issue_type": "epic", "labels": []},
            {"id": "jev-b35c.16", "status": "open", "issue_type": "feature", "labels": ["pillar:live"]},
        ]
        findings = bead_lint.lint_graph(
            beads, [("jev-q3q8", "jev-b35c")], [("jev-b35c.16", "jev-b35c")]
        )
        self.assertNotIn(
            ("jev-b35c", "epic-blocks-own-child"),
            {(finding["id"], finding["code"]) for finding in findings},
        )

    def test_gitignored_source_is_reported(self):
        bead = dict(
            COMPLETE,
            description="WHAT: x. WHY: y. SOURCE: var/agent-tmp/x.md",
        )
        findings = bead_lint.lint_ignored_sources([bead])
        self.assertEqual(
            [(finding["id"], finding["code"]) for finding in findings],
            [("jev-x.1", "gitignored-source")],
        )

    def test_linter_description_does_not_treat_source_prose_as_citation(self):
        bead = dict(
            COMPLETE,
            description=(
                "WHAT: add lint rules. WHY: preserve graph invariants. "
                "gitignored-source: a SOURCE or input citation of a path that "
                "git check-ignore reports ignored (var/agent-tmp/...) is a finding."
            ),
        )
        self.assertEqual(bead_lint.lint_ignored_sources([bead]), [])

    def test_gitignored_input_is_reported_unless_declared_created(self):
        source = dict(
            COMPLETE,
            description="WHAT: x. WHY: y. INPUT: var/agent-tmp/x.md",
        )
        created = dict(
            source,
            acceptance_criteria="creates: var/agent-tmp/x.md. Plant a bad row.",
        )
        self.assertIn(
            ("jev-x.1", "gitignored-source"),
            {
                (finding["id"], finding["code"])
                for finding in bead_lint.lint_ignored_sources([source])
            },
        )
        self.assertEqual(bead_lint.lint_ignored_sources([created]), [])

    def test_all_open_json_lists_graph_and_source_findings(self):
        root = dict(COMPLETE, id="jev-q3q8", issue_type="epic", labels=[])
        epic = dict(
            COMPLETE,
            id="jev-b35c",
            status="in_progress",
            issue_type="epic",
            labels=[],
        )
        child = dict(
            COMPLETE,
            id="jev-b35c.16",
            description="WHAT: x. WHY: y. SOURCE: var/agent-tmp/x.md",
            labels=["pillar:live"],
        )
        issues = [root, epic, child]
        ids = {bead["id"] for bead in issues}
        blocks = [("jev-b35c", "jev-b35c.16")]
        parent_child = [("jev-b35c.16", "jev-b35c")]
        output = StringIO()
        with patch.object(
            bead_lint, "load", return_value=(issues, ids, blocks, parent_child, issues)
        ), redirect_stdout(output):
            exit_code = bead_lint.main(["--all-open", "--json"])
        try:
            payload = json.loads(output.getvalue())
        except json.JSONDecodeError as exc:
            self.fail(f"bead-lint JSON output is invalid: {exc}")
        codes = {finding["code"] for finding in payload["findings"]}
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["checked"], 3)
        self.assertTrue(
            {
                "unreachable-from-root",
                "blocked-in-progress",
                "epic-blocks-own-child",
                "gitignored-source",
            }.issubset(codes)
        )


if __name__ == "__main__":
    unittest.main()
