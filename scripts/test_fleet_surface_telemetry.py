"""Profile eligibility regressions using isolated session files, not live proof."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from dataclasses import replace

import fleet_surface_heartbeat as heartbeat
import fleet_surface_telemetry as telemetry

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "work/blast-radius/surfaces.json"


class ProfileEligibility(unittest.TestCase):
    def setUp(self) -> None:
        scratch = Path(os.environ.get("TMPDIR", REPO / "var/agent-tmp"))
        if not scratch.resolve().is_relative_to(REPO / "var/agent-tmp"):
            raise RuntimeError("test TMPDIR must be repo-owned scratch")
        scratch.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="profile-telemetry-", dir=scratch))
        (self.root / ".owner").write_text(
            f"pid={os.getpid()}\nlabel=profile-telemetry-test\nrepo={REPO}\n",
            encoding="utf-8",
        )
        # Reaper-owned; no TemporaryDirectory or cleanup deletion.
        self.omp = self.root / "omp"
        self.current = 1_790_000_000 // telemetry.HOUR * telemetry.HOUR
        self.end = self.current + telemetry.HOUR
        self.start = self.current - telemetry.HISTORY_SECONDS
        self.surfaces = {s.id: s for s in telemetry.load_registry(REGISTRY)}
        self.lab = self.surfaces["jev-lab-review"]
        self.guard = self.surfaces["guard-rule"]

    def session(self, profile: str, rows: list[dict], name: str = "session") -> Path:
        agent = self.omp / "agent" if profile == "default" else self.omp / "profiles" / profile / "agent"
        path = agent / "sessions" / "-Developer-other" / f"{name}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return path

    def call(self, stamp: float, tool: str = "bash") -> dict:
        return {"type": "custom", "timestamp": stamp, "customType": "tool_execution_start", "data": {"toolName": tool, "toolCallId": "call-1"}}

    def decision(self, stamp: float, surface=None, **data) -> dict:
        surface = surface or self.lab
        return {"type": "custom", "timestamp": stamp, "customType": surface.custom_types[0], "data": {"status": "observed", "error": False, **data}}

    def scan(self, surfaces=None):
        surfaces = surfaces or [self.lab, self.guard]
        return telemetry.scan_omp_sessions(self.omp, self.start, self.end, {t for s in surfaces for t in s.custom_types}, surfaces)

    def assess(self, events, rows, surface=None):
        return telemetry.assess_surface(surface or self.lab, events, rows, self.start, self.current, self.end)

    def test_registry_declares_exact_installed_profiles(self) -> None:
        five = frozenset({"default", "claude", "codex", "grok", "muse"})
        self.assertEqual(self.guard.eligible_profiles, five | {"jev-lab", "glm"})
        for name in ("memory-filter", "webscreen-global"):
            self.assertEqual(self.surfaces[name].eligible_profiles, five)
        for name in ("jev-lab-route", "jev-lab-review", "jev-lab-preaction", "jev-lab-observer"):
            self.assertEqual(self.surfaces[name].eligible_profiles, frozenset({"jev-lab"}))
        self.assertEqual(self.lab.switch_polarity, "presence-OFF")
        self.assertEqual(self.surfaces["harm-rule"].source, "none")

    def test_eligible_events_and_decisions_stay_distinct(self) -> None:
        stamp = self.current + 60
        self.session("jev-lab", [self.call(stamp), self.call(stamp + 1), self.call(stamp + 2, "read"), self.decision(stamp), self.decision(stamp + 3, error=True)])
        events, rows, available = self.scan()
        self.assertTrue(available)
        self.assertIsInstance(events[self.lab.id], list)
        self.assertEqual(events[self.lab.id], [stamp, stamp + 1])
        self.assertEqual(len(events["tool_call"]), 3)
        self.assertEqual(rows[self.lab.custom_types[0]].counts(self.current, self.end), (2, 1))

    def test_out_of_profile_identical_rows_cannot_assess_lab_silent(self) -> None:
        stamp = self.current + 60
        self.session("codex", [self.call(stamp), self.decision(stamp, error=True)])
        events, rows, _ = self.scan()
        self.assertEqual(events[self.lab.id], [])
        self.assertEqual(rows[self.lab.custom_types[0]].counts(self.current, self.end), (0, 0))
        self.assertEqual(events[self.guard.id], [stamp])
        result = self.assess(events[self.lab.id], rows[self.lab.custom_types[0]])
        self.assertEqual(result.state, "unknown")
        self.assertFalse(result.unhealthy)
        self.assertIsNone(result.interval)

    def test_uncovered_profile_slot_is_unknown_not_idle(self) -> None:
        (self.omp / "profiles/jev-lab/agent/sessions").mkdir(parents=True)
        self.session("codex", [self.call(self.current + 10)])
        events, rows, _ = self.scan()
        self.assertEqual(self.assess(events[self.lab.id], rows[self.lab.custom_types[0]]).state, "unknown")

    def test_covered_profile_with_no_eligible_traffic_is_idle(self) -> None:
        self.session("jev-lab", [{"type": "session", "cwd": str(REPO)}, self.call(self.current + 10, "read")])
        events, rows, _ = self.scan()
        result = self.assess(events[self.lab.id], rows[self.lab.custom_types[0]])
        self.assertEqual(result.state, "idle")
        self.assertFalse(result.unhealthy)

    def test_file_profile_wins_over_header_title_and_decision_hints(self) -> None:
        stamp = self.current + 60
        self.session("codex", [{"type": "session", "profile": "jev-lab", "title": "jev-lab", "cwd": str(REPO)}, self.call(stamp), self.decision(stamp, profile="jev-lab")], "jev-lab-neighbour")
        self.session("jev-lab", [{"type": "session", "profile": "codex", "title": "codex", "cwd": str(REPO)}, self.call(stamp + 1), self.decision(stamp + 1, profile="codex")])
        events, rows, _ = self.scan()
        self.assertEqual(events[self.lab.id], [stamp + 1])
        self.assertEqual([r.timestamp for r in rows[self.lab.custom_types[0]].observations], [stamp + 1])

    def test_guard_counts_only_seven_installed_profile_slots(self) -> None:
        profiles = ["default", "claude", "codex", "grok", "muse", "jev-lab", "glm"] + [f"uninstalled-{n}" for n in range(13)]
        for profile in profiles:
            self.session(profile, [self.call(self.current + 10), self.decision(self.current + 10, self.guard)])
        events, rows, _ = self.scan()
        self.assertEqual(len(events["tool_call"]), 20)
        self.assertEqual(len(events[self.guard.id]), 7)
        self.assertEqual(rows[self.guard.custom_types[0]].counts(self.current, self.end), (7, 0))
        self.assertEqual(len(events[self.lab.id]), 1)

    def test_positive_baseline_ignores_out_of_profile_errors_and_volume(self) -> None:
        rows = []
        for hour in range(27):
            stamp = self.start + hour * telemetry.HOUR + 60
            rows.extend([self.call(stamp), self.decision(stamp)])
        stamp = self.current + 60
        rows.extend([self.call(stamp), self.decision(stamp)])
        self.session("jev-lab", rows)
        self.session("codex", [self.call(stamp)] * 30 + [self.decision(stamp, error=True)] * 30)
        events, custom, _ = self.scan()
        result = self.assess(events[self.lab.id], custom[self.lab.custom_types[0]])
        self.assertEqual((result.host_events, result.rows, result.errors, result.rate), (1, 1, 0, 1.0))
        self.assertEqual(result.state, "healthy")

    def test_out_of_profile_traffic_cannot_make_valid_lab_baseline_silent(self) -> None:
        history = []
        for hour in range(27):
            stamp = self.start + hour * telemetry.HOUR + 60
            history.extend([self.call(stamp), self.decision(stamp)])
        self.session("jev-lab", history)
        self.session("codex", [self.call(self.current + 60)] * 30)
        events, rows, _ = self.scan()
        result = self.assess(events[self.lab.id], rows[self.lab.custom_types[0]])
        self.assertIsNotNone(result.interval)
        self.assertEqual((result.host_events, result.rows, result.state), (0, 0, "idle"))
        self.assertFalse(result.unhealthy)

    def test_actual_in_profile_silence_remains_detectable(self) -> None:
        rows = []
        for hour in range(27):
            stamp = self.start + hour * telemetry.HOUR + 60
            rows.extend([self.call(stamp), self.decision(stamp)])
        rows.append(self.call(self.current + 60))
        self.session("jev-lab", rows)
        events, custom, _ = self.scan()
        result = self.assess(events[self.lab.id], custom[self.lab.custom_types[0]])
        self.assertEqual(result.state, "silent")
        self.assertTrue(result.unhealthy)

    def test_malformed_scope_refuses_instead_of_becoming_universal(self) -> None:
        original = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for scope in ([], "jev-lab", None, ["*"], ["../jev-lab"], [""], [7], ["jev-lab", "jev-lab"], ["jev-lab "]):
            with self.subTest(scope=scope):
                entry = next(e for e in original["surfaces"] if e["id"] == self.lab.id)
                entry["heartbeat"]["eligible_profiles"] = scope
                path = self.root / "registry.json"
                path.write_text(json.dumps(original), encoding="utf-8")
                with self.assertRaisesRegex(telemetry.HeartbeatError, "eligible_profiles"):
                    telemetry.load_registry(path)

    def test_missing_scope_is_unmeasured_even_with_positive_rows(self) -> None:
        surface = replace(self.lab, eligible_profiles=None)
        result = self.assess([self.current + 10], telemetry.Telemetry(observations=[telemetry.Observation(self.current + 10, False)]), surface)
        self.assertEqual(result.state, "unknown")
        self.assertFalse(result.unhealthy)
        self.assertIsNone(result.rate)

    def test_webscreen_keeps_tool_cwd_error_and_pause_semantics(self) -> None:
        surface = self.surfaces["webscreen-global"]
        stamp = self.current + 10
        def result(tool, **extra):
            return {"type": "message", "timestamp": stamp, "message": {"role": "toolResult", "toolName": tool, **extra}}
        self.session("claude", [{"type": "session", "cwd": "/Users/josh/Developer/other"}, result("web_extract"), result("eval"), result("web_search", isError=True)])
        self.session("codex", [{"type": "session", "cwd": str(REPO)}, result("web_search")])
        self.session("glm", [{"type": "session", "cwd": "/Users/josh/Developer/other"}, result("web_search")])
        events, _, _ = self.scan([surface])
        self.assertEqual(events[surface.id], [stamp])
        log = self.root / "webscreen.jsonl"
        log.write_text(json.dumps({"ts": stamp, "status": "local-only"}) + "\n", encoding="utf-8")
        self.assertEqual(self.assess(events[surface.id], telemetry.read_jsonl(log, surface, self.start, self.end), surface).state, "paused")

    def test_route_counts_only_in_profile_user_turns(self) -> None:
        surface = self.surfaces["jev-lab-route"]
        stamp = self.current + 10
        turn = {"type": "message", "timestamp": stamp, "message": {"role": "user", "content": [{"type": "text", "text": "probe"}]}}
        self.session("jev-lab", [turn, self.decision(stamp, surface)])
        self.session("default", [turn, self.decision(stamp, surface)])
        events, rows, _ = self.scan([surface])
        self.assertEqual(events[surface.id], [stamp])
        self.assertEqual(len(events["turn"]), 2)
        self.assertEqual(rows[surface.custom_types[0]].counts(self.current, self.end), (1, 0))

    def test_missing_registry_scope_does_not_fall_back_to_all_profiles(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        entry = next(e for e in registry["surfaces"] if e["id"] == self.lab.id)
        entry["heartbeat"].pop("eligible_profiles", None)
        path = self.root / "missing-scope.json"
        path.write_text(json.dumps({"schema_version": registry["schema_version"], "surfaces": [entry]}), encoding="utf-8")
        surface = telemetry.load_registry(path)[0]
        self.session("jev-lab", [self.call(self.current + 10), self.decision(self.current + 10)])
        events, rows, _ = self.scan([surface])
        self.assertEqual(events[surface.id], [])
        self.assertEqual(rows[surface.custom_types[0]].counts(self.current, self.end), (0, 0))
        self.assertEqual(self.assess(events[surface.id], rows[surface.custom_types[0]], surface).state, "unknown")

    def test_monitor_out_of_profile_does_not_auto_off_or_enable_markers(self) -> None:
        stamp = self.current + 10
        self.session("codex", [self.call(stamp), self.decision(stamp, error=True)])
        original = json.loads(REGISTRY.read_text(encoding="utf-8"))
        entry = next(e for e in original["surfaces"] if e["id"] == self.lab.id)
        marker = self.root / "lab.off"
        entry["off_switch"]["path"] = str(marker)
        registry = self.root / "registry.json"
        registry.write_text(json.dumps({"schema_version": original["schema_version"], "surfaces": [entry]}), encoding="utf-8")
        messages = []
        def send(message: str) -> bool:
            messages.append(message)
            return True
        result = heartbeat.monitor(registry, self.root / "state", now=self.end + 1, omp_root=self.omp, send=send)
        self.assertEqual(result[0].state, "unknown")
        self.assertFalse(marker.exists())
        marker.write_text("intentional OFF\n", encoding="utf-8")
        heartbeat.monitor(registry, self.root / "state", now=self.end + 1, omp_root=self.omp, send=send)
        self.assertEqual(marker.read_text(encoding="utf-8"), "intentional OFF\n")
        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()
