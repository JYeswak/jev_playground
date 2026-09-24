"""Dirty or untracked bar: zero provider calls. Reversed pair in /tmp fails."""

import asyncio
import importlib.util
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from phase_gate import AttemptPanic, call_after_bar

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "work/sr-adopt/audit_bars.py"
PAIRS = ROOT / "work/sr-adopt/prereg-pairs.tsv"


def git(repo, *args):
    subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True)


def load_runner():
    path = Path(os.environ.get("GROK_RUN_PATH", ROOT / "work/grok-incumbent-3/run.py"))
    spec = importlib.util.spec_from_file_location("grok_run", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # A deleted gate used to die here on a missing typesafe_sdk import inside
    # the fever loader, before the provider existed. The stub makes that plant
    # fail on "provider constructed" under plain python3 too.
    mod.LOADERS = {"fever": lambda: [(0, {"text": "x"}, {"q": {"type": "noul"}})]}
    return mod


class RequireBarTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="prereg-", dir="/tmp")
        git(self.tmp, "init", "-q")
        git(self.tmp, "config", "user.email", "test@example.com")
        git(self.tmp, "config", "user.name", "test")

    def test_untracked_bar_makes_zero_calls(self):
        bar = Path(self.tmp) / "bar.md"
        bar.write_text("bar\n")
        calls = {"n": 0}

        def asker():
            calls["n"] += 1

        with self.assertRaises(AttemptPanic):
            call_after_bar("bar.md", asker, repo=self.tmp)
        self.assertEqual(calls["n"], 0)

    def test_dirty_bar_makes_zero_calls(self):
        bar = Path(self.tmp) / "bar.md"
        bar.write_text("bar\n")
        git(self.tmp, "add", "bar.md")
        git(self.tmp, "commit", "-q", "-m", "[test] bar")
        bar.write_text("bar dirty\n")
        calls = {"n": 0}

        def asker():
            calls["n"] += 1

        with self.assertRaises(AttemptPanic):
            call_after_bar("bar.md", asker, repo=self.tmp)
        self.assertEqual(calls["n"], 0)

    def test_runner_main_dirty_bar_constructs_no_provider(self):
        bar = Path(self.tmp) / "bar.md"
        bar.write_text("bar\n")
        git(self.tmp, "add", "bar.md")
        git(self.tmp, "commit", "-q", "-m", "[test] bar")
        bar.write_text("dirty\n")
        constructed = {"n": 0}

        def boom(*_args, **_kwargs):
            constructed["n"] += 1
            raise AssertionError("provider constructed")

        fake = types.ModuleType("system_one_adapter")
        fake.AsyncSystemOneAdapterClient = boom
        openai = types.ModuleType("system_one_adapter.providers.openai")
        openai.AsyncOpenAIProvider = boom
        providers = types.ModuleType("system_one_adapter.providers")
        providers.openai = openai
        saved = {}
        for name, mod in (
            ("system_one_adapter", fake),
            ("system_one_adapter.providers", providers),
            ("system_one_adapter.providers.openai", openai),
        ):
            saved[name] = sys.modules.get(name)
            sys.modules[name] = mod
        previous = os.environ.get("XAI_API_KEY")
        os.environ["XAI_API_KEY"] = "test-key-not-used"
        try:
            runner = load_runner()
            with self.assertRaises(AttemptPanic):
                asyncio.run(
                    runner.main("fever", "run1", bar_path="bar.md", repo=self.tmp)
                )
        finally:
            if previous is None:
                os.environ.pop("XAI_API_KEY", None)
            else:
                os.environ["XAI_API_KEY"] = previous
            for name, mod in saved.items():
                if mod is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = mod
        self.assertEqual(constructed["n"], 0)

    def test_clean_committed_bar_calls_once(self):
        bar = Path(self.tmp) / "bar.md"
        bar.write_text("bar\n")
        git(self.tmp, "add", "bar.md")
        git(self.tmp, "commit", "-q", "-m", "[test] bar")
        calls = {"n": 0}

        def asker():
            calls["n"] += 1
            return "called"

        self.assertEqual(call_after_bar("bar.md", asker, repo=self.tmp), "called")
        self.assertEqual(calls["n"], 1)


class AuditTest(unittest.TestCase):
    def test_committed_pairs_agree(self):
        result = subprocess.run(
            ["python3", str(AUDIT), str(PAIRS), str(ROOT)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok 70", result.stdout)

    def test_reversed_pair_in_tmp_fails(self):
        tmp = tempfile.mkdtemp(prefix="prereg-rev-", dir="/tmp")
        git(tmp, "init", "-q")
        git(tmp, "config", "user.email", "test@example.com")
        git(tmp, "config", "user.name", "test")
        Path(tmp, "rows.jsonl").write_text("row\n")
        git(tmp, "add", "rows.jsonl")
        git(tmp, "commit", "-q", "-m", "[test] rows first")
        Path(tmp, "bar.md").write_text("bar\n")
        git(tmp, "add", "bar.md")
        git(tmp, "commit", "-q", "-m", "[test] bar second")
        bar_sha = subprocess.run(
            ["git", "-C", tmp, "log", "-1", "--format=%H", "--", "bar.md"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        tsv = Path(tmp) / "pairs.tsv"
        tsv.write_text(
            f"bead\tbar_path\tbar_sha\trows_path\nrev\tbar.md\t{bar_sha[:7]}\trows.jsonl\n"
        )
        result = subprocess.run(
            ["python3", str(AUDIT), str(tsv), tmp],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not precede", result.stdout)


if __name__ == "__main__":
    unittest.main()
