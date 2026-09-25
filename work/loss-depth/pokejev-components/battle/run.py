#!/usr/bin/env python3
"""Run the frozen-alpha battle arm without modifying the committed Stage B tree.

This wrapper imports ``work/poke-jev/stage_b.py`` and its player/policy modules, then
replaces only the action-prior and opponent-model distributions.  It keeps the Stage B
battle, clock, team pairing, and decision machinery as the execution harness while writing
all arm output under this directory.
"""

from __future__ import annotations

import argparse
import asyncio
import contextvars
import hashlib
import hmac
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

BATTLE_DIR = Path(__file__).resolve().parent
COMPONENT_DIR = BATTLE_DIR.parent
ROOT = COMPONENT_DIR.parents[2]

POKE = ROOT / "work" / "poke-jev"
OUT = BATTLE_DIR / "stage-b"
LEAF_OUT = COMPONENT_DIR
ALPHA_PATH = COMPONENT_DIR / "frozen-alpha-v1.json"
LEAF_MODEL_PATH = COMPONENT_DIR / "leaf-model-v1.json"
LEAF_MODEL_SHA256 = "ad8cd16482eb41e409409c94c968d0b2857f736bd6258b9afd556d785273c49b"
RUN_PY_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
RUN_STARTED_AT_UTC = datetime.now(timezone.utc).isoformat()
STOP_PATH = OUT / "mix-v1-stop.json"

# Stage B is an import target, not a copied implementation.  It changes cwd while loading
# PokéChamp, so all paths used by this wrapper are absolute and computed first.
sys.path.insert(0, str(POKE))
import player as player_module  # noqa: E402
import replay  # noqa: E402
import stage_b  # noqa: E402


MODULE_PATHS = {
    name: POKE / name for name in ("stage_b.py", "player.py", "policy.py", "replay.py")
}
MODULE_SHA256 = {
    name: hashlib.sha256(path.read_bytes()).hexdigest()
    for name, path in MODULE_PATHS.items()
}
FROZEN_ALPHA_SHA256 = hashlib.sha256(ALPHA_PATH.read_bytes()).hexdigest()

with ALPHA_PATH.open(encoding="utf-8") as fh:
    ALPHA = json.load(fh)
PLAYER_ALPHA = float(ALPHA["components"]["player"]["alpha"])
OPPONENT_ALPHA = float(ALPHA["components"]["opponent"]["alpha"])
if (PLAYER_ALPHA, OPPONENT_ALPHA) != (0.4, 0.25):
    raise RuntimeError("frozen-alpha-v1.json does not contain the preregistered alphas")


@dataclass(frozen=True)
class FrozenLeafModel:
    """A hash-pinned logistic leaf model loaded from committed JSON."""

    features: tuple[str, ...]
    noul_features: tuple[str, ...]
    intercept: float
    code_weights: tuple[float, ...]
    means: tuple[float, ...]
    scales: tuple[float, ...]
    noul_intercept: float
    noul_code_weights: tuple[float, ...]
    noul_weights: tuple[float, ...]
    noul_means: tuple[float, ...]
    noul_scales: tuple[float, ...]

    @classmethod
    def from_json(cls, path: Path, *, expected_sha256: str) -> FrozenLeafModel:
        actual_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        if not hmac.compare_digest(actual_sha256, expected_sha256):
            raise ValueError(
                f"frozen leaf model sha256 mismatch: expected {expected_sha256}, "
                f"got {actual_sha256}"
            )
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("format") != "leaf-model-v1":
            raise ValueError("unsupported frozen leaf model format")
        features = tuple(str(name) for name in payload["features"])
        noul_features = tuple(str(name) for name in payload["noul_features"])
        code_weights = tuple(float(value) for value in payload["code_weights"])
        noul_weights = tuple(float(value) for value in payload["noul_weights"])
        means = tuple(float(value) for value in payload["means"])
        scales = tuple(float(value) for value in payload["scales"])
        if not features or len(code_weights) != len(features):
            raise ValueError("frozen leaf code feature/weight shape mismatch")
        if len(means) != len(features) or len(scales) != len(features):
            raise ValueError("frozen leaf standardizer shape mismatch")
        noul_intercept = float(payload["noul_intercept"])
        noul_code_weights = tuple(
            float(value) for value in payload["noul_code_weights"]
        )
        noul_means = tuple(float(value) for value in payload["noul_means"])
        noul_scales = tuple(float(value) for value in payload["noul_scales"])
        if len(noul_code_weights) != len(features):
            raise ValueError("frozen leaf Noul code feature/weight shape mismatch")
        if len(noul_means) != len(features) + len(noul_features):
            raise ValueError("frozen leaf Noul standardizer shape mismatch")
        if len(noul_scales) != len(noul_means):
            raise ValueError("frozen leaf Noul scale shape mismatch")
        all_weights = (*code_weights, *noul_code_weights, *noul_weights)
        if any(
            not math.isfinite(value) for value in (*all_weights, *means, *noul_means)
        ):
            raise ValueError("frozen leaf model contains a non-finite weight")
        if any(
            not math.isfinite(value) or value <= 0 for value in (*scales, *noul_scales)
        ):
            raise ValueError("frozen leaf model contains an invalid scale")
        return cls(
            features=features,
            noul_features=noul_features,
            intercept=float(payload["intercept"]),
            code_weights=code_weights,
            means=means,
            scales=scales,
            noul_intercept=noul_intercept,
            noul_code_weights=noul_code_weights,
            noul_weights=noul_weights,
            noul_means=noul_means,
            noul_scales=noul_scales,
        )

    def score(
        self,
        code_values: dict[str, float],
        noul_values: dict[str, float] | None = None,
    ) -> float:
        if noul_values is None:
            intercept = self.intercept
            names = self.features
            weights = self.code_weights
            means = self.means
            scales = self.scales
            values = [code_values[name] for name in names]
        else:
            intercept = self.noul_intercept
            names = (*self.features, *self.noul_features)
            weights = (*self.noul_code_weights, *self.noul_weights)
            means = self.noul_means
            scales = self.noul_scales
            values = [
                *(code_values[name] for name in self.features),
                *(noul_values[name] for name in self.noul_features),
            ]
        return intercept + sum(
            weight * ((float(value) - mean) / scale)
            for value, weight, mean, scale in zip(
                values, weights, means, scales, strict=True
            )
        )


@dataclass(frozen=True)
class LeafDecision:
    choice: str
    used_noul: bool
    fallback_reason: str | None


class LeafArmStopped(RuntimeError):
    """Raised when a paid leaf arm must stop instead of falling back."""


class LeafArm:
    """Choose a leaf action with frozen code features and optional Noul evidence."""

    def __init__(self, *, mode: str, model: FrozenLeafModel, asker):
        if mode not in {"code", "code+noul"}:
            raise ValueError(f"unsupported leaf arm: {mode}")
        self.mode = mode
        self.model = model
        self.asker = asker
        self.stopped = False

    def choose(
        self,
        leaf_state: dict,
        candidates: list[dict],
    ) -> LeafDecision:
        if self.mode != "code+noul":
            return self.choose_with_values(leaf_state, candidates, None)
        try:
            if self.asker is None:
                raise RuntimeError("Noul asker is not configured")
            noul_values = self.asker(leaf_state)
            return self.choose_with_values(leaf_state, candidates, noul_values)
        except LeafArmStopped:
            raise
        except Exception as exc:
            status = getattr(exc, "status_code", getattr(exc, "status", None))
            if status in {401, 402}:
                self.stopped = True
                raise LeafArmStopped(f"leaf Noul arm stopped on HTTP {status}") from exc
            return self.choose_with_values(
                leaf_state,
                candidates,
                None,
                fallback_reason=f"{type(exc).__name__}: {str(exc)[:300]}",
            )

    def choose_with_values(
        self,
        leaf_state: dict,
        candidates: list[dict],
        noul_values: dict[str, float] | None,
        *,
        fallback_reason: str | None = None,
    ) -> LeafDecision:
        del leaf_state
        if not candidates:
            raise ValueError("leaf arm received no candidates")
        if noul_values is not None:
            if set(noul_values) != set(self.model.noul_features):
                raise ValueError("Noul answer keys do not match the frozen model")
            if any(
                not math.isfinite(float(noul_values[name]))
                or not 0.0 <= float(noul_values[name]) <= 1.0
                for name in self.model.noul_features
            ):
                raise ValueError("Noul answer is outside [0, 1]")
        scored = [
            (
                self.model.score(candidate["features"], noul_values),
                index,
                str(candidate["id"]),
            )
            for index, candidate in enumerate(candidates)
        ]
        _, _, choice = max(scored, key=lambda row: (row[0], -row[1]))
        return LeafDecision(
            choice=choice,
            used_noul=noul_values is not None,
            fallback_reason=fallback_reason,
        )


def _calibration_params() -> tuple[float, float]:
    rows = [
        json.loads(line)
        for line in (POKE / "stage-a" / "calib.jsonl").read_text().splitlines()
        if line.strip()
    ]
    switch_rows = [row for row in rows if row["switch_available"]]
    move_rows = [row for row in rows if row["kind"] == "move" and row["tera_available"]]
    return (
        sum(row["kind"] == "switch" for row in switch_rows) / len(switch_rows),
        sum(row["tera"] for row in move_rows) / len(move_rows),
    )


P_SWITCH, P_TERA = _calibration_params()
SETS = json.loads(
    (
        ROOT
        / "pokechamp"
        / "poke_env"
        / "data"
        / "static"
        / "gen9"
        / "ou"
        / "sets_1000.json"
    ).read_text()
)


def _mix(
    jev: dict[str, float], floor: dict[str, float], alpha: float
) -> dict[str, float]:
    """Return alpha * Jev + (1-alpha) * usage floor on the exact asked support."""
    if set(jev) != set(floor):
        raise ValueError("frozen mixture support differs from the legal option set")
    mixed = {key: alpha * jev[key] + (1.0 - alpha) * floor[key] for key in jev}
    total = sum(mixed.values())
    if not math.isfinite(total) or total <= 0:
        raise ValueError("frozen mixture is not a positive finite distribution")
    return {key: value / total for key, value in mixed.items()}


def action_prior_distribution(
    jev: dict[str, float], display: dict[str, str], battle
) -> dict[str, float]:
    """The sole action-prior intervention, using the frozen 0.40 alpha."""
    opts = list(display)
    floor = replay.usage_floor(
        opts,
        replay.to_id(battle.active_pokemon.species),
        SETS,
        P_SWITCH,
        P_TERA,
    )
    return _mix(jev, floor, PLAYER_ALPHA)


def opponent_model_distribution(
    jev: dict[str, float], display: dict[str, str], battle
) -> dict[str, float]:
    """The sole opponent-model intervention, using the frozen 0.25 alpha."""
    opts = list(display)
    floor = replay.usage_floor(
        opts,
        replay.to_id(battle.opponent_active_pokemon.species),
        SETS,
        P_SWITCH,
        P_TERA,
    )
    return _mix(jev, floor, OPPONENT_ALPHA)


_MIX_CONTEXT: contextvars.ContextVar[dict | None] = contextvars.ContextVar(
    "pokejev_frozen_mix_context", default=None
)
_ORIGINAL_VALIDATED = player_module.validated
_ORIGINAL_PLAYER = player_module.PokeJevPlayer


def _mixed_validated(probabilities: dict[str, float], display: dict[str, str]):
    result = _ORIGINAL_VALIDATED(probabilities, display)
    context = _MIX_CONTEXT.get()
    if context is None:
        return result
    slot = context["slot"]
    context["slot"] += 1
    if slot == 0:
        return action_prior_distribution(result, display, context["battle"])
    if slot == 1:
        return opponent_model_distribution(result, display, context["battle"])
    # Leaf probabilities are intentionally unchanged.
    return result


player_module.validated = _mixed_validated


class FrozenAlphaPlayer(_ORIGINAL_PLAYER):
    """Stage B player with only the two preregistered distribution substitutions."""

    async def _decide(self, battle, rec, box):
        token = _MIX_CONTEXT.set({"battle": battle, "slot": 0})
        try:
            return await super()._decide(battle, rec, box)
        finally:
            _MIX_CONTEXT.reset(token)

    async def _ask(self, state, questions, rec):
        try:
            return await super()._ask(state, questions, rec)
        except Exception as exc:
            text = f"{type(exc).__name__}: {exc}".lower()
            status = getattr(exc, "status_code", getattr(exc, "status", None))
            if (
                status in {401, 402}
                or "401" in text
                or "402" in text
                or "credit" in text
                or "billing" in text
            ):
                OUT.mkdir(parents=True, exist_ok=True)
                STOP_PATH.write_text(
                    json.dumps(
                        {
                            "reason": f"{type(exc).__name__}: {str(exc)[:300]}",
                            "module_sha256": MODULE_SHA256,
                            "frozen_alpha_sha256": FROZEN_ALPHA_SHA256,
                        },
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            raise


_LEAF_BATTLE: contextvars.ContextVar[object | None] = contextvars.ContextVar(
    "pokejev_leaf_battle", default=None
)


class LeafPlayer(FrozenAlphaPlayer):
    """Frozen-alpha root with a deterministic or one-request leaf arm."""

    def __init__(
        self,
        *args,
        leaf_mode: str | None = None,
        leaf_model: FrozenLeafModel | None = None,
        **kwargs,
    ):
        if leaf_mode is None or leaf_model is None:
            if _LEAF_CONFIG is None:
                raise ValueError("LeafPlayer requires a configured leaf arm")
            leaf_mode, leaf_model = _LEAF_CONFIG
        super().__init__(*args, **kwargs)
        self._leaf_arm = LeafArm(mode=leaf_mode, model=leaf_model, asker=None)

    async def _decide(self, battle, rec, box):
        token = _LEAF_BATTLE.set(battle)
        try:
            return await super()._decide(battle, rec, box)
        finally:
            _LEAF_BATTLE.reset(token)

    @staticmethod
    def _team_hp_remaining(team) -> float:
        return (
            sum(
                max(0.0, min(1.0, float(getattr(mon, "current_hp_fraction", 0.0))))
                for mon in team.values()
            )
            / 6.0
        )

    @classmethod
    def _base_features(cls, battle) -> dict[str, float]:
        team = getattr(battle, "team", {}) or {}
        opponent_team = getattr(battle, "opponent_team", {}) or {}
        hp = cls._team_hp_remaining(team)
        opponent_hp = cls._team_hp_remaining(opponent_team)
        return {
            "hp_weighted_remaining": hp,
            "status_count": sum(
                bool(getattr(mon, "status", None)) for mon in team.values()
            )
            / 6.0,
            "hazard_count": len(getattr(battle, "side_conditions", {}) or {}) / 4.0,
            "speed_order_rate": 0.5,
            "opponent_hp_remaining": opponent_hp,
            "hp_differential": hp - opponent_hp,
        }

    @staticmethod
    def _summary_features(summary: dict, _label: str, base: dict[str, float]):
        own_lines = [summary.get("your_active", ""), *summary.get("your_bench", [])]
        opponent_lines = [
            summary.get("opponent_active", ""),
            *summary.get("opponent_bench_seen", summary.get("opponent_bench", [])),
        ]

        def hp_values(lines):
            return [
                float(match) / 100.0
                for line in lines
                for match in re.findall(r"(\d+)%", str(line))
            ]

        own_hp = hp_values(own_lines)
        opponent_hp = hp_values(opponent_lines)
        statuses = ("burn", "par", "poison", "tox", "sleep", "freeze")
        hp = sum(own_hp) / 6.0 if own_hp else base["hp_weighted_remaining"]
        opponent = (
            sum(opponent_hp) / 6.0 if opponent_hp else base["opponent_hp_remaining"]
        )
        return {
            "hp_weighted_remaining": hp,
            "status_count": sum(
                any(status in str(line).lower() for status in statuses)
                for line in own_lines
            )
            / 6.0,
            "hazard_count": base["hazard_count"],
            "speed_order_rate": base["speed_order_rate"],
            "opponent_hp_remaining": opponent,
            "hp_differential": hp - opponent,
        }

    async def _leaf_nouls(self, state, rec) -> dict[str, float]:
        from typesafe_sdk import Noul

        questions = {
            "ko_now": Noul(
                instructions="Can our active Pokémon secure a knockout with a legal action this turn?",
                criteria={
                    "true": "A legal action can secure a knockout this turn",
                    "false": "No legal action can secure a knockout this turn",
                },
            ),
            "danger_now": Noul(
                instructions="Is our active Pokémon in immediate danger of being knocked out this turn?",
                criteria={
                    "true": "The active Pokémon is likely to be knocked out this turn",
                    "false": "The active Pokémon is not likely to be knocked out this turn",
                },
            ),
            "switch_needed": Noul(
                instructions="Is switching necessary to avoid a materially worse position this turn?",
                criteria={
                    "true": "Switching is necessary to avoid a materially worse position",
                    "false": "Switching is not necessary to avoid a materially worse position",
                },
            ),
        }
        response = await super()._ask(state, questions, rec)
        answers = getattr(response, "answers", None)
        if answers is None:
            answers = getattr(response, "nouls", None)
        if answers is None:
            raise ValueError("Noul response has no answers")
        values = {}
        for name in questions:
            answer = answers[name]
            value = (
                answer.get("noul")
                if isinstance(answer, dict)
                else getattr(answer, "noul", None)
            )
            if value is None:
                raise ValueError(f"Noul response missing {name}")
            values[name] = float(value)
        return values

    async def _ask(self, state, questions, rec):
        if not questions or not all(
            name.startswith("best_after_") for name in questions
        ):
            return await super()._ask(state, questions, rec)
        outcomes = state.get("outcomes") if isinstance(state, dict) else None
        battle = _LEAF_BATTLE.get()
        if not isinstance(outcomes, dict) or battle is None:
            raise ValueError("leaf arm requires outcomes and the live battle")
        base = self._base_features(battle)
        noul_values = None
        fallback_reason = None
        if self._leaf_arm.mode == "code+noul":
            try:
                noul_values = await self._leaf_nouls(state, rec)
            except Exception as exc:
                status = getattr(exc, "status_code", getattr(exc, "status", None))
                if status in {401, 402}:
                    self._leaf_arm.stopped = True
                    raise LeafArmStopped(
                        f"leaf Noul arm stopped on HTTP {status}"
                    ) from exc
                fallback_reason = f"{type(exc).__name__}: {str(exc)[:300]}"
                rec["fallback"] = f"leaf-noul: {fallback_reason}"
        opponent_rows = list(outcomes.values())
        names = list(questions)
        candidate_labels = list(next(iter(questions.values())).criteria)
        answers = {}
        for index, question_name in enumerate(names):
            row = opponent_rows[index] if index < len(opponent_rows) else {}
            candidates = [
                {
                    "id": label,
                    "features": self._summary_features(row.get(label, {}), label, base),
                }
                for label in candidate_labels
            ]
            decision = self._leaf_arm.choose_with_values(
                state,
                candidates,
                noul_values,
                fallback_reason=fallback_reason,
            )
            probabilities = {
                label: 1.0 if label == decision.choice else 0.0
                for label in candidate_labels
            }
            answers[question_name] = SimpleNamespace(probabilities=probabilities)
        return SimpleNamespace(answers=answers)


_LEAF_CONFIG: tuple[str, FrozenLeafModel] | None = None
_RUN_ID: str | None = None

_ORIGINAL_MAKE_PLAYERS = stage_b.make_players


def _make_players(opp_name, w, replays, decisions, client_factory=None, cls=None):
    chosen = (
        LeafPlayer
        if _LEAF_CONFIG is not None and (cls is None or cls is _ORIGINAL_PLAYER)
        else FrozenAlphaPlayer
        if cls is None or cls is _ORIGINAL_PLAYER
        else cls
    )
    return _ORIGINAL_MAKE_PLAYERS(
        opp_name,
        w,
        replays,
        decisions,
        client_factory,
        cls=chosen,
    )


stage_b.make_players = _make_players


# Decision/result JSONL rows are emitted by imported Stage B code.  Add provenance at the
# serialization boundary so every row records precisely which imported source and wrapper
# revision were used.
_ORIGINAL_JSON_DUMPS = json.dumps


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dumps_with_provenance(obj, *args, **kwargs):
    if isinstance(obj, dict) and ("k" in obj or ("battle" in obj and "turn" in obj)):
        obj = dict(obj)
        obj["stage_b_import_sha256"] = MODULE_SHA256
        obj["frozen_alpha_sha256"] = FROZEN_ALPHA_SHA256
        obj["run_py_sha256"] = RUN_PY_SHA256
        obj["run_started_at_utc"] = RUN_STARTED_AT_UTC
        obj["row_recorded_at_utc"] = _utc_now()
        if _LEAF_CONFIG is not None:
            obj["leaf_mode"] = _LEAF_CONFIG[0]
            obj["leaf_model_sha256"] = LEAF_MODEL_SHA256
        if _RUN_ID is not None:
            obj["run_id"] = _RUN_ID
    return _ORIGINAL_JSON_DUMPS(obj, *args, **kwargs)


json.dumps = _dumps_with_provenance


def _tag(control: bool, leaf_mode: str | None = None, run_id: str | None = None) -> str:
    if leaf_mode is not None:
        suffix = f"-{run_id}" if run_id is not None else "-v1"
        return f"-leaf-{leaf_mode.replace('+', '-')}{suffix}"
    return "-mix-v1-control" if control else "-mix-v1"


def _arm_paths(opponent: str, tag: str):
    if tag.startswith("-leaf-"):
        stem = f"{opponent}{tag}"
        return (
            str(LEAF_OUT / f"replays-{stem}"),
            str(LEAF_OUT / f"results-{stem}.jsonl"),
            str(LEAF_OUT / f"decisions-{stem}.jsonl"),
        )
    return stage_b.arm_paths(opponent, tag)


def _configure(seed: int) -> None:
    stage_b.PAIR_SEED = seed
    stage_b.OUT = str(OUT)
    OUT.mkdir(parents=True, exist_ok=True)


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


async def _run_shard(
    opp_name: str,
    n: int,
    workers: int,
    worker: int,
    control: bool,
    leaf_mode: str | None = None,
    run_id: str | None = None,
) -> int:
    global _LEAF_CONFIG, _RUN_ID
    _RUN_ID = run_id
    if leaf_mode is not None and control:
        raise ValueError("leaf arms cannot be combined with --control")
    _LEAF_CONFIG = (
        (
            leaf_mode,
            FrozenLeafModel.from_json(
                LEAF_MODEL_PATH, expected_sha256=LEAF_MODEL_SHA256
            ),
        )
        if leaf_mode is not None
        else None
    )
    tag = _tag(control, leaf_mode, run_id)
    if leaf_mode is not None:
        LEAF_OUT.mkdir(parents=True, exist_ok=True)
    replays, results, decisions = _arm_paths(opp_name, tag)
    done = {row["k"] for row in _load_jsonl(Path(results)) if "won" in row}
    mine = [k for k in range(n) if k % workers == worker and k not in done]
    client_factory = stage_b.DisabledJev if control else None
    me, opp = stage_b.make_players(
        opp_name,
        worker + 50,
        replays,
        decisions,
        client_factory,
    )
    for k in mine:
        if not control and STOP_PATH.exists() and STOP_PATH.stat().st_size:
            return 3
        row_started_at_utc = _utc_now()
        try:
            row = await stage_b.play(me, opp, k, replays)
        except Exception as exc:  # noqa: BLE001 - record each harness failure and continue
            row = {"k": k, "error": f"{type(exc).__name__}: {str(exc)[:300]}"}
        row["row_started_at_utc"] = row_started_at_utc
        await asyncio.to_thread(_append_jsonl, Path(results), row)
        if not control and STOP_PATH.exists() and STOP_PATH.stat().st_size:
            return 3
    return 0


def _spawn(
    opp_name: str,
    n: int,
    workers: int,
    control: bool,
    seed: int,
    leaf_mode: str | None = None,
    run_id: str | None = None,
) -> int:
    env = dict(
        os.environ,
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        VECLIB_MAXIMUM_THREADS="1",
    )
    base = [
        sys.executable,
        str(Path(__file__).resolve()),
        "_shard",
        opp_name,
        str(n),
        str(workers),
        "--pair-seed",
        str(seed),
    ]
    if run_id is not None:
        base.extend(["--run-id", run_id])
    procs = [
        subprocess.Popen(
            base
            + [str(worker)]
            + (["--control"] if control else [])
            + (["--leaf", leaf_mode] if leaf_mode is not None else []),
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            env=env,
        )
        for worker in range(workers)
    ]
    codes = [proc.wait() for proc in procs]
    _, results, _ = _arm_paths(opp_name, _tag(control, leaf_mode, run_id))
    rows = _load_jsonl(Path(results))
    complete = {row["k"] for row in rows if "won" in row and row["k"] < n}
    print(
        f"{opp_name}{'-control' if control else ''}: {len(complete)}/{n} battles with a result, "
        f"{sum(1 for row in rows if 'error' in row)} harness-error rows, child codes {codes}",
        file=sys.stderr,
    )
    if STOP_PATH.exists() and STOP_PATH.stat().st_size:
        print(f"STOPPED: credit exhaustion marker at {STOP_PATH}", file=sys.stderr)
    return max(codes)


def selftest() -> int:
    """Keyless wrapper test: frozen supports, alphas, leaf passthrough, and row provenance."""
    battle = SimpleNamespace(
        active_pokemon=SimpleNamespace(species="pikachu"),
        opponent_active_pokemon=SimpleNamespace(species="charizard"),
    )
    display = {"move thunderbolt": "Thunderbolt", "move protect": "Protect"}
    answer = {"Thunderbolt": 0.75, "Protect": 0.25}
    prior = action_prior_distribution(
        _ORIGINAL_VALIDATED(answer, display), display, battle
    )
    floor = replay.usage_floor(
        list(display),
        replay.to_id(battle.active_pokemon.species),
        SETS,
        P_SWITCH,
        P_TERA,
    )
    expected = _mix(_ORIGINAL_VALIDATED(answer, display), floor, PLAYER_ALPHA)
    if prior != expected or abs(sum(prior.values()) - 1.0) >= 1e-12:
        raise AssertionError("action-prior mixture mismatch")

    opponent = opponent_model_distribution(
        _ORIGINAL_VALIDATED(answer, display), display, battle
    )
    opp_floor = replay.usage_floor(
        list(display),
        replay.to_id(battle.opponent_active_pokemon.species),
        SETS,
        P_SWITCH,
        P_TERA,
    )
    expected_opponent = _mix(
        _ORIGINAL_VALIDATED(answer, display), opp_floor, OPPONENT_ALPHA
    )
    if opponent != expected_opponent:
        raise AssertionError("opponent-model mixture mismatch")

    token = _MIX_CONTEXT.set({"battle": battle, "slot": 2})
    try:
        leaf = _mixed_validated(answer, display)
    finally:
        _MIX_CONTEXT.reset(token)
    if leaf != _ORIGINAL_VALIDATED(answer, display):
        raise AssertionError("leaf distribution was modified")

    row = json.loads(json.dumps({"k": 0, "battle": "test", "turn": 1}))
    if row.get("stage_b_import_sha256") != MODULE_SHA256:
        raise AssertionError("row is missing imported module provenance")
    if row.get("frozen_alpha_sha256") != FROZEN_ALPHA_SHA256:
        raise AssertionError("row is missing frozen-alpha provenance")
    if row.get("run_py_sha256") != RUN_PY_SHA256:
        raise AssertionError("row is missing run.py provenance")
    if row.get("run_started_at_utc") is None or row.get("row_recorded_at_utc") is None:
        raise AssertionError("row is missing UTC provenance timestamps")
    print("WRAPPER SELFTEST PASS 5/5")
    return 0


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 4), round(c + h, 4))


def _score_arm(opp_name: str, control: bool) -> dict | None:
    tag = _tag(control)
    rows = _load_jsonl(OUT / f"results-{opp_name}{tag}.jsonl")
    decisions = _load_jsonl(OUT / f"decisions-{opp_name}{tag}.jsonl")
    completed = list({row["k"]: row for row in rows if "won" in row}.values())
    errors = [row for row in rows if "error" in row]
    if not completed and not errors:
        return None
    fallback_reasons: dict[str, int] = {}
    for decision in decisions:
        if decision.get("fallback"):
            reason = str(decision["fallback"])
            fallback_reasons[reason] = fallback_reasons.get(reason, 0) + 1
    latencies = sorted(decision["ms"] for decision in decisions if "ms" in decision)
    tokens = sum(int(decision.get("input_tokens", 0)) for decision in decisions)
    wins = sum(bool(row["won"]) for row in completed)
    return {
        "battles": len(completed),
        "harness_errors": len(errors),
        "wins": wins,
        "losses": len(completed) - wins,
        "win_rate": round(wins / len(completed), 4) if completed else None,
        "wilson95": _wilson(wins, len(completed)),
        "own_time_losses": sum(row.get("time_loss") == "pokejev" for row in completed),
        "opponent_time_losses": sum(
            row.get("time_loss") == "opponent" for row in completed
        ),
        "unfinished": sum(not row.get("finished", False) for row in completed),
        "decisions": len(decisions),
        "fallbacks": sum(fallback_reasons.values()),
        "fallback_reasons": dict(sorted(fallback_reasons.items())),
        "decision_ms_p50": latencies[len(latencies) // 2] if latencies else None,
        "decision_ms_p95": latencies[int(len(latencies) * 0.95)] if latencies else None,
        "decision_ms_max": latencies[-1] if latencies else None,
        "jev_calls": sum(len(decision.get("jev_ms", [])) for decision in decisions),
        "input_tokens": tokens,
        "spend_usd_at_0.042_per_M_input": round(tokens * 0.042 / 1e6, 4),
        "models": sorted(
            {model for decision in decisions for model in decision.get("models", [])}
        ),
        "module_sha256": MODULE_SHA256,
        "frozen_alpha_sha256": FROZEN_ALPHA_SHA256,
    }


def score() -> int:
    out = {
        "model": "jev-1.13.0",
        "pair_seed": stage_b.PAIR_SEED,
        "arms": {
            "abyssal-mix-v1": _score_arm("abyssal", False),
            "abyssal-mix-v1-control": _score_arm("abyssal", True),
        },
        "stop_marker": str(STOP_PATH)
        if STOP_PATH.exists() and STOP_PATH.stat().st_size
        else None,
        "module_sha256": MODULE_SHA256,
        "frozen_alpha_sha256": FROZEN_ALPHA_SHA256,
    }
    live = out["arms"]["abyssal-mix-v1"]
    control = out["arms"]["abyssal-mix-v1-control"]
    if live and control and live["battles"] and control["battles"]:
        p_live = live["wins"] / live["battles"]
        p_control = control["wins"] / control["battles"]
        pooled = (live["wins"] + control["wins"]) / (
            live["battles"] + control["battles"]
        )
        se = (
            math.sqrt(
                pooled * (1 - pooled) * (1 / live["battles"] + 1 / control["battles"])
            )
            if 0 < pooled < 1
            else 0.0
        )
        z = (p_live - p_control) / se if se else 0.0
        out["live_minus_control"] = {
            "difference": round(p_live - p_control, 4),
            "z": round(z, 3),
            "p_two_sided": round(math.erfc(abs(z) / math.sqrt(2)), 4),
        }
    (OUT / "receipt-mix-v1.json").write_text(
        _ORIGINAL_JSON_DUMPS(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(_ORIGINAL_JSON_DUMPS(out, indent=1, sort_keys=True))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("command", choices=("selftest", "battles", "_shard", "score"))
    parser.add_argument("opponent", nargs="?")
    parser.add_argument("count", nargs="?", type=int)
    parser.add_argument("worker_count", nargs="?", type=int)
    parser.add_argument("worker", nargs="?", type=int)
    parser.add_argument("--workers", dest="workers", type=int, default=stage_b.WORKERS)
    parser.add_argument("--pair-seed", type=int, default=20260925)
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--leaf", choices=("code", "code+noul"))
    parser.add_argument("--run-id")
    args = parser.parse_args(argv)
    _configure(args.pair_seed)
    if args.command == "selftest":
        return selftest()
    if args.command == "score":
        return score()
    if args.opponent not in stage_b.OPPONENTS or args.count is None:
        parser.error("an opponent and battle count are required")
    if args.command == "battles":
        if args.leaf is not None and args.control:
            parser.error("--leaf cannot be combined with --control")
        if not args.control and not os.environ.get("TYPESAFE_API_KEY"):
            print(
                "unconfigured: TYPESAFE_API_KEY unset, no battle played (NOT_RUN)",
                file=sys.stderr,
            )
            return 2
        if not args.control:
            STOP_PATH.write_text("", encoding="utf-8")
        return _spawn(
            args.opponent,
            args.count,
            args.workers,
            args.control,
            args.pair_seed,
            args.leaf,
            args.run_id,
        )
    if args.worker_count is None or args.worker is None:
        parser.error("_shard requires worker count and worker index")
    return asyncio.run(
        _run_shard(
            args.opponent,
            args.count,
            args.worker_count,
            args.worker,
            args.control,
            args.leaf,
            args.run_id,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
