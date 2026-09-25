#!/usr/bin/env python3
"""Live Jev arm on the MiniWoB++ BrowserGym split (bead jev-jy7t.1.5).

The floor harness work/game-floors/miniwob/run.py runs every episode. Its split, seeds, env,
0.5 s wait, 10-step cap, action space and metric are used unchanged. This file adds one policy,
`jev`, beside the floor's `random` and `scripted`, and a resumable driver for it.

One TypeSafe request per step, official Python SDK, model pinned jev-1.13.0:
  state      the floor's serialize_state(...) output, unchanged: the utterance, the step, the
             step budget, this episode's actions so far, and the DOM elements with bbox
  "action"   Choice over code-enumerated {element, operation} candidates: click [ref] for every
             ref the floor's clickable_refs() returns, type [ref] for every text input and every
             <select> one of whose options is a span of the utterance, and "none". At most 255.
  "text_<r>" one Choice per type candidate r over code-extracted spans of the utterance: quoted
             strings, then tokens, then contiguous token n-grams by length, at most 255. For a
             <select>, only the spans equal to one of its options.
The action head decides. A text head is read only when the action is type [r], following
jev-ultrafast's operation/target fan-out (jev-ultrafast/jev_ultrafast/model.py:81-148).
Jev never writes text; it only picks.

A failed or invalid answer makes its step a no-op (Farama NONE) and is recorded. Three failed
calls in a row, or an HTTP 401/402/403, halt the run without writing the episode in progress,
so a resumed run replays that episode from reset.

Preregistration: docs/demos/upstream-repro/miniwob-jev-prereg-20260925.md, committed before the
first live call; `live` refuses to start unless it and this file are committed and clean.

  P=/tmp/jev-miniwob-jev/venv/bin/python     (uv venv; see the prereg)
  $P work/miniwob-jev/jev_arm.py selftest                       keyless, no Chrome
  $P work/miniwob-jev/jev_arm.py dev --fake greedy --tasks click-button --seeds 9000-9001
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \\
    $P work/miniwob-jev/jev_arm.py live --shard k/4             live, resumable
  python3 work/miniwob-jev/score.py                             keyless re-score

Never prints a key.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FLOOR_PATH = ROOT / "work" / "game-floors" / "miniwob" / "run.py"
PREREG = "docs/demos/upstream-repro/miniwob-jev-prereg-20260925.md"
PREREG_V2 = "docs/demos/upstream-repro/miniwob-jev-v2-prereg-20260925.md"
PREREG_V3 = "docs/demos/upstream-repro/miniwob-jev-v3-prereg-20260925.md"
ROWS_DIR = HERE / "rows"

MODEL = "jev-1.13.0"
V3_ENABLED = os.environ.get("MINIWOB_V3") == "1"
V3_ARM = os.environ.get("MINIWOB_V3_ARM", "all")


def v3_on(name: str) -> bool:
    return V3_ENABLED and V3_ARM in {"all", name}


OPTION_CAP = 255  # docs-mirror/typesafe/api.md:125, per Choice
NONE_KEY = "none: do nothing this step"
HALT_AFTER_CONSECUTIVE_FAILURES = 3
HALT_STATUSES = {401, 402, 403}
REQUEST_TIMEOUT_S = 30.0
SPAN_STRIP = "\"'.,:;!?()"
LABEL_TEXT_CHARS = 60
LABEL_VALUE_CHARS = 40


def load_floor():
    """Import the floor runner under its own name (this directory has no run.py to shadow)."""
    if "miniwob_floor" in sys.modules:
        return sys.modules["miniwob_floor"]
    spec = importlib.util.spec_from_file_location("miniwob_floor", FLOOR_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["miniwob_floor"] = mod
    spec.loader.exec_module(mod)
    return mod


floor = load_floor()


# ------------------------------------------------------------------ candidates and questions
def utterance_spans(utterance: str, cap: int = OPTION_CAP) -> list[str]:
    """Quoted strings, then tokens, then contiguous token n-grams by length; deduped, capped.

    Every span is stripped of SPAN_STRIP at its ends. N-gram words drop their own quote marks
    first, so a quoted word joins its neighbours without a stray quote inside the span.
    """
    out: list[str] = []
    seen: set[str] = set()

    def add(s: str, quoted: bool = False) -> bool:
        raw = s.strip()
        if v3_on("quoted") and quoted:
            s = raw
        else:
            s = raw.strip(SPAN_STRIP).strip()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
        return len(out) >= cap

    for a, b in re.findall(r'"([^"]*)"|\u201c([^\u201d]*)\u201d', utterance):
        if add(a or b, quoted=True):
            return out
    words = utterance.split()
    for w in words:
        if add(w):
            return out
    bare = [w.strip('"\u201c\u201d') for w in words]
    for n in range(2, len(words) + 1):
        for i in range(len(words) - n + 1):
            if add(" ".join(bare[i : i + n])):
                return out
    return out


def _clip(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "\u2026"


def element_texts(els: list[dict]) -> dict[int, str]:
    """Visible text per positive ref: own text, else its text runs, else its <label>'s runs."""
    by_ref = {e["ref"]: e for e in els}
    runs: dict[int, list[str]] = {}
    for e in els:
        if e["ref"] < 0 and e["text"]:
            runs.setdefault(e["parent"], []).append(e["text"])
    out: dict[int, str] = {}
    for e in els:
        if e["ref"] <= 0:
            continue
        t = e["text"] or " ".join(runs.get(e["ref"], []))
        if not t and e["kind"] in floor.BUTTON_TAGS:
            t = e["value"]
        parent = by_ref.get(e["parent"])
        if not t and parent is not None and parent["kind"] == "LABEL":
            t = " ".join(runs.get(parent["ref"], []))
        out[e["ref"]] = t
    return out


def describe(e: dict, text: str) -> str:
    parts = [e["tag"]]
    if e["id"]:
        parts.append("#" + e["id"])
    if text:
        parts.append(json.dumps(_clip(text, LABEL_TEXT_CHARS), ensure_ascii=False))
    if e["value"] and e["kind"] not in floor.BUTTON_TAGS:
        parts.append(
            "value="
            + json.dumps(_clip(e["value"], LABEL_VALUE_CHARS), ensure_ascii=False)
        )
    return " ".join(parts)


def _interactive(e: dict) -> bool:
    return e["kind"] in floor.INTERACTIVE_TAGS or e["kind"].startswith("INPUT_")


TIME_RE = re.compile(r"\b(\d{1,2}):(\d{2})\s*(AM|PM)\b", re.I)


def format_time_for_input(value: str) -> str | None:
    match = TIME_RE.search(value)
    if not match:
        return None
    hour = int(match.group(1)) % 12
    if match.group(3).upper() == "PM":
        hour += 12
    return f"{hour:02d}:{match.group(2)}"


def build_candidates(
    utterance: str,
    els: list[dict],
    options: dict[int, list[str]] | None,
    include_none: bool = True,
):
    """Return (actions, text_spans, truncated_clicks).

    actions: ordered {key: (kind, ref)} with kind in click/type/none, at most OPTION_CAP.
    text_spans: {ref: [span, ...]} for every type candidate kept.
    Over the cap, every type candidate and "none" are kept, then click candidates on
    interactive elements, then the rest, each group in DOM order; kept options stay in DOM order.
    """
    by_ref = {e["ref"]: e for e in els}
    texts = element_texts(els)
    spans = utterance_spans(utterance)
    page_spans = []
    if v3_on("page_text"):
        for e in els:
            for value in (e.get("text", ""), e.get("value", "")):
                value = str(value).strip()
                if value and len(value) <= 160 and value not in page_spans:
                    page_spans.append(value)
    options = options or {}
    order = {e["ref"]: i for i, e in enumerate(els)}

    type_spans: dict[int, list[str]] = {}
    for e in els:
        r = e["ref"]
        if r <= 0:
            continue
        if e["kind"] in floor.TEXT_INPUT_TAGS or (
            v3_on("date_time") and e["kind"] in {"INPUT_DATE", "INPUT_TIME"}
        ):
            candidates = list(dict.fromkeys(spans + page_spans))
            if v3_on("date_time") and e["kind"] == "INPUT_TIME":
                formatted = format_time_for_input(utterance)
                candidates = [
                    s for s in candidates if not re.fullmatch(r"\d{1,2}:\d{2}", s)
                ]
                if formatted:
                    candidates.insert(0, formatted)
            type_spans[r] = list(dict.fromkeys(candidates))
        elif e["kind"] == "SELECT" and r in options:
            opts = {floor._norm(o) for o in options[r]}
            ok = [s for s in spans if floor._norm(s) in opts]
            if ok:
                type_spans[r] = ok
    clicks = floor.clickable_refs(els)
    drag_pairs = []
    if v3_on("drag") and re.search(r"\b(?:drag|draw|resize|slider)\b", utterance, re.I):
        drag_refs = [
            e for e in els if e["ref"] > 0 and e["width"] > 0 and e["height"] > 0
        ]
        for source in drag_refs:
            for target in drag_refs:
                if source["ref"] == target["ref"]:
                    continue
                drag_pairs.append(
                    (
                        (
                            source["left"] + source["width"] / 2,
                            source["top"] + source["height"] / 2,
                        ),
                        (
                            target["left"] + target["width"] / 2,
                            target["top"] + target["height"] / 2,
                        ),
                        source["ref"],
                        target["ref"],
                    )
                )

    budget = OPTION_CAP - (1 if include_none else 0)
    types = sorted(type_spans, key=lambda r: order[r])[:budget]
    budget -= len(types)
    ranked = sorted(clicks, key=lambda r: (not _interactive(by_ref[r]), order[r]))
    kept_clicks = set(ranked[:budget])
    truncated = len(clicks) - len(kept_clicks)
    budget -= len(kept_clicks)

    items: list[tuple[int, int, str, int]] = []
    for r in clicks:
        if r in kept_clicks:
            items.append((order[r], 0, "click", r))
    for r in types:
        items.append((order[r], 1, "type", r))
    items.sort()
    actions: dict[str, tuple[str, int]] = {}
    for _, _, kind, r in items:
        actions[f"{kind} [{r}] {describe(by_ref[r], texts.get(r, ''))}"] = (kind, r)
    if v3_on("drag"):
        for source_xy, target_xy, source_ref, target_ref in drag_pairs[
            : max(0, budget)
        ]:
            actions[f"drag [{source_ref}] -> [{target_ref}]"] = (
                "drag",
                (source_xy, target_xy),
            )
    if include_none:
        actions[NONE_KEY] = ("none", 0)
    return actions, {r: type_spans[r] for r in types}, truncated


def action_instructions(utterance: str) -> str:
    return (
        f"Goal: {utterance}\n"
        "Choose the one next action that makes progress on this goal on the current web page. "
        "The state lists the page elements (ref, tag, text, value, id, classes, bbox) and the "
        "actions already taken this episode (history). "
        "'click [ref]' clicks that element. 'type [ref]' types text taken from the goal into "
        "that field or dropdown; the text is chosen separately. "
        "Do not repeat an action from the history unless the goal requires doing it again. "
        "Choose 'none' only if no offered action makes progress."
    )


def text_instructions(utterance: str, ref: int, label: str) -> str:
    return (
        f"Goal: {utterance}\n"
        f"Which text from the goal{'' if not v3_on('page_text') else ' or visible page'} should be typed into element [{ref}] ({label})?"
    )


def build_questions(utterance, els, actions, text_spans) -> dict[str, dict]:
    by_ref = {e["ref"]: e for e in els}
    texts = element_texts(els)
    qs: dict[str, dict] = {
        "action": {
            "type": "choice",
            "instructions": action_instructions(utterance),
            "criteria": {k: None for k in actions},
        }
    }
    for r, spans in text_spans.items():
        qs[f"text_{r}"] = {
            "type": "choice",
            "instructions": text_instructions(
                utterance, r, describe(by_ref[r], texts.get(r, ""))
            ),
            "criteria": {s: None for s in spans},
        }
    return qs


def validate_choice(answer, ids) -> dict:
    """jev-ultrafast's validate_choice invariants; refuse, never coerce."""
    ids = set(ids)
    try:
        probs = answer["probabilities"]
        nums = [*probs.values(), answer["confidence"]]
        ok = (
            answer["choice"] in ids
            and set(probs) == ids
            and all(
                type(n) in (int, float) and math.isfinite(n) and 0 <= n <= 1
                for n in nums
            )
            and abs(sum(probs.values()) - 1) < 0.02
            and probs[answer["choice"]] >= max(probs.values()) - 1e-6
        )
    except (KeyError, TypeError, ValueError, AttributeError):
        ok = False
    if not ok:
        raise ValueError("invalid Choice answer; no action executed")
    return answer


# ------------------------------------------------------------------ askers
class MissingKey(RuntimeError):
    pass


class HaltRun(BaseException):
    """Escapes the floor's run_episode `except Exception`: the episode row is not written."""


class LiveAsker:
    """The official SDK, model pinned; a missing key raises before any client exists."""

    def __init__(self):
        if not os.environ.get("TYPESAFE_API_KEY", "").strip():
            raise MissingKey("TYPESAFE_API_KEY unset")
        from typesafe_sdk import RetryPolicy, TypeSafeClient

        self.client = TypeSafeClient(
            model=MODEL, retry=RetryPolicy(), timeout=REQUEST_TIMEOUT_S
        )

    def __call__(self, state: dict, questions: dict[str, dict]) -> dict:
        from typesafe_sdk import Choice

        resp = self.client.system_one(
            state,
            {
                n: Choice(instructions=q["instructions"], criteria=q["criteria"])
                for n, q in questions.items()
            },
            model=MODEL,
        )
        return {
            "model": resp.model,
            "answers": {
                n: {
                    "choice": a.choice,
                    "confidence": float(a.confidence),
                    "probabilities": {k: float(v) for k, v in a.probabilities.items()},
                }
                for n, a in resp.choices.items()
            },
            "usage": {
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
            },
        }


def _uniform_with(ids: list[str], pick: str) -> dict:
    rest = (0.5 / (len(ids) - 1)) if len(ids) > 1 else 0.0
    probs = {k: (0.5 if k == pick else rest) if len(ids) > 1 else 1.0 for k in ids}
    return {"choice": pick, "confidence": probs[pick], "probabilities": probs}


class FakeAsker:
    """Keyless stand-in. No network. modes:
    greedy     action: the first type candidate this episode has not typed into yet, else
               the option sharing the most words with the goal (ties: first); text: the first
               span. A plumbing check that drives both paths, not a policy anyone should cite.
    malformed  answers whose probabilities sum to 0.5 (the validator must refuse them)
    raise      raises ConnectionError on every call
    """

    def __init__(self, mode: str, dump_request: str | None = None):
        self.mode = mode
        self.calls = 0
        self.dump_request = dump_request

    def __call__(self, state: dict, questions: dict[str, dict]) -> dict:
        self.calls += 1
        if self.dump_request and self.calls == 1:
            body = {"model": MODEL, "state": state, "questions": questions}
            Path(self.dump_request).write_text(
                json.dumps(body, separators=(",", ":"), ensure_ascii=False) + "\n"
            )
        if self.mode == "raise":
            raise ConnectionError("fake asker: no network")
        goal = set(re.findall(r"\w+", state["utterance"].lower()))
        typed = {h["ref"] for h in state["history"] if h["type"] == "type"}
        answers = {}
        for name, q in questions.items():
            ids = list(q["criteria"])
            if name == "action":
                fresh = [
                    k
                    for k in ids
                    if k.startswith("type [") and int(k[6 : k.index("]")]) not in typed
                ]
                pick_pool = (
                    [k for k in ids if not k.startswith("type [")]
                    if self.mode == "click_only"
                    else ids
                )
                pick = (
                    fresh[0]
                    if fresh and self.mode != "click_only"
                    else max(
                        pick_pool,
                        key=lambda k: (
                            len(
                                goal
                                & set(re.findall(r"\w+", k.lower().split("] ", 1)[-1]))
                            )
                            if k != NONE_KEY
                            else -1
                        ),
                    )
                )
            else:
                pick = ids[0]
            ans = _uniform_with(ids, pick)
            if self.mode == "malformed":
                ans["probabilities"] = {
                    k: v / 2 for k, v in ans["probabilities"].items()
                }
            answers[name] = ans
        return {
            "model": "fake-offline",
            "answers": answers,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }


def _http_status(exc: BaseException) -> int | None:
    st = getattr(exc, "status", None)
    return st if isinstance(st, int) else None


# ------------------------------------------------------------------ policy
class RunState:
    """Run-level counters shared by every episode of one process."""

    def __init__(self):
        self.consecutive_failures = 0


class JevPolicy:
    name = "jev"

    def __init__(self, ask, run: RunState, max_steps: int, none_policy: str = "always"):
        if none_policy not in {"always", "after-page-change"}:
            raise ValueError(f"unknown none policy: {none_policy}")
        self.ask = ask
        self.run = run
        self.max_steps = max_steps
        self.none_policy = none_policy
        self.page_fingerprint: str | None = None
        self.step = 0
        self.history: list[dict] = []
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.jev_ms = 0
        self.policy_s = 0.0
        self.models: set[str] = set()
        self.failures: list[dict] = []
        self.decisions: list[dict] = []
        self.halt: str | None = None

    def act(self, utterance, els, options):
        t0 = time.perf_counter()
        try:
            kind, ref, text = self._act(utterance, els, options)
        finally:
            self.policy_s += time.perf_counter() - t0
        rec = {"type": kind, "ref": ref}
        if text is not None:
            rec["text"] = text
        self.history.append(rec)  # the same record the floor's run_episode keeps
        self.step += 1
        return kind, ref, text

    def _act(self, utterance, els, options):
        page_fingerprint = json.dumps(
            {"elements": els, "options": options},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        allow_none = (
            self.none_policy == "always"
            or self.page_fingerprint is None
            or page_fingerprint != self.page_fingerprint
        )
        self.page_fingerprint = page_fingerprint
        state = floor.serialize_state(
            utterance, els, self.step, self.max_steps, list(self.history), options
        )
        actions, text_spans, truncated = build_candidates(
            utterance, els, options, include_none=allow_none
        )
        questions = build_questions(utterance, els, actions, text_spans)
        dec = {
            "step": self.step,
            "n_action_options": len(actions),
            "none_allowed": allow_none,
            "clicks_truncated": truncated,
            "n_text_heads": len(text_spans),
            "state_bytes": len(
                json.dumps(state, separators=(",", ":"), ensure_ascii=False).encode()
            ),
            "question_bytes": len(
                json.dumps(
                    questions, separators=(",", ":"), ensure_ascii=False
                ).encode()
            ),
        }
        t0 = time.perf_counter()
        self.calls += 1
        try:
            got = self.ask(state, questions)
            dec["latency_ms"] = int((time.perf_counter() - t0) * 1000)
            self.jev_ms += dec["latency_ms"]
            usage = got.get("usage") or {}
            if usage.get("input_tokens") is not None:
                self.input_tokens += int(usage["input_tokens"])
                dec["input_tokens"] = int(usage["input_tokens"])
            if usage.get("output_tokens") is not None:
                self.output_tokens += int(usage["output_tokens"])
            self.models.add(str(got.get("model")))
            a = validate_choice(got["answers"].get("action"), actions)
            kind, ref = actions[a["choice"]]
            dec["action"] = a["choice"]
            dec["action_conf"] = round(float(a["confidence"]), 4)
            text = None
            if kind == "type":
                t = validate_choice(got["answers"].get(f"text_{ref}"), text_spans[ref])
                text = t["choice"]
                dec["text"] = text
                dec["text_conf"] = round(float(t["confidence"]), 4)
                dec["n_text_options"] = len(text_spans[ref])
        except Exception as exc:  # noqa: BLE001 - recorded; the step becomes a no-op
            dec.setdefault("latency_ms", int((time.perf_counter() - t0) * 1000))
            msg = f"{type(exc).__name__}: {str(exc)[:300]}"
            self.failures.append({"step": self.step, "error": msg})
            dec["failed"] = True
            self.decisions.append(dec)
            self.run.consecutive_failures += 1
            status = _http_status(exc)
            if status in HALT_STATUSES:
                self.halt = f"HTTP {status}: {msg}"
            elif self.run.consecutive_failures >= HALT_AFTER_CONSECUTIVE_FAILURES:
                self.halt = (
                    f"{self.run.consecutive_failures} consecutive failed calls: {msg}"
                )
            if self.halt:
                raise HaltRun(self.halt) from None
            return ("none", 0, None)
        self.run.consecutive_failures = 0
        self.decisions.append(dec)
        return (kind, ref, text)

    def row_fields(self) -> dict:
        return {
            "model_requested": MODEL,
            **({"none_policy": self.none_policy} if V3_ENABLED else {}),
            "model": sorted(self.models),
            "jev_calls": self.calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "jev_ms": self.jev_ms,
            "policy_s": round(self.policy_s, 4),
            "failures": self.failures,
            "n_failures": len(self.failures),
            "decisions": self.decisions,
        }


# ------------------------------------------------------------------ driver
def repair_tail(path: Path) -> None:
    """Drop one trailing partial line left by a crash. Never deletes the file."""
    if not path.exists():
        return
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        path.write_bytes(data[: data.rfind(b"\n") + 1])


def load_arm_sanity():
    path = ROOT / "scripts" / "arm-sanity.py"
    spec = importlib.util.spec_from_file_location("arm_sanity", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load arm sanity checker: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SanityGate:
    def __init__(self, reference: Path, sanity_after: int = 200):
        if sanity_after < 1:
            raise ValueError("sanity_after must be positive")
        self.reference = reference
        self.sanity_after = sanity_after
        self.rows: list[dict] = []
        self.checked = False
        self.checker = load_arm_sanity()

    def observe(self, row: dict) -> dict | None:
        if self.checked:
            return None
        self.rows.append(row)
        _, eligible = self.checker.mix_rows(self.rows)
        if eligible < self.sanity_after:
            return None
        result = self.checker.compare_records(
            self.rows, self.reference, min_rows=self.sanity_after
        )
        result["sanity_after"] = self.sanity_after
        result["reference"] = str(self.reference)
        if result["exit_code"] != 2:
            self.checked = True
        return result if result["exit_code"] == 1 else None


def write_sanity_stop_row(
    out, result: dict, *, code_sha256: str, started_utc: str
) -> None:
    row = {
        "row_type": "arm_sanity_stop",
        "reason": "arm_sanity_exit_1",
        "checker_output": result["output"],
        "eligible_rows": result["arm_rows"],
        "reference_rows": result["reference_rows"],
        "sanity_after": result["sanity_after"],
        "reference": result["reference"],
        "code_sha256": code_sha256,
        "started_utc": started_utc,
        "finished_utc": utc_now(),
    }
    if out is not None:
        out.write(json.dumps(row, ensure_ascii=False) + "\n")
        out.flush()


def done_keys(path: Path) -> set[tuple[str, int, int]]:
    repair_tail(path)
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("row_type") != "arm_sanity_stop":
                out.add((r["task"], r["seed"], r["rep"]))
    return out


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def code_sha256_at_run_start() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def write_row(out, row: dict, pol, *, code_sha256: str, started_utc: str) -> None:
    row.update(
        pol.row_fields() if pol else {"jev_calls": 0, "input_tokens": 0, "failures": []}
    )
    steps = row.get("steps") or 0
    if steps and row.get("wall_s") is not None:
        row["s_per_step_end_to_end"] = round(
            (row["wall_s"] - (row.get("reset_s") or 0.0)) / steps, 4
        )
    row["code_sha256"] = code_sha256
    row["started_utc"] = started_utc
    row["finished_utc"] = utc_now()
    if out is not None:
        out.write(json.dumps(row, ensure_ascii=False) + "\n")
        out.flush()


def run_plan(
    plan,
    ask,
    out_path: Path | None,
    max_steps: int,
    none_policy: str = "always",
    sanity_reference: Path | None = None,
    sanity_after: int = 200,
):
    """Run episodes, optionally stopping on an action-mix sanity failure."""
    code_sha256 = code_sha256_at_run_start()
    args = argparse.Namespace(
        max_steps=max_steps,
        episode_max_ms=floor.BENCHMARK_EPISODE_MAX_MS,
        wait_ms=floor.BENCHMARK_WAIT_MS,
    )
    all_tasks = floor.load_task_list()
    bench = floor.benchmark_seeds(all_tasks)
    bench_pairs = {(t, s) for t, ss in bench.items() for s in ss}
    bench_js = {floor.js_seed_for(s) for ss in bench.values() for s in ss}
    floor.logging.getLogger().setLevel(floor.logging.WARNING)
    warn = floor.WarningCollector()
    floor.logging.getLogger().addHandler(warn)

    run = RunState()
    holder: dict = {}

    def factory(rng: random.Random):
        holder["policy"] = JevPolicy(ask, run, max_steps, none_policy)
        return holder["policy"]

    floor.POLICIES["jev"] = (
        factory  # runtime registration; the floor file is not edited
    )

    by_task: dict[str, list[tuple[int, int]]] = {}
    for task, seed, rep in plan:
        by_task.setdefault(task, []).append((seed, rep))
    out = open(out_path, "a") if out_path else None
    if sanity_reference is not None and out is None:
        raise ValueError("--sanity-reference requires --out for dev runs")
    sanity_gate = (
        SanityGate(sanity_reference, sanity_after)
        if sanity_reference is not None
        else None
    )
    n = succ = 0
    try:
        for task, pairs in by_task.items():
            env = floor.make_env(task, args.wait_ms)
            try:
                for seed, rep in pairs:
                    started_utc = utc_now()
                    holder.pop("policy", None)
                    try:
                        row = floor.run_episode(
                            env,
                            task,
                            seed,
                            rep,
                            "jev",
                            args,
                            bench_pairs,
                            bench_js,
                            warn,
                        )
                    except HaltRun as exc:
                        print(
                            f"HALT at {task} seed={seed} rep={rep}: {exc} "
                            "(episode row not written; resume replays it)",
                            file=sys.stderr,
                            flush=True,
                        )
                        return 4
                    pol = holder.get("policy")
                    write_row(
                        out,
                        row,
                        pol,
                        code_sha256=code_sha256,
                        started_utc=started_utc,
                    )
                    if sanity_gate is not None:
                        result = sanity_gate.observe(row)
                        if result is not None:
                            write_sanity_stop_row(
                                out,
                                result,
                                code_sha256=code_sha256,
                                started_utc=started_utc,
                            )
                            print(
                                "arm sanity gate stopped run: "
                                + " | ".join(result["output"]),
                                file=sys.stderr,
                                flush=True,
                            )
                            return 5
                    n += 1
                    succ += row["success"] > 0
                    print(
                        f"{task:28s} seed={seed:<5d} rep={rep} success={row['success']:.0f} "
                        f"raw={row['raw_reward']:+.2f} steps={row['steps']:2d} "
                        f"calls={row['jev_calls']} tok={row['input_tokens']} "
                        f"fail={len(row['failures'])} wall={row['wall_s']:.1f}s "
                        f"err={row['error']}  [{succ}/{n}]",
                        file=sys.stderr,
                        flush=True,
                    )
                    if row["error"]:
                        try:
                            env.close()
                        except Exception:  # noqa: BLE001
                            pass
                        env = floor.make_env(task, args.wait_ms)
            finally:
                try:
                    env.close()
                except Exception:  # noqa: BLE001
                    pass
    finally:
        if out:
            out.close()
    print(f"done: {n} episodes, {succ} successes", file=sys.stderr)
    return 0


def cmd_live(
    shard: str,
    seeds: str = "benchmark",
    none_policy: str = "always",
    tasks_spec: str = "all",
    label: str = "",
    plan_file: str | None = None,
    sanity_reference: Path | None = None,
    sanity_after: int = 200,
) -> int:
    if not os.environ.get("TYPESAFE_API_KEY", "").strip():
        print(
            "unconfigured: TYPESAFE_API_KEY unset, no call made (NOT_RUN)",
            file=sys.stderr,
        )
        return 2
    sys.path.insert(0, str(ROOT / "work" / "sr-adopt"))
    from phase_gate import require_bar

    here_rel = str(Path(__file__).resolve().relative_to(ROOT))
    prereg = (
        PREREG_V3
        if V3_ENABLED
        else (PREREG if seeds == "benchmark" and none_policy == "always" else PREREG_V2)
    )
    for p in (prereg, here_rel, str(FLOOR_PATH.relative_to(ROOT))):
        require_bar(p, repo=str(ROOT))  # AttemptPanic: zero calls
    if sanity_reference is not None:
        require_bar(str(sanity_reference.relative_to(ROOT)), repo=str(ROOT))
    ask = LiveAsker()
    k, n = (int(x) for x in shard.split("/"))
    all_tasks = floor.load_task_list()
    selected_tasks = (
        all_tasks
        if tasks_spec == "all"
        else [t.strip() for t in tasks_spec.split(",") if t.strip()]
    )
    unknown = sorted(set(selected_tasks) - set(all_tasks))
    if unknown:
        raise ValueError(f"unknown MiniWoW tasks: {unknown}")
    tasks = selected_tasks[k::n]
    if plan_file:
        plan = []
        for line in Path(plan_file).read_text().splitlines():
            task, seed, rep = line.strip().split(",")
            plan.append((task, int(seed), int(rep)))
    else:
        plan = floor.episode_plan(tasks, seeds, floor.benchmark_seeds(all_tasks))
    ROWS_DIR.mkdir(parents=True, exist_ok=True)
    if label:
        filename = f"miniwob-jev-{label}.s{k}.jsonl"
    elif seeds == "benchmark" and none_policy == "always":
        filename = f"miniwob-jev.s{k}.jsonl"
    elif none_policy == "after-page-change":
        filename = f"miniwob-jev-v2.s{k}.jsonl"
    else:
        filename = f"miniwob-jev-v1-heldout.s{k}.jsonl"
    out_path = ROWS_DIR / filename
    have = done_keys(out_path)
    todo = [p for p in plan if p not in have]
    print(
        f"shard {k}/{n}: {len(todo)} to run, {len(plan) - len(todo)} resumed; seeds={seeds}; none_policy={none_policy}",
        file=sys.stderr,
        flush=True,
    )
    return run_plan(
        todo,
        ask,
        out_path,
        floor.BENCHMARK_MAX_STEPS,
        none_policy,
        sanity_reference,
        sanity_after,
    )


def cmd_dev(
    fake,
    tasks,
    seeds,
    out,
    max_steps,
    dump_request=None,
    sanity_reference: Path | None = None,
    sanity_after: int = 200,
) -> int:
    seed_list = floor.parse_seeds(seeds)
    if any(s < 9000 for s in seed_list):
        print("dev seeds must be >= 9000 (never a benchmark seed)", file=sys.stderr)
        return 2
    task_list = [t.strip() for t in tasks.split(",") if t.strip()]
    plan = floor.episode_plan(task_list, seeds, {})
    ask = FakeAsker(fake, dump_request)
    return run_plan(
        plan,
        ask,
        Path(out) if out else None,
        max_steps,
        sanity_reference=sanity_reference,
        sanity_after=sanity_after,
    )


# ------------------------------------------------------------------ selftest
def _el(ref, parent, tag, text="", value="", id_="", leaf=True):
    return {
        "ref": ref,
        "parent": parent,
        "tag": tag,
        "kind": tag.upper(),
        "text": text,
        "value": value,
        "id": id_,
        "classes": "",
        "left": 0.0,
        "top": 0.0,
        "width": 10.0,
        "height": 10.0,
        "focused": False,
        "is_leaf": leaf,
    }


def selftest() -> int:
    """Keyless, no Chrome: options, cap, spans, validator, fail-safe, halt, missing key."""
    bad: list[str] = []

    def check(cond, what):
        if not cond:
            bad.append(what)

    utt = 'Enter "Bob Smith" into the text field and press Submit.'
    sp = utterance_spans(utt)
    check(sp[0] == "Bob Smith", "quoted span first")
    check("Submit" in sp and "Enter" in sp, "tokens present")
    check("press Submit" in sp, "bigram present")
    check(len(sp) == len(set(sp)), "spans deduped")
    sp2 = utterance_spans(
        'Enter the username "rex" and the password "CP" and press login.'
    )
    check(sp2[:2] == ["rex", "CP"], "quoted spans first, in order")
    check(
        "CP and press" in sp2 and not any('"' in s for s in sp2),
        "n-grams carry no quote marks",
    )
    check(
        len(utterance_spans(" ".join(f"w{i}" for i in range(60)))) == OPTION_CAP,
        "span cap",
    )

    els = [
        _el(1, 0, "body", leaf=False),
        _el(2, 1, "input_text", id_="tt"),
        _el(3, 1, "button", text="Submit"),
        _el(4, 1, "select", id_="sel", leaf=False),
        _el(5, 1, "label", leaf=False),
        _el(6, 5, "input_checkbox", id_="ch0"),
        _el(-1, 5, "t", text="Tomato"),
    ]
    acts, tspans, trunc = build_candidates(
        "Select Tomato and click Submit", els, {4: ["Apple", "Tomato"]}
    )
    kinds = sorted(acts.values())
    check(
        ("type", 2) in kinds and ("type", 4) in kinds,
        "type candidates: input and select",
    )
    check(tspans[4] == ["Tomato"], "select text head = spans equal to an option")
    check(("click", 3) in kinds and ("none", 0) in kinds, "click and none offered")
    check(trunc == 0, "no truncation on a small page")
    acts_v2, _, _ = build_candidates(
        "Select Tomato and click Submit",
        els,
        {4: ["Apple", "Tomato"]},
        include_none=False,
    )
    check(NONE_KEY not in acts_v2, "after-page-change policy can remove none")
    lab6 = next(k for k, v in acts.items() if v == ("click", 6))
    check('"Tomato"' in lab6, "checkbox labelled by its <label> text run")
    acts2, tspans2, _ = build_candidates("Select nothing", els, {4: ["Apple"]})
    check(
        4 not in tspans2 and ("type", 4) not in acts2.values(),
        "select with no span match",
    )

    many = [_el(1, 0, "body", leaf=False)] + [
        _el(r, 1, "div", text=f"item {r}") for r in range(2, 402)
    ]
    many.insert(5, _el(900, 1, "input_text", id_="q"))
    many.insert(9, _el(901, 1, "button", text="Go"))
    a3, t3, tr3 = build_candidates("Type go and click Go", many, {})
    check(
        len(a3) == OPTION_CAP, f"action options capped at {OPTION_CAP} (got {len(a3)})"
    )
    check(
        ("type", 900) in a3.values() and ("click", 901) in a3.values(),
        "cap keeps typed and interactive",
    )
    check(
        NONE_KEY in a3 and tr3 == len(floor.clickable_refs(many)) - (OPTION_CAP - 2),
        "cap count",
    )

    ids = ["a", "b", "c"]
    good = {
        "choice": "b",
        "confidence": 0.6,
        "probabilities": {"a": 0.2, "b": 0.6, "c": 0.2},
    }
    check(validate_choice(good, ids) is good, "valid answer accepted")
    hostile = [
        None,
        {},
        {**good, "choice": "z"},
        {**good, "probabilities": {"a": 0.4, "b": 0.6}},
        {**good, "probabilities": {"a": 0.2, "b": 0.6, "c": 0.2, "z": 0.0}},
        {**good, "probabilities": {"a": 0.2, "b": 0.3, "c": 0.2}},
        {**good, "probabilities": {"a": 0.5, "b": 0.3, "c": 0.2}},
        {**good, "probabilities": {"a": float("nan"), "b": 0.6, "c": 0.2}},
        {**good, "probabilities": {"a": -0.2, "b": 0.6, "c": 0.6}},
        {**good, "confidence": 1.5},
        {**good, "probabilities": {"a": "0.2", "b": 0.6, "c": 0.2}},
    ]
    for i, h in enumerate(hostile):
        try:
            validate_choice(h, ids)
            bad.append(f"hostile answer {i} accepted")
        except ValueError:
            pass

    # Fail-safe direction: an invalid answer executes nothing (a no-op), is recorded, and three
    # in a row halt the run instead of burning the split.
    run = RunState()
    pol = JevPolicy(FakeAsker("malformed"), run, 10)
    check(
        pol.act("click Submit", els, {}) == ("none", 0, None),
        "malformed answer -> no-op",
    )
    check(pol.failures and pol.calls == 1, "malformed answer recorded as a failed call")
    pol.act("click Submit", els, {})
    try:
        pol.act("click Submit", els, {})
        bad.append("third consecutive failure did not halt")
    except HaltRun:
        pass
    run = RunState()
    pol = JevPolicy(FakeAsker("greedy"), run, 10)
    kind, ref, text = pol.act('Enter "Bob Smith" and click Submit', els, {})
    check(
        pol.failures == [] and run.consecutive_failures == 0,
        "valid answer resets the streak",
    )
    check(
        pol.history[0]
        == ({"type": kind, "ref": ref} | ({"text": text} if text else {})),
        "history",
    )

    class Status402(Exception):
        status = 402

    def pay(*_):
        raise Status402("no credits")

    try:
        JevPolicy(pay, RunState(), 10).act("click Submit", els, {})
        bad.append("402 did not halt")
    except HaltRun:
        pass

    saved = os.environ.pop("TYPESAFE_API_KEY", None)
    try:
        try:
            LiveAsker()
            bad.append("LiveAsker built without a key")
        except MissingKey:
            pass
        check(
            cmd_live("0/4") == 2,
            "live without a key returns NOT_RUN (2) before any Chrome",
        )
    finally:
        if saved is not None:
            os.environ["TYPESAFE_API_KEY"] = saved

    for b in bad:
        print("FAIL", b)
    print(f"selftest: {'FAIL' if bad else 'ok'} ({len(bad)} failures)")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    d = sub.add_parser("dev")
    d.add_argument("--fake", choices=["greedy", "malformed", "raise"], required=True)
    d.add_argument("--tasks", default="click-button,enter-text,click-checkboxes")
    d.add_argument("--seeds", default="9000")
    d.add_argument("--out")
    d.add_argument("--max-steps", type=int, default=floor.BENCHMARK_MAX_STEPS)
    d.add_argument(
        "--dump-request", help="write the first request body (state+questions)"
    )
    d.add_argument("--sanity-reference", type=Path)
    d.add_argument("--sanity-after", type=int, default=200)
    lv = sub.add_parser("live")
    lv.add_argument("--shard", default="0/1")
    lv.add_argument("--seeds", default="benchmark")
    lv.add_argument("--tasks", default="all")
    lv.add_argument("--label", default="")
    lv.add_argument("--plan-file")
    lv.add_argument(
        "--none-policy", choices=["always", "after-page-change"], default="always"
    )
    lv.add_argument("--sanity-reference", type=Path)
    lv.add_argument("--sanity-after", type=int, default=200)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "dev":
        return cmd_dev(
            a.fake,
            a.tasks,
            a.seeds,
            a.out,
            a.max_steps,
            a.dump_request,
            a.sanity_reference,
            a.sanity_after,
        )
    return cmd_live(
        a.shard,
        a.seeds,
        a.none_policy,
        a.tasks,
        a.label,
        a.plan_file,
        a.sanity_reference,
        a.sanity_after,
    )


if __name__ == "__main__":
    sys.exit(main())
