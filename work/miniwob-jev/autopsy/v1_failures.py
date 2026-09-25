#!/usr/bin/env python3
"""Keyless failure autopsy of the MiniWoB++ Jev v1 run (bead jev-9gtw.3).

Reads only the committed v1 rows, work/miniwob-jev/rows/miniwob-jev.s{0,1,2,3}.jsonl
(625 episodes; 319 with success == 0), and gives every failed episode one root cause,
the step where it went wrong, and a task family. No network, no model, no key.

Evidence used:
  - each row's utterance, success, raw_reward, done, truncated, steps, failures, and its
    per-step `decisions` (chosen option label, option count, text-head count, typed text);
  - two constants read from the committed harness source with `ast`, never imported:
    TEXT_INPUT_TAGS (work/game-floors/miniwob/run.py) and SPAN_STRIP
    (work/miniwob-jev/jev_arm.py);
  - a static table of what each MiniWoB task needs (TASK_NEEDS below), with the reason.

The rows log the chosen option, not the page, so the task-level entries in TASK_NEEDS are
MiniWoB task knowledge; each one is paired with a per-episode check on the row that must
hold for the class to apply, and an episode that fails every check is reported as
`unclassified` (the script exits 1 if any are).

Causes are applied in precedence order: first the blockers that a perfect chooser could
not get past with the options v1 offered (the upstream cause), then the policy errors.

    python3 work/miniwob-jev/autopsy/v1_failures.py            # tables
    python3 work/miniwob-jev/autopsy/v1_failures.py --episodes # one line per failure
    python3 work/miniwob-jev/autopsy/v1_failures.py --sample 12 # seeded random spot-check
    python3 work/miniwob-jev/autopsy/v1_failures.py --json     # everything, JSON
"""

from __future__ import annotations

import argparse
import ast
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
ROWS = [ROOT / f"work/miniwob-jev/rows/miniwob-jev.s{i}.jsonl" for i in range(4)]
ARM_SRC = ROOT / "work/miniwob-jev/jev_arm.py"
FLOOR_SRC = ROOT / "work/game-floors/miniwob/run.py"
EXPECTED_EPISODES = 625
NONE_LABEL = "none: do nothing this step"


def _module_constant(path: Path, name: str):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise SystemExit(f"{name} not found in {path}")


SPAN_STRIP: str = _module_constant(ARM_SRC, "SPAN_STRIP")
TEXT_INPUT_TAGS: set[str] = _module_constant(FLOOR_SRC, "TEXT_INPUT_TAGS")

# ------------------------------------------------------------------ task families
FAMILY_TASKS = {
    "click": """ascending-numbers bisect-angle circle-center click-button
        click-button-sequence click-checkboxes click-checkboxes-large click-checkboxes-soft
        click-checkboxes-transfer click-collapsible click-collapsible-2
        click-collapsible-2-nodelay click-collapsible-nodelay click-color click-dialog
        click-dialog-2 click-link click-shades click-shape click-tab click-tab-2
        click-tab-2-easy click-tab-2-hard click-tab-2-medium click-test click-test-2
        click-test-transfer click-widget count-shape count-sides find-greatest find-midpoint
        focus-text focus-text-2 generate-number grid-coordinate hot-cold identify-shape
        navigate-tree number-checkboxes odd-or-even right-angle social-media social-media-all
        social-media-some stock-market tic-tac-toe unicode-test""",
    "type": """copy-paste copy-paste-2 enter-date enter-password enter-text enter-text-2
        enter-text-dynamic enter-time find-word guess-number read-table read-table-2
        scroll-text simple-algebra simple-arithmetic terminal text-transform
        visual-addition""",
    "widget-select": """choose-date choose-date-easy choose-date-medium choose-date-nodelay
        choose-list click-menu click-menu-2 click-option click-pie click-pie-nodelay
        click-scroll-list use-autocomplete use-autocomplete-nodelay use-colorwheel
        use-colorwheel-2 use-spinner""",
    "drag-pointer": """drag-box drag-circle drag-cube drag-items drag-items-grid drag-shapes
        drag-shapes-2 drag-single-shape drag-sort-numbers draw-circle draw-line
        highlight-text highlight-text-2 resize-textarea scroll-text-2 text-editor use-slider
        use-slider-2""",
    "multi-step-form": """book-flight book-flight-nodelay buy-ticket daily-calendar
        email-inbox email-inbox-delete email-inbox-forward email-inbox-forward-nl
        email-inbox-forward-nl-turk email-inbox-important email-inbox-nl-turk
        email-inbox-noscroll email-inbox-reply email-inbox-star-reply form-sequence
        form-sequence-2 form-sequence-3 login-user login-user-popup multi-layouts
        multi-orderings order-food phone-book search-engine sign-agreement""",
}
FAMILY = {t: fam for fam, ts in FAMILY_TASKS.items() for t in ts.split()}
FAMILIES = list(FAMILY_TASKS)

# ------------------------------------------------------------------ what each task needs
# (need, why). `need` is checked per episode in classify(); `why` is MiniWoB task knowledge.
DRAG = "drag"
TASK_NEEDS: dict[str, tuple[str, str]] = {
    **{
        t: (DRAG, "a mouse drag (press, move, release) moves or draws the object")
        for t in """drag-box drag-circle drag-cube drag-items drag-items-grid drag-shapes
            drag-shapes-2 drag-single-shape drag-sort-numbers draw-circle draw-line""".split()
    },
    "resize-textarea": (DRAG, "dragging the textarea's resize handle"),
    "use-slider": (DRAG, "dragging the jQuery UI slider handle to a value"),
    "use-slider-2": (DRAG, "dragging three slider handles to values"),
    "form-sequence": (DRAG, "its first sub-step drags a slider to a value"),
    "daily-calendar": (
        DRAG,
        "an event of a duration is created by dragging across slots",
    ),
    **{
        t: (
            "coordinate",
            "the task scores the click's x,y inside one shape, not an element",
        )
        for t in "bisect-angle circle-center find-midpoint right-angle hot-cold".split()
    },
    **{
        t: ("text-selection", "a text range must be selected with the mouse")
        for t in "highlight-text highlight-text-2 text-editor".split()
    },
    "scroll-text-2": ("scroll", "the textarea must be scrolled to the bottom"),
    "sign-agreement": (
        "scroll",
        "the agreement textarea must be scrolled to the bottom",
    ),
    "click-menu": ("hover", "submenus of a jQuery UI menu open on hover"),
    "terminal": ("keypress", "the command runs on Enter"),
    # the needed text is not in the utterance
    **{
        t: ("page-value", "the text to type is on the page, not in the utterance")
        for t in """copy-paste copy-paste-2 find-word read-table read-table-2 scroll-text
            text-transform""".split()
    },
    **{
        t: ("computed-value", "the text to type is computed from the page")
        for t in "visual-addition simple-arithmetic simple-algebra guess-number".split()
    },
    "enter-text-2": (
        "case-transformed-value",
        "the quoted word must be retyped in another case",
    ),
    # the decisive attribute is not in the serialized state
    **{
        t: ("color", "the target is picked by color; the state has no color field")
        for t in "click-color click-shades click-shape count-shape".split()
    },
    "count-sides": (
        "geometry",
        "the side count is in SVG points; the state has tag and bbox",
    ),
}

COLOR_WORDS = set(
    """red green blue yellow black white grey gray purple orange pink brown magenta cyan
    lime aqua teal navy maroon olive silver violet indigo gold""".split()
)
MONTHS_FROM = (
    12  # choose-date / book-flight calendars open on December 2016 (rows show it)
)


# ------------------------------------------------------------------ helpers
def load_rows() -> list[dict]:
    rows = []
    for p in ROWS:
        with p.open() as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return rows


def ep_id(r: dict) -> str:
    return f"{r['task']}/s{r['seed']}/r{r['rep']}"


def label(d: dict) -> str:
    return d.get("action", "<call failed>")


def kind(d: dict) -> str:
    a = d.get("action")
    if a is None:
        return "failed"
    return a.split(" ", 1)[0].rstrip(":")


def ref_of(d: dict) -> int | None:
    m = re.match(r"(?:click|type) \[(\d+)\]", d.get("action", ""))
    return int(m.group(1)) if m else None


def tag_of(d: dict) -> str:
    m = re.match(r"(?:click|type) \[\d+\] (\S+)", d.get("action", ""))
    return m.group(1) if m else ""


def quoted(utt: str) -> list[str]:
    return [a or b for a, b in re.findall(r'"([^"]*)"|\u201c([^\u201d]*)\u201d', utt)]


def tail_run(decs: list[dict], pred) -> int:
    n = 0
    for d in reversed(decs):
        if not pred(d):
            break
        n += 1
    return n


def tail_repeat(decs: list[dict]) -> int:
    """Length of the final run of one identical non-none action."""
    if not decs or kind(decs[-1]) in {"none", "failed"}:
        return 0
    last = label(decs[-1])
    return tail_run(decs, lambda d: label(d) == last)


def redundant_focus_steps(decs: list[dict]) -> list[int]:
    """Steps that clicked a field the very next step types into (type already focuses)."""
    out = []
    for a, b in zip(decs, decs[1:]):
        if kind(a) == "click" and kind(b) == "type" and ref_of(a) == ref_of(b):
            out.append(a["step"])
    return out


def wasted_steps(decs: list[dict]) -> int:
    rep = sum(
        1 for a, b in zip(decs, decs[1:]) if kind(b) == "click" and label(a) == label(b)
    )
    none = sum(1 for d in decs if kind(d) == "none")
    return len(redundant_focus_steps(decs)) + rep + none


def ending(r: dict) -> str:
    decs = r["decisions"]
    if r["done"]:
        return "terminal-wrong-answer"
    if tail_run(decs, lambda d: kind(d) == "none") >= 3:
        return "timeout-none-tail"
    if tail_repeat(decs) >= 3:
        return "timeout-repeat-tail"
    return "timeout-other"


def typed(decs: list[dict]) -> list[dict]:
    return [d for d in decs if kind(d) == "type"]


def date_month(utt: str) -> int | None:
    m = re.search(r"\b(\d{2})/\d{2}/\d{4}\b", utt)
    return int(m.group(1)) if m else None


# ------------------------------------------------------------------ classifier
# cause -> (the AGENTS.md LOSS DEPTH bucket, one-line meaning)
CAUSES: dict[str, tuple[str, str]] = {
    "op-inexpressible": (
        "harness (action space)",
        "the task needs drag, a coordinate click, text selection, scroll, hover or a key; "
        "v1 has click(ref), type(ref, span) and none",
    ),
    "op-not-offered": (
        "harness or code bug",
        "the needed element or operation exists on the page but the candidate builder "
        "never offered it",
    ),
    "value-mangled-by-span-strip": (
        "harness or code bug",
        "the exact quoted value was never offered: SPAN_STRIP removed its final '.'",
    ),
    "value-not-in-utterance": (
        "question design",
        "the text to type comes from the page, a computation or a case change; the text "
        "question offers only utterance spans",
    ),
    "evidence-absent-from-state": (
        "missing evidence in the state",
        "the attribute that decides the target (color, SVG geometry) is not serialized",
    ),
    "step-cap-infeasible": (
        "harness (10-step cap) x widget path",
        "the only working click path needs more steps than the cap allows",
    ),
    "right-element-wrong-op": (
        "question design",
        "the right target was chosen through the wrong operation or node while the right "
        "one was offered",
    ),
    "step-cap-wasted": (
        "question design",
        "a feasible path, lost to wasted steps (a click before type, a repeat, a none)",
    ),
    "wrong-span": (
        "model limit or question design",
        "the right field, but a worse span of the utterance than one offered",
    ),
    "none-while-action-needed": (
        "question design",
        "'none' chosen repeatedly while the page still needed an offered action",
    ),
    "no-progress-loop": (
        "model limit or question design",
        "the same non-effective click repeated to the step cap",
    ),
    "wrong-choice": (
        "model limit",
        "a wrong element or answer chosen with the deciding evidence in the state",
    ),
    "harness-call-error": (
        "harness or code bug",
        "a failed Jev call was the decisive step",
    ),
    "unclassified": ("unknown", "no rule matched"),
}
# Causes a perfect chooser could not get past with v1's options, state and step cap.
UPSTREAM = {
    "op-inexpressible",
    "op-not-offered",
    "value-mangled-by-span-strip",
    "value-not-in-utterance",
    "evidence-absent-from-state",
    "step-cap-infeasible",
}


def classify(r: dict) -> dict:
    """Return {cause, subtype, step, note} for one failed episode."""
    t, utt, decs = r["task"], r["utterance"], r["decisions"]
    need = TASK_NEEDS.get(t)
    n = len(decs)
    last = decs[-1]["step"] if decs else 0

    def out(cause, subtype, step, note):
        return {"cause": cause, "subtype": subtype, "step": step, "note": note}

    # 1. operation the action space cannot express (each with a per-episode guard)
    if need and need[0] in {
        DRAG,
        "coordinate",
        "text-selection",
        "scroll",
        "hover",
        "keypress",
    }:
        sub = need[0]
        guard = True
        if t == "scroll-text-2":
            guard = "bottom" in utt.lower()  # 'top' episodes need no scroll and succeed
        elif t == "sign-agreement":
            guard = (
                "scroll" in utt.lower()
            )  # 'Click the cancel button.' needs no scroll
        elif t == "click-menu":
            guard = ">" in utt  # single-level paths need no hover and succeed
        elif t == "daily-calendar":
            # every click left the option count unchanged: no dialog ever opened
            guard = len({d["n_action_options"] for d in decs}) == 1
        elif t == "terminal":
            guard = any(kind(d) == "type" for d in decs)  # it typed; Enter never came
        if guard:
            step = next((d["step"] for d in decs if kind(d) == "click"), 0)
            return out("op-inexpressible", sub, step, need[1])

    # 2. needed element or operation never offered
    if t in {"enter-date", "enter-time"} and all(d["n_text_heads"] == 0 for d in decs):
        field = "INPUT_DATE" if t == "enter-date" else "INPUT_TIME"
        assert field not in TEXT_INPUT_TAGS
        step = next((d["step"] for d in decs if tag_of(d).startswith("input_")), 0)
        return out(
            "op-not-offered",
            "type-on-" + field.lower(),
            step,
            f"{field} is not in TEXT_INPUT_TAGS, so no type option; it clicked the field",
        )
    if t == "find-greatest" and max(d["n_action_options"] for d in decs) <= 2:
        return out(
            "op-not-offered",
            "cards-not-clickable",
            0,
            "at most 2 options every step (Submit + none): no card was a click candidate",
        )

    # 3. the exact quoted value was stripped by SPAN_STRIP
    for d in typed(decs):
        for q in quoted(utt):
            stripped = q.strip().strip(SPAN_STRIP).strip()
            if q != stripped and d.get("text") == stripped:
                return out(
                    "value-mangled-by-span-strip",
                    "trailing-punctuation",
                    d["step"],
                    f"needed {q!r}, typed {d['text']!r}; {q!r} was not an option",
                )

    # 4. the text to type is not in the utterance
    if need and need[0] in {"page-value", "computed-value", "case-transformed-value"}:
        guard = True
        if t == "enter-text-2":
            guard = bool(re.search(r"(lower|upper) case", utt)) and any(
                d.get("text") in quoted(utt) for d in typed(decs)
            )
        tds = typed(decs)
        if guard:
            step = tds[0]["step"] if tds else 0
            got = repr(tds[0]["text"]) if tds else "nothing"
            return out(
                "value-not-in-utterance", need[0], step, f"{need[1]}; typed {got}"
            )

    # 5. decisive attribute absent from the state
    if need and need[0] == "geometry":
        return out("evidence-absent-from-state", "geometry", last, need[1])
    if need and need[0] == "color":
        if COLOR_WORDS & set(re.findall(r"[a-z]+", utt.lower())):
            return out("evidence-absent-from-state", "color", last, need[1])

    # 6. the only working path cannot fit the step cap
    if t.startswith(("choose-date", "book-flight")):
        tds = [d for d in typed(decs) if "#datepicker" in label(d)]
        if tds:
            return out(
                "right-element-wrong-op",
                "typed-date-into-datepicker",
                tds[0]["step"],
                "typed the date into the jQuery datepicker; the episode still failed "
                "(Search inert or a wrong date submitted)",
            )
        m = date_month(utt)
        if m is not None:
            base = (
                3 if t.startswith("choose-date") else 8
            )  # open+day+submit / 4+open+day+search+book
            needed = base + (MONTHS_FROM - m)
            if needed > r["max_steps"]:
                return out(
                    "step-cap-infeasible",
                    "calendar-prev-clicks",
                    0,
                    f"month {m:02d} needs {needed} clicks from December; cap {r['max_steps']}",
                )
            focus = redundant_focus_steps(decs)
            if (
                not r["done"]
                and focus
                and tail_repeat(decs) < 3
                and wasted_steps(decs) > r["max_steps"] - needed
            ):
                return out(
                    "step-cap-wasted",
                    "click-before-type",
                    focus[0],
                    f"needs {needed} of {r['max_steps']} steps; {len(focus)} spent clicking "
                    "a field the next step typed into",
                )

    # 7. right element, wrong operation or node, with the right one offered
    for d in decs:
        if kind(d) == "click" and tag_of(d) == "option" and d["n_text_heads"] > 0:
            return out(
                "right-element-wrong-op",
                "clicked-option-not-select",
                d["step"],
                "clicked an <option> of the list; `type` on its <select> was offered",
            )
    if tail_repeat(decs) >= 3 and tag_of(decs[-1]) == "tspan":
        start = n - tail_repeat(decs)
        return out(
            "right-element-wrong-op",
            "clicked-label-node",
            decs[start]["step"],
            "re-clicked the item's <tspan> label; the slice <path> was offered",
        )
    for d in typed(decs):
        if 'value="' in label(d) and r["done"]:
            return out(
                "right-element-wrong-op",
                "typed-into-prefilled-field",
                d["step"],
                "typed into a prefilled field; type appends (no clear), e.g. the spinner",
            )

    # 8. wrong span in the right field
    if t.startswith("use-autocomplete"):
        q = quoted(utt)
        bad = [d for d in typed(decs) if q and not d["text"].startswith(q[0])]
        if bad:
            return out(
                "wrong-span",
                "not-the-prefix",
                bad[0]["step"],
                f"typed {bad[0]['text']!r}; the value starts with {q[0]!r}",
            )
    if t.startswith("multi-"):
        g = re.search(r"for (\S+) movies", utt)
        bad = [d for d in typed(decs) if g and "movies" in d["text"].split()]
        if bad:
            return out(
                "wrong-span",
                "extra-word",
                bad[0]["step"],
                f"typed {bad[0]['text']!r} into the genre field; the genre is {g.group(1)!r}",
            )
    if t.startswith("email-inbox-forward"):
        bad = [d for d in typed(decs) if len(d["text"].split()) > 1]
        if bad:
            return out(
                "wrong-span",
                "phrase-as-recipient",
                bad[0]["step"],
                f"typed {bad[0]['text']!r} into the forward-to field",
            )

    # 9. 'none' while the page still needed an action
    tn = tail_run(decs, lambda d: kind(d) == "none")
    if not r["done"] and tn >= 3:
        return out(
            "none-while-action-needed",
            "none-tail",
            decs[n - tn]["step"],
            f"last {tn} steps were 'none' with {decs[-1]['n_action_options'] - 1} "
            "actions offered",
        )

    # 10. the same click, no effect, to the cap
    tr = tail_repeat(decs)
    if not r["done"] and tr >= 3:
        return out(
            "no-progress-loop",
            "repeat-tail",
            decs[n - tr]["step"],
            f"last {tr} steps repeated {label(decs[-1])[:60]!r}",
        )

    # 11. harness call error as the decisive step
    if r["n_failures"] and r["failures"][-1]["step"] == last:
        return out(
            "harness-call-error", "call-failed", last, r["failures"][-1]["error"][:80]
        )

    # 12. a wrong element or answer, the deciding evidence in the state
    if r["done"] and decs:
        return out(
            "wrong-choice", "terminal", last, f"ended on {label(decs[-1])[:60]!r}"
        )
    if decs:
        seen: set[str] = set()
        revisit = next(
            (d["step"] for d in decs if label(d) in seen or seen.add(label(d))),
            decs[0]["step"],
        )
        return out(
            "wrong-choice",
            "timeout-wandering",
            revisit,
            f"{len({label(d) for d in decs})} distinct actions in {n} steps, no submit that "
            "ended the episode",
        )
    return out("unclassified", "", 0, "no decisions")


# ------------------------------------------------------------------ report
def examples(eps: list[dict], k: int = 3) -> list[dict]:
    """Up to k episodes, preferring distinct tasks, in sorted id order."""
    picked, seen = [], set()
    for e in sorted(eps, key=lambda e: e["id"]):
        if e["task"] not in seen:
            picked.append(e)
            seen.add(e["task"])
        if len(picked) == k:
            break
    return picked


def controls(rows: list[dict]) -> dict:
    """Within-task splits that test three causes against the successes (all 625 rows)."""
    color = Counter()
    for r in rows:
        if TASK_NEEDS.get(r["task"], ("",))[0] == "color":
            has = bool(COLOR_WORDS & set(re.findall(r"[a-z]+", r["utterance"].lower())))
            color[("color word" if has else "no color word", bool(r["success"]))] += 1
    cal = Counter()
    for r in rows:
        if r["task"].startswith(("choose-date", "book-flight")):
            m = date_month(r["utterance"])
            if m is not None:
                cal[(f"{MONTHS_FROM - m:02d} months back", bool(r["success"]))] += 1
    quote = Counter()
    for r in rows:
        for q in quoted(r["utterance"]):
            if q != q.strip().strip(SPAN_STRIP).strip() and r["task"].startswith(
                "email"
            ):
                quote[("reply quote ends in punctuation", bool(r["success"]))] += 1
                break

    def fmt(c: Counter) -> dict:
        keys = sorted({k for k, _ in c})
        return {k: {"success": c[(k, True)], "fail": c[(k, False)]} for k in keys}

    return {"color": fmt(color), "calendar": fmt(cal), "reply_quote": fmt(quote)}


def analyse(rows: list[dict]) -> dict:
    fails = [r for r in rows if not r["success"]]
    eps = []
    for r in fails:
        c = classify(r)
        eps.append(
            {
                "id": ep_id(r),
                "task": r["task"],
                "family": FAMILY.get(r["task"], "?"),
                "raw_reward": r["raw_reward"],
                "steps": r["steps"],
                "ending": ending(r),
                "call_failures": r["n_failures"],
                **c,
                "decisive_action": next(
                    (label(d) for d in r["decisions"] if d["step"] == c["step"]), ""
                ),
            }
        )
    by_cause_family = defaultdict(Counter)
    for e in eps:
        by_cause_family[e["cause"]][e["family"]] += 1
    fam_total = Counter(FAMILY.get(r["task"], "?") for r in rows)
    fam_fail = Counter(e["family"] for e in eps)

    # step accounting over all 625 episodes
    all_redundant = sum(len(redundant_focus_steps(r["decisions"])) for r in rows)
    fail_redundant = sum(len(redundant_focus_steps(r["decisions"])) for r in fails)
    none_steps_fail = sum(1 for r in fails for d in r["decisions"] if kind(d) == "none")
    none_steps_all = sum(1 for r in rows for d in r["decisions"] if kind(d) == "none")
    none_by_cause = Counter()
    for r, e in zip(fails, eps):
        none_by_cause[e["cause"]] += sum(1 for d in r["decisions"] if kind(d) == "none")
    ending_by_cause = defaultdict(Counter)
    for e in eps:
        ending_by_cause[e["cause"]][e["ending"]] += 1

    return {
        "n_episodes": len(rows),
        "n_success": sum(1 for r in rows if r["success"]),
        "n_fail": len(fails),
        "span_strip": SPAN_STRIP,
        "text_input_tags": sorted(TEXT_INPUT_TAGS),
        "families": FAMILIES,
        "family_total": dict(fam_total),
        "family_fail": dict(fam_fail),
        "by_cause_family": {c: dict(v) for c, v in by_cause_family.items()},
        "cause_bucket": {c: CAUSES[c][0] for c in CAUSES},
        "cause_meaning": {c: CAUSES[c][1] for c in CAUSES},
        "ending_by_cause": {c: dict(v) for c, v in ending_by_cause.items()},
        "none_steps": {"all": none_steps_all, "failed": none_steps_fail},
        "none_steps_by_cause": dict(none_by_cause),
        "click_before_type_steps": {"all": all_redundant, "failed": fail_redundant},
        "upstream_fail": sum(1 for e in eps if e["cause"] in UPSTREAM),
        "policy_fail": sum(1 for e in eps if e["cause"] not in UPSTREAM),
        "call_failure_episodes": [
            {"id": e["id"], "cause": e["cause"]} for e in eps if e["call_failures"]
        ],
        "examples": {
            c: [
                {k: e[k] for k in ("id", "step", "decisive_action", "note")}
                for e in examples([e for e in eps if e["cause"] == c])
            ]
            for c in CAUSES
            if any(e["cause"] == c for e in eps)
        },
        "controls": controls(rows),
        "episodes": eps,
    }


def print_report(a: dict) -> None:
    fams = a["families"]
    order = [c for c in CAUSES if c in a["by_cause_family"]]
    short = {
        "click": "click",
        "type": "type",
        "widget-select": "widget",
        "drag-pointer": "drag",
        "multi-step-form": "form",
    }
    print(
        f"v1 rows: {a['n_episodes']} episodes, {a['n_success']} success, "
        f"{a['n_fail']} failed\n"
    )
    head = f"{'cause':30}" + "".join(f"{short[f]:>8}" for f in fams) + f"{'total':>8}"
    print(head)
    print("-" * len(head))
    for c in order:
        row = a["by_cause_family"][c]
        print(
            f"{c:30}"
            + "".join(f"{row.get(f, 0):>8}" for f in fams)
            + f"{sum(row.values()):>8}"
        )
    print("-" * len(head))
    print(
        f"{'failed':30}"
        + "".join(f"{a['family_fail'].get(f, 0):>8}" for f in fams)
        + f"{a['n_fail']:>8}"
    )
    print(
        f"{'episodes':30}"
        + "".join(f"{a['family_total'].get(f, 0):>8}" for f in fams)
        + f"{a['n_episodes']:>8}"
    )

    print(
        "\nhow each cause ends (terminal = wrong answer submitted; timeout = 10 steps)"
    )
    ends = [
        "terminal-wrong-answer",
        "timeout-none-tail",
        "timeout-repeat-tail",
        "timeout-other",
    ]
    print(f"{'cause':30}" + "".join(f"{e.split('-', 1)[1][:12]:>14}" for e in ends))
    for c in order:
        row = a["ending_by_cause"][c]
        print(f"{c:30}" + "".join(f"{row.get(e, 0):>14}" for e in ends))

    print(
        f"\n'none' steps: {a['none_steps']['all']} of all steps, "
        f"{a['none_steps']['failed']} in failed episodes; by cause:"
    )
    for c, k in sorted(a["none_steps_by_cause"].items(), key=lambda x: -x[1]):
        if k:
            print(f"  {c:30}{k:>6}")
    cbt = a["click_before_type_steps"]
    print(
        f"click-then-type-same-field steps: {cbt['all']} in all episodes, "
        f"{cbt['failed']} in failed ones"
    )
    up, pol, n = a["upstream_fail"], a["policy_fail"], a["n_episodes"]
    print(
        f"upstream failures (no offered choice could win): {up}; policy failures: {pol}.\n"
        f"ceiling for a perfect chooser on v1's options: {n - up}/{n} = "
        f"{100 * (n - up) / n:.1f}%"
    )
    cf = a["call_failure_episodes"]
    print(
        f"failed episodes with a failed Jev call: {len(cf)} "
        + ", ".join(f"{c['id']} ({c['cause']})" for c in cf)
    )

    print("\ncontrols: success/fail within the same tasks")
    for name, split in a["controls"].items():
        for k, v in split.items():
            print(f"  {name:12} {k:34} {v['success']:>3} success {v['fail']:>3} fail")
    print("\nexamples (episode id, decisive step: action)")
    for c, exs in a["examples"].items():
        print(f"  {c}  [{a['cause_bucket'][c]}]")
        for e in exs:
            print(f"    {e['id']} step {e['step']}: {e['decisive_action'][:70]}")
            print(f"      {e['note']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--episodes", action="store_true", help="one line per failed episode"
    )
    ap.add_argument("--sample", type=int, default=0, help="seeded random spot-check")
    args = ap.parse_args(argv)

    rows = load_rows()
    if len(rows) != EXPECTED_EPISODES:
        print(f"expected {EXPECTED_EPISODES} rows, got {len(rows)}", file=sys.stderr)
        return 1
    a = analyse(rows)
    if args.json:
        print(json.dumps(a, indent=1))
    elif args.episodes:
        for e in sorted(a["episodes"], key=lambda e: (e["cause"], e["id"])):
            print(f"{e['cause']:28} {e['subtype']:28} {e['id']:40} step {e['step']}")
    elif args.sample:
        rng = random.Random(0)
        for e in rng.sample(a["episodes"], args.sample):
            print(f"{e['id']:40} {e['cause']:28} {e['ending']:22} {e['note'][:70]}")
    else:
        print_report(a)
    unc = a["by_cause_family"].get("unclassified", {})
    if unc:
        print(f"{sum(unc.values())} unclassified episodes", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
