#!/usr/bin/env python3
"""Keyless contract tests for isolated MiniWoB v3 option construction."""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import unittest
from unittest import mock
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))


def _ensure_miniwob_deps():
    try:
        import gymnasium  # noqa: F401
        import miniwob  # noqa: F401
    except ModuleNotFoundError:
        candidate = Path(
            os.environ.get("MINIWOB_TEST_VENV", "/tmp/jev-miniwob-jev/venv/bin/python")
        )
        if candidate.exists() and Path(sys.executable).resolve() != candidate.resolve():
            os.execv(str(candidate), [str(candidate), *sys.argv])
        print("SKIP (missing prerequisite: gymnasium)")
        raise SystemExit(8)


_ensure_miniwob_deps()


class V3OptionsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import gymnasium  # noqa: F401
            import miniwob  # noqa: F401
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest(
                f"SKIP (missing MiniWoB dependency: {exc.name})"
            ) from exc

    def probe(self, arm: str, payload: dict) -> dict:
        code = """
import json, os, sys
sys.path.insert(0, r'{here}')
if {arm!r}:
    os.environ['MINIWOB_V3'] = '1'
    os.environ['MINIWOB_V3_ARM'] = {arm!r}
else:
    os.environ.pop('MINIWOB_V3', None)
    os.environ.pop('MINIWOB_V3_ARM', None)
source = os.environ.get("MINIWOB_ARM_SOURCE")
if source:
    ns = {{"__name__": "tested_jev_arm", "__file__": r'{here}/jev_arm.py'}}
    exec(compile(open(source).read(), source, "exec"), ns)
    import types
    jev_arm = types.SimpleNamespace(**ns)
else:
    import jev_arm
payload = json.loads({payload!r})
els = payload['els']
acts, spans, _ = jev_arm.build_candidates(payload['utterance'], els, payload.get('options'), include_none=payload.get('include_none', True))
state = jev_arm.floor.serialize_state(payload['utterance'], els, 0, 10, [], payload.get('options'))
print(json.dumps({{'actions': sorted(acts), 'spans': spans, 'state': state}}, sort_keys=True))
""".format(here=str(HERE), arm=arm, payload=json.dumps(payload))
        env = os.environ.copy()
        env.pop("MINIWOB_V3", None)
        env.pop("MINIWOB_V3_ARM", None)
        out = subprocess.check_output(
            [sys.executable, "-c", code], cwd=ROOT, env=env, text=True
        )
        return json.loads(out)

    def base_state(self) -> dict:
        return {
            "utterance": 'Enter "Quoted." and drag Source to Target.',
            "els": [
                {
                    "ref": 1,
                    "parent": 0,
                    "tag": "input_text",
                    "kind": "INPUT_TEXT",
                    "text": "",
                    "value": "",
                    "id": "field",
                    "classes": "",
                    "left": 1,
                    "top": 1,
                    "width": 20,
                    "height": 10,
                    "focused": False,
                    "is_leaf": True,
                },
                {
                    "ref": 2,
                    "parent": 0,
                    "tag": "div",
                    "kind": "DIV",
                    "text": "Source",
                    "value": "",
                    "id": "source",
                    "classes": "",
                    "left": 10,
                    "top": 10,
                    "width": 20,
                    "height": 20,
                    "color": "red",
                    "focused": False,
                    "is_leaf": True,
                },
                {
                    "ref": 3,
                    "parent": 0,
                    "tag": "div",
                    "kind": "DIV",
                    "text": "Target",
                    "value": "",
                    "id": "target",
                    "classes": "",
                    "left": 60,
                    "top": 60,
                    "width": 20,
                    "height": 20,
                    "color": "blue",
                    "focused": False,
                    "is_leaf": True,
                },
            ],
            "options": {},
        }

    def test_text_input_is_offered_under_every_arm(self):
        payload = self.base_state()
        for arm in ["", "quoted", "date_time", "page_text", "color", "drag", "none"]:
            result = self.probe(arm, payload)
            self.assertTrue(
                any(action.startswith("type [") for action in result["actions"]),
                arm or "v1-default",
            )

    def test_each_arm_changes_only_its_declared_surface(self):
        base = self.base_state()
        quoted = self.probe("quoted", base)
        page = self.probe(
            "page_text",
            {
                **base,
                "els": base["els"] + [{**base["els"][1], "ref": 4, "text": "ONPAGE"}],
            },
        )
        color = self.probe("color", base)
        drag = self.probe("drag", base)
        date = self.probe(
            "date_time",
            {
                "utterance": "Enter 04/15/2018",
                "els": [{**base["els"][0], "kind": "INPUT_DATE", "tag": "input_date"}],
                "options": {},
            },
        )
        none = self.probe("none", {**base, "include_none": False})
        all_quoted = [s for values in quoted["spans"].values() for s in values]
        self.assertIn("Quoted.", all_quoted)
        self.assertTrue(
            any("ONPAGE" in s for values in page["spans"].values() for s in values)
        )
        self.assertIn('"color"', json.dumps(color["state"]))
        self.assertTrue(any(a.startswith("drag [") for a in drag["actions"]))
        self.assertTrue(any(a.startswith("type [") for a in date["actions"]))
        self.assertFalse(any(a.startswith("none:") for a in none["actions"]))

    def test_default_v1_options_match_pinned_dd04baf(self):
        payload = self.base_state()
        current = self.probe("", payload)
        old_source = subprocess.check_output(
            ["git", "show", "dd04baf:work/miniwob-jev/jev_arm.py"], cwd=ROOT, text=True
        )
        namespace = {"__name__": "old_jev_arm", "__file__": str(HERE / "jev_arm.py")}
        exec(compile(old_source, "dd04baf:jev_arm.py", "exec"), namespace)
        acts, spans, _ = namespace["build_candidates"](
            payload["utterance"], payload["els"], payload["options"]
        )
        old = {
            "actions": sorted(acts),
            "spans": spans,
            "state": namespace["floor"].serialize_state(
                payload["utterance"], payload["els"], 0, 10, [], payload["options"]
            ),
        }
        current["spans"] = {str(k): v for k, v in current["spans"].items()}
        old["spans"] = {str(k): v for k, v in old["spans"].items()}
        self.assertEqual(current, old)

    def test_row_writer_adds_provenance_for_fake_jev(self):
        import jev_arm

        payload = self.base_state()
        policy = jev_arm.JevPolicy(
            jev_arm.FakeAsker("greedy"), jev_arm.RunState(), max_steps=1
        )
        policy.act(payload["utterance"], payload["els"], payload["options"])
        row = {"task": "click-button", "seed": 9000, "rep": 0}
        started_utc = "2026-09-25T00:00:00.000000Z"
        code_sha256 = hashlib.sha256(Path(jev_arm.__file__).read_bytes()).hexdigest()
        self.assertEqual(jev_arm.code_sha256_at_run_start(), code_sha256)

        out = io.StringIO()
        jev_arm.write_row(
            out,
            row,
            policy,
            code_sha256=code_sha256,
            started_utc=started_utc,
        )
        written = json.loads(out.getvalue())

        self.assertEqual(written["code_sha256"], code_sha256)
        self.assertEqual(written["started_utc"], started_utc)
        finished = datetime.fromisoformat(
            written["finished_utc"].replace("Z", "+00:00")
        )
        started = datetime.fromisoformat(started_utc.replace("Z", "+00:00"))
        self.assertEqual(finished.tzinfo, timezone.utc)
        self.assertGreaterEqual(finished, started)

    def test_type_starved_fake_jev_stops_at_sanity_threshold(self):
        import jev_arm

        payload = self.base_state()
        reference = (
            HERE / "rows" / "miniwob-jev-v3-contaminated-smoke-quoted-exact.s0.jsonl"
        )
        gate = jev_arm.SanityGate(reference, sanity_after=4)
        policy = jev_arm.JevPolicy(
            jev_arm.FakeAsker("click_only"), jev_arm.RunState(), max_steps=1
        )
        result = None
        for i in range(4):
            policy.act(payload["utterance"], payload["els"], payload["options"])
            result = gate.observe({"decisions": [policy.decisions[-1]]})
            if i < 3:
                self.assertIsNone(result)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["exit_code"], 1)
        self.assertIn("type=type arm=0.000", "\n".join(result["output"]))

        out = io.StringIO()
        jev_arm.write_sanity_stop_row(
            out,
            result,
            code_sha256="test-sha",
            started_utc="2026-09-25T00:00:00.000000Z",
        )
        stop = json.loads(out.getvalue())
        self.assertEqual(stop["row_type"], "arm_sanity_stop")
        self.assertEqual(stop["reason"], "arm_sanity_exit_1")
        self.assertEqual(stop["eligible_rows"], 4)

    def test_restart_after_stop_requires_tracked_continuation_note(self):
        import jev_arm

        out_path = Path("/tmp/jev-ztp9-existing-stop.jsonl")
        out_path.write_text(json.dumps({"row_type": "arm_sanity_stop"}) + "\n")
        restart_error = jev_arm.sanity_restart_error(out_path, None)
        self.assertIsNotNone(restart_error)
        assert restart_error is not None
        self.assertIn("refusing restart", restart_error)
        untracked_error = jev_arm.sanity_restart_error(
            out_path, Path("/tmp/untracked-note.md")
        )
        self.assertIsNotNone(untracked_error)
        assert untracked_error is not None
        self.assertIn("not tracked", untracked_error)
        self.assertIsNone(jev_arm.sanity_restart_error(out_path, HERE / "jev_arm.py"))

    def test_run_plan_refuses_stopped_output_before_restart(self):
        import jev_arm

        out_path = Path("/tmp/jev-ztp9-run-plan-stop.jsonl")
        out_path.write_text(json.dumps({"row_type": "arm_sanity_stop"}) + "\n")
        reference = ROOT / "work/arm-sanity/fixtures/difference-only-reference.jsonl"
        result = jev_arm.run_plan(
            [],
            jev_arm.FakeAsker("click_only"),
            out_path,
            max_steps=1,
            sanity_reference=reference,
            sanity_after=4,
        )
        self.assertEqual(result, 5)

    def test_resumed_gate_counts_prior_rows_before_new_episode(self):
        import jev_arm

        reference = ROOT / "work/arm-sanity/fixtures/difference-only-reference.jsonl"
        prior = [
            {
                "n_options": 2,
                "candidates": ["switch alpha", "move tackle"],
                "chosen": "switch alpha",
            }
            for _ in range(150)
        ]
        gate = jev_arm.SanityGate(reference, sanity_after=200, prior_rows=prior)
        stopped_at = None
        result = None
        for i in range(60):
            result = gate.observe(
                {
                    "n_options": 2,
                    "candidates": ["switch alpha", "move tackle"],
                    "chosen": "switch alpha",
                }
            )
            if result is not None:
                stopped_at = i + 1
                break
        self.assertEqual(stopped_at, 50)
        assert result is not None
        self.assertEqual(result["exit_code"], 1)

    def test_run_plan_seeds_prior_rows_before_new_eligible_decision(self):
        import jev_arm
        import random

        reference = ROOT / "work/arm-sanity/fixtures/difference-only-reference.jsonl"
        out_path = Path("/tmp/jev-ztp9-run-plan-prior.jsonl")
        prior_row = {"decisions": [{"n_action_options": 2, "action": "click [2]"}]}
        out_path.write_text("".join(json.dumps(prior_row) + "\n" for _ in range(150)))

        class FakeEnv:
            def close(self):
                pass

        def fake_run_episode(env, task, seed, rep, policy_name, args, *rest):
            policy = jev_arm.floor.POLICIES[policy_name](random.Random(seed))
            policy.act(
                "Click Submit",
                [
                    jev_arm._el(1, 0, "input_text"),
                    jev_arm._el(2, 0, "button", text="Submit"),
                ],
                {},
            )
            return {
                "task": task,
                "seed": seed,
                "rep": rep,
                "success": 0.0,
                "raw_reward": 0.0,
                "steps": 1,
                "wall_s": 0.01,
                "reset_s": 0.0,
                "error": "",
            }

        old_policies = jev_arm.floor.POLICIES.copy()
        try:
            with (
                mock.patch.object(
                    jev_arm.floor, "load_task_list", return_value=["gate"]
                ),
                mock.patch.object(
                    jev_arm.floor,
                    "benchmark_seeds",
                    return_value={"gate": list(range(60))},
                ),
                mock.patch.object(
                    jev_arm.floor, "js_seed_for", side_effect=lambda seed: seed
                ),
                mock.patch.object(jev_arm.floor, "make_env", return_value=FakeEnv()),
                mock.patch.object(
                    jev_arm.floor, "run_episode", side_effect=fake_run_episode
                ),
            ):
                result = jev_arm.run_plan(
                    [("gate", seed, 0) for seed in range(60)],
                    jev_arm.FakeAsker("click_only"),
                    out_path,
                    max_steps=1,
                    sanity_reference=reference,
                    sanity_after=200,
                )
        finally:
            jev_arm.floor.POLICIES.clear()
            jev_arm.floor.POLICIES.update(old_policies)

        self.assertEqual(result, 5)
        rows = [json.loads(line) for line in out_path.read_text().splitlines()]
        self.assertEqual(
            sum(row.get("row_type") != "arm_sanity_stop" for row in rows), 200
        )
        self.assertEqual(rows[-1]["row_type"], "arm_sanity_stop")

    def test_comma_arm_list_enables_only_named_v3_arms(self):
        code = """
import importlib.util, json, os, sys
sys.path.insert(0, "work/miniwob-jev")
os.environ["MINIWOB_V3"] = "1"
os.environ["MINIWOB_V3_ARM"] = "quoted,none"
import jev_arm
spec = importlib.util.spec_from_file_location("floor", "work/game-floors/miniwob/run.py")
floor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(floor)
print(json.dumps({
    "jev_quoted": jev_arm.v3_on("quoted"),
    "jev_none": jev_arm.v3_on("none"),
    "jev_color": jev_arm.v3_on("color"),
    "floor_quoted": floor.v3_on("quoted"),
    "floor_none": floor.v3_on("none"),
    "floor_color": floor.v3_on("color"),
}))
"""
        result = subprocess.run(
            ["/tmp/jev-miniwob-jev/venv/bin/python", "-c", code],
            cwd=HERE.parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            json.loads(result.stdout.splitlines()[-1]),
            {
                "jev_quoted": True,
                "jev_none": True,
                "jev_color": False,
                "floor_quoted": True,
                "floor_none": True,
                "floor_color": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
