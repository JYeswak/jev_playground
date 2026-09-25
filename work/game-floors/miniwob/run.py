#!/usr/bin/env python3
"""No-model floors for MiniWoB++ in the BrowserGym/AgentLab `miniwob` benchmark setting.

Runs the Farama `miniwob` package (Selenium + local Google Chrome, headless) over the
BrowserGym task list and seed scheme, with a seeded random policy and a generic
hand-written DOM heuristic. No model of any kind is called.

Published setting mirrored (BrowserGym 0.13.3 / @9e779f0, see tasks.json and the report):
  - 125 tasks, 5 seeds each drawn from np.random.RandomState(42).randint(0, SEED_MAX)
    with SEED_MAX = 2 ^ 32 == 34 (experiments/loop.py:35; benchmark/configs.py:101-114,
    benchmark/utils.py:50-78).
  - task seed s -> Math.seedrandom(np.random.RandomState(s).randint(0, 1000000))
    (core/task.py:20, miniwob/base.py:127-136).
  - max 10 actions per episode (configs.py:109, gym TimeLimit via loop.py:89).
  - core.EPISODE_MAX_TIME = 1,000,000 ms (miniwob/base.py:25,130), fresh page each episode.
  - 0.5 s pause after every action before the reward is read (core/env.py:416).
  - success = float(WOB_RAW_REWARD_GLOBAL > 0) (miniwob/base.py:183 @0.13.3).

Rows (one JSON object per episode) also carry MiniWoB's own time-scaled reward
(`env_reward`, as returned by the Farama env under the run's EPISODE_MAX_TIME) and the
counterfactual under MiniWoB's default 10 s timer (`reward_miniwob_10s`).
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import random
import re
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = Path("/tmp/jev-game-floors")
# Keep Selenium Manager's driver cache and Chrome's temporary profiles under /tmp.
os.environ.setdefault("SE_CACHE_PATH", str(SCRATCH / "selenium"))
os.environ.setdefault("SE_AVOID_STATS", "true")
os.environ.setdefault("TMPDIR", str(SCRATCH / "tmp"))
Path(os.environ["TMPDIR"]).mkdir(parents=True, exist_ok=True)

import gymnasium as gym  # noqa: E402
import miniwob  # noqa: E402
import numpy as np  # noqa: E402
from miniwob.action import ActionTypes  # noqa: E402

gym.register_envs(miniwob)

# ---------------------------------------------------------------- published setting
BENCHMARK_SEED_RNG = 42  # configs.py:111
BENCHMARK_SEED_MAX = 2 ^ 32  # loop.py:35 -- Python XOR, == 34
BENCHMARK_N_REPEATS = 5  # configs.py:101 (n_repeats=5)
BENCHMARK_MAX_STEPS = 10  # configs.py:109
BENCHMARK_EPISODE_MAX_MS = 1_000_000  # miniwob/base.py:25
BENCHMARK_WAIT_MS = 500  # core/env.py:416 time.sleep(0.5) after each action
MINIWOB_DEFAULT_EPISODE_MAX_MS = 10_000  # miniwob html/core/core.js:50

TASKS_FILE = HERE / "tasks.json"

# Policy logic compares upper-cased tags ("kind"): the Farama docs say "INPUT_text", but this
# Chrome (154) reports lowercase tag names ("input_text", "button") for the task pages.
TEXT_INPUT_TAGS = {
    "INPUT_TEXT",
    "INPUT_PASSWORD",
    "INPUT_EMAIL",
    "INPUT_NUMBER",
    "INPUT_SEARCH",
    "INPUT_TEL",
    "INPUT_URL",
    "TEXTAREA",
}

V3_ACTION_SPACE = os.environ.get("MINIWOB_V3") == "1"
V3_ARM = os.environ.get("MINIWOB_V3_ARM", "all")
V3_ARM_NAMES = {part.strip() for part in V3_ARM.split(",") if part.strip()}


def v3_on(name: str) -> bool:
    return V3_ACTION_SPACE and ("all" in V3_ARM_NAMES or name in V3_ARM_NAMES)


if v3_on("date_time"):
    TEXT_INPUT_TAGS.update({"INPUT_DATE", "INPUT_TIME"})
INTERACTIVE_TAGS = {"BUTTON", "A", "SELECT", "TEXTAREA", "LABEL", "OPTION"}
BUTTON_TAGS = {"BUTTON", "INPUT_SUBMIT", "INPUT_BUTTON", "INPUT_RESET"}


# ---------------------------------------------------------------- split and seeds
def load_task_list() -> list[str]:
    return [t["task"] for t in json.loads(TASKS_FILE.read_text())["tasks"]]


def benchmark_seeds(task_list: list[str]) -> dict[str, list[int]]:
    """BrowserGym make_env_args_list_from_repeat_tasks (benchmark/utils.py:50-78)."""
    rng = np.random.RandomState(BENCHMARK_SEED_RNG)
    return {
        task: [
            int(s)
            for s in rng.randint(
                low=0, high=BENCHMARK_SEED_MAX, size=BENCHMARK_N_REPEATS
            )
        ]
        for task in task_list
    }


def js_seed_for(task_seed: int) -> int:
    """AbstractBrowserTask.random = RandomState(seed) (core/task.py:20); miniwob/base.py:133."""
    return int(np.random.RandomState(task_seed).randint(0, 1000000))


def parse_seeds(spec: str) -> list[int]:
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if re.fullmatch(r"\d+-\d+", part):
            a, b = (int(x) for x in part.split("-"))
            out.extend(range(a, b + 1))
        else:
            out.append(int(part))
    return out


def episode_plan(tasks: list[str], seeds_spec: str, bench: dict[str, list[int]]):
    """Yield (task, seed, rep) in run order. rep numbers repeated (task, seed) pairs."""
    plan = []
    for task in tasks:
        seeds = bench[task] if seeds_spec == "benchmark" else parse_seeds(seeds_spec)
        seen: dict[int, int] = {}
        for s in seeds:
            rep = seen.get(s, 0)
            seen[s] = rep + 1
            plan.append((task, s, rep))
    return plan


# ---------------------------------------------------------------- observation helpers
def elements_from_obs(obs) -> list[dict]:
    els = []
    for e in obs["dom_elements"]:
        flags = [int(x) for x in e["flags"]]
        els.append(
            {
                "ref": int(e["ref"]),
                "parent": int(e["parent"]),
                "tag": str(e["tag"]),
                "kind": str(e["tag"]).upper(),
                "text": str(e["text"]),
                "value": str(e["value"]),
                "id": str(e["id"]),
                "classes": str(e["classes"]),
                "color": str(e.get("color", "")) if v3_on("color") else "",
                "left": float(e["left"][0]),
                "top": float(e["top"][0]),
                "width": float(e["width"][0]),
                "height": float(e["height"][0]),
                "focused": bool(flags[0]),
                "is_leaf": bool(flags[3]),
            }
        )
    return els


def select_options(driver) -> dict[int, list[str]]:
    """Option texts of every <select> in the last DOM snapshot.

    Farama's dom_elements drop zero-size nodes, so a closed <select> shows no options;
    BrowserGym's AXTree lists them as combobox children. This restores that information.
    """
    raw = (
        driver.execute_script(
            "var o={};for(var r in core.previousDOMInfo){var e=core.previousDOMInfo[r];"
            "if(e instanceof HTMLSelectElement){o[r]=Array.from(e.options).map(function(x){return x.text;});}}"
            "return o;"
        )
        or {}
    )
    return {int(k): list(v) for k, v in raw.items()}


def serialize_state(
    utterance: str,
    els: list[dict],
    step: int,
    max_steps: int,
    history: list[dict],
    options: dict[int, list[str]] | None = None,
) -> dict:
    """The JSON state a Jev arm receives for one decision.

    Only what a BrowserGym agent could see at decision time: the goal text (BrowserGym
    `goal`), the rendered DOM (text, values, ids, classes, geometry), the step budget and the
    arm's own past actions. Excluded: Farama `fields` (task-specific parses of the goal that
    published agents never got), rewards, and any simulator internals.
    Refs < 0 are text runs; clicking one clicks its parent element.
    """
    out = []
    for e in els:
        d: dict = {"ref": e["ref"], "parent": e["parent"], "tag": e["tag"]}
        if e["text"]:
            d["text"] = e["text"]
        if e["value"]:
            d["value"] = e["value"]
        if e["id"]:
            d["id"] = e["id"]
        if e["classes"]:
            d["classes"] = e["classes"]
        d["bbox"] = [
            round(e["left"]),
            round(e["top"]),
            round(e["width"]),
            round(e["height"]),
        ]
        if v3_on("color") and e.get("color"):
            d["color"] = e["color"]
        if e["focused"]:
            d["focused"] = True
        if options and e["ref"] in options:
            d["options"] = options[e["ref"]]
        out.append(d)
    return {
        "utterance": utterance,
        "step": step,
        "max_steps": max_steps,
        "actions": ["click(ref)", "type(ref, text)"],
        "history": history,
        "elements": out,
    }


def _label(e: dict) -> str:
    if e["text"]:
        return e["text"]
    if e["kind"] in BUTTON_TAGS:
        return e["value"]
    return ""


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip(" .,:;!?\"'")


def clickable_refs(els: list[dict]) -> list[int]:
    """Leaves, interactive elements, and parents of text runs (text runs are not clickable)."""
    by_ref = {e["ref"]: e for e in els}
    out: list[int] = []
    seen: set[int] = set()
    for e in els:
        r = e["ref"] if e["ref"] > 0 else e["parent"]
        if r <= 0 or r in seen:
            continue
        t = by_ref.get(r)
        if t is None or t["kind"] == "BODY":
            continue
        if (
            e["ref"] < 0
            or t["is_leaf"]
            or t["kind"] in INTERACTIVE_TAGS
            or t["kind"].startswith("INPUT_")
        ):
            seen.add(r)
            out.append(r)
    return out


def utterance_tokens(utterance: str) -> list[str]:
    toks = [w.strip("\"'.,:;!?()") for w in utterance.split()]
    return [t for t in toks if t] or ["a"]


# ---------------------------------------------------------------- policies
class RandomPolicy:
    """Uniform over clickable elements; a text field gets a random utterance token typed in."""

    name = "random"

    def __init__(self, rng: random.Random):
        self.rng = rng

    def act(
        self, utterance: str, els: list[dict], options
    ) -> tuple[str, int, str | None]:
        cands = clickable_refs(els)
        if not cands:
            return ("none", 0, None)
        ref = self.rng.choice(cands)
        kind = next(e["kind"] for e in els if e["ref"] == ref)
        if kind in TEXT_INPUT_TAGS:
            return ("type", ref, self.rng.choice(utterance_tokens(utterance)))
        return ("click", ref, None)


TYPE_VERBS = {"enter", "type", "write", "fill", "input"}
CLICK_VERBS = {
    "click",
    "select",
    "choose",
    "press",
    "check",
    "pick",
    "mark",
    "tick",
    "tap",
    "hit",
    "open",
    "expand",
    "find",
}
VERBS = TYPE_VERBS | CLICK_VERBS
_VERB_ALT = "|".join(sorted(VERBS))
_CLAUSE_SPLIT = re.compile(
    r"[.;!?](?:\s+|$)"
    rf"|,?\s+(?:and\s+then|then|and)\s+(?=(?:{_VERB_ALT})\b)"
    rf"|,\s+(?=(?:{_VERB_ALT})\b)",
    re.I,
)
_PREP_CUT = re.compile(
    r"\s+(?:into|in|from|on|to|with|under|inside|below|above|for|of|by|as)\s+.*$", re.I
)
_STOP_OBJECTS = {"nothing", "none", "it", "them", "all", "this", "that"}


def _clean_object(o: str) -> str:
    o = o.strip(" .,:;!?")
    o = re.sub(r"^(?:on|at)\s+", "", o, flags=re.I)
    o = re.sub(r"^(?:the|a|an)\s+", "", o, flags=re.I)
    o = re.sub(
        r"^(?:button|link|tab|checkbox|option|item|word|entry)\s+", "", o, flags=re.I
    )
    o = re.sub(
        r"\s+(?:buttons?|links?|tabs?|checkbox(?:es)?|box(?:es)?|options?|items?|icons?|"
        r"fields?|text\s*fields?|textbox(?:es)?)$",
        "",
        o,
        flags=re.I,
    )
    return o.strip()


def parse_intents(utterance: str) -> list[tuple[str, str]]:
    """Ordered (kind, object) intents from the utterance; kind is 'type' or 'click'."""
    quotes: list[str] = []

    def _stash(m):
        quotes.append(m.group(1) if m.group(1) is not None else m.group(2))
        return f"\x00{len(quotes) - 1}\x00"

    masked = re.sub(r'"([^"]*)"|\u201c([^\u201d]*)\u201d', _stash, utterance)
    intents: list[tuple[str, str]] = []
    for clause in _CLAUSE_SPLIT.split(masked):
        words = clause.split()
        idx = next(
            (i for i, w in enumerate(words) if w.lower().strip(",:") in VERBS), None
        )
        if idx is None:
            continue
        kind = "type" if words[idx].lower().strip(",:") in TYPE_VERBS else "click"
        rest = " ".join(words[idx + 1 :])
        qidx = [int(m) for m in re.findall(r"\x00(\d+)\x00", rest)]
        if qidx:
            objs = [quotes[i] for i in qidx]
        else:
            rest = _PREP_CUT.sub("", rest)
            objs = [
                _clean_object(o) for o in re.split(r",\s*|\s+and\s+|\s+or\s+", rest)
            ]
        for o in objs:
            if o and o.lower() not in _STOP_OBJECTS:
                intents.append((kind, o))
    return intents


def best_match(target: str, els: list[dict], exclude: set[int]) -> int | None:
    t = _norm(target)
    if not t:
        return None
    by_ref = {e["ref"]: e for e in els}
    t_re = re.compile(r"(?<!\w)" + re.escape(t) + r"(?!\w)")
    best, best_key = None, None
    for order, e in enumerate(els):
        lab = _norm(_label(e))
        if not lab:
            continue
        if lab == t:
            score = 3
        elif t_re.search(lab) and len(lab) <= 2 * len(t) + 12:
            score = 2
        elif all(tok in lab.split() for tok in t.split()):
            score = 1
        else:
            continue
        r = e["ref"] if e["ref"] > 0 else e["parent"]
        tgt = by_ref.get(r)
        if r <= 0 or r in exclude or tgt is None or tgt["kind"] == "BODY":
            continue
        interactive = tgt["kind"] in INTERACTIVE_TAGS or tgt["kind"].startswith(
            "INPUT_"
        )
        key = (score, interactive, -(tgt["width"] * tgt["height"]), -order)
        if best_key is None or key > best_key:
            best, best_key = r, key
    return best


class ScriptedPolicy:
    """Generic DOM heuristic, no per-task code.

    1. Parse the utterance into ordered intents: clauses split at sentence ends and at
       ', ' / ' and ' / ' then ' before a verb; a clause's first verb decides the kind
       (enter/type/write/fill/input -> type, click/select/choose/press/check/... -> click);
       objects are the quoted spans, else the verb's object with prepositional tail,
       articles and role nouns (button, link, tab, checkbox, ...) stripped, split on , / and / or.
    2. Execute intents in order, one per step: 'type' fills the next untouched text input
       (DOM order); 'click' clicks the best text match (exact > whole-word containment >
       all-tokens; interactive first, then smaller); if no visible match and an unused
       <select> exists whose options contain the object, type the object into it.
       Unmatched intents are skipped without spending a step.
    3. Then click an unclicked button whose label appears in the utterance, else one
       labelled 'submit'.
    4. Then fall back to a seeded random clickable element (same rule as RandomPolicy).
    """

    name = "scripted"

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.intents: list[tuple[str, str]] | None = None
        self.clicked: set[int] = set()
        self.typed: set[int] = set()
        self.fallback = RandomPolicy(rng)

    def act(
        self, utterance: str, els: list[dict], options
    ) -> tuple[str, int, str | None]:
        if self.intents is None:
            self.intents = parse_intents(utterance)
        while self.intents:
            kind, obj = self.intents.pop(0)
            if kind == "type":
                ref = next(
                    (
                        e["ref"]
                        for e in els
                        if e["kind"] in TEXT_INPUT_TAGS
                        and e["ref"] > 0
                        and e["ref"] not in self.typed
                    ),
                    None,
                )
                if ref is None:
                    continue
                self.typed.add(ref)
                return ("type", ref, obj)
            ref = best_match(obj, els, self.clicked)
            if ref is not None:
                self.clicked.add(ref)
                return ("click", ref, None)
            for sref, opts in (options or {}).items():
                if sref not in self.typed and any(_norm(obj) == _norm(o) for o in opts):
                    self.typed.add(sref)
                    return ("type", sref, obj)
        u = _norm(utterance)
        buttons = [
            e
            for e in els
            if e["kind"] in BUTTON_TAGS and e["ref"] not in self.clicked and _label(e)
        ]
        for e in buttons:
            if re.search(r"(?<!\w)" + re.escape(_norm(_label(e))) + r"(?!\w)", u):
                self.clicked.add(e["ref"])
                return ("click", e["ref"], None)
        for e in buttons:
            if _norm(_label(e)) == "submit":
                self.clicked.add(e["ref"])
                return ("click", e["ref"], None)
        return self.fallback.act(utterance, els, options)


POLICIES = {"random": RandomPolicy, "scripted": ScriptedPolicy}


# ---------------------------------------------------------------- env plumbing
_PATCH_JS = """
var X = arguments[0];
core.EPISODE_MAX_TIME = X;
if (core.EP_TIMER !== null) {
  clearTimeout(core.EP_TIMER);
  var rem = Math.max(0, X - (new Date().getTime() - core.ept0));
  core.EP_TIMER = setTimeout(function(){ core.endEpisode(-1, false, 'timed out'); }, rem);
}
window.__jev_end = null;
if (!core.__jev_wrapped) {
  core.__jev_end_orig = core.endEpisode;
  core.endEpisode = function(reward, time_proportional, reason) {
    if (core.EP_TIMER !== null && window.__jev_end === null) {
      window.__jev_end = {dt: new Date().getTime() - core.ept0, tp: !!time_proportional, r: reward};
    }
    return core.__jev_end_orig(reward, time_proportional, reason);
  };
  core.__jev_wrapped = true;
}
return core.EPISODE_MAX_TIME;
"""


class WarningCollector(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.records: list[str] = []

    def emit(self, record):
        self.records.append(record.getMessage()[:200])


def make_env(task: str, wait_ms: float):
    env = gym.make(
        f"miniwob/{task}-v1",
        render_mode=None,
        wait_ms=wait_ms,
        refresh_freq=1,
        data_mode="default",
        disable_env_checker=True,
    )
    env.unwrapped.set_record_screenshots(False)
    return env


def to_env_action(env, act):
    kind, ref, text = act
    u = env.unwrapped
    if kind == "click":
        return u.create_action(ActionTypes.CLICK_ELEMENT, ref=ref)
    if kind == "type":
        return u.create_action(
            ActionTypes.FOCUS_ELEMENT_AND_TYPE_TEXT, ref=ref, text=text
        )
    return u.create_action(ActionTypes.NONE)


def drag_env_actions(env, coords):
    source, target = coords
    u = env.unwrapped
    source_xy = np.asarray(source, dtype=np.float32)
    target_xy = np.asarray(target, dtype=np.float32)
    return [
        u.create_action(ActionTypes.MOUSEDOWN_COORDS, coords=source_xy),
        u.create_action(ActionTypes.MOVE_COORDS, coords=target_xy),
        u.create_action(ActionTypes.MOUSEUP_COORDS, coords=target_xy),
    ]


def resolve_ref(els: list[dict], ref: int) -> int:
    if ref < 0:
        return next((e["parent"] for e in els if e["ref"] == ref), ref)
    return ref


def run_episode(
    env,
    task: str,
    seed: int,
    rep: int,
    policy_name: str,
    args,
    bench_pairs,
    bench_js,
    warn: WarningCollector,
    dump_path: str | None = None,
) -> dict:
    js_seed = js_seed_for(seed)
    row = {
        "env": "miniwob",
        "benchmark": "browsergym-miniwob",
        "task": task,
        "policy": policy_name,
        "seed": seed,
        "rep": rep,
        "js_seed": js_seed,
        "seed_in_benchmark_list": (task, seed) in bench_pairs,
        "js_seed_in_benchmark_js_seeds": js_seed in bench_js,
        "max_steps": args.max_steps,
        "episode_max_ms": args.episode_max_ms,
        "wait_ms": args.wait_ms,
        "data_mode": "default",
        "page_reload_each_episode": True,
        "action_space": "farama CLICK_ELEMENT(ref) + FOCUS_ELEMENT_AND_TYPE_TEXT(ref,text)"
        + (" + code-enumerated DRAG(source,target)" if v3_on("drag") else ""),
        "utterance": None,
        "success": 0.0,
        "success_strict": 0.0,
        "raw_reward": 0.0,
        "env_reward": 0.0,
        "reward_miniwob_10s": 0.0,
        "done": False,
        "truncated": False,
        "reason": None,
        "steps": 0,
        "wall_s": None,
        "reset_s": None,
        "mean_step_s": None,
        "max_step_s": None,
        "actions": [],
        "action_warnings": [],
        "error": None,
    }
    warn.records.clear()
    t0 = time.perf_counter()
    step_times: list[float] = []
    try:
        rng = random.Random(f"{policy_name}|{task}|{seed}|{rep}")
        policy = POLICIES[policy_name](rng)
        tr = time.perf_counter()
        obs, info = env.reset(seed=js_seed)
        driver = env.unwrapped.instance.driver
        max_ms = driver.execute_script(_PATCH_JS, args.episode_max_ms)
        row["reset_s"] = round(time.perf_counter() - tr, 4)
        assert int(max_ms) == args.episode_max_ms, max_ms
        utterance = obs["utterance"]
        row["utterance"] = utterance
        history: list[dict] = []
        done = False
        info = {}
        for step in range(args.max_steps):
            els = elements_from_obs(obs)
            opts = select_options(driver)
            if step == 0:
                # Compact JSON: the exact bytes a Jev arm would be sent as `state`.
                blob = json.dumps(
                    serialize_state(
                        utterance, els, step, args.max_steps, history, opts
                    ),
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
                row["state_bytes_step0"] = len(blob.encode())
                if dump_path:
                    Path(dump_path).write_text(blob + "\n")
            kind, ref, text = policy.act(utterance, els, opts)
            if kind != "drag":
                ref = resolve_ref(els, ref)
            ts = time.perf_counter()
            if kind == "drag":
                for action in drag_env_actions(env, ref):
                    obs, reward, done, trunc, info = env.step(action)
                    if done:
                        break
            else:
                obs, reward, done, trunc, info = env.step(
                    to_env_action(env, (kind, ref, text))
                )
            step_times.append(time.perf_counter() - ts)
            rec = {"type": kind, "ref": ref}
            if text is not None:
                rec["text"] = text
            history.append(rec)
            row["steps"] = step + 1
            if done:
                break
        row["actions"] = history
        row["done"] = bool(done)
        row["truncated"] = not done
        raw = float(info.get("raw_reward") or 0.0) if done else 0.0
        row["raw_reward"] = raw
        row["env_reward"] = float(info.get("env_reward") or 0.0) if done else 0.0
        row["reason"] = info.get("reason") if done else None
        row["success"] = float(
            raw > 0
        )  # BrowserGym: partial credit (e.g. 0.2) counts as success
        row["success_strict"] = float(
            raw >= 1.0
        )  # MiniWoB get_binary_reward (reward.py:43-51)
        # Counterfactual MiniWoB reward under the default 10 s timer (core.js:98-128).
        end = driver.execute_script("return window.__jev_end;")
        if done and end:
            dt = float(end["dt"])
            row["episode_ms"] = dt
            if dt > MINIWOB_DEFAULT_EPISODE_MAX_MS:
                row["reward_miniwob_10s"] = -1.0
            elif end["tp"]:
                row["reward_miniwob_10s"] = float(end["r"]) * max(
                    0.0, 1.0 - dt / MINIWOB_DEFAULT_EPISODE_MAX_MS
                )
            else:
                row["reward_miniwob_10s"] = float(end["r"])
        else:
            dt = float(
                driver.execute_script("return new Date().getTime() - core.ept0;")
            )
            row["episode_ms"] = dt
            row["reward_miniwob_10s"] = (
                -1.0 if dt > MINIWOB_DEFAULT_EPISODE_MAX_MS else 0.0
            )
    except Exception as exc:  # recorded, never dropped
        row["error"] = (
            f"{type(exc).__name__}: {str(exc).splitlines()[0][:300] if str(exc) else ''}"
        )
        row["traceback_tail"] = traceback.format_exc().strip().splitlines()[-3:]
        row["success"] = 0.0
    row["wall_s"] = round(time.perf_counter() - t0, 4)
    if step_times:
        row["mean_step_s"] = round(sum(step_times) / len(step_times), 4)
        row["max_step_s"] = round(max(step_times), 4)
    row["action_warnings"] = list(warn.records)
    return row


def summarize(rows: list[dict]) -> dict:
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r["policy"], []).append(r)
    out = {}
    for pol, rs in by.items():
        n = len(rs)
        p = sum(r["success"] for r in rs) / n
        step_s = [r["mean_step_s"] for r in rs if r["mean_step_s"] is not None]
        out[pol] = {
            "episodes": n,
            "success_mean": round(p, 4),
            "success_se_binomial": round(math.sqrt(p * (1 - p) / n), 4),
            "success_strict_mean": round(
                sum(r.get("success_strict", 0.0) for r in rs) / n, 4
            ),
            "raw_reward_mean": round(sum(r["raw_reward"] for r in rs) / n, 4),
            "env_reward_mean": round(sum(r["env_reward"] for r in rs) / n, 4),
            "reward_miniwob_10s_mean": round(
                sum(r["reward_miniwob_10s"] for r in rs) / n, 4
            ),
            "errors": sum(1 for r in rs if r["error"]),
            "mean_s_per_step": round(sum(step_s) / len(step_s), 4) if step_s else None,
            "mean_wall_s_per_episode": round(sum(r["wall_s"] for r in rs) / n, 3),
        }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--policy",
        default="random",
        help="random | scripted | comma list (policies share one Chrome per task)",
    )
    ap.add_argument(
        "--seeds",
        default="benchmark",
        help="'benchmark' = BrowserGym's 5 per-task seeds (published), or a-b / a,b,c for every task",
    )
    ap.add_argument(
        "--tasks",
        default="all",
        help="'all' = the 125 BrowserGym tasks in tasks.json order, or a comma list",
    )
    ap.add_argument(
        "--shard",
        default="0/1",
        help="k/n: run tasks[k::n] (task-level sharding for parallel processes)",
    )
    ap.add_argument("--max-steps", type=int, default=BENCHMARK_MAX_STEPS)
    ap.add_argument("--episode-max-ms", type=int, default=BENCHMARK_EPISODE_MAX_MS)
    ap.add_argument(
        "--wait-ms",
        type=float,
        default=BENCHMARK_WAIT_MS,
        help="pause after every action before reading reward/observation (BrowserGym: 500)",
    )
    ap.add_argument("--out", help="output JSONL (appended)")
    ap.add_argument(
        "--dump-state",
        help="write one real step-0 state from a dev seed (>=9000) and exit",
    )
    ap.add_argument("--dump-task", default="click-checkboxes")
    ap.add_argument("--dump-seed", type=int, default=9000)
    ap.add_argument(
        "--print-split",
        action="store_true",
        help="print tasks + benchmark seeds as JSON and exit",
    )
    args = ap.parse_args(argv)

    all_tasks = load_task_list()
    bench = benchmark_seeds(all_tasks)
    bench_pairs = {(t, s) for t, ss in bench.items() for s in ss}
    bench_js = {js_seed_for(s) for ss in bench.values() for s in ss}

    if args.print_split:
        print(
            json.dumps(
                {
                    "seed_max": BENCHMARK_SEED_MAX,
                    "seeds": bench,
                    "js_seeds": {
                        t: [js_seed_for(s) for s in ss] for t, ss in bench.items()
                    },
                },
                indent=1,
            )
        )
        return 0

    logging.getLogger().setLevel(logging.WARNING)
    warn = WarningCollector()
    logging.getLogger().addHandler(warn)

    if args.dump_state:
        if args.dump_seed < 9000 or (args.dump_task, args.dump_seed) in bench_pairs:
            ap.error("--dump-state must use a dev seed >= 9000")
        env = make_env(args.dump_task, args.wait_ms)
        try:
            row = run_episode(
                env,
                args.dump_task,
                args.dump_seed,
                0,
                "scripted",
                args,
                bench_pairs,
                bench_js,
                warn,
                dump_path=args.dump_state,
            )
        finally:
            env.close()
        print(
            json.dumps(
                {k: row[k] for k in ("task", "seed", "utterance", "success", "error")}
            )
        )
        return 0

    if not args.out:
        ap.error("--out is required")
    policies = [p.strip() for p in args.policy.split(",") if p.strip()]
    for p in policies:
        if p not in POLICIES:
            ap.error(f"unknown policy {p}")
    tasks = (
        all_tasks
        if args.tasks == "all"
        else [t.strip() for t in args.tasks.split(",") if t.strip()]
    )
    for t in tasks:
        if t not in bench:
            ap.error(f"{t} is not in the BrowserGym miniwob task list")
    k, n = (int(x) for x in args.shard.split("/"))
    tasks = tasks[k::n]
    plan = episode_plan(tasks, args.seeds, bench)

    out = open(args.out, "a")
    rows: list[dict] = []
    by_task: dict[str, list[tuple[int, int]]] = {}
    for task, seed, rep in plan:
        by_task.setdefault(task, []).append((seed, rep))
    t_run = time.perf_counter()
    for task, pairs in by_task.items():
        available = f"miniwob/{task}-v1" in gym.registry
        env, launch_s, launch_err = None, None, None
        if available:
            tl = time.perf_counter()
            try:
                env = make_env(task, args.wait_ms)
            except Exception as exc:
                launch_err = f"{type(exc).__name__}: {str(exc).splitlines()[0][:300] if str(exc) else ''}"
            launch_s = round(time.perf_counter() - tl, 3)
        for pol in policies:
            for seed, rep in pairs:
                if env is None:
                    row = {
                        "env": "miniwob",
                        "benchmark": "browsergym-miniwob",
                        "task": task,
                        "policy": pol,
                        "seed": seed,
                        "rep": rep,
                        "js_seed": js_seed_for(seed),
                        "seed_in_benchmark_list": (task, seed) in bench_pairs,
                        "max_steps": args.max_steps,
                        "episode_max_ms": args.episode_max_ms,
                        "wait_ms": args.wait_ms,
                        "success": 0.0,
                        "success_strict": 0.0,
                        "raw_reward": 0.0,
                        "env_reward": 0.0,
                        "reward_miniwob_10s": 0.0,
                        "steps": 0,
                        "wall_s": 0.0,
                        "mean_step_s": None,
                        "error": launch_err
                        or f"unavailable: miniwob/{task}-v1 not registered in miniwob 1.1.0",
                    }
                else:
                    row = run_episode(
                        env, task, seed, rep, pol, args, bench_pairs, bench_js, warn
                    )
                    if row["error"]:
                        try:
                            env.close()
                        except Exception:
                            pass
                        try:
                            env = make_env(task, args.wait_ms)
                        except Exception as exc:
                            env = None
                            launch_err = f"{type(exc).__name__}: {str(exc).splitlines()[0][:300]}"
                row["env_launch_s"] = launch_s
                launch_s = None
                out.write(json.dumps(row) + "\n")
                out.flush()
                rows.append(row)
                print(
                    f"{task:28s} {pol:8s} seed={seed:<5d} rep={rep} success={row['success']:.0f} "
                    f"raw={row['raw_reward']:+.2f} r10={row['reward_miniwob_10s']:+.2f} steps={row['steps']:2d} "
                    f"wall={row['wall_s']:.2f}s err={row['error']}",
                    file=sys.stderr,
                    flush=True,
                )
        if env is not None:
            env.close()
    out.close()
    summary = summarize(rows)
    summary["_run"] = {
        "tasks": len(by_task),
        "episodes": len(rows),
        "wall_s_total": round(time.perf_counter() - t_run, 1),
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
