from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "mission-sync.py"
PROTOCOL = ROOT / "work" / "plan-20261004" / "MISSION-PROTOCOL.md"
SCRATCH = ROOT / "var" / "agent-tmp"

LIVE_CHECK_CELL = "`python3 scripts/doctor.py --json`: exits non-zero when the check fails"

# Row 3 keeps the shape of the real Portable row: a bare workflow path in a code span next to
# the commands, a `|` inside a code span, and the failure condition after the commands.
ROADMAP = """# Fixture

| # | Pillar | Clause | Check | Today | Owning beads |
|---|---|---|---|---|---|
| 1 | **Live** | Live clause. | `python3 scripts/doctor.py --json`: exits non-zero when the check fails | PARTIAL | `jev-aaaa`, `jev-a2b`, `pillar:live` |
| 2 | **Measured** | Measured clause. | `python3 scripts/ledger.py --gate`: exits non-zero when the receipt is missing | MISSING | `jev-bbbb`, `pillar:measured` |
| 3 | **Portable** | Portable clause. | the last 7 `schedule` runs of `.github/workflows/stranger-run.yml` all green (`gh run list --workflow stranger-run.yml --event schedule --limit 7 --json conclusion --jq 'all(.[]; .conclusion == "success")' | grep -qx true`; manual reruns counted separately); `classifier ready`: exits non-zero when readiness fails | PARTIAL | `jev-cccc`, `pillar:portable` |
"""

MISSION = '''name = "fixture"

[[pillar]]
id = "live"
clause = "stale live clause"
check = "python3 stale.py"
check_fails_when = "live check fails"
status = "partial"
beads = ["jev-aaaa", "jev-zzzz"]

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

PORTABLE_CHECK = (
    "gh run list --workflow stranger-run.yml --event schedule --limit 7 --json conclusion "
    "--jq 'all(.[]; .conclusion == \"success\")' | grep -qx true && classifier ready"
)


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
        self.mission = self.workspace / ".omp" / "mission.toml"
        self.mission.write_text(MISSION, encoding="utf-8")
        self.roadmap = self.workspace / "ROADMAP.md"
        self.roadmap.write_text(ROADMAP, encoding="utf-8")
        self.protocol = self.workspace / "work" / "plan-20261004" / "MISSION-PROTOCOL.md"
        self.protocol.parent.mkdir(parents=True)
        shutil.copyfile(PROTOCOL, self.protocol)

    def run_sync(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.workspace / "scripts" / SCRIPT.name), *args],
            cwd=self.workspace,
            capture_output=True,
            check=False,
            text=True,
            timeout=15,
        )

    def synced_mission(self) -> str:
        written = self.run_sync("--write")
        self.assertEqual(written.returncode, 0, written.stderr)
        checked = self.run_sync("--check")
        self.assertEqual(checked.returncode, 0, checked.stderr)
        return self.mission.read_text(encoding="utf-8")

    def edit_mission(self, old: str, new: str) -> None:
        text = self.mission.read_text(encoding="utf-8")
        self.assertIn(old, text)
        self.mission.write_text(text.replace(old, new, 1), encoding="utf-8")

    def edit_roadmap(self, old: str, new: str) -> None:
        text = self.roadmap.read_text(encoding="utf-8")
        self.assertIn(old, text)
        self.roadmap.write_text(text.replace(old, new, 1), encoding="utf-8")

    def assert_refused(self, result: subprocess.CompletedProcess[str], *fragments: str) -> None:
        self.assertNotEqual(result.returncode, 0, result.stdout)
        for fragment in fragments:
            self.assertIn(fragment, result.stderr)

    def test_write_then_check_regenerates_source_fields_and_preserves_metadata(self) -> None:
        text = self.synced_mission()

        self.assertIn(
            'id = "live"\nclause = "Live clause."\ncheck = "python3 scripts/doctor.py --json"\n'
            'check_fails_when = "live check fails"\nstatus = "partial"\n'
            'beads = ["jev-aaaa", "jev-a2b"]',
            text,
        )
        self.assertIn(f"check = {_toml_string(PORTABLE_CHECK)}", text)
        self.assertNotIn(".github/workflows", text)
        self.assertIn('daily = ["keep this metadata"]', text)

        self.assertIsNotNone(tomllib, "need Python >= 3.11 (tomllib) or tomli to parse the output")
        parsed = tomllib.loads(text)
        self.assertEqual([row["id"] for row in parsed["pillar"]], ["live", "measured", "portable"])
        self.assertEqual(parsed["pillar"][0]["beads"], ["jev-aaaa", "jev-a2b"])
        self.assertEqual(parsed["pillar"][2]["check"], PORTABLE_CHECK)
        self.assertEqual(parsed["pillar"][1]["status"], "missing")
        self.assertEqual(parsed["cadence"]["daily"], ["keep this metadata"])

    def test_write_is_idempotent_and_check_never_writes(self) -> None:
        before = self.synced_mission().encode()

        again = self.run_sync("--write")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn("already matches", again.stdout)
        self.assertEqual(self.mission.read_bytes(), before)

        self.edit_mission("Live clause.", "edited")
        drifted = self.mission.read_bytes()
        self.assert_refused(self.run_sync("--check"), "pillar 'live'")
        self.assertEqual(self.mission.read_bytes(), drifted)

    def test_removed_or_reordered_bead_fails_naming_pillar_and_bead(self) -> None:
        synced = self.synced_mission()
        base = 'beads = ["jev-aaaa", "jev-a2b"]'
        cases = {
            'beads = ["jev-aaaa"]': ("pillar 'live'", "missing=['jev-a2b']", "extra=[]"),
            'beads = ["jev-aaaa", "jev-a2b", "jev-zzzz"]': ("pillar 'live'", "missing=[]", "extra=['jev-zzzz']"),
            'beads = ["jev-a2b", "jev-aaaa"]': ("pillar 'live'", "only in order"),
            "beads = []": ("pillar 'live'", "missing=['jev-aaaa', 'jev-a2b']"),
        }
        for replacement, fragments in cases.items():
            with self.subTest(replacement=replacement):
                self.mission.write_text(synced, encoding="utf-8")
                self.edit_mission(base, replacement)
                self.assert_refused(self.run_sync("--check"), *fragments)

    def test_clause_edit_in_either_file_fails_roadmap_wins(self) -> None:
        self.synced_mission()

        self.edit_mission('clause = "Live clause."', 'clause = "edited"')
        self.assert_refused(self.run_sync("--check"), "pillar 'live': clause differs from ROADMAP.md")
        self.assertEqual(self.run_sync("--write").returncode, 0)
        self.assertEqual(self.run_sync("--check").returncode, 0)

        self.edit_roadmap("Live clause.", "Live clause, tightened.")
        self.assert_refused(self.run_sync("--check"), "pillar 'live': clause differs from ROADMAP.md")
        self.assertEqual(self.run_sync("--write").returncode, 0)
        self.assertIn('clause = "Live clause, tightened."', self.mission.read_text(encoding="utf-8"))

    def test_check_drifting_to_a_valid_command_fails_as_drift_only(self) -> None:
        self.synced_mission()
        self.edit_mission(
            'check = "python3 scripts/doctor.py --json"',
            'check = "python3 scripts/other.py --json"',
        )

        result = self.run_sync("--check")
        self.assert_refused(result, "pillar 'live': check differs from ROADMAP.md")
        self.assertNotIn("exit-coded", result.stderr)
        self.assertNotIn("separator", result.stderr)

    def test_mission_check_that_is_not_exit_coded_fails_with_the_reason(self) -> None:
        synced = self.synced_mission()
        good = 'check = "python3 scripts/doctor.py --json"'
        cases = {
            "value ledger receipt per surface": "not an exit-coded command",
            ".github/workflows/stranger-run.yml": "not an exit-coded command",
            "echo ok && python3 scripts/doctor.py --json": "not an exit-coded command",
            "python3": "not an exit-coded command",
            "python3 scripts/doctor.py --json &&": "not an exit-coded command",
            "python3 scripts/doctor.py --json && echo ok": "not an exit-coded command",
            "python3 scripts/doctor.py --json || true": "non-failing shell separator",
            "python3 scripts/doctor.py --json; echo ok": "non-failing shell separator",
            "python3 scripts/doctor.py --json &": "non-failing shell separator",
        }
        for bad, reason in cases.items():
            with self.subTest(check=bad):
                self.mission.write_text(synced, encoding="utf-8")
                self.edit_mission(good, f"check = {_toml_string(bad)}")
                self.assert_refused(self.run_sync("--check"), "pillar 'live'", reason)

    def test_roadmap_check_that_is_not_exit_coded_is_rejected_in_both_modes(self) -> None:
        synced = self.synced_mission().encode()
        cases = {
            "value ledger receipt per surface: exits non-zero when it is empty":
                "no supported exit-coded command",
            "`.github/workflows/stranger-run.yml`: exits non-zero when the run failed":
                "no supported exit-coded command",
            "`value ledger receipt per surface`: exits non-zero when it is empty":
                "no supported exit-coded command",
            "`classifier route --mode auto`": "explicit failure condition",
            "`python3 scripts/doctor.py --json; echo ok`: exits non-zero when it fails":
                "non-failing shell separator",
            "`python3 scripts/doctor.py --json && echo ok`: exits non-zero when it fails":
                "not an exit-coded command",
        }
        for cell, reason in cases.items():
            with self.subTest(cell=cell):
                self.roadmap.write_text(ROADMAP, encoding="utf-8")
                self.edit_roadmap(LIVE_CHECK_CELL, cell)
                for mode in ("--check", "--write"):
                    self.assert_refused(self.run_sync(mode), "pillar 'live'", reason)
                    self.assertEqual(self.mission.read_bytes(), synced)

    def test_protocol_that_is_changed_or_missing_fails_both_modes(self) -> None:
        synced = self.synced_mission().encode()
        original = self.protocol.read_bytes()
        flipped = bytes([original[0] ^ 0x01]) + original[1:]
        cases = {
            "appended byte": (original + b"x", "SHA256 mismatch"),
            "flipped byte": (flipped, "SHA256 mismatch"),
            "truncated": (original[:-1], "SHA256 mismatch"),
            "emptied": (b"", "SHA256 mismatch"),
        }
        for name, (content, reason) in cases.items():
            with self.subTest(change=name):
                self.protocol.write_bytes(content)
                for mode in ("--check", "--write"):
                    self.assert_refused(self.run_sync(mode), reason)
                    self.assertEqual(self.mission.read_bytes(), synced)
        with self.subTest(change="missing file"):
            self.protocol.unlink()
            for mode in ("--check", "--write"):
                self.assert_refused(self.run_sync(mode), "cannot read pinned protocol file")
                self.assertEqual(self.mission.read_bytes(), synced)
        self.protocol.write_bytes(original)
        self.assertEqual(self.run_sync("--check").returncode, 0)

    def test_pillar_missing_from_mission_fails_and_write_refuses_to_invent_it(self) -> None:
        self.synced_mission()
        text = self.mission.read_text(encoding="utf-8")
        start = text.index('[[pillar]]\nid = "portable"')
        end = text.index("[cadence]")
        self.mission.write_text(text[:start] + text[end:], encoding="utf-8")
        trimmed = self.mission.read_bytes()

        for mode in ("--check", "--write"):
            self.assert_refused(self.run_sync(mode), "missing mission rows=['portable']")
            self.assertEqual(self.mission.read_bytes(), trimmed)


def _toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


if __name__ == "__main__":
    unittest.main()
