from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "mission-sync.py"
PROTOCOL = ROOT / "work" / "plan-20261004" / "MISSION-PROTOCOL.md"
SCRATCH = ROOT / "var" / "agent-tmp"

ROADMAP = """# Fixture

| # | Pillar | Clause | Check | Today | Owning beads |
|---|---|---|---|---|---|
| 1 | **Live** | Live clause. | `python3 scripts/doctor.py --json`: exits non-zero when the check fails | PARTIAL | `jev-aaaa`, `pillar:live` |
| 2 | **Measured** | Measured clause. | `python3 scripts/ledger.py --gate`: exits non-zero when the receipt is missing | MISSING | `jev-bbbb`, `pillar:measured` |
| 3 | **Portable** | Portable clause. | all green (`gh run list --workflow stranger-run.yml --event schedule --limit 7 --json conclusion --jq 'all(.[]; .conclusion == \"success\")' | grep -qx true`); `classifier ready` exits non-zero when readiness fails | PARTIAL | `jev-cccc`, `pillar:portable` |
"""

MISSION = '''name = "fixture"

[[pillar]]
id = "live"
clause = "stale live clause"
check = "python3 stale.py"
check_fails_when = "live check fails"
status = "partial"
beads = ["jev-aaaa"]

[[pillar]]
id = "measured"
clause = "stale measured clause"
check = "python3 stale.py"
check_fails_when = "measured check fails"
status = "missing"
beads = ["jev-bbbb"]

[[pillar]]
id = "portable"
clause = "stale portable clause"
check = "gh run list"
check_fails_when = "portable check fails"
status = "partial"
beads = ["jev-cccc"]

[cadence]
daily = ["keep this metadata"]
'''


class MissionSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.workspace = Path(
            tempfile.mkdtemp(prefix=f"mission-sync.{os.getpid()}.", dir=SCRATCH)
        )
        (self.workspace / ".owner").write_text(
            f"pid={os.getpid()} label=mission-sync-tests repo={ROOT} "
            f"created={datetime.now(timezone.utc).isoformat()}\n",
            encoding="utf-8",
        )
        (self.workspace / "scripts").mkdir()
        shutil.copy2(SCRIPT, self.workspace / "scripts" / SCRIPT.name)
        (self.workspace / ".omp").mkdir()
        (self.workspace / ".omp" / "mission.toml").write_text(MISSION, encoding="utf-8")
        (self.workspace / "ROADMAP.md").write_text(ROADMAP, encoding="utf-8")
        protocol_path = self.workspace / "work" / "plan-20261004" / "MISSION-PROTOCOL.md"
        protocol_path.parent.mkdir(parents=True)
        shutil.copyfile(PROTOCOL, protocol_path)

    def run_sync(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.workspace / "scripts" / SCRIPT.name), *args],
            cwd=self.workspace,
            capture_output=True,
            check=False,
            text=True,
            timeout=15,
        )

    def test_write_then_check_syncs_source_fields_and_preserves_metadata(self) -> None:
        written = self.run_sync("--write")
        self.assertEqual(written.returncode, 0, written.stderr)
        checked = self.run_sync("--check")
        self.assertEqual(checked.returncode, 0, checked.stderr)

        text = (self.workspace / ".omp" / "mission.toml").read_text(encoding="utf-8")
        self.assertIn('id = "live"\nclause = "Live clause."', text)
        self.assertIn(
            'id = "live"\nclause = "Live clause."\ncheck = "python3 scripts/doctor.py --json"\n'
            'check_fails_when = "live check fails"\nstatus = "partial"\nbeads = ["jev-aaaa"]',
            text,
        )
        self.assertIn(
            r'''check = "gh run list --workflow stranger-run.yml --event schedule --limit 7 --json conclusion --jq 'all(.[]; .conclusion == \"success\")' | grep -qx true && classifier ready"''',
            text,
        )
        self.assertIn('daily = ["keep this metadata"]', text)

    def test_missing_source_bead_fails_with_pillar_and_bead_id(self) -> None:
        written = self.run_sync("--write")
        self.assertEqual(written.returncode, 0, written.stderr)
        path = self.workspace / ".omp" / "mission.toml"
        text = path.read_text(encoding="utf-8")
        self.assertIn('beads = ["jev-aaaa"]', text)
        path.write_text(text.replace('beads = ["jev-aaaa"]', "beads = []", 1), encoding="utf-8")

        result = self.run_sync("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("live", result.stderr)
        self.assertIn("jev-aaaa", result.stderr)

    def test_clause_drift_fails_with_pillar(self) -> None:
        written = self.run_sync("--write")
        self.assertEqual(written.returncode, 0, written.stderr)
        path = self.workspace / ".omp" / "mission.toml"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace('clause = "Live clause."', 'clause = "edited"', 1), encoding="utf-8")

        result = self.run_sync("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("live", result.stderr)
        self.assertIn("clause", result.stderr)

    def test_prose_check_fails(self) -> None:
        written = self.run_sync("--write")
        self.assertEqual(written.returncode, 0, written.stderr)
        path = self.workspace / ".omp" / "mission.toml"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(
                'check = "python3 scripts/doctor.py --json"',
                'check = "value ledger receipt per surface"',
                1,
            ),
            encoding="utf-8",
        )

        result = self.run_sync("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("live", result.stderr)

    def test_bare_path_check_fails(self) -> None:
        written = self.run_sync("--write")
        self.assertEqual(written.returncode, 0, written.stderr)
        path = self.workspace / ".omp" / "mission.toml"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(
                'check = "python3 scripts/doctor.py --json"',
                'check = ".github/workflows/stranger-run.yml"',
                1,
            ),
            encoding="utf-8",
        )

        result = self.run_sync("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("live", result.stderr)

    def test_route_without_failure_condition_is_rejected(self) -> None:
        roadmap_path = self.workspace / "ROADMAP.md"
        roadmap_path.write_text(
            ROADMAP.replace(
                "`python3 scripts/doctor.py --json`: exits non-zero when the check fails",
                "`classifier route --mode auto`",
                1,
            ),
            encoding="utf-8",
        )

        result = self.run_sync("--write")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("failure condition", result.stderr)

    def test_protocol_byte_change_fails_sha256_check(self) -> None:
        protocol_path = self.workspace / "work" / "plan-20261004" / "MISSION-PROTOCOL.md"
        protocol_path.write_bytes(protocol_path.read_bytes() + b"x")

        result = self.run_sync("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sha256", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
