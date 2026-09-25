#!/usr/bin/env python3
"""MiniWoB observation-pruning experiment (jev-jy7t.1.6).

The planner is the already-measured MiniWoB Jev v1 policy.  The only arm
variable is the element list passed to that policy:

* full: the complete serialized DOM/AX-like observation;
* code: a deterministic label/selector subgraph;
* jev: parallel Noul judgments over each node, followed by a safe subgraph
  closure;
* random: a seeded 50% node sample with the same closure rules.

The floor's environment and checker remain authoritative.  This module never
calls a planner other than the Jev v1 policy and never writes to /tmp for
experiment rows.  ``selftest`` is keyless and does not import the SDK.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import random
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FLOOR_PATH = ROOT / "work" / "game-floors" / "miniwob" / "run.py"
JEV_ARM_PATH = ROOT / "work" / "miniwob-jev" / "jev_arm.py"
MODEL = "jev-1.13.0"
MAX_STEPS = 1
NONE_POLICY = "after-page-change"
KEEP_FRACTION = 0.5
TASK_LIMIT = 50
SPLIT_SEEDS = {"dev": 200, "heldout": 300}
ROW_PATHS = {
    (split, arm): ROOT / "work" / "miniwob-ax-prune" / "rows" / f"{split}-{arm}.jsonl"
    for split in SPLIT_SEEDS
    for arm in ("full", "code", "jev", "random")
}


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


floor = _load(FLOOR_PATH, "miniwob_ax_floor")
jev_v1 = _load(JEV_ARM_PATH, "miniwob_ax_jev_v1")


def compact_bytes(state: dict[str, Any]) -> int:
    return len(json.dumps(state, separators=(",", ":"), ensure_ascii=False).encode())


def node_texts(elements: list[dict[str, Any]]) -> dict[int, str]:
    runs: dict[int, list[str]] = {}
    by_ref = {int(e["ref"]): e for e in elements}
    for e in elements:
        if int(e["ref"]) < 0 and e.get("text"):
            runs.setdefault(int(e["parent"]), []).append(str(e["text"]))
    out: dict[int, str] = {}
    for e in elements:
        ref = int(e["ref"])
        if ref <= 0:
            continue
        text = str(e.get("text") or "") or " ".join(runs.get(ref, []))
        if not text and str(e.get("kind", "")) in floor.BUTTON_TAGS:
            text = str(e.get("value") or "")
        parent = by_ref.get(int(e.get("parent", 0)))
        if not text and parent and parent.get("kind") == "LABEL":
            text = " ".join(runs.get(int(parent["ref"]), []))
        out[ref] = text
    return out


def goal_terms(utterance: str) -> set[str]:
    return {
        word.lower().strip("\"'.,:;!?()")
        for word in utterance.split()
        if word.lower().strip("\"'.,:;!?()")
    }


def labels_for(elements: list[dict[str, Any]]) -> dict[int, str]:
    text = node_texts(elements)
    return {
        int(e["ref"]): " ".join(
            x
            for x in (
                str(e.get("tag") or ""),
                str(e.get("id") or ""),
                text.get(int(e["ref"]), ""),
                str(e.get("value") or ""),
            )
            if x
        )
        for e in elements
        if int(e["ref"]) > 0
    }


def ancestors(elements: list[dict[str, Any]], keep: set[int]) -> set[int]:
    by_ref = {int(e["ref"]): e for e in elements}
    out = set(keep)
    for ref in tuple(keep):
        seen: set[int] = set()
        cur = ref
        while cur in by_ref and cur not in seen:
            seen.add(cur)
            parent = int(by_ref[cur].get("parent", 0))
            if parent <= 0:
                break
            out.add(parent)
            cur = parent
    # Text runs are part of the observed subgraph only when their parent stays.
    return {
        int(e["ref"]) for e in elements if int(e["ref"]) > 0 and int(e["ref"]) in out
    } | {
        int(e["ref"])
        for e in elements
        if int(e["ref"]) < 0 and int(e.get("parent", 0)) in out
    }


def close_subgraph(
    elements: list[dict[str, Any]], positive_refs: set[int]
) -> list[dict[str, Any]]:
    """Keep selected positive nodes, their ancestors, and attached text runs."""
    positive_refs = {ref for ref in positive_refs if ref > 0}
    if not positive_refs:
        positive_refs = {1} if any(int(e["ref"]) == 1 for e in elements) else set()
    keep = ancestors(elements, positive_refs)
    return [e for e in elements if int(e["ref"]) in keep]


def code_selector(
    utterance: str, elements: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Cheap control: retain goal-overlapping interactive nodes and their context."""
    terms = goal_terms(utterance)
    labels = labels_for(elements)
    interactive = {
        int(e["ref"])
        for e in elements
        if int(e["ref"]) > 0
        and (
            str(e.get("kind", "")) in floor.INTERACTIVE_TAGS
            or str(e.get("kind", "")).startswith("INPUT_")
        )
    }
    selected = {ref for ref in interactive if terms & goal_terms(labels.get(ref, ""))}
    if not selected:
        # A no-match control still exposes actionable nodes, but not containers.
        selected = interactive
    return close_subgraph(elements, selected)


def random_selector(
    elements: list[dict[str, Any]], rng: random.Random
) -> list[dict[str, Any]]:
    positive = [int(e["ref"]) for e in elements if int(e["ref"]) > 0]
    target = max(1, round(len(positive) * KEEP_FRACTION)) if positive else 0
    selected = set(rng.sample(positive, min(target, len(positive))))
    return close_subgraph(elements, selected)


def _node_description(e: dict[str, Any], text: str) -> str:
    fields = {
        "ref": int(e["ref"]),
        "parent": int(e.get("parent", 0)),
        "tag": e.get("tag", ""),
        "id": e.get("id", ""),
        "text": text,
        "value": e.get("value", ""),
        "focused": bool(e.get("focused", False)),
    }
    return json.dumps(fields, sort_keys=True, ensure_ascii=False)


def validate_nouls(values: dict[str, Any], names: set[str]) -> dict[str, float]:
    if set(values) != names:
        raise ValueError("Noul response keys do not match request")
    out: dict[str, float] = {}
    for name, answer in values.items():
        value = getattr(answer, "noul", answer)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"non-numeric Noul answer for {name}")
        value = float(value)
        if not 0 <= value <= 1:
            raise ValueError(f"out-of-range Noul answer for {name}")
        out[name] = value
    return out


class LiveNoulPruner:
    """Official SDK Noul arm; one request carries three questions per node."""

    def __init__(self):
        if not os.environ.get("TYPESAFE_API_KEY", "").strip():
            raise RuntimeError("TYPESAFE_API_KEY unset")
        from typesafe_sdk import RetryPolicy, TypeSafeClient

        self.client = TypeSafeClient(model=MODEL, retry=RetryPolicy(), timeout=30.0)
        self.calls = 0
        self.input_tokens = 0
        self.models: set[str] = set()

    def __call__(
        self, utterance: str, elements: list[dict[str, Any]], full_state: dict[str, Any]
    ):
        from typesafe_sdk import Noul

        texts = node_texts(elements)
        questions: dict[str, Any] = {}
        for e in elements:
            ref = int(e["ref"])
            description = _node_description(e, texts.get(ref, ""))
            for suffix, instruction, truth, falsity in (
                (
                    "relevant",
                    "Is this accessibility node relevant to the current user goal?",
                    "Yes when it helps choose or perform the next action for the goal.",
                    "No when it is unrelated decoration or structural noise.",
                ),
                (
                    "required",
                    "Does this accessibility node contain a label or value required to complete the goal?",
                    "Yes when omitting it could remove task-required text or a target.",
                    "No when the goal can be completed without this node's label or value.",
                ),
                (
                    "omit",
                    "Is it safe to omit this accessibility node from the planner observation?",
                    "Yes only when omission cannot hide a target, required value, or necessary context.",
                    "No when the node should remain visible to the planner.",
                ),
            ):
                questions[f"r{ref}_{suffix}"] = Noul(
                    instructions=f"{instruction}\nNode: {description}\nGoal: {utterance}",
                    criteria={"true": truth, "false": falsity},
                )
        response = self.client.system_one(full_state, questions, model=MODEL)
        self.calls += 1
        self.models.add(str(response.model))
        usage = response.usage
        self.input_tokens += int(usage.input_tokens or 0)
        values = validate_nouls(response.nouls, set(questions))
        selected: set[int] = set()
        for e in elements:
            ref = int(e["ref"])
            if ref <= 0:
                continue
            relevant = values[f"r{ref}_relevant"]
            required = values[f"r{ref}_required"]
            safe_to_omit = values[f"r{ref}_omit"]
            if relevant >= 0.5 or required >= 0.5 or safe_to_omit < 0.5:
                selected.add(ref)
        return close_subgraph(elements, selected)


class FakeNoulPruner:
    """Keyless deterministic transport for plumbing and selector invariants."""

    def __init__(self):
        self.calls = 0
        self.input_tokens = 0
        self.models: set[str] = set()

    def __call__(
        self, utterance: str, elements: list[dict[str, Any]], full_state: dict[str, Any]
    ):
        terms = goal_terms(utterance)
        labels = labels_for(elements)
        selected = {ref for ref, label in labels.items() if terms & goal_terms(label)}
        return close_subgraph(elements, selected)


class ObservationPolicy:
    """Adapter that changes only the observation passed to the Jev v1 planner."""

    def __init__(
        self,
        arm: str,
        planner: Callable,
        pruner: Callable | None,
        rng: random.Random,
        max_steps: int,
    ):
        self.arm = arm
        self.rng = rng
        self.pruner = pruner
        self.pruner_input_tokens_start = int(
            getattr(pruner, "input_tokens", 0) if pruner else 0
        )
        self.base = jev_v1.JevPolicy(
            planner, jev_v1.RunState(), max_steps, none_policy=NONE_POLICY
        )
        self.full_bytes: list[int] = []
        self.seen_bytes: list[int] = []
        self.full_nodes: list[int] = []
        self.seen_nodes: list[int] = []
        self.pruner_calls = 0

    def act(self, utterance: str, elements: list[dict[str, Any]], options):
        full_state = floor.serialize_state(
            utterance,
            elements,
            self.base.step,
            self.base.max_steps,
            list(self.base.history),
            options,
        )
        if self.arm == "full":
            seen = elements
        elif self.arm == "code":
            seen = code_selector(utterance, elements)
        elif self.arm == "random":
            seen = random_selector(elements, self.rng)
        elif self.arm == "jev":
            if self.pruner is None:
                raise RuntimeError("jev arm missing pruner")
            seen = self.pruner(utterance, elements, full_state)
            self.pruner_calls += 1
        else:
            raise ValueError(f"unknown arm {self.arm}")
        seen_state = floor.serialize_state(
            utterance,
            seen,
            self.base.step,
            self.base.max_steps,
            list(self.base.history),
            options,
        )
        self.full_bytes.append(compact_bytes(full_state))
        self.seen_bytes.append(compact_bytes(seen_state))
        self.full_nodes.append(len(elements))
        self.seen_nodes.append(len(seen))
        return self.base.act(utterance, seen, options)

    def row_metrics(self, pruner: Any | None) -> dict[str, Any]:
        return {
            "planner_input_tokens": self.base.input_tokens,
            "planner_output_tokens": self.base.output_tokens,
            "planner_models": sorted(self.base.models),
            "planner_calls": self.base.calls,
            "full_state_bytes": self.full_bytes,
            "seen_state_bytes": self.seen_bytes,
            "full_state_bytes_total": sum(self.full_bytes),
            "seen_state_bytes_total": sum(self.seen_bytes),
            "full_nodes_total": sum(self.full_nodes),
            "seen_nodes_total": sum(self.seen_nodes),
            "pruner_calls": self.pruner_calls,
            "pruner_input_tokens": int(
                getattr(pruner, "input_tokens", 0) if pruner else 0
            )
            - self.pruner_input_tokens_start,
            "pruner_models": sorted(
                getattr(pruner, "models", set()) if pruner else set()
            ),
        }


def _factory(
    holder: list[ObservationPolicy], arm: str, planner, pruner, max_steps: int
):
    def make(rng):
        p = ObservationPolicy(arm, planner, pruner, rng, max_steps)
        holder.append(p)
        return p

    return make


def task_names() -> list[str]:
    return floor.load_task_list()[:TASK_LIMIT]


def run(split: str, arm: str, out_path: Path) -> int:
    if split not in SPLIT_SEEDS or arm not in {"full", "code", "jev", "random"}:
        raise ValueError("invalid split or arm")
    expected = ROW_PATHS[(split, arm)]
    if out_path.resolve() != expected.resolve():
        raise ValueError(f"rows must be written to preregistered path {expected}")

    planner = jev_v1.LiveAsker()
    pruner = LiveNoulPruner() if arm == "jev" else None
    holder: list[ObservationPolicy] = []
    floor.POLICIES[arm] = _factory(holder, arm, planner, pruner, MAX_STEPS)
    tasks = task_names()
    benchmark = floor.benchmark_seeds(floor.load_task_list())
    bench_pairs = {(task, seed) for task, seeds in benchmark.items() for seed in seeds}
    bench_js = {
        floor.js_seed_for(seed) for seeds in benchmark.values() for seed in seeds
    }
    args = argparse.Namespace(
        max_steps=MAX_STEPS,
        episode_max_ms=floor.BENCHMARK_EPISODE_MAX_MS,
        wait_ms=floor.BENCHMARK_WAIT_MS,
    )
    floor.logging.getLogger().setLevel(floor.logging.WARNING)
    warning = floor.WarningCollector()
    floor.logging.getLogger().addHandler(warning)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    seed = SPLIT_SEEDS[split]
    with out_path.open("a", encoding="utf-8") as out:
        for task in tasks:
            if f"miniwob/{task}-v1" not in floor.gym.registry:
                raise RuntimeError(f"missing MiniWoB task {task}")
            env = floor.make_env(task, floor.BENCHMARK_WAIT_MS)
            try:
                row = floor.run_episode(
                    env,
                    task,
                    seed,
                    0,
                    arm,
                    args,
                    bench_pairs,
                    bench_js,
                    warning,
                )
            finally:
                env.close()
            if not holder:
                raise RuntimeError("policy factory did not run")
            row.update(holder[-1].row_metrics(pruner))
            row["arm"] = arm
            row["split"] = split
            row["prereg_seed"] = seed
            out.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            out.flush()
            rows.append(row)
            print(
                json.dumps(
                    {
                        k: row[k]
                        for k in ("task", "split", "arm", "success", "steps", "error")
                    },
                    sort_keys=True,
                ),
                file=sys.stderr,
                flush=True,
            )
    summary = {
        "split": split,
        "arm": arm,
        "episodes": len(rows),
        "successes": sum(float(r.get("success", 0)) > 0 for r in rows),
        "state_bytes": sum(r["seen_state_bytes_total"] for r in rows),
        "full_state_bytes": sum(r["full_state_bytes_total"] for r in rows),
        "planner_input_tokens": sum(r["planner_input_tokens"] for r in rows),
        "pruner_input_tokens": sum(r["pruner_input_tokens"] for r in rows),
        "models": sorted(
            {m for r in rows for m in r["planner_models"] + r["pruner_models"]}
        ),
    }
    print(json.dumps(summary, indent=2))
    return 0


def selftest() -> int:
    elements = [
        {
            "ref": 1,
            "parent": 0,
            "tag": "body",
            "kind": "BODY",
            "text": "",
            "value": "",
            "id": "",
            "classes": "",
            "is_leaf": False,
            "left": 0,
            "top": 0,
            "width": 100,
            "height": 100,
            "focused": False,
        },
        {
            "ref": 2,
            "parent": 1,
            "tag": "button",
            "kind": "BUTTON",
            "text": "Submit",
            "value": "",
            "id": "submit",
            "classes": "",
            "is_leaf": True,
            "left": 0,
            "top": 0,
            "width": 10,
            "height": 10,
            "focused": False,
        },
        {
            "ref": 3,
            "parent": 1,
            "tag": "div",
            "kind": "DIV",
            "text": "noise",
            "value": "",
            "id": "noise",
            "classes": "",
            "is_leaf": True,
            "left": 0,
            "top": 0,
            "width": 10,
            "height": 10,
            "focused": False,
        },
        {
            "ref": -1,
            "parent": 2,
            "tag": "t",
            "kind": "T",
            "text": "Submit",
            "value": "",
            "id": "",
            "classes": "",
            "is_leaf": True,
            "left": 0,
            "top": 0,
            "width": 10,
            "height": 10,
            "focused": False,
        },
    ]
    assert [e["ref"] for e in code_selector("Click Submit", elements)] == [1, 2, -1]
    rng = random.Random("random-arm|click-button|200")
    sampled = random_selector(elements, rng)
    assert sampled[0]["ref"] == 1
    assert all(
        e["ref"] > 0 or e["parent"] in {x["ref"] for x in sampled} for e in sampled
    )
    fake = FakeNoulPruner()
    jev_seen = fake("Click Submit", elements, {})
    assert [e["ref"] for e in jev_seen] == [1, 2, -1]
    try:
        validate_nouls({"x": 1.2}, {"x"})
    except ValueError:
        pass
    else:
        raise AssertionError("out-of-range Noul was accepted")
    holder: list[ObservationPolicy] = []
    floor.POLICIES["selftest"] = _factory(
        holder, "code", jev_v1.FakeAsker("greedy"), None, MAX_STEPS
    )
    policy = floor.POLICIES["selftest"](random.Random(0))
    action = policy.act("Click Submit", elements, {})
    assert action[0] in {"click", "none"}
    assert policy.seen_bytes[-1] <= policy.full_bytes[-1]
    print("SELFTEST PASS: selectors, subgraph closure, Noul refusal, Jev v1 adapter")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selftest")
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--split", choices=sorted(SPLIT_SEEDS), required=True)
    run_parser.add_argument(
        "--arm", choices=("full", "code", "jev", "random"), required=True
    )
    run_parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "selftest":
        return selftest()
    return run(args.split, args.arm, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
