from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("outside-repo-surface-audit.py")
SPEC = importlib.util.spec_from_file_location("outside_repo_surface_audit", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load outside-repo surface audit module")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def registry_for(path: str, **overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "id": "fixture-hook",
        "installed_paths": [path],
        "loaded_from": path,
        "outside_repo": True,
        "latency_budget_ms": 1000,
        "fail_open_test": "fixture.test_hook_fail_open",
        "off_switch": {"path": "state/off", "polarity": "presence-OFF"},
        "safe_side": "return undefined; do not block",
        "owner": "fixture-owner",
    }
    entry.update(overrides)
    return {"surfaces": [entry]}


class OutsideRepoSurfaceAuditTests(unittest.TestCase):
    def test_valid_installed_surface_is_green(self) -> None:
        path = "/fixture/agent/hooks/post/jev-hook.ts"
        report = AUDIT.audit(
            registry_for(path),
            [{"path": path, "name": "jev-hook.ts", "loaded_from": path}],
        )
        self.assertEqual(report["status"], "GREEN")
        self.assertEqual(report["errors"], [])

    def test_hook_without_off_switch_is_red(self) -> None:
        path = "/fixture/agent/hooks/post/jev-hook.ts"
        report = AUDIT.audit(
            registry_for(path, off_switch=None),
            [{"path": path, "name": "jev-hook.ts", "loaded_from": path}],
        )
        self.assertIn(
            "missing_or_invalid_off_switch", {row["kind"] for row in report["errors"]}
        )
        self.assertEqual(report["status"], "RED")

    def test_latency_at_handler_limit_is_red(self) -> None:
        path = "/fixture/agent/hooks/post/jev-hook.ts"
        report = AUDIT.audit(
            registry_for(path, latency_budget_ms=30000),
            [{"path": path, "name": "jev-hook.ts", "loaded_from": path}],
        )
        self.assertIn(
            "invalid_latency_budget", {row["kind"] for row in report["errors"]}
        )
        self.assertEqual(report["status"], "RED")

    def test_installed_hook_absent_from_registry_is_red(self) -> None:
        path = "/fixture/agent/hooks/post/jev-hook.ts"
        report = AUDIT.audit(
            {"surfaces": []},
            [{"path": path, "name": "jev-hook.ts", "loaded_from": path}],
        )
        self.assertIn(
            "installed_surface_unregistered", {row["kind"] for row in report["errors"]}
        )
        self.assertEqual(report["status"], "RED")

    def test_unknown_switch_polarity_is_refused(self) -> None:
        path = "/fixture/agent/hooks/post/jev-hook.ts"
        report = AUDIT.audit(
            registry_for(
                path, off_switch={"path": "state/off", "polarity": "sometimes-OFF"}
            ),
            [{"path": path, "name": "jev-hook.ts", "loaded_from": path}],
        )
        self.assertIn(
            "missing_or_invalid_off_switch", {row["kind"] for row in report["errors"]}
        )
        self.assertEqual(report["status"], "RED")

    def test_configured_external_extension_is_enumerated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            root = home / ".omp/agent"
            root.mkdir(parents=True)
            extension = home / "repo/.omp/extensions/jev-memory-filter.ts"
            extension.parent.mkdir(parents=True)
            extension.write_text("export {};\n", encoding="utf-8")
            (root / "config.yml").write_text(
                f"extensions:\n  - {extension}\n", encoding="utf-8"
            )
            rows = AUDIT.installed(home)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["name"], "jev-memory-filter.ts")
            self.assertEqual(rows[0]["configured_at"], str(root / "config.yml"))


if __name__ == "__main__":
    unittest.main()
