#!/usr/bin/env python3
"""Keyless contract tests for isolated MiniWoB v3 option construction."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))


class V3OptionsContract(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
