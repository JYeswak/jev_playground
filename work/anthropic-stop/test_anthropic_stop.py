"""No Anthropic API spend on comparisons, held in code (bead jev-sybt).

Joshua, 2026-09-24: "i want us to stop using haiku api credits to compare our systems, i've been
charged $100 from anthropic since yesterday" (AGENTS.md, ed8ef13).

Four arms:
  census     every tracked code file naming a claude model id is either a guarded runner or a
             named keyless file; a new file naming one fails until it is classified here.
  static     each guarded entry calls refuse_anthropic_comparator before any Anthropic reference.
  behaviour  each guarded entry, called with keys set and every provider stubbed, raises
             AnthropicSpendStopped and constructs nothing; the same source with the call deleted
             reaches a stub provider instead. Jev and grok arms still reach their own paths.
No network, no key, no provider is ever constructed for real.
"""

import ast
import asyncio
import importlib.machinery
import importlib.util
import os
import re
import socket
import subprocess
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from anthropic_stop import AnthropicSpendStopped, refuse_anthropic_comparator  # noqa: E402

GUARD = "refuse_anthropic_comparator"
# Every Claude model id shape, old and new: claude-3-5-sonnet-20241022, claude-3-opus, claude-2.1,
# claude-instant-1.2, claude-haiku-4-5, anthropic/claude-haiku-4.5. The first version matched only
# claude-(haiku|sonnet|opus) and would have passed a new runner naming claude-3-5-sonnet (README check
# of 10706d9).
CLAUDE_ID = re.compile(
    r"\bclaude-(?:\d|instant|[\w.-]*(?:haiku|sonnet|opus))|anthropic/claude"
)
# An Anthropic client with no id string in the file: the adapter's provider, the SDK, the endpoint,
# or the adapter's provider name "anthropic" as a string.
ANTHROPIC_CLIENT = re.compile(
    r"AnthropicProvider|providers\.anthropic|api\.anthropic\.com|@anthropic-ai/sdk"
    r"|^\s*(?:import|from)\s+anthropic\b|['\"]anthropic['\"]",
    re.M,
)
CODE = re.compile(r"\.(?:py|mjs|cjs|js|ts|sh)$")
ANTHROPIC_REF = re.compile(r"haiku|claude|anthropic|SystemOneAdapterClient", re.I)

# Guarded runners: file -> (entry function, positional args, keyword args, is_async). The entry is
# the function the file's CLI calls for its Haiku or Anthropic arm. run-b.py defines run_haiku
# twice (the second wins); the static arm checks both definitions.
GUARDED = {
    "work/adapter-uniform/live.py": ("run", (), {}, False),
    "work/bicameral-gate/real-haiku.py": ("main", (), {}, True),
    "work/bicameral-gate/run-b.py": ("run_haiku", ([], "/tmp/unused.jsonl"), {}, False),
    "work/bicameral-gate/run-c.py": (
        "run_haiku",
        ([], "/tmp/unused.jsonl", {}),
        {},
        False,
    ),
    "work/jev-injection-flag/run-haiku.py": ("main", (), {}, True),
    "work/jev-toolout-flag/run-haiku.py": (
        "main",
        ("instructions", "corpus"),
        {},
        True,
    ),
    "work/choice-banking77/run_prompted.py": ("main", ([],), {}, False),
    "work/nev-differential/run_diff.py": (
        "make_model",
        ("B-anthropic-claude-haiku-4-5",),
        {},
        False,
    ),
    "work/choice-banking77/run.py": (
        "run_haiku",
        ([], {}, "/tmp/unused.jsonl"),
        {},
        False,
    ),
    "work/choice-clinc150/run.py": (
        "run_haiku",
        ([], {}, "/tmp/unused.jsonl", {}, 1),
        {},
        False,
    ),
    "work/noul-scifact/run.py": ("main", ("haiku",), {}, True),
    "work/score-quixbugs/run.py": ("main", ("haiku", "/tmp/unused.jsonl"), {}, True),
    "work/score-sst5/run.py": ("main", ("haiku",), {}, True),
    "work/score-yelp/run.py": ("main", ("haiku",), {}, True),
}

# Tracked code that names a claude model id or an Anthropic client and never calls the Anthropic
# API, with the reason.
KEYLESS = {
    "demos/routing-backtest/bin/adapt-claude.mjs": "reads Claude Code session files; price table only",
    "work/jev-billing-units/measure.mjs": "cites a cookbook price line; no call",
    "work/nev-differential/analyze_diff.py": "scores committed rows",
    "work/nev-differential/variance-20260924/variance.py": "scores committed rows",
    "work/openrouter/test_provider.py": "builds an OpenRouter provider offline with a fake key",
    "work/adapter-pin/finish-audit.py": "audits committed rows; names providers to classify them",
}

KEYS = ("TYPESAFE_API_KEY", "XAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY")


def tracked():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True
    ).stdout
    return out.splitlines()


class Question:
    """Stands in for an SDK question type: keeps its keyword fields as attributes."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.__dict__.update(kwargs)


class Stubs:
    """Stub SDK, adapter and provider modules, fake keys, and a socket that refuses to connect."""

    def __init__(self):
        self.constructed = []

    def __enter__(self):
        def boom(name):
            def make(*_a, **_k):
                self.constructed.append(name)
                raise AssertionError(f"provider constructed: {name}")

            return make

        sdk = types.ModuleType("typesafe_sdk")
        for name in ("TypeSafeClient", "AsyncTypeSafeClient"):
            setattr(sdk, name, boom(name))
        sdk.RetryPolicy = lambda *a, **k: None
        sdk.Choice = sdk.Noul = sdk.Score = Question
        adapter = types.ModuleType("system_one_adapter")
        adapter.AsyncSystemOneAdapterClient = boom("AsyncSystemOneAdapterClient")
        adapter.SystemOneAdapterClient = boom("SystemOneAdapterClient")
        adapter.Noul = adapter.Score = adapter.Choice = Question
        providers = types.ModuleType("system_one_adapter.providers")
        openai = types.ModuleType("system_one_adapter.providers.openai")
        openai.AsyncOpenAIProvider = boom("AsyncOpenAIProvider")
        anthropic = types.ModuleType("system_one_adapter.providers.anthropic")
        anthropic.AsyncAnthropicProvider = boom("AsyncAnthropicProvider")
        providers.openai, providers.anthropic = openai, anthropic
        self.saved_modules = {}
        for name, mod in (
            ("typesafe_sdk", sdk),
            ("system_one_adapter", adapter),
            ("system_one_adapter.providers", providers),
            ("system_one_adapter.providers.openai", openai),
            ("system_one_adapter.providers.anthropic", anthropic),
        ):
            self.saved_modules[name] = sys.modules.get(name)
            sys.modules[name] = mod
        self.saved_env = {k: os.environ.get(k) for k in KEYS}
        for k in KEYS:
            os.environ[k] = "test-key-not-used"
        self.saved_connect = socket.socket.connect

        def no_network(*_a, **_k):
            raise AssertionError("network used")

        socket.socket.connect = no_network
        self.saved_path = list(sys.path)
        # Runner siblings a guarded file imports by bare name; restored, not popped, so a module
        # another test already holds (phase_gate's AttemptPanic) keeps its identity.
        self.saved_siblings = {
            name: sys.modules.get(name) for name in ("run", "phase_gate")
        }
        for name in self.saved_siblings:
            sys.modules.pop(name, None)
        return self

    def __exit__(self, *_exc):
        socket.socket.connect = self.saved_connect
        for k, v in self.saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        for name, mod in self.saved_modules.items():
            if mod is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod
        sys.path[:] = self.saved_path
        for name, mod in self.saved_siblings.items():
            if mod is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod
        return False


class _TextLoader(importlib.machinery.SourceFileLoader):
    """Imports `source` under the real file's path, so the module's __file__ and ROOT are the real ones.

    path_stats raises, which makes the import system skip the bytecode cache in both directions:
    a mutated source is never answered from the original's .pyc, and never written to one.
    """

    def __init__(self, name, path, source):
        super().__init__(name, path)
        self._source = source.encode("utf-8")

    def get_data(self, _path):
        return self._source

    def path_stats(self, _path):
        raise OSError("no bytecode cache for a text-loaded module")


def load_source(rel, source, name):
    """Import `source` as if it were the file at `rel` (its own directory first on sys.path)."""
    path = ROOT / rel
    sys.path.insert(0, str(path.parent))
    loader = _TextLoader(name, str(path), source)
    spec = importlib.util.spec_from_file_location(name, str(path), loader=loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def call(mod, fn, args, kwargs, is_async):
    target = getattr(mod, fn)
    if is_async:
        return asyncio.run(target(*args, **kwargs))
    return target(*args, **kwargs)


def without_guard(source):
    """The source with every refusal call deleted (the import stays)."""
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)
    drop = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.If)
            and any(is_guard(s) for s in node.body)
            and len(node.body) == 1
        ):
            drop.update(range(node.lineno, node.end_lineno + 1))
        elif is_guard(node):
            drop.update(range(node.lineno, node.end_lineno + 1))
    return "".join(line for i, line in enumerate(lines, 1) if i not in drop)


def is_guard(node):
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == GUARD
    )


class AnthropicStopTest(unittest.TestCase):
    def test_refusal_raises_past_a_per_row_except_exception(self):
        with self.assertRaises(AnthropicSpendStopped) as got:
            try:
                refuse_anthropic_comparator("planted arm")
            except Exception:  # noqa: BLE001 - the shape of a runner's per-row handler
                self.fail("the refusal was swallowed by `except Exception`")
        text = str(got.exception)
        self.assertIn("planted arm", text)
        self.assertIn("i've been charged $100 from anthropic", text)
        self.assertIn("There is no override", text)

    def test_census_pattern_knows_every_claude_id_shape(self):
        for text in (
            'model="claude-3-5-sonnet-20241022"',
            'model="claude-3-opus-20240229"',
            'model="claude-2.1"',
            'model="claude-instant-1.2"',
            'model="claude-haiku-4-5"',
            'model="anthropic/claude-haiku-4.5"',
        ):
            self.assertTrue(CLAUDE_ID.search(text), text)
        for text in (
            "from system_one_adapter.providers.anthropic import AsyncAnthropicProvider",
            "import anthropic",
            'provider, model = "anthropic", MODEL',
            'fetch("https://api.anthropic.com/v1/messages")',
        ):
            self.assertTrue(ANTHROPIC_CLIENT.search(text), text)
        for text in ("claude-code-session-jsonl", "# about Anthropic's pricing"):
            self.assertFalse(
                CLAUDE_ID.search(text) or ANTHROPIC_CLIENT.search(text), text
            )

    def test_census_every_claude_naming_file_is_guarded_or_keyless(self):
        naming = set()
        for rel in tracked():
            if not CODE.search(rel) or rel.startswith("work/anthropic-stop/"):
                continue
            path = ROOT / rel
            text = (
                path.read_text(encoding="utf-8", errors="replace")
                if path.is_file()
                else ""
            )
            if CLAUDE_ID.search(text) or ANTHROPIC_CLIENT.search(text):
                naming.add(rel)
        self.assertEqual(
            sorted(naming - set(GUARDED) - set(KEYLESS)),
            [],
            "a tracked file names a claude model id and is neither guarded nor listed keyless",
        )
        self.assertEqual(
            sorted((set(GUARDED) | set(KEYLESS)) - naming),
            [],
            "a listed file no longer names one",
        )
        for rel in KEYLESS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for shape in (
                "SystemOneAdapterClient",
                "AnthropicProvider",
                "api.anthropic.com",
                "import anthropic",
            ):
                self.assertNotIn(
                    shape, text, f"{rel} is listed keyless but has {shape}"
                )

    def test_static_guard_precedes_every_anthropic_reference(self):
        for rel, (fn, *_rest) in GUARDED.items():
            source = (ROOT / rel).read_text(encoding="utf-8")
            with self.subTest(file=rel):
                self.assertIn(f"from anthropic_stop import {GUARD}", source)
                defs = [
                    n
                    for n in ast.walk(ast.parse(source))
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.name == fn
                ]
                self.assertTrue(defs, f"no def {fn}")
                for d in defs:
                    guards = [n for n in ast.walk(d) if is_guard(n)]
                    self.assertTrue(
                        guards, f"{rel}:{d.lineno} def {fn} has no {GUARD} call"
                    )
                    first = min(g.lineno for g in guards)
                    # The guard itself, and the test of an `if` whose body is the guard (the arm
                    # condition, e.g. `if arm == "haiku":`), are not Anthropic references.
                    arm_tests = [
                        n.test
                        for n in ast.walk(d)
                        if isinstance(n, ast.If) and any(is_guard(s) for s in n.body)
                    ]
                    inside = {id(x) for g in guards + arm_tests for x in ast.walk(g)}
                    early = [
                        n.lineno
                        for n in ast.walk(d)
                        if id(n) not in inside
                        and getattr(n, "lineno", first) < first
                        and n is not d
                        and ANTHROPIC_REF.search(
                            ast.unparse(n) if isinstance(n, ast.expr) else ""
                        )
                    ]
                    self.assertEqual(
                        early,
                        [],
                        f"{rel}: an Anthropic reference precedes the guard in {fn}",
                    )

    def test_behaviour_each_entry_refuses_and_constructs_nothing(self):
        for rel, (fn, args, kwargs, is_async) in GUARDED.items():
            with self.subTest(file=rel), Stubs() as stubs:
                source = (ROOT / rel).read_text(encoding="utf-8")
                mod = load_source(
                    rel, source, "guarded_" + Path(rel).stem.replace("-", "_")
                )
                with self.assertRaises(AnthropicSpendStopped):
                    call(mod, fn, args, kwargs, is_async)
                self.assertEqual(stubs.constructed, [])

    def test_deleting_the_guard_reaches_a_provider_or_key_read(self):
        """Mutation arm: with the refusal deleted, the same entry no longer raises it."""
        for rel, (fn, args, kwargs, is_async) in GUARDED.items():
            with self.subTest(file=rel), Stubs():
                source = (ROOT / rel).read_text(encoding="utf-8")
                cut = without_guard(source)
                self.assertNotEqual(cut, source, f"{rel}: no refusal call to delete")
                mod = load_source(
                    rel, cut, "deleted_" + Path(rel).stem.replace("-", "_")
                )
                try:
                    call(mod, fn, args, kwargs, is_async)
                except AnthropicSpendStopped:
                    self.fail(
                        f"{rel}: still refuses with the call deleted; the arm tests nothing"
                    )
                except BaseException:  # noqa: BLE001 - any other outcome proves the guard was load-bearing
                    pass

    def test_jev_and_grok_arms_are_unaffected(self):
        cases = (
            ("work/noul-scifact/run.py", "main", ("jev",), True),
            ("work/score-quixbugs/run.py", "main", ("jev", "/tmp/unused.jsonl"), True),
            ("work/score-sst5/run.py", "main", ("jev",), True),
            ("work/score-yelp/run.py", "main", ("jev",), True),
        )
        for rel, fn, args, is_async in cases:
            with self.subTest(file=rel, arm="jev"), Stubs():
                os.environ.pop("TYPESAFE_API_KEY", None)
                mod = load_source(
                    rel,
                    (ROOT / rel).read_text(encoding="utf-8"),
                    "jev_" + Path(rel).parent.name.replace("-", "_"),
                )
                self.assertEqual(
                    call(mod, fn, args, {}, is_async),
                    2,
                    "the keyless Jev arm stays 'unconfigured'",
                )
        rel = "work/nev-differential/run_diff.py"
        with self.subTest(file=rel, arm="grok"), Stubs() as stubs:
            mod = load_source(
                rel, (ROOT / rel).read_text(encoding="utf-8"), "grok_run_diff"
            )
            with self.assertRaises(AssertionError):
                mod.make_model("A-xai-grok-4")
            self.assertEqual(
                stubs.constructed,
                ["AsyncOpenAIProvider"],
                "the grok arm builds its own provider",
            )


if __name__ == "__main__":
    unittest.main()
