"""Golden + conformance tests for the Jev surface inventory.

Golden: the structural diagram (expected.json only, no live counts) is frozen in
goldens/inventory-structure.mmd. Any change to a claimed surface, verdict or wiring changes the
diagram and FAILS until a human reviews `git diff work/jev-inventory/goldens/` and re-blesses with
UPDATE_GOLDENS=1. Conformance: a claim that disagrees with live state is reported, never hidden.

Run: python3 -m unittest work/jev-inventory/test_inventory.py
"""

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("inventory", HERE / "inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
GOLDEN = HERE / "goldens" / "inventory-structure.mmd"


class StructuralGolden(unittest.TestCase):
    def test_structure_matches_reviewed_golden(self):
        actual = inv.mermaid(inv.load_expected(), None)
        if os.environ.get("UPDATE_GOLDENS"):
            GOLDEN.parent.mkdir(exist_ok=True)
            GOLDEN.write_text(actual)
            self.skipTest(
                f"golden updated: {GOLDEN}; review with git diff before committing"
            )
        self.assertTrue(
            GOLDEN.exists(), "golden missing: run UPDATE_GOLDENS=1, review, commit"
        )
        expected = GOLDEN.read_text()
        if actual != expected:
            (GOLDEN.with_suffix(".actual")).write_text(actual)
        self.assertEqual(
            actual,
            expected,
            f"structure drifted; diff {GOLDEN} {GOLDEN.with_suffix('.actual')}",
        )

    def test_structure_is_valid_mermaid(self):
        binary = shutil.which("frankenmermaid")
        if binary is None:
            self.skipTest("NOT_RUN: frankenmermaid not installed")
        with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as fh:
            fh.write(inv.mermaid(inv.load_expected(), None))
        result = subprocess.run(
            [binary, "validate", fh.name, "--fail-on", "error"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_every_surface_has_a_node_and_a_verdict_class(self):
        expected = inv.load_expected()
        diagram = inv.mermaid(expected, None)
        for s in expected["surfaces"]:
            self.assertIn(f'{inv.node_id(s["id"])}["', diagram)
            self.assertIn(
                s["verdict"],
                inv.VERDICT_CLASS,
                f"{s['id']} verdict has no colour class",
            )


class Conformance(unittest.TestCase):
    def test_claimed_hook_without_file_is_reported_off(self):
        surface = {
            "id": "planted",
            "group": "hook",
            "file": ".omp/hooks/post/does-not-exist.ts",
            "expect": "on",
        }
        self.assertEqual(inv.live_state(surface, {}), "off")

    def test_claimed_off_extension_still_listed_is_reported_on(self):
        surface = {
            "id": "planted",
            "group": "extension",
            "extension": "./x.ts",
            "expect": "off",
        }
        self.assertEqual(inv.live_state(surface, {"extensions": ["./x.ts"]}), "on")

    def test_native_surface_off_when_one_profile_lacks_the_judge(self):
        surface = {"id": "find", "group": "native"}
        ctx = {
            "profiles": {
                "a": {"modelRoles": {"judge": "typesafe/jev-latest"}},
                "b": {"modelRoles": {}},
            }
        }
        self.assertEqual(inv.live_state(surface, ctx), "off")


class GlobalHookDrift(unittest.TestCase):
    PROFILES = ["default", "claude", "codex", "muse", "grok"]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.prev_home = inv.HOME
        inv.HOME = self.home
        self.surface = {
            "id": "webscreen-global",
            "group": "global",
            "repo": "work/jev-j0er/jev-webscreen-global.ts",
            "hookfile": "jev-webscreen-global.ts",
            "expect": "on",
        }
        self.ctx = {"profile_names": list(self.PROFILES)}

    def tearDown(self):
        inv.HOME = self.prev_home
        self.tmp.cleanup()

    def link_all(self):
        src = Path(inv.ROOT) / self.surface["repo"]
        for p in self.PROFILES:
            base = self.home / (
                ".omp/agent" if p == "default" else f".omp/profiles/{p}/agent"
            )
            target = base / "hooks" / "post" / self.surface["hookfile"]
            target.parent.mkdir(parents=True, exist_ok=True)
            os.link(src, target)

    def test_matching_hardlinks_are_on(self):
        self.link_all()
        self.assertEqual(inv.live_state(self.surface, self.ctx), "on")

    def test_rewritten_same_bytes_new_inode_is_off(self):
        # git/editor replace-by-rename keeps bytes but breaks the link
        self.link_all()
        victim = (
            self.home
            / ".omp/profiles/codex/agent/hooks/post"
            / self.surface["hookfile"]
        )
        data = victim.read_bytes()
        victim.unlink()
        victim.write_bytes(data)
        self.assertEqual(inv.live_state(self.surface, self.ctx), "off")

    def test_changed_content_is_off(self):
        self.link_all()
        victim = self.home / ".omp/agent/hooks/post" / self.surface["hookfile"]
        victim.unlink()
        victim.write_text("// drifted\n")
        self.assertEqual(inv.live_state(self.surface, self.ctx), "off")

    def test_missing_copy_is_off(self):
        self.link_all()
        (
            self.home / ".omp/profiles/grok/agent/hooks/post" / self.surface["hookfile"]
        ).unlink()
        self.assertEqual(inv.live_state(self.surface, self.ctx), "off")


if __name__ == "__main__":
    unittest.main()
