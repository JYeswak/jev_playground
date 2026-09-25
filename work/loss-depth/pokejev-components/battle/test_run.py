"""Offline tests for the frozen leaf evaluator arms."""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


def require_prerequisites() -> None:
    missing = []
    if sys.version_info < (3, 12):
        missing.append("Python >= 3.12")
    root = Path(__file__).resolve().parents[4]
    if not (root / "pokechamp" / "pokechamp").is_dir():
        missing.append("pokechamp clone")
    if missing:
        print(f"SKIP (missing prerequisite: {', '.join(missing)})")
        raise SystemExit(8)


require_prerequisites()

sys.path.insert(0, str(Path(__file__).parent))
import run as battle_run  # noqa: E402


class _FakeAsker:
    def __init__(self, result=None, error=None):
        self.calls = []
        self.result = result
        self.error = error

    def __call__(self, state):
        self.calls.append(state)
        if self.error is not None:
            raise self.error
        return self.result


class _HttpError(RuntimeError):
    def __init__(self, status_code):
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


def _model_file(directory: Path) -> tuple[Path, str]:
    payload = {
        "format": "leaf-model-v1",
        "features": ["hp", "pressure"],
        "noul_features": ["ko", "danger", "switch"],
        "intercept": 0.0,
        "code_weights": [1.0, 0.5],
        "means": [0.0, 0.0],
        "scales": [1.0, 1.0],
        "noul_intercept": 0.0,
        "noul_code_weights": [1.0, 0.5],
        "noul_weights": [0.2, -0.1, 0.3],
        "noul_means": [0.0, 0.0, 0.0, 0.0, 0.0],
        "noul_scales": [1.0, 1.0, 1.0, 1.0, 1.0],
    }
    path = directory / "leaf-model.json"
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, digest


class FrozenLeafArmTests(unittest.TestCase):
    def test_code_arm_never_calls_jev_in_leaf(self):
        with tempfile.TemporaryDirectory() as temp:
            model_path, digest = _model_file(Path(temp))
            asker = _FakeAsker(result={"ko": 0.9, "danger": 0.1, "switch": 0.2})
            model = battle_run.FrozenLeafModel.from_json(
                model_path, expected_sha256=digest
            )
            arm = battle_run.LeafArm(mode="code", model=model, asker=asker)

            decision = arm.choose(
                {"hp": 0.8, "pressure": 0.4},
                [
                    {"id": "hold", "features": {"hp": 0.8, "pressure": 0.4}},
                    {"id": "switch", "features": {"hp": 0.2, "pressure": 0.1}},
                ],
            )

            self.assertEqual(decision.choice, "hold")
            self.assertEqual(asker.calls, [])

    def test_noul_arm_calls_once_per_leaf(self):
        with tempfile.TemporaryDirectory() as temp:
            model_path, digest = _model_file(Path(temp))
            asker = _FakeAsker(result={"ko": 0.9, "danger": 0.1, "switch": 0.2})
            model = battle_run.FrozenLeafModel.from_json(
                model_path, expected_sha256=digest
            )
            arm = battle_run.LeafArm(mode="code+noul", model=model, asker=asker)

            decision = arm.choose(
                {"hp": 0.8, "pressure": 0.4},
                [
                    {"id": "hold", "features": {"hp": 0.8, "pressure": 0.4}},
                    {"id": "switch", "features": {"hp": 0.2, "pressure": 0.1}},
                ],
            )

            self.assertIn(decision.choice, {"hold", "switch"})
            self.assertEqual(len(asker.calls), 1)

    def test_unauthorized_or_billing_error_stops_noul_arm(self):
        for status_code in (401, 402):
            with (
                self.subTest(status_code=status_code),
                tempfile.TemporaryDirectory() as temp,
            ):
                model_path, digest = _model_file(Path(temp))
                asker = _FakeAsker(error=_HttpError(status_code))
                model = battle_run.FrozenLeafModel.from_json(
                    model_path, expected_sha256=digest
                )
                arm = battle_run.LeafArm(mode="code+noul", model=model, asker=asker)

                with self.assertRaises(battle_run.LeafArmStopped):
                    arm.choose(
                        {"hp": 0.8, "pressure": 0.4},
                        [{"id": "hold", "features": {"hp": 0.8, "pressure": 0.4}}],
                    )
                self.assertTrue(arm.stopped)
                self.assertEqual(len(asker.calls), 1)

    def test_frozen_weights_hash_mismatch_refuses_to_start(self):
        with tempfile.TemporaryDirectory() as temp:
            model_path, _digest = _model_file(Path(temp))
            with self.assertRaisesRegex(ValueError, "sha256"):
                battle_run.FrozenLeafModel.from_json(
                    model_path,
                    expected_sha256="0" * 64,
                )

    def test_two_move_summaries_with_different_opponent_hp_get_different_leaf_scores(
        self,
    ):
        model = battle_run.FrozenLeafModel(
            features=("opponent_hp_remaining",),
            noul_features=(),
            intercept=0.0,
            code_weights=(1.0,),
            means=(0.0,),
            scales=(1.0,),
            noul_intercept=0.0,
            noul_code_weights=(1.0,),
            noul_weights=(),
            noul_means=(0.0,),
            noul_scales=(1.0,),
        )
        base = {
            "hp_weighted_remaining": 0.5,
            "status_count": 0.0,
            "hazard_count": 0.0,
            "speed_order_rate": 0.5,
            "opponent_hp_remaining": 0.5,
            "hp_differential": 0.0,
        }
        high = battle_run.LeafPlayer._summary_features(
            {
                "your_active": "Pikachu 80%",
                "your_bench": [],
                "opponent_active": "Eevee 20%",
                "opponent_bench": [],
            },
            "move Thunderbolt",
            base,
        )
        low = battle_run.LeafPlayer._summary_features(
            {
                "your_active": "Pikachu 80%",
                "your_bench": [],
                "opponent_active": "Eevee 80%",
                "opponent_bench": [],
            },
            "move Thunderbolt",
            base,
        )
        self.assertNotEqual(model.score(high), model.score(low))

    def test_frozen_model_drops_action_type_and_adds_opponent_features(self):
        model = battle_run.FrozenLeafModel.from_json(
            battle_run.LEAF_MODEL_PATH,
            expected_sha256=battle_run.LEAF_MODEL_SHA256,
        )
        self.assertNotIn("ko_threat", model.features)
        self.assertIn("opponent_hp_remaining", model.features)
        self.assertIn("hp_differential", model.features)

    def test_live_features_match_full_team_replay_features_on_three_turns(self):
        from types import SimpleNamespace

        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import leaf_c  # noqa: PLC0415

        replay_dir = Path(__file__).resolve().parents[1] / (
            "replays-abyssal-leaf-code-leaf-c-r2-code"
        )
        checked = 0
        for replay_path in sorted(replay_dir.glob("*.html")):
            snapshots = leaf_c.snapshot_features(replay_path)
            first_turn = snapshots[min(snapshots)]
            if first_turn["speed_order_rate"] != 0.5:
                continue
            species = [
                name for name in str(first_turn["known_species"]).split(",") if name
            ]
            team = {
                name: SimpleNamespace(current_hp_fraction=1.0, status=None)
                for name in species
            }
            opponent_team = {
                name: SimpleNamespace(current_hp_fraction=1.0, status=None)
                for name in species
            }
            battle = SimpleNamespace(
                team=team,
                opponent_team=opponent_team,
                side_conditions={},
            )
            live = battle_run.LeafPlayer._base_features(battle)
            for feature in (
                "hp_weighted_remaining",
                "status_count",
                "hazard_count",
                "speed_order_rate",
                "opponent_hp_remaining",
                "hp_differential",
            ):
                self.assertAlmostEqual(
                    live[feature],
                    float(first_turn[feature]),
                    delta=1e-6,
                    msg=f"{replay_path.name}:{min(snapshots)}:{feature}",
                )
            checked += 1
            if checked == 3:
                break
        self.assertEqual(checked, 3)

    def test_recorded_dev_leaf_switch_rate_is_near_stage_b_sanity_rate(self):
        root = Path(__file__).resolve().parents[1]
        path = root / "decisions-abyssal-leaf-code-v1.jsonl"
        rows = [
            json.loads(line) for line in path.read_text().splitlines() if line.strip()
        ]
        offered = [
            row
            for row in rows
            if any(
                str(candidate).startswith("switch ")
                for candidate in row.get("candidates", [])
            )
        ][:100]
        self.assertEqual(len(offered), 100)
        switch_rate = sum(
            str(row.get("chosen", "")).startswith("switch ") for row in offered
        ) / len(offered)
        self.assertLessEqual(abs(switch_rate - 0.41), 0.10)

    def test_shard_row_records_start_and_finish_timestamps(self):
        async def fake_play(_me, _opp, k, _replays):
            return {"k": k, "won": True}

        with tempfile.TemporaryDirectory() as temp:
            previous_out = battle_run.OUT
            previous_stage_out = battle_run.stage_b.OUT
            previous_make_players = battle_run.stage_b.make_players
            previous_play = battle_run.stage_b.play
            try:
                battle_run.OUT = Path(temp)
                battle_run.stage_b.OUT = temp
                battle_run.stage_b.make_players = lambda *args, **kwargs: (
                    object(),
                    object(),
                )
                battle_run.stage_b.play = fake_play
                result = asyncio.run(
                    battle_run._run_shard("abyssal", 1, 1, 0, True, run_id="unit")
                )
                row_path = Path(temp) / "results-abyssal-mix-v1-control.jsonl"
                row = json.loads(row_path.read_text(encoding="utf-8"))
            finally:
                battle_run.OUT = previous_out
                battle_run.stage_b.OUT = previous_stage_out
                battle_run.stage_b.make_players = previous_make_players
                battle_run.stage_b.play = previous_play

        self.assertEqual(result, 0)
        datetime.fromisoformat(row["row_started_at_utc"])
        self.assertEqual(row["run_id"], "unit")
        datetime.fromisoformat(row["row_recorded_at_utc"])

    def test_jsonl_row_records_wrapper_hash_and_utc_timestamp(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "rows.jsonl"
            battle_run._append_jsonl(path, {"k": 4, "battle": "test", "turn": 2})
            row = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(
            row["run_py_sha256"],
            hashlib.sha256(Path(battle_run.__file__).read_bytes()).hexdigest(),
        )
        self.assertEqual(row["run_py_sha256"], battle_run.RUN_PY_SHA256)
        datetime.fromisoformat(row["run_started_at_utc"])
        datetime.fromisoformat(row["row_recorded_at_utc"])

    def test_leaf_run_id_isolated_from_default_output_tag(self):
        self.assertEqual(
            battle_run._tag(False, "code+noul"),
            "-leaf-code-noul-v1",
        )
        self.assertEqual(
            battle_run._tag(False, "code+noul", "resume-k2"),
            "-leaf-code-noul-resume-k2",
        )


if __name__ == "__main__":
    unittest.main()
