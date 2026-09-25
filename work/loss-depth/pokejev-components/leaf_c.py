#!/usr/bin/env python3
"""Leaf evaluator Arm C for the frozen PokéJev Stage B component split.

The extractor is keyless and only uses replay events through each decision turn.  The
optional ``--fetch-nouls`` lane is the only live lane: it writes one cache row per
eligible decision using the pinned TypeSafe SDK and does not fit or score a model.
The ``--score`` lane is deterministic and fits/scorers code-only or code+Noul models.
"""

from __future__ import annotations

import argparse
import asyncio
import html
import json
import math
import os
import random
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
POKE = ROOT / "work" / "poke-jev"
COMPONENT_DIR = Path(__file__).resolve().parent
STAGE_B = POKE / "stage-b"
SPLIT_PATH = COMPONENT_DIR / "decision-split-v1.json"
Noul_CACHE = COMPONENT_DIR / "leaf-c-nouls.jsonl"
SEED = 20260925
BOOTSTRAP_REPS = 5000
FEATURES = (
    "hp_weighted_remaining",
    "status_count",
    "hazard_count",
    "speed_order_rate",
    "ko_threat",
)
HAZARDS = {"stealthrock", "spikes", "toxicspikes", "stickyweb"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {path}:{line_number}") from exc
    return rows


def to_id(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def side_of(ident: str) -> str:
    return ident[:2]


def nick_of(ident: str) -> str:
    return ident.split(":", 1)[1].strip() if ":" in ident else ident


def species_key(species: str) -> str:
    return to_id(species.split(",", 1)[0].split("-", 1)[0])


def parse_hp(value: str) -> float | None:
    if value.strip().endswith("fnt"):
        return 0.0
    token = value.split()[0]
    if "/" in token:
        left, right = token.split("/", 1)
        try:
            return (
                max(0.0, min(1.0, float(left) / float(right))) if float(right) else 0.0
            )
        except ValueError:
            return None
    if token.endswith("%"):
        try:
            return max(0.0, min(1.0, float(token[:-1]) / 100.0))
        except ValueError:
            return None
    try:
        return max(0.0, min(1.0, float(token)))
    except ValueError:
        return None


def replay_lines(path: Path) -> list[str]:
    marker = '<script type="text/plain" class="battle-log-data">'
    text = path.read_text(encoding="utf-8", errors="replace")
    if marker not in text:
        raise ValueError(f"missing battle-log-data in {path}")
    payload = text.split(marker, 1)[1].split("</script>", 1)[0]
    return [
        line for line in html.unescape(payload).splitlines() if line.startswith("|")
    ]


def snapshot_features(path: Path) -> dict[int, dict[str, float | str]]:
    """Return pre-turn player(p1) features and a compact state for each turn."""
    teams: dict[str, dict[str, float]] = {"p1": {}, "p2": {}}
    active: dict[str, str | None] = {"p1": None, "p2": None}
    nick_species: dict[tuple[str, str], str] = {}
    statuses: dict[str, set[str]] = {"p1": set(), "p2": set()}
    hazards: dict[str, set[str]] = {"p1": set(), "p2": set()}
    prior_pairs = 0
    own_first = 0
    turn_actions: list[str] = []
    current_turn: int | None = None
    out: dict[int, dict[str, float | str]] = {}

    def finish_actions() -> None:
        nonlocal prior_pairs, own_first, turn_actions
        seen = set(turn_actions)
        if {"p1", "p2"} <= seen:
            prior_pairs += 1
            if turn_actions.index("p1") < turn_actions.index("p2"):
                own_first += 1
        turn_actions = []

    def make_snapshot() -> dict[str, float | str]:
        hp = sum(teams["p1"].values()) / 6.0
        speed = (own_first + 1.0) / (prior_pairs + 2.0)
        return {
            "hp_weighted_remaining": hp,
            "status_count": len(statuses["p1"]) / 6.0,
            "hazard_count": len(hazards["p1"]) / 4.0,
            "speed_order_rate": speed,
            "active": active["p1"] or "unknown",
            "opponent_active": active["p2"] or "unknown",
            "known_species": ",".join(sorted(teams["p1"])),
        }

    for line in replay_lines(path):
        fields = line.split("|")
        kind = fields[1] if len(fields) > 1 else ""
        if kind == "turn" and len(fields) > 2:
            finish_actions()
            current_turn = int(fields[2])
            out[current_turn] = make_snapshot()
            continue
        if kind == "move" and len(fields) > 2:
            side = side_of(fields[2])
            if side in ("p1", "p2") and side not in turn_actions:
                turn_actions.append(side)
            continue
        if len(fields) < 3:
            continue
        ident = fields[2]
        side = side_of(ident)
        if side not in teams:
            continue
        if kind in ("switch", "drag", "replace") and len(fields) > 4:
            species = fields[3].split(",", 1)[0].strip()
            key = species_key(species)
            nick_species[(side, nick_of(ident))] = key
            active[side] = key
            hp = parse_hp(fields[4])
            if hp is not None:
                teams[side][key] = hp
            else:
                teams[side].setdefault(key, 1.0)
        elif kind == "poke" and len(fields) > 3:
            teams[side].setdefault(species_key(fields[3]), 0.0)
        elif kind in ("-damage", "-heal") and len(fields) > 3:
            key = nick_species.get((side, nick_of(ident)))
            hp = parse_hp(fields[3])
            if key is not None and hp is not None:
                teams[side][key] = hp
        elif kind == "faint":
            key = nick_species.get((side, nick_of(ident)))
            if key is not None:
                teams[side][key] = 0.0
        elif kind == "-status" and len(fields) > 3:
            statuses[side].add(
                f"{nick_species.get((side, nick_of(ident)), nick_of(ident))}:{to_id(fields[3])}"
            )
        elif kind == "-curestatus":
            prefix = f"{nick_species.get((side, nick_of(ident)), nick_of(ident))}:"
            statuses[side] = {
                status for status in statuses[side] if not status.startswith(prefix)
            }
        elif kind == "-sidestart" and len(fields) > 3:
            hazard = to_id(fields[3].rsplit(":", 1)[-1])
            if hazard in HAZARDS:
                hazards[side].add(hazard)
        elif kind == "-sideend" and len(fields) > 3:
            hazard = to_id(fields[3].rsplit(":", 1)[-1])
            hazards[side].discard(hazard)
    return out


def eligible_rows(
    split: dict[str, Any], part: str
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    decisions = load_jsonl(STAGE_B / "decisions-abyssal.jsonl")
    results = {
        row["battle"]: row for row in load_jsonl(STAGE_B / "results-abyssal.jsonl")
    }
    battles = set(split["stage_b"][f"{part}_battles"])
    replay_cache: dict[str, dict[int, dict[str, float | str]]] = {}
    rows: list[dict[str, Any]] = []
    excluded = {"not_in_split": 0, "fallback": 0, "unusable": 0, "missing_turn": 0}
    for index, decision in enumerate(decisions):
        battle = decision["battle"]
        if battle not in battles:
            excluded["not_in_split"] += 1
            continue
        if decision.get("fallback"):
            excluded["fallback"] += 1
            continue
        result = results.get(battle)
        values = decision.get("values") or {}
        chosen = decision.get("chosen")
        if (
            result is None
            or not result.get("finished")
            or not isinstance(result.get("won"), bool)
            or chosen not in values
        ):
            excluded["unusable"] += 1
            continue
        if battle not in replay_cache:
            replay_cache[battle] = snapshot_features(POKE / result["replay"])
        snapshot = replay_cache[battle].get(int(decision["turn"]))
        if snapshot is None:
            excluded["missing_turn"] += 1
            continue
        code = {name: float(snapshot[name]) for name in FEATURES[:-1]}
        code["ko_threat"] = float(
            bool((decision.get("tool") or "").startswith("move "))
        )
        state = {
            "turn": decision["turn"],
            "features": code,
            "active": snapshot["active"],
            "opponent_active": snapshot["opponent_active"],
            "known_species": snapshot["known_species"],
            "n_options": decision.get("n_options"),
            "tool": decision.get("tool"),
            "prior_top": decision.get("prior_top"),
            "candidates": decision.get("candidates", []),
        }
        rows.append(
            {
                "id": f"{battle}:{decision['turn']}:{index}",
                "battle": battle,
                "turn": decision["turn"],
                "won": bool(result["won"]),
                "leaf_value": float(values[chosen]),
                "prior_value": float(values.get(decision.get("prior_top"), 0.5)),
                "features": code,
                "state": state,
            }
        )
    excluded.pop("not_in_split")
    return rows, excluded


def load_nouls(path: Path) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}
    if not path.exists():
        return out
    for row in load_jsonl(path):
        values = row.get("nouls")
        if (
            isinstance(values, list)
            and len(values) == 3
            and all(math.isfinite(float(value)) for value in values)
        ):
            out[row["id"]] = [float(value) for value in values]
    return out


def auc(scores: list[tuple[float, bool]]) -> float:
    ordered = sorted(scores, key=lambda item: item[0])
    positives = sum(label for _score, label in ordered)
    negatives = len(ordered) - positives
    if not positives or not negatives:
        raise ValueError("AUC requires both outcome classes")
    rank_sum = 0.0
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][0] == ordered[index][0]:
            end += 1
        average_rank = (index + 1 + end) / 2.0
        rank_sum += average_rank * sum(label for _score, label in ordered[index:end])
        index = end
    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def grouped_bootstrap(
    scores: list[tuple[str, float, bool]],
) -> tuple[float, list[float]]:
    by_battle: dict[str, list[tuple[float, bool]]] = {}
    for battle, score, label in scores:
        by_battle.setdefault(battle, []).append((score, label))
    battles = sorted(by_battle)
    point = auc([(score, label) for _battle, score, label in scores])
    rng = random.Random(SEED)  # nosec B311
    samples: list[float] = []
    for _ in range(BOOTSTRAP_REPS):
        sampled = [row for _ in battles for row in by_battle[rng.choice(battles)]]
        if any(label for _score, label in sampled) and any(
            not label for _score, label in sampled
        ):
            samples.append(auc(sampled))
    samples.sort()
    lo = samples[int(0.025 * (len(samples) - 1))]
    hi = samples[int(0.975 * (len(samples) - 1))]
    return point, [lo, hi]


def baseline_row(rows: list[dict[str, Any]], field: str, name: str) -> dict[str, Any]:
    scores = [(row["battle"], float(row[field]), row["won"]) for row in rows]
    point, interval = grouped_bootstrap(scores)
    return {
        "arm": name,
        "n": len(rows),
        "battles": len({row["battle"] for row in rows}),
        "positive": sum(row["won"] for row in rows),
        "negative": sum(not row["won"] for row in rows),
        "auc": point,
        "auc95": interval,
    }


def score_model(
    rows: list[dict[str, Any]], nouls: dict[str, list[float]], with_nouls: bool
) -> dict[str, Any]:
    try:
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import roc_auc_score
        from sklearn.model_selection import GroupKFold
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise SystemExit(f"scoring dependencies unavailable: {exc}") from exc
    if with_nouls:
        rows = [row for row in rows if row["id"] in nouls]
    names = list(FEATURES) + (
        ["ko_now", "danger_now", "switch_needed"] if with_nouls else []
    )
    X = np.asarray(
        [
            [*row["features"].values(), *(nouls[row["id"]] if with_nouls else [])]
            for row in rows
        ],
        dtype=float,
    )
    y = np.asarray([row["won"] for row in rows], dtype=int)
    groups = np.asarray([row["battle"] for row in rows])

    def model_factory():
        return make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=1.0, penalty="l2", solver="liblinear", random_state=SEED
            ),
        )

    cv_scores = []
    cv_folds = []
    for fold_index, (train, test) in enumerate(
        GroupKFold(n_splits=5).split(X, y, groups), 1
    ):
        model = model_factory()
        model.fit(X[train], y[train])
        full_auc = float(roc_auc_score(y[test], model.predict_proba(X[test])[:, 1]))
        fold = {"fold": fold_index, "auc": full_auc}
        if with_nouls:
            code_model = model_factory()
            code_model.fit(X[train, : len(FEATURES)], y[train])
            code_auc = float(
                roc_auc_score(
                    y[test], code_model.predict_proba(X[test, : len(FEATURES)])[:, 1]
                )
            )
            fold["code_only_auc"] = code_auc
            fold["paired_delta"] = full_auc - code_auc
        cv_scores.append(full_auc)
        cv_folds.append(fold)
    model = model_factory()
    model.fit(X, y)
    scores = model.predict_proba(X)[:, 1]
    scored = [
        (row["battle"], float(score), row["won"]) for row, score in zip(rows, scores)
    ]
    point, interval = grouped_bootstrap(scored)
    result: dict[str, Any] = {
        "arm": "C_code_plus_noul" if with_nouls else "C_code_only",
        "n": len(rows),
        "battles": len(set(groups)),
        "positive": int(y.sum()),
        "negative": int((1 - y).sum()),
        "auc": point,
        "auc95": interval,
        "cv_auc_mean": float(np.mean(cv_scores)),
        "cv_auc_std": float(np.std(cv_scores, ddof=1)),
        "cv_folds": cv_folds,
        "features": names,
        "noul_rows": len(rows) if with_nouls else 0,
        "boundary": "Dev-fit score only; no held-out result is reported until the frozen dev fit is frozen and run on held-out battles.",
    }
    try:
        import statsmodels.api as sm

        fitted = sm.Logit(y, sm.add_constant(StandardScaler().fit_transform(X))).fit(
            disp=False
        )
        result["logit_coefficients"] = {
            name: {
                "estimate": float(fitted.params[index]),
                "ci95": [float(value) for value in fitted.conf_int()[index]],
            }
            for index, name in enumerate(["intercept", *names])
        }
    except Exception as exc:  # noqa: BLE001
        result["logit_coefficients_error"] = f"{type(exc).__name__}: {exc}"
    if with_nouls:
        code_scores = [fold["code_only_auc"] for fold in cv_folds]
        deltas = [fold["paired_delta"] for fold in cv_folds]
        result["cv_code_only_auc_mean"] = float(np.mean(code_scores))
        result["cv_code_only_auc_std"] = float(np.std(code_scores, ddof=1))
        result["cv_paired_deltas"] = deltas
        result["cv_paired_delta_mean"] = float(np.mean(deltas))
        result["cv_paired_delta_std"] = float(np.std(deltas, ddof=1))
    return result


def score_heldout_model(
    train_rows: list[dict[str, Any]],
    eval_rows: list[dict[str, Any]],
    nouls: dict[str, list[float]],
    with_nouls: bool,
) -> dict[str, Any]:
    try:
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise SystemExit(f"scoring dependencies unavailable: {exc}") from exc
    if with_nouls:
        train_rows = [row for row in train_rows if row["id"] in nouls]
        eval_rows = [row for row in eval_rows if row["id"] in nouls]
    names = list(FEATURES) + (
        ["ko_now", "danger_now", "switch_needed"] if with_nouls else []
    )

    def matrix(rows: list[dict[str, Any]]) -> Any:
        return np.asarray(
            [
                [
                    *(row["features"][name] for name in FEATURES),
                    *(nouls[row["id"]] if with_nouls else []),
                ]
                for row in rows
            ],
            dtype=float,
        )

    x_train = matrix(train_rows)
    y_train = np.asarray([row["won"] for row in train_rows], dtype=int)
    x_eval = matrix(eval_rows)
    y_eval = np.asarray([row["won"] for row in eval_rows], dtype=int)
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=1.0, penalty="l2", solver="liblinear", random_state=SEED),
    )
    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_eval)[:, 1]
    scored = [
        (row["battle"], float(score), row["won"])
        for row, score in zip(eval_rows, probabilities)
    ]
    point, interval = grouped_bootstrap(scored)
    return {
        "arm": "C_code_plus_noul" if with_nouls else "C_code_only",
        "n": len(eval_rows),
        "battles": len({row["battle"] for row in eval_rows}),
        "positive": int(y_eval.sum()),
        "negative": int((1 - y_eval).sum()),
        "auc": point,
        "auc95": interval,
        "fit_n": len(train_rows),
        "fit_battles": len({row["battle"] for row in train_rows}),
        "features": names,
        "noul_rows": len(eval_rows) if with_nouls else 0,
        "heldout": True,
        "boundary": "Fit on frozen dev rows only; score on held-out battles once. No battle arm was run.",
    }


def markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Arm | N | Battles | Positive | Negative | AUC (95% CI) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lo, hi = row["auc95"]
        lines.append(
            f"| {row['arm']} | {row['n']} | {row['battles']} | {row['positive']} | {row['negative']} | {row['auc']:.4f} [{lo:.4f}, {hi:.4f}] |"
        )
    return "\n".join(lines)


def build_rows(part: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    try:
        split = json.loads(SPLIT_PATH.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid split JSON: {SPLIT_PATH}") from exc
    return eligible_rows(split, part)


async def fetch_nouls(rows: list[dict[str, Any]], output: Path) -> int:
    sys.path.insert(
        0, str(ROOT / "upstream" / "typesafe-ai" / "typesafe-sdk-python" / "src")
    )
    from typesafe_sdk import AsyncTypeSafeClient, Noul, RetryPolicy

    if not os.environ.get("TYPESAFE_API_KEY"):
        print(
            "NOT_RUN: TYPESAFE_API_KEY is unset; no Jev request made", file=sys.stderr
        )
        return 2
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
    have = load_nouls(output)
    todo = [row for row in rows if row["id"] not in have]
    client = AsyncTypeSafeClient(model="jev-1.13.0", retry=RetryPolicy())
    semaphore = asyncio.Semaphore(8)

    async def one(row: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            try:
                response = await client.system_one(row["state"], questions)
                values = [float(response.nouls[name].noul) for name in questions]
                if not all(
                    math.isfinite(value) and 0 <= value <= 1 for value in values
                ):
                    raise ValueError("Noul answer outside [0,1]")
                return {
                    "id": row["id"],
                    "nouls": values,
                    "model": response.model,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            except Exception as exc:  # noqa: BLE001
                return {
                    "id": row["id"],
                    "error": f"{type(exc).__name__}: {str(exc)[:200]}",
                }

    async with client:
        tasks = [one(row) for row in todo]
        with output.open("a", encoding="utf-8") as handle:
            for index, task in enumerate(asyncio.as_completed(tasks), 1):
                result = await task
                handle.write(json.dumps(result, sort_keys=True) + "\n")
                handle.flush()
                if index % 25 == 0:
                    print(f"nouls {index}/{len(todo)}", file=sys.stderr)
    return 0


def selftest() -> None:
    import tempfile

    replay = """<script type="text/plain" class="battle-log-data">|poke|p1|Pikachu, L50\n|poke|p2|Eevee, L50\n|switch|p1a: Pika|Pikachu, L50|100/100\n|switch|p2a: Eve|Eevee, L50|100/100\n|turn|1\n|move|p1a: Pika|Thunderbolt|p2a: Eve\n|move|p2a: Eve|Tackle|p1a: Pika\n|-damage|p1a: Pika|50/100\n|turn|2\n</script>"""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "sample.html"
        path.write_text(replay)
        got = snapshot_features(path)
        if (
            got[1]["hp_weighted_remaining"] != 1 / 6
            or got[2]["hp_weighted_remaining"] != 0.5 / 6
            or got[2]["speed_order_rate"] <= 0.5
        ):
            raise AssertionError(f"unexpected selftest features: {got}")
    print("SELFTEST PASS 2/2")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", choices=("dev", "heldout"), default="dev")
    parser.add_argument("--score", action="store_true")
    parser.add_argument("--heldout", action="store_true")
    parser.add_argument("--fetch-nouls", action="store_true")
    parser.add_argument("--nouls", type=Path, default=Noul_CACHE)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    rows, exclusions = build_rows(args.part)
    if args.fetch_nouls:
        return asyncio.run(fetch_nouls(rows, args.nouls))
    if args.heldout:
        if not args.score:
            raise SystemExit("--heldout requires --score")
        dev_rows, dev_exclusions = build_rows("dev")
        nouls = load_nouls(args.nouls)
        results = [
            baseline_row(rows, "prior_value", "A_action_prior"),
            baseline_row(rows, "leaf_value", "B_leaf_value"),
            score_heldout_model(dev_rows, rows, nouls, with_nouls=False),
            score_heldout_model(dev_rows, rows, nouls, with_nouls=True),
        ]
        payload = {
            "part": "heldout",
            "fit_part": "dev",
            "exclusions": exclusions,
            "fit_exclusions": dev_exclusions,
            "nouls_cached": len(nouls),
            "results": results,
        }
        print(
            json.dumps(payload, indent=2, sort_keys=True)
            if args.json
            else markdown(results)
        )
        return 0
    if not args.score:
        print(
            json.dumps(
                {"part": args.part, "rows": len(rows), "exclusions": exclusions},
                indent=2,
            )
        )
        return 0
    nouls = load_nouls(args.nouls)
    results = [
        baseline_row(rows, "prior_value", "A_action_prior"),
        baseline_row(rows, "leaf_value", "B_leaf_value"),
    ]
    results.append(score_model(rows, nouls, with_nouls=False))
    if nouls:
        results.append(score_model(rows, nouls, with_nouls=True))
    payload = {
        "part": args.part,
        "exclusions": exclusions,
        "nouls_cached": len(nouls),
        "results": results,
    }
    print(
        json.dumps(payload, indent=2, sort_keys=True)
        if args.json
        else markdown(results)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
