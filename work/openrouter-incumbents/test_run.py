"""Keyless, no network: the comparator runner sends each unit's exact inputs and refuses other models.

Run: upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python -m unittest \
       work/openrouter-incumbents/test_run.py
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run
import score

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


class FreeArmAmendment2(unittest.TestCase):
    """Amendment 2: qualification from run 2's rows, and run 2's paced loop for :free models."""

    def test_comparators_are_run2_qualifiers_in_order_then_paid(self):
        self.assertEqual(
            score.comparators(),
            [
                "dots-studio/dots-3-note-preview:free",
                "nex-agi/nex-n2.5-mini:free",
                "liquid/lfm-2.5-2.6b:free",
                *score.PAID,
            ],
        )

    def test_daily_cap_429_is_quota_and_provider_429_is_not(self):
        self.assertTrue(
            run.is_quota(
                "TypeSafeRateLimitError: 429 Rate limit exceeded: free-models-per-day"
            )
        )
        self.assertFalse(
            run.is_quota("TypeSafeRateLimitError: 429 Provider returned error")
        )

    def run_script(self, script, n_rows=6, max_requests=50, resume=False, path=None):
        """run_free over n_rows fake rows; `script` is what each system_one call does, in order."""
        import httpx
        from typesafe_sdk import TypeSafeRateLimitError

        def limit(message):
            return TypeSafeRateLimitError(429, None, httpx.Headers({}), message)

        actions = [limit(a[1]) if isinstance(a, tuple) else a for a in script]
        path = path or os.path.join(tempfile.mkdtemp(), "rows.jsonl")
        sample = [{"i": i} for i in range(n_rows)]

        class Inner:
            model_name = "x/y:free"

            async def request(self, messages, *, schema, structured):
                return None

            async def aclose(self):
                pass

        class Usage:
            (
                input_tokens_total,
                output_tokens_total,
                n_retries,
                n_retries_malformed_structure,
            ) = 10, 0, 0, 0

        class Client:
            def __init__(self, **kw):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def system_one(self, state, questions, model):
                await model.request(
                    [], schema={}, structured=True
                )  # pacer and require_free
                action = actions.pop(0)
                if isinstance(action, Exception):
                    raise action
                resp = mock.Mock()
                resp.usage = Usage()
                return resp

        with (
            mock.patch.object(
                run,
                "setup",
                return_value=(sample, {}, lambda s: s, lambda s, r: {"score": 3}),
            ),
            mock.patch.object(run, "out_path", return_value=path),
            mock.patch.object(run.SI, "attempt_facts", return_value={}),
            mock.patch.object(run.OR, "openrouter_provider", return_value=Inner()),
            mock.patch.object(run.RS, "PACED_429_DEFAULT_S", 0.0),
            mock.patch("system_one_adapter.AsyncSystemOneAdapterClient", Client),
        ):
            code = asyncio.run(
                run.run_free("x/y:free", "sst5", False, None, max_requests, resume)
            )
        with open(path) as fh:
            rows = [json.loads(line) for line in fh if line.strip()]
        return code, rows, path

    def test_provider_429_is_waited_and_the_row_answers(self):
        code, rows, _ = self.run_script(
            [("r", "Provider returned error"), ("r", "Provider returned error"), "ok"],
            n_rows=1,
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            (rows[0]["score"], rows[0]["rateLimitWaits"], rows[0]["requests"]),
            (3, 2, 3),
        )

    def test_fourth_provider_429_fails_the_row(self):
        code, rows, _ = self.run_script(
            [("r", "Provider returned error")] * 4, n_rows=1
        )
        self.assertEqual(code, 3)
        self.assertIn("429 Provider returned error", rows[0]["error"])
        self.assertEqual(rows[0]["rateLimitWaits"], 3)

    def test_daily_quota_is_recorded_once_and_stops_the_model(self):
        code, rows, path = self.run_script(
            ["ok", ("r", "Rate limit exceeded: free-models-per-day")], n_rows=6
        )
        self.assertEqual(code, 3)
        self.assertEqual(
            [("score" in r, r.get("rateLimitWaits")) for r in rows],
            [(True, 0), (False, 0)],
        )
        self.assertEqual(
            [s["i"] for s in run.free_todo([{"i": i} for i in range(6)], path, False)],
            [1, 2, 3, 4, 5],
        )

    def test_request_cap_writes_no_row_for_the_unsent_request(self):
        code, rows, _ = self.run_script(["ok", "ok", "ok"], n_rows=3, max_requests=2)
        self.assertEqual(code, 3)
        self.assertEqual([r["i"] for r in rows], [0, 1])

    def test_five_failures_of_one_class_stop_and_resume_retries_each_once(self):
        code, rows, path = self.run_script([RuntimeError("boom")] * 5, n_rows=8)
        self.assertEqual((code, len(rows)), (3, 5))
        todo_main = [
            s["i"] for s in run.free_todo([{"i": i} for i in range(8)], path, False)
        ]
        todo_resume = [
            s["i"] for s in run.free_todo([{"i": i} for i in range(8)], path, True)
        ]
        self.assertEqual((todo_main, todo_resume), ([5, 6, 7], [0, 1, 2, 3, 4]))
        self.run_script([RuntimeError("boom")] * 5, n_rows=8, resume=True, path=path)
        self.assertEqual(
            [s["i"] for s in run.free_todo([{"i": i} for i in range(8)], path, True)],
            [],
        )


if __name__ == "__main__":
    unittest.main()
