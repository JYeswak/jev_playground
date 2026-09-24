"""Keyless, no network: the comparator runner sends each unit's exact inputs and refuses other models.

Run: upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python -m unittest \
       work/openrouter-incumbents/test_run.py
"""

import json
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run

WORK = os.path.dirname(HERE)
SIZES = {"sst5": 500, "banking77": 400, "clinc150": 750, "scifact": 400, "fever": 400}
SAMPLES = {
    "sst5": "score-sst5/sample.jsonl",
    "banking77": "choice-banking77/subset.jsonl",
    "clinc150": "choice-clinc150/subset.jsonl",
    "scifact": "noul-scifact/sample.jsonl",
    "fever": "noul-fever/sample.jsonl",
}


def rows(rel):
    with open(os.path.join(WORK, rel), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


class Inputs(unittest.TestCase):
    def test_rows_are_the_units_rows(self):
        for dataset, n in SIZES.items():
            sample, questions, state, _ = run.setup(dataset)
            self.assertEqual(len(sample), n, dataset)
            self.assertEqual(sample, rows(SAMPLES[dataset]), dataset)
            self.assertEqual(len(questions), 1, dataset)
            state(sample[0])  # builds without error

    def test_fever_question_is_the_scifact_question(self):
        _, q_sci, _state_sci, _ = run.setup("scifact")
        _, q_fev, _state_fev, _ = run.setup("fever")
        self.assertEqual(
            [q.model_dump() for q in q_sci.values()],
            [q.model_dump() for q in q_fev.values()],
        )


class Stsb(unittest.TestCase):
    def test_question_is_the_pinned_runners(self):
        source = run.SI.git_show(*run.STSB_PIN)
        self.assertIn(f'instructions="{run.STSB_INSTRUCTIONS}"', source)
        runner = run.SI.pinned_module("stsb_runner_test", *run.STSB_PIN)
        self.assertEqual(len(runner.QUESTION_CRITERIA), 6)


class Models(unittest.TestCase):
    def test_refuses_unapproved_paid_model(self):
        env = {"OPENROUTER_API_KEY": "x"}
        with mock.patch.dict(os.environ, env), self.assertRaises(ValueError):
            run.provider_for("openai/gpt-5")

    def test_approved_models_build_on_openrouter(self):
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "x"}):
            for model in run.PAID + ("nex-agi/nex-n2.5-pro:free",):
                p = run.provider_for(model)
                self.assertEqual(p.api, "chat_completions")
                self.assertEqual(str(p._client.base_url).rstrip("/"), run.BASE_URL)

    def test_missing_key_refuses(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            for model in run.PAID + ("nex-agi/nex-n2.5-pro:free",):
                with self.assertRaises(RuntimeError):
                    run.provider_for(model)


if __name__ == "__main__":
    unittest.main()
