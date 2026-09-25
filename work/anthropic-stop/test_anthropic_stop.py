"""No paid comparisons, held in code (beads jev-sybt, jev-lbgk).

Joshua, 2026-09-24: "i want us to stop using haiku api credits to compare our systems, i've been
charged $100 from anthropic since yesterday", then "we're not going to use any of the paid
comparisons" (AGENTS.md 'No paid comparisons', 1cc7876). A comparator is a free OpenRouter model
(a ':free' id) or nothing.

Four arms:
  census     every tracked code file naming a paid comparator (a Claude model id or an Anthropic
             client; a grok id, XAI_API_KEY, api.x.ai or an xai/ label; an OpenRouter client or a
             quoted OpenRouter id without ':free') is either a guarded runner or a named keyless
             file; a new file naming one fails until it is classified here.
  static     each guarded entry calls refuse_paid_comparator or require_free_comparator before any
             paid reference.
  behaviour  each guarded entry, called with keys set and every provider stubbed, raises
             PaidComparisonStopped and constructs nothing; the same source with the call deleted
             no longer refuses. A layered entry has a second guard downstream (the OpenRouter
             provider refuses a paid id itself), so deleting its call is caught by the static arm.
             Jev arms and ':free' OpenRouter arms still reach their own paths.
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
from collections import namedtuple
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from anthropic_stop import (  # noqa: E402
    PaidComparisonStopped,
    refuse_paid_comparator,
    require_free_comparator,
)

GUARDS = {"refuse_paid_comparator", "require_free_comparator"}
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
# xAI: a grok model id (grok-4, grok-4.20-0309-...), the key, the endpoint, or an xai/ or x-ai/ label.
# "grokbot" (a repo name) and "grok's" are not ids.
XAI = re.compile(r"\bgrok-\d|XAI_API_KEY|api\.x\.ai|\bx-ai/|\bxai/")
# An OpenRouter client: the endpoint, the key, or the lane's provider helper.
OPENROUTER_CLIENT = re.compile(r"openrouter\.ai|OPENROUTER_API_KEY|openrouter_provider")
# A quoted OpenRouter id with no ':free' suffix: the closing quote follows the name directly.
OPENROUTER_PAID_ID = re.compile(
    r"[\"'](?:openai|deepseek|google|meta-llama|mistralai|qwen|moonshotai|z-ai|nvidia|nex-agi"
    r"|liquid|dots-studio|cohere|amazon|microsoft|minimax|perplexity|nousresearch|x-ai|anthropic)"
    r"/[\w.-]+[\"']"
)
NAMING = (CLAUDE_ID, ANTHROPIC_CLIENT, XAI, OPENROUTER_CLIENT, OPENROUTER_PAID_ID)
# A client or endpoint a keyless file must not hold.
CLIENT_SHAPE = re.compile(
    r"(?:OpenAIProvider|AnthropicProvider|SystemOneAdapterClient)\(|api\.x\.ai"
    r"|api\.anthropic\.com|openrouter\.ai/api/v1(?!/key)|^\s*import anthropic",
    re.M,
)
CODE = re.compile(r"\.(?:py|mjs|cjs|js|ts|sh)$")
PAID_REF = re.compile(
    r"haiku|claude|anthropic|SystemOneAdapterClient|OpenAIProvider|XAI_API_KEY|x\.ai|GROK_"
    r"|openrouter|provider_for|PacedProvider",
    re.I,
)

# One guarded entry: the function the file's CLI reaches for its paid arm, how to call it, and
# module attributes to replace so that, with the guard deleted, the call reaches its provider
# quickly instead of returning "nothing to do" over committed rows.
Entry = namedtuple("Entry", "fn args kwargs is_async layered patch")


def entry(fn, *args, is_async=False, layered=False, patch=None, **kwargs):
    return Entry(fn, args, kwargs, is_async, layered, patch or {})


def nothing_scored(_path):
    """A run's prior(path) with no scored ids and no error counts: every item is still to do."""
    return set(), {}


# The bicameral grok runners check their bar and adapter pins, then skip scored ids; the adapter
# clone has since moved past the pinned sha and every id is scored, so a guard-deleted run would
# return before its provider without these.
GROK_GATE_PATCH = {"check_pins": lambda: None, "prior": nothing_scored}


# Guarded runners. run-b.py defines run_haiku twice (the second wins); the static arm checks both
# definitions. grok-incumbent-3 reads its committed bar first (test_prereg.py proves a dirty bar
# panics through it), then refuses.
GUARDED = {
    # Anthropic (jev-sybt)
    "work/adapter-uniform/live.py": (entry("run"),),
    "work/bicameral-gate/real-haiku.py": (entry("main", is_async=True),),
    "work/bicameral-gate/run-b.py": (entry("run_haiku", [], "/tmp/unused.jsonl"),),
    "work/bicameral-gate/run-c.py": (entry("run_haiku", [], "/tmp/unused.jsonl", {}),),
    "work/jev-injection-flag/run-haiku.py": (entry("main", is_async=True),),
    "work/jev-toolout-flag/run-haiku.py": (
        entry("main", "instructions", "corpus", is_async=True),
    ),
    "work/choice-banking77/run_prompted.py": (entry("main", []),),
    "work/choice-banking77/run.py": (entry("run_haiku", [], {}, "/tmp/unused.jsonl"),),
    "work/choice-clinc150/run.py": (
        entry("run_haiku", [], {}, "/tmp/unused.jsonl", {}, 1),
    ),
    "work/noul-scifact/run.py": (entry("main", "haiku", is_async=True),),
    "work/score-quixbugs/run.py": (
        entry("main", "haiku", "/tmp/unused.jsonl", is_async=True),
    ),
    "work/score-sst5/run.py": (entry("main", "haiku", is_async=True),),
    "work/score-yelp/run.py": (entry("main", "haiku", is_async=True),),
    # Anthropic and xAI
    "work/nev-differential/run_diff.py": (
        entry("make_model", "B-anthropic-claude-haiku-4-5"),
        entry("make_model", "A-xai-grok-4"),
    ),
    # xAI (jev-lbgk)
    "work/bicameral-gate/run-grok-criteria.py": (
        entry("main", "real", 1, is_async=True, patch=GROK_GATE_PATCH),
    ),
    "work/bicameral-gate/run-grok-gate.py": (
        entry("main", "real", 1, is_async=True, patch=GROK_GATE_PATCH),
    ),
    "work/grok-incumbent-3/run.py": (entry("main", "fever", "run1", is_async=True),),
    "work/noul-toxicity/run.py": (entry("main", "grok", is_async=True),),
    "work/rerank-scifact/run.py": (
        entry(
            "run_arm",
            "grok",
            is_async=True,
            patch={
                "load_text": lambda: ({}, {}),
                "pairs": lambda: [("q", "d")],
                "answered": lambda _arm: set(),
            },
        ),
    ),
    "work/score-stsb/run.py": (entry("main", "grok", is_async=True),),
    "work/second-incumbent/run.py": (
        entry("run", "scifact", is_async=True),
        entry("smoke", is_async=True),
    ),
    # OpenRouter, any id without ':free' (jev-lbgk)
    "work/openrouter/provider.py": (entry("openrouter_provider", "openai/gpt-5-nano"),),
    "work/openrouter/run_sst5.py": (
        entry(
            "run_model_paced", "openai/gpt-5-nano", None, is_async=True, layered=True
        ),
    ),
    "work/openrouter-incumbents/run.py": (
        entry("provider_for", "deepseek/deepseek-v4-flash", layered=True),
        entry(
            "run_free",
            "openai/gpt-5-nano",
            "sst5",
            False,
            None,
            10,
            False,
            is_async=True,
            layered=True,
        ),
    ),
}

# Tracked code that names a paid comparator and never calls one, with the reason.
KEYLESS = {
    ".omp/tools/jev-screen.ts": "cites grok-4's published bench score in a comment; calls Jev only",
    "work/osw-bestofn/select_pool.py": "names released OSWorld-Verified run archives; builds no client",
    "demos/routing-backtest/bin/adapt-claude.mjs": "reads Claude Code session files; price table only",
    "work/adapter-pin/finish-audit.py": "audits committed rows; names providers to classify them",
    "work/bicameral-gate/emit-c-labels.py": "names the adjudicating agent's model in a label",
    "work/bicameral-gate/score-grok-criteria.py": "scores committed grok rows",
    "work/bicameral-gate/score-grok-gate.py": "scores committed grok rows",
    "work/jev-billing-units/measure.mjs": "cites a cookbook price line; no call",
    "work/nev-differential/analyze_diff.py": "scores committed rows",
    "work/nev-differential/variance-20260924/variance.py": "scores committed rows",
    "work/openrouter-incumbents/test_run.py": "offline test: paid ids refuse; client stubbed, fake key",
    "work/openrouter/test_provider.py": "offline test: builds a :free provider, a paid id refuses; fake key",
    "work/openrouter/usage_daily.py": "reads the OpenRouter key's usage counter; sends no model request",
    "work/readme-stranger-run/run.py": "names grok-4.20 in a number-parsing comment",
    "work/second-incumbent/grok_variance.py": "scores committed grok rows",
    "work/second-incumbent/score_n4j.py": "scores committed grok rows",
    "work/sr-adopt/test_prereg.py": "offline test: fake XAI_API_KEY, providers stubbed",
    "work/sr-adopt/test_runner_gates.py": "offline test: fake keys, providers stubbed",
}

KEYS = ("TYPESAFE_API_KEY", "XAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY")


def tracked():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    ).stdout
    return out.splitlines()


class Question:
    """Stands in for an SDK question type: keeps its keyword fields as attributes."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.__dict__.update(kwargs)


class Stubs:
    """Stub SDK, adapter and provider modules, fake keys, and sockets that refuse to resolve or connect."""

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
        sdk.TypeSafeAPITimeoutError = type("TypeSafeAPITimeoutError", (Exception,), {})
        sdk.TypeSafeRateLimitError = type("TypeSafeRateLimitError", (Exception,), {})
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
        self.saved_socket = (socket.socket.connect, socket.getaddrinfo)

        def no_network(*_a, **_k):
            raise AssertionError("network used")

        socket.socket.connect = no_network
        socket.getaddrinfo = no_network
        self.saved_path = list(sys.path)
        # Runner siblings a guarded file imports by bare name; restored, not popped, so a module
        # another test already holds (phase_gate's AttemptPanic) keeps its identity.
        self.saved_siblings = {
            name: sys.modules.get(name) for name in ("run", "phase_gate", "provider")
        }
        for name in self.saved_siblings:
            sys.modules.pop(name, None)
        return self

    def __exit__(self, *_exc):
        socket.socket.connect, socket.getaddrinfo = self.saved_socket
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


def module_name(prefix, rel):
    return prefix + re.sub(r"\W", "_", rel)


def call(mod, e):
    for name, value in e.patch.items():
        setattr(mod, name, value)
    target = getattr(mod, e.fn)
    if e.is_async:
        return asyncio.run(target(*e.args, **e.kwargs))
    return target(*e.args, **e.kwargs)


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
        and node.value.func.id in GUARDS
    )


def is_docstring(node, fn):
    return (
        fn.body
        and node is fn.body[0]
        and isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


class PaidStopTest(unittest.TestCase):
    def test_refusal_raises_past_a_per_row_except_exception(self):
        with self.assertRaises(PaidComparisonStopped) as got:
            try:
                refuse_paid_comparator("planted arm")
            except Exception:  # noqa: BLE001 - the shape of a runner's per-row handler
                self.fail("the refusal was swallowed by `except Exception`")
        text = str(got.exception)
        self.assertIn("REFUSED: planted arm", text)
        self.assertIn("i've been charged $100 from anthropic", text)
        self.assertIn("we're not going to use any of the paid comparisons", text)
        self.assertIn("not run (paid comparisons stopped 2026-09-24)", text)
        self.assertIn("There is no override", text)

    def test_only_a_free_openrouter_id_passes(self):
        self.assertIsNone(
            require_free_comparator("dots-studio/dots-3-note-preview:free", "arm")
        )
        for model in (
            "openai/gpt-5-nano",
            "deepseek/deepseek-v4-flash",
            "x-ai/grok-4",
            "anthropic/claude-haiku-4.5",
            "qwen/qwen3.8-27b:free-trial",
        ):
            with (
                self.subTest(model=model),
                self.assertRaises(PaidComparisonStopped) as got,
            ):
                require_free_comparator(model, "arm")
            self.assertIn(f"REFUSED: arm ({model})", str(got.exception))

    def test_census_patterns_know_every_paid_shape(self):
        for pattern, texts in (
            (
                CLAUDE_ID,
                (
                    'model="claude-3-5-sonnet-20241022"',
                    'model="claude-3-opus-20240229"',
                    'model="claude-2.1"',
                    'model="claude-instant-1.2"',
                    'model="claude-haiku-4-5"',
                    'model="anthropic/claude-haiku-4.5"',
                ),
            ),
            (
                ANTHROPIC_CLIENT,
                (
                    "from system_one_adapter.providers.anthropic import AsyncAnthropicProvider",
                    "import anthropic",
                    'provider, model = "anthropic", MODEL',
                    'fetch("https://api.anthropic.com/v1/messages")',
                ),
            ),
            (
                XAI,
                (
                    'GROK_MODEL = "grok-4.20-0309-non-reasoning"',
                    'AsyncOpenAIProvider("grok-4", base_url=URL)',
                    'os.environ["XAI_API_KEY"]',
                    'BASE = "https://api.x.ai/v1"',
                    'MODEL_LABEL = f"xai/{GROK_MODEL}"',
                    'model="x-ai/grok-4"',
                ),
            ),
            (
                OPENROUTER_CLIENT,
                (
                    'BASE_URL = "https://openrouter.ai/api/v1"',
                    'os.environ.get("OPENROUTER_API_KEY")',
                    "prov = OR.openrouter_provider(model)",
                ),
            ),
            (
                OPENROUTER_PAID_ID,
                (
                    'PAID = ("openai/gpt-5-nano", "deepseek/deepseek-v4-flash")',
                    "model = 'google/gemini-3-pro'",
                ),
            ),
        ):
            for text in texts:
                with self.subTest(text=text):
                    self.assertTrue(pattern.search(text))
        for text in (
            "claude-code-session-jsonl",
            "# about Anthropic's pricing",
            "-Developer-grokbot/2026-09-11",
            "against grok's 23",
            '"dots-studio/dots-3-note-preview:free"',
            '"work/second-incumbent/run.py"',
        ):
            with self.subTest(text=text):
                self.assertFalse(any(p.search(text) for p in NAMING))

    def test_census_every_paid_naming_file_is_guarded_or_keyless(self):
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
            if any(p.search(text) for p in NAMING):
                naming.add(rel)
        self.assertEqual(
            sorted(naming - set(GUARDED) - set(KEYLESS)),
            [],
            "a tracked file names a paid comparator and is neither guarded nor listed keyless",
        )
        self.assertEqual(
            sorted((set(GUARDED) | set(KEYLESS)) - naming),
            [],
            "a listed file no longer names one",
        )
        self.assertEqual(sorted(set(GUARDED) & set(KEYLESS)), [])
        for rel in KEYLESS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            with self.subTest(file=rel):
                self.assertEqual(
                    CLIENT_SHAPE.findall(text),
                    [],
                    f"{rel} is listed keyless but builds a client or names an endpoint",
                )

    def test_static_guard_precedes_every_paid_reference(self):
        for rel, entries in GUARDED.items():
            source = (ROOT / rel).read_text(encoding="utf-8")
            tree = ast.parse(source)
            with self.subTest(file=rel):
                imported = {
                    a.name
                    for n in ast.walk(tree)
                    if isinstance(n, ast.ImportFrom) and n.module == "anthropic_stop"
                    for a in n.names
                }
                self.assertTrue(imported & GUARDS, f"{rel} imports no guard")
            for fn in {e.fn for e in entries}:
                defs = [
                    n
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.name == fn
                ]
                with self.subTest(file=rel, fn=fn):
                    self.assertTrue(defs, f"no def {fn}")
                for d in defs:
                    guards = [n for n in ast.walk(d) if is_guard(n)]
                    with self.subTest(file=rel, fn=fn, line=d.lineno):
                        self.assertTrue(
                            guards, f"{rel}:{d.lineno} def {fn} has no guard call"
                        )
                        first = min(g.lineno for g in guards)
                        # The guard itself, the test of an `if` whose body is the guard (the arm
                        # condition, e.g. `if not arm.startswith("jev"):`), and the docstring are
                        # not paid references.
                        arm_tests = [
                            n.test
                            for n in ast.walk(d)
                            if isinstance(n, ast.If)
                            and any(is_guard(s) for s in n.body)
                        ]
                        inside = {
                            id(x)
                            for g in guards
                            + arm_tests
                            + [s for s in d.body if is_docstring(s, d)]
                            for x in ast.walk(g)
                        }
                        early = [
                            n.lineno
                            for n in ast.walk(d)
                            if id(n) not in inside
                            and getattr(n, "lineno", first) < first
                            and n is not d
                            and PAID_REF.search(
                                ast.unparse(n) if isinstance(n, ast.expr) else ""
                            )
                        ]
                        self.assertEqual(
                            early,
                            [],
                            f"{rel}: a paid reference precedes the guard in {fn}",
                        )

    def test_behaviour_each_entry_refuses_and_constructs_nothing(self):
        for rel, entries in GUARDED.items():
            for e in entries:
                with self.subTest(file=rel, fn=e.fn, args=e.args), Stubs() as stubs:
                    source = (ROOT / rel).read_text(encoding="utf-8")
                    mod = load_source(rel, source, module_name("guarded_", rel))
                    with self.assertRaises(PaidComparisonStopped):
                        call(mod, e)
                    self.assertEqual(stubs.constructed, [])

    def test_cli_entry_points_refuse_and_construct_nothing(self):
        for rel, fn, argv in (
            (
                "work/openrouter-incumbents/run.py",
                "main",
                ["openai/gpt-5-nano", "sst5", "--max-requests", "10"],
            ),
            ("work/second-incumbent/run.py", "main", ["scifact"]),
            ("work/rerank-scifact/run.py", "main", ["grok"]),
        ):
            with self.subTest(file=rel, argv=argv), Stubs() as stubs:
                mod = load_source(
                    rel,
                    (ROOT / rel).read_text(encoding="utf-8"),
                    module_name("cli_", rel),
                )
                with self.assertRaises(PaidComparisonStopped):
                    getattr(mod, fn)(argv)
                self.assertEqual(stubs.constructed, [])

    def test_deleting_the_guard_no_longer_refuses(self):
        """Mutation arm: with the refusal deleted, the same entry no longer raises it."""
        for rel, entries in GUARDED.items():
            source = (ROOT / rel).read_text(encoding="utf-8")
            cut = without_guard(source)
            self.assertNotEqual(cut, source, f"{rel}: no refusal call to delete")
            for e in entries:
                if e.layered:
                    continue
                with self.subTest(file=rel, fn=e.fn, args=e.args), Stubs():
                    mod = load_source(rel, cut, module_name("deleted_", rel))
                    try:
                        call(mod, e)
                    except PaidComparisonStopped:
                        self.fail(
                            f"{rel}: still refuses with the call deleted; the arm tests nothing"
                        )
                    except BaseException:  # noqa: BLE001 - any other outcome proves the guard was load-bearing
                        pass

    def test_jev_and_free_arms_are_unaffected(self):
        cases = (
            ("work/noul-scifact/run.py", "main", ("jev",)),
            ("work/score-quixbugs/run.py", "main", ("jev", "/tmp/unused.jsonl")),
            ("work/score-sst5/run.py", "main", ("jev",)),
            ("work/score-yelp/run.py", "main", ("jev",)),
            ("work/noul-toxicity/run.py", "main", ("jev",)),
            ("work/score-stsb/run.py", "main", ("jev",)),
        )
        for rel, fn, args in cases:
            with self.subTest(file=rel, arm="jev"), Stubs():
                os.environ.pop("TYPESAFE_API_KEY", None)
                mod = load_source(
                    rel,
                    (ROOT / rel).read_text(encoding="utf-8"),
                    module_name("jev_", rel),
                )
                self.assertEqual(
                    asyncio.run(getattr(mod, fn)(*args)),
                    2,
                    "the keyless Jev arm stays 'unconfigured'",
                )
        for rel, fn, args in (
            (
                "work/openrouter/provider.py",
                "openrouter_provider",
                ("nex-agi/nex-n2.5-mini:free",),
            ),
            (
                "work/openrouter-incumbents/run.py",
                "provider_for",
                ("dots-studio/dots-3-note-preview:free",),
            ),
        ):
            with self.subTest(file=rel, arm=":free"), Stubs() as stubs:
                mod = load_source(
                    rel,
                    (ROOT / rel).read_text(encoding="utf-8"),
                    module_name("free_", rel),
                )
                with self.assertRaises(AssertionError):
                    getattr(mod, fn)(*args)
                self.assertEqual(
                    stubs.constructed,
                    ["AsyncOpenAIProvider"],
                    "a :free OpenRouter arm passes the guard and builds its provider",
                )


if __name__ == "__main__":
    unittest.main()
