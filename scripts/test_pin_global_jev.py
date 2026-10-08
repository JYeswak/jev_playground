#!/usr/bin/env python3
"""Offline coverage for the commit-pinned global Jev loader."""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess  # ubs:ignore — tests use only the allowlisted Git and Python executables below.
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pin-global-jev.py"
SDK_FALLBACK = "../node_modules/@typesafe-ai/sdk/dist/index.mjs"
SDK_PINNED = "../../work/sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs"
PROFILES = ("default", "claude", "codex", "grok", "muse")
ENTRY_FILES = (
    ".omp/extensions/jev-memory-filter.ts",
    "work/jev-j0er/jev-webscreen-global.ts",
    "work/jev-j0er/jev-injection-global.ts",
)
EXPECTED_CLOSURE = {
    ".omp/extensions/jev-memory-filter.ts",
    ".omp/hooks/post/jev-web-duel.ts",
    ".omp/hooks/post/jev-webscreen.ts",
    ".omp/hooks/post/jev-injection-shadow.ts",
    "kit/src/client.ts",
    "kit/src/validate.ts",
    "work/jev-client/src/use-infisical-key.ts",
    "work/jev-client/src/infisical-key.ts",
    "work/jev-a9fv/seat.mjs",
    "work/jev-j0er/jev-webscreen-global.ts",
    "work/jev-j0er/jev-injection-global.ts",
    "work/jev-j0er/repo-scope.ts",
}


def owned_scratch(label: str) -> Path:
    base = Path(os.environ["TMPDIR"]).resolve()
    if not base.is_relative_to(ROOT / "var" / "agent-tmp"):
        raise RuntimeError(f"test scratch directory must stay in the repository: {base}")
    path = Path(tempfile.mkdtemp(prefix="jev-49oe-", dir=base))
    (path / ".owner").write_text(
        f"pid={os.getpid()} label={label} repo={ROOT} created={datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )
    return path


def put(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def command(args: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    if not args or args[0] not in {"git", sys.executable}:
        raise AssertionError(f"unexpected test executable: {args[:1]}")
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False, timeout=30)  # ubs:ignore — allowlisted test executables and argv mode, without a shell.
    if check and result.returncode:
        raise AssertionError(f"command failed ({result.returncode}): {args}\n{result.stdout}\n{result.stderr}")
    return result


def load_object_json(text: str) -> dict[str, object]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise AssertionError("command emitted invalid JSON") from error
    if not isinstance(value, dict):
        raise AssertionError("command JSON output is not an object")
    return value


class PinGlobalJevTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = owned_scratch(self._testMethodName)
        self.repo = self.scratch / "repo"
        self.home = self.scratch / "home"
        self.empty_hooks = self.scratch / "empty-hooks"
        self.empty_hooks.mkdir()
        (self.home / ".omp" / "agent").mkdir(parents=True)
        for profile in PROFILES[1:]:
            (self.home / ".omp" / "profiles" / profile / "agent").mkdir(parents=True)
        self._source_tree()
        command(["git", "init", "-q"], cwd=self.repo)
        command(["git", "config", "core.hooksPath", str(self.empty_hooks)], cwd=self.repo)
        command(["git", "config", "user.name", "Pin Test"], cwd=self.repo)
        command(["git", "config", "user.email", "pin-test@example.invalid"], cwd=self.repo)
        command(["git", "add", "--all"], cwd=self.repo)
        command(["git", "commit", "-qm", "fixture [test]"], cwd=self.repo)
        self.commit = command(["git", "rev-parse", "HEAD"], cwd=self.repo).stdout.strip()
        self._installed_surfaces()
        put(self.repo, "work/sdk/node_modules/@typesafe-ai/sdk/package.json", json.dumps({"name": "@typesafe-ai/sdk", "version": "0.6.0"}))
        put(self.repo, "work/sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs", "export const sdk = true;\n")

    def _source_tree(self) -> None:
        source = {
            ".omp/extensions/jev-memory-filter.ts": (
                'import { askJev } from "../../kit/src/client.ts";\n'
                'import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";\n'
                'export default function memory(pi) { useInfisicalKey(); return askJev; }\n'
            ),
            ".omp/hooks/post/jev-web-duel.ts": (
                'import { makeWebscreenHandler } from "./jev-webscreen.ts";\n'
                'import { makeInjectionShadowHandler } from "./jev-injection-shadow.ts";\n'
                f'import {{ useInfisicalKey }} from "{self.repo}/work/jev-client/src/use-infisical-key.ts";\n'
                'export function makeDuelHandler() { return [makeWebscreenHandler, makeInjectionShadowHandler, useInfisicalKey]; }\n'
            ),
            ".omp/hooks/post/jev-webscreen.ts": (
                f'import {{ askJev }} from "{self.repo}/kit/src/client.ts";\n'
                f'import {{ useInfisicalKey }} from "{self.repo}/work/jev-client/src/use-infisical-key.ts";\n'
                'export function makeWebscreenHandler() { return [askJev, useInfisicalKey]; }\n'
            ),
            ".omp/hooks/post/jev-injection-shadow.ts": (
                'import { QUESTION } from "../../../work/jev-a9fv/seat.mjs";\n'
                'export function makeInjectionShadowHandler() { return QUESTION; }\n'
            ),
            "kit/src/client.ts": (
                'import type * as SdkModule from "@typesafe-ai/sdk";\n'
                'import { validateChoiceAnswer } from "./validate.ts";\n'
                'const SDK_PATH = "../../work/sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs";\n'
                'export async function askJev() { return [validateChoiceAnswer, import(SDK_PATH), new URL("../node_modules/@typesafe-ai/sdk/dist/index.mjs", import.meta.url)]; }\n'
            ),
            "kit/src/validate.ts": "export function validateChoiceAnswer() { return true; }\n",
            "work/jev-client/src/use-infisical-key.ts": (
                'import { keyProviderInstalled } from "../../../kit/src/client.ts";\n'
                'import { infisicalKeyProvider } from "./infisical-key.ts";\n'
                'export function useInfisicalKey() { return [keyProviderInstalled, infisicalKeyProvider]; }\n'
            ),
            "work/jev-client/src/infisical-key.ts": "export function infisicalKeyProvider() { return undefined; }\n",
            "work/jev-a9fv/seat.mjs": 'export const QUESTION = "frozen test question";\n',
            "work/jev-j0er/repo-scope.ts": "export function isJevRepoPath(cwd, root) { return cwd === root; }\n",
            "work/jev-j0er/jev-webscreen-global.ts": (
                f'import {{ makeDuelHandler }} from "{self.repo}/.omp/hooks/post/jev-web-duel.ts";\n'
                f'import {{ isJevRepoPath }} from "{self.repo}/work/jev-j0er/repo-scope.ts";\n'
                f'import {{ useInfisicalKey }} from "{self.repo}/work/jev-client/src/use-infisical-key.ts";\n'
                f'const REPO = "{self.repo}";\n'
                'export default function hook(pi) { useInfisicalKey(); return [makeDuelHandler, isJevRepoPath, REPO]; }\n'
            ),
            "work/jev-j0er/jev-injection-global.ts": "export default function retired(pi) { return undefined; }\n",
            "work/sdk/package-lock.json": json.dumps({
                "packages": {"node_modules/@typesafe-ai/sdk": {"version": "0.6.0", "integrity": "sha512-fixture"}}
            }),
            ".gitignore": "work/sdk/node_modules/\n",
        }
        for rel, text in source.items():
            put(self.repo, rel, text)

    def _installed_surfaces(self) -> None:
        for profile in PROFILES:
            agent = self.home / ".omp" / "agent" if profile == "default" else self.home / ".omp" / "profiles" / profile / "agent"
            config = agent / "config.yml"
            config.write_text(
                f"extensions:\n  - {self.repo}/.omp/extensions/jev-memory-filter.ts\n  - /opt/omp/keep-this.ts\n",
                encoding="utf-8",
            )
            hooks = agent / "hooks" / "post"
            hooks.mkdir(parents=True)
            for rel in ENTRY_FILES[1:]:
                os.link(self.repo / rel, hooks / Path(rel).name)
        global_extensions = self.home / ".omp" / "omp-extensions"
        global_extensions.mkdir()
        os.link(self.repo / ENTRY_FILES[0], global_extensions / Path(ENTRY_FILES[0]).name)

    def run_tool(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return command(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo), "--home", str(self.home), *args],
            check=check,
        )


    def test_plan_enumerates_all_configs_hooks_and_transitive_sources(self) -> None:
        result = self.run_tool("--plan", "--json")
        plan = load_object_json(result.stdout)
        self.assertEqual(len(plan["configs"]), 5)
        self.assertEqual(len(plan["hooks"]), 11)
        self.assertEqual(set(plan["closure"]), EXPECTED_CLOSURE)
        self.assertTrue(plan["external_sdk"])
        self.assertTrue(all("source_sha256" in row for row in plan["closure_details"]))

    def test_install_uses_frozen_commit_and_check_rejects_drift(self) -> None:
        baseline = command(["git", "show", f"{self.commit}:kit/src/client.ts"], cwd=self.repo).stdout
        source = self.repo / "kit" / "src" / "client.ts"
        source.write_text("export const working_tree_edit = true;\n", encoding="utf-8")
        installed = self.run_tool("--install", "--commit", self.commit)
        rollback_args = shlex.split(load_object_json(installed.stdout)["rollback_command"])
        self.assertEqual(rollback_args[1], str(SCRIPT))
        pin = self.home / ".omp" / "jev-pinned" / self.commit
        manifest = load_object_json((pin / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["closure"]), EXPECTED_CLOSURE)
        self.assertTrue((pin / "MANIFEST.sha256").is_file())
        pinned = pin / "repo" / "kit" / "src" / "client.ts"
        self.assertEqual(pinned.read_text(encoding="utf-8"), baseline.replace(SDK_FALLBACK, SDK_PINNED))
        sdk_package = pin / "repo" / "work" / "sdk" / "node_modules" / "@typesafe-ai" / "sdk"
        self.assertEqual((sdk_package / "package.json").read_text(encoding="utf-8"), '{"name": "@typesafe-ai/sdk", "version": "0.6.0"}')
        self.assertEqual((sdk_package / "dist" / "index.mjs").read_text(encoding="utf-8"), "export const sdk = true;\n")
        for profile in PROFILES:
            agent = self.home / ".omp" / "agent" if profile == "default" else self.home / ".omp" / "profiles" / profile / "agent"
            self.assertIn(str(pin / "repo" / ".omp" / "extensions" / "jev-memory-filter.ts"), (agent / "config.yml").read_text(encoding="utf-8"))
            for rel in ENTRY_FILES[1:]:
                hook = agent / "hooks" / "post" / Path(rel).name
                self.assertIn(str(pin / "repo" / rel), hook.read_text(encoding="utf-8"))
        global_extension = self.home / ".omp" / "omp-extensions" / Path(ENTRY_FILES[0]).name
        self.assertIn(str(pin / "repo" / ENTRY_FILES[0]), global_extension.read_text(encoding="utf-8"))
        profile_hook = self.home / ".omp" / "profiles" / "claude" / "agent" / "hooks" / "post" / Path(ENTRY_FILES[2]).name
        loaded_hook = profile_hook.read_text(encoding="utf-8")
        self.assertIn(str(pin / "repo" / ENTRY_FILES[2]), loaded_hook)
        self.assertNotEqual(source.read_text(encoding="utf-8"), baseline)
        self.run_tool("--check")

        replacement = source.with_suffix(".replacement")
        replacement.write_text("export const second_worktree_edit = true;\n", encoding="utf-8")
        os.replace(replacement, source)
        self.assertEqual(pinned.read_text(encoding="utf-8"), baseline.replace(SDK_FALLBACK, SDK_PINNED))
        self.assertEqual(profile_hook.read_text(encoding="utf-8"), loaded_hook)
        self.run_tool("--check")

        pinned.write_text("export const altered = true;\n", encoding="utf-8")
        drift = self.run_tool("--check", check=False)
        self.assertNotEqual(drift.returncode, 0)
        self.assertIn("pinned file digest mismatch", (drift.stdout + drift.stderr).lower())
        rollback_result = command(rollback_args)
        self.assertEqual(load_object_json(rollback_result.stdout)["status"], "rolled_back")


    def test_check_rejects_unpinned_global_working_tree_paths(self) -> None:
        check = self.run_tool("--check", check=False)
        self.assertNotEqual(check.returncode, 0)
        self.assertIn("working tree", (check.stdout + check.stderr).lower())

    def test_check_rejects_pinned_checkout_import_even_with_matching_hashes(self) -> None:
        self.run_tool("--install", "--commit", self.commit)
        pin = self.home / ".omp" / "jev-pinned" / self.commit
        rel = "work/jev-j0er/jev-webscreen-global.ts"
        pinned = pin / "repo" / rel
        source = pinned.read_text(encoding="utf-8")
        local_import = 'from "../../.omp/hooks/post/jev-web-duel.ts"'
        checkout_import = f'from "{self.repo}/.omp/hooks/post/jev-web-duel.ts"'
        self.assertIn(local_import, source)
        pinned.write_text(source.replace(local_import, checkout_import), encoding="utf-8")

        manifest_path = pin / "MANIFEST.json"
        manifest = load_object_json(manifest_path.read_text(encoding="utf-8"))
        manifest["files"][f"repo/{rel}"] = hashlib.sha256(pinned.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        checksums = "".join(f"{digest}  {path}\n" for path, digest in sorted(manifest["files"].items()))
        (pin / "MANIFEST.sha256").write_text(checksums, encoding="utf-8")

        check = self.run_tool("--check", check=False)
        self.assertNotEqual(check.returncode, 0)
        self.assertIn("pinned import resolves into working tree", (check.stdout + check.stderr).lower())

    def test_rollback_restores_config_values_and_hardlinked_hook_files(self) -> None:
        before = {
            profile: (self.home / ".omp" / "agent" / "config.yml" if profile == "default" else self.home / ".omp" / "profiles" / profile / "agent" / "config.yml").read_bytes()
            for profile in PROFILES
        }
        self.run_tool("--install", "--commit", self.commit)
        global_extension = self.home / ".omp" / "omp-extensions" / Path(ENTRY_FILES[0]).name
        installed_paths = [global_extension] + [
            self.home / ".omp" / "agent" / "hooks" / "post" / Path(rel).name
            if profile == "default"
            else self.home / ".omp" / "profiles" / profile / "agent" / "hooks" / "post" / Path(rel).name
            for profile in PROFILES for rel in ENTRY_FILES[1:]
        ]
        self.assertEqual(len({path.stat().st_ino for path in installed_paths}), len(installed_paths))
        self.run_tool("--rollback", "--commit", self.commit)
        for profile in PROFILES:
            config = self.home / ".omp" / "agent" / "config.yml" if profile == "default" else self.home / ".omp" / "profiles" / profile / "agent" / "config.yml"
            self.assertEqual(config.read_bytes(), before[profile])
        self.assertEqual({global_extension.stat().st_nlink}, {2})
        for rel in ENTRY_FILES[1:]:
            linked_group = [path for path in installed_paths if path.name == Path(rel).name]
            self.assertEqual(len({path.stat().st_ino for path in linked_group}), 1)
            self.assertEqual({path.stat().st_nlink for path in linked_group}, {len(PROFILES) + 1})
        self.assertEqual(len({path.stat().st_ino for path in installed_paths}), len(ENTRY_FILES))


if __name__ == "__main__":
    unittest.main()
