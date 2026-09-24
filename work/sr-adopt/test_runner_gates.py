"""Each live runner panics on a dirty bar before a provider exists.

Deleting the production call_after_bar line makes that runner's test fail.
The deleted source is executed from /tmp with the original path, so the
production file is not edited.

The banking77 Haiku arms (run_haiku, run_prompted) are not here: since jev-sybt
they refuse before the bar is read, which work/anthropic-stop/test_anthropic_stop.py
tests.
"""

import asyncio
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from phase_gate import AttemptPanic

ROOT = Path(__file__).resolve().parents[2]
KEYS = ("TYPESAFE_API_KEY", "XAI_API_KEY", "ANTHROPIC_API_KEY")
GATES = (
    "    call_after_bar(bar, lambda: None, repo=repo or ROOT)\n",
    "    call_after_bar(bar, lambda: None, repo=repo or root)\n",
)


def git(repo, *args):
    subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stub_providers(constructed):
    def boom(*_args, **_kwargs):
        constructed["n"] += 1
        raise AssertionError("provider constructed")

    fake_sdk = types.ModuleType("typesafe_sdk")
    fake_sdk.AsyncTypeSafeClient = boom
    fake_sdk.TypeSafeClient = boom
    fake_sdk.RetryPolicy = lambda **_k: None
    fake_sdk.Choice = dict
    fake_sdk.Noul = dict
    fake_adapter = types.ModuleType("system_one_adapter")
    fake_adapter.AsyncSystemOneAdapterClient = boom
    fake_adapter.Noul = dict
    fake_adapter.Score = dict
    openai = types.ModuleType("system_one_adapter.providers.openai")
    openai.AsyncOpenAIProvider = boom
    providers = types.ModuleType("system_one_adapter.providers")
    providers.openai = openai
    saved = {}
    for name, mod in (
        ("typesafe_sdk", fake_sdk),
        ("system_one_adapter", fake_adapter),
        ("system_one_adapter.providers", providers),
        ("system_one_adapter.providers.openai", openai),
    ):
        saved[name] = sys.modules.get(name)
        sys.modules[name] = mod
    return saved


def restore(saved, previous):
    for key, value in previous.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    for name, mod in saved.items():
        if mod is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = mod


def with_keys(constructed):
    saved = stub_providers(constructed)
    previous = {key: os.environ.get(key) for key in KEYS}
    for key in KEYS:
        os.environ[key] = "test-key-not-used"
    return saved, previous


class RunnerGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="runner-gate-", dir="/tmp")
        git(self.tmp, "init", "-q")
        git(self.tmp, "config", "user.email", "test@example.com")
        git(self.tmp, "config", "user.name", "test")
        bar = Path(self.tmp) / "bar.md"
        bar.write_text("bar\n")
        git(self.tmp, "add", "bar.md")
        git(self.tmp, "commit", "-q", "-m", "[test] bar")
        bar.write_text("dirty\n")

    def _call(self, which):
        constructed = {"n": 0}
        saved, previous = with_keys(constructed)
        try:
            if which == "rerank":
                mod = load(ROOT / "work/rerank-scifact/run.py", "rerank_run")
                asyncio.run(mod.run_arm("jev", bar_path="bar.md", repo=self.tmp))
            elif which == "clinc":
                mod = load(ROOT / "work/choice-clinc150/run-variance.py", "clinc_var")
                mod.main(["jev-run2"], bar_path="bar.md", repo=self.tmp)
            elif which == "b77-jev":
                mod = load(ROOT / "work/choice-banking77/run.py", "b77_run")
                mod.run_jev(
                    [], {}, "/tmp/unused.jsonl", bar_path="bar.md", repo=self.tmp
                )
            elif which == "rf57":
                mod = load(
                    ROOT / "work/nev-differential/variance-20260924/run-jev.py",
                    "rf57_run",
                )
                asyncio.run(mod.main(bar_path="bar.md", repo=self.tmp))
            else:
                raise AssertionError(which)
        finally:
            restore(saved, previous)
        return constructed["n"]

    def test_dirty_bar_constructs_nothing(self):
        for which in (
            "rerank",
            "clinc",
            "b77-jev",
            "rf57",
        ):
            with self.subTest(which=which):
                with self.assertRaises(AttemptPanic):
                    self._call(which)

    def test_clean_bar_and_no_key_stays_unconfigured(self):
        previous = {key: os.environ.get(key) for key in KEYS}
        for key in KEYS:
            os.environ.pop(key, None)
        constructed = {"n": 0}
        saved = stub_providers(constructed)
        try:
            rerank = load(ROOT / "work/rerank-scifact/run.py", "rerank_clean")
            self.assertEqual(asyncio.run(rerank.run_arm("jev")), 2)
            b77 = load(ROOT / "work/choice-banking77/run.py", "b77_clean")
            self.assertEqual(b77.run_jev([], {}, "/tmp/unused.jsonl"), 2)
            rf57 = load(
                ROOT / "work/nev-differential/variance-20260924/run-jev.py",
                "rf57_clean",
            )
            self.assertEqual(asyncio.run(rf57.main()), 2)
        finally:
            restore(saved, previous)
        self.assertEqual(constructed["n"], 0)

    def test_deleting_each_gate_fails_in_a_tmp_copy(self):
        cases = [
            (
                ROOT / "work/rerank-scifact/run.py",
                "run_arm",
                ("jev",),
                {"bar_path": "bar.md", "repo": self.tmp},
                True,
            ),
            (
                ROOT / "work/choice-banking77/run.py",
                "run_jev",
                ([], {}, "/tmp/unused.jsonl"),
                {"bar_path": "bar.md", "repo": self.tmp},
                False,
            ),
            (
                ROOT / "work/nev-differential/variance-20260924/run-jev.py",
                "main",
                (),
                {"bar_path": "bar.md", "repo": self.tmp},
                True,
            ),
            (
                ROOT / "work/choice-clinc150/run-variance.py",
                "main",
                (["jev-run2"],),
                {"bar_path": "bar.md", "repo": self.tmp},
                False,
            ),
        ]
        for src, fn, args, kwargs, is_async in cases:
            text = src.read_text()
            removed = text
            for gate in GATES:
                if gate in removed:
                    removed = removed.replace(gate, "", 1)
                    break
            else:
                self.fail(f"no gate line in {src}")
            copy = Path(self.tmp) / f"deleted-{src.name}"
            copy.write_text(removed)
            constructed = {"n": 0}
            saved, previous = with_keys(constructed)
            try:
                mod = types.ModuleType(f"deleted_{src.stem}")
                mod.__file__ = str(src)
                exec(compile(removed, str(src), "exec"), mod.__dict__)
                if src.name == "run.py" and "rerank-scifact" in str(src):
                    # rows-jev.jsonl holds all 6000 pairs since cf70e28, so the real pairs and
                    # answered() leave nothing to do and the gateless copy returned 0 unbuilt.
                    mod.load_text = lambda: ({}, {})
                    mod.pairs = lambda: [("q", "d")]
                    mod.answered = lambda _arm: set()
                if src.name == "run-jev.py":
                    corpus = {
                        "samples": [{"text": "x", "label": 0} for _ in range(662)]
                    }
                    planted = Path(self.tmp) / "injection.json"
                    planted.write_text(json.dumps(corpus))
                    mod.RD.SRC = str(planted)
                target = getattr(mod, fn)
                with self.assertRaises(AssertionError):
                    if is_async:
                        asyncio.run(target(*args, **kwargs))
                    else:
                        target(*args, **kwargs)
            finally:
                restore(saved, previous)
            self.assertGreater(constructed["n"], 0, src.name)
            self.assertTrue(copy.is_file())


if __name__ == "__main__":
    unittest.main()
