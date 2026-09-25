#!/usr/bin/env python3
"""Keyless Stage B loss-depth autopsy.

Reads only the committed abyssal decision/result JSONL and saved replay HTML.  It
finds the first own-side faint in each loss and assigns one mechanistic hypothesis
using fixed, predeclared rules:

1. missing state: the faint is residual/contact/status/hazard/recoil damage or has
   no current opponent move in the turn log;
2. opponent model: a direct faint follows an opponent action absent from the
   predicted distribution or with predicted probability < 0.25;
3. leaf value: the selected action differs from the Jev action-prior top action
   after the opponent action was not surprising;
4. action prior: the selected action equals the action-prior top action after the
   opponent action was not surprising.

This is a hypothesis generator, not causal proof.  The 0.25 surprise threshold is
not tuned from these results.  The script emits a complete per-loss table and
aggregate counts so another reader can reproduce the committed autopsy.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STAGE = ROOT / "work" / "poke-jev" / "stage-b"
DECISIONS = STAGE / "decisions-abyssal.jsonl"
RESULTS = STAGE / "results-abyssal.jsonl"
SURPRISE_THRESHOLD = 0.25


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def normal_action(kind: str, value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "", value.lower())
    return f"{kind} {value}"


def normalized_key(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().lower()
    if value.startswith("move "):
        return normal_action("move", value[5:])
    if value.startswith("switch "):
        return normal_action("switch", value[7:])
    return re.sub(r"[^a-z0-9+ ]+", "", value)


def replay_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    marker = '<script type="text/plain" class="battle-log-data">'
    if marker not in text:
        raise ValueError(f"missing battle-log-data script: {path}")
    payload = text.split(marker, 1)[1].split("</script>", 1)[0]
    return html.unescape(payload).splitlines()


def damage_cause(line: str) -> str:
    parts = line.split("|")
    return "|".join(parts[4:]).strip() if len(parts) > 4 else ""


def cause_label(source: str, turn_lines: list[str], opp_self_target: bool) -> str:
    lower = source.lower()
    if "rocky helmet" in lower:
        return "contact/item"
    if "stealth rock" in lower or "spikes" in lower or "sticky web" in lower:
        return "hazard"
    if "psn" in lower or "tox" in lower or "burn" in lower or "leech seed" in lower:
        return "status"
    if "future sight" in lower or "doom desire" in lower:
        return "delayed"
    if "[from]" in lower:
        return "residual/recoil"
    if not any(line.startswith("|move|p2a:") for line in turn_lines) or opp_self_target:
        return "delayed"
    return "direct"


def first_faint(path: Path) -> dict:
    turn = 0
    turn_lines: list[str] = []
    for line in replay_lines(path):
        if line.startswith("|turn|"):
            turn = int(line.split("|")[2])
            turn_lines = []
        turn_lines.append(line)
        if line.startswith("|faint|p1a:"):
            faint_mon = line.split("|", 2)[2]
            damage = next(
                (
                    candidate
                    for candidate in reversed(turn_lines)
                    if candidate.startswith("|-damage|p1a:")
                ),
                "",
            )
            opp_line = next(
                (
                    candidate
                    for candidate in reversed(turn_lines)
                    if candidate.startswith("|move|p2a:")
                ),
                None,
            )
            opp_move = (
                normal_action("move", opp_line.split("|")[3]) if opp_line else None
            )
            opp_self_target = bool(
                opp_line
                and len(opp_line.split("|")) > 4
                and opp_line.split("|")[4].startswith("p2a:")
            )
            own_move = next(
                (
                    normal_action("move", candidate.split("|")[3])
                    for candidate in reversed(turn_lines)
                    if candidate.startswith("|move|p1a:")
                ),
                None,
            )
            return {
                "turn": turn,
                "faint": faint_mon.removeprefix("p1a: "),
                "opp_action": opp_move,
                "own_action": own_move,
                "source": damage_cause(damage),
                "cause": cause_label(damage_cause(damage), turn_lines, opp_self_target),
                "turn_lines": turn_lines,
            }
    raise ValueError(f"loss replay has no own-side faint: {path}")


def row_for(rows: dict[tuple[str, int], list[dict]], battle: str, turn: int) -> dict:
    candidates = rows.get((battle, turn), [])
    if not candidates:
        raise ValueError(f"no decision row for {battle} turn {turn}")
    return next((row for row in candidates if not row.get("forced")), candidates[0])


def predicted_probability(row: dict, actual: str | None) -> float | None:
    if actual is None:
        return None
    for key, probability in (row.get("opponent") or {}).items():
        if normalized_key(key) == actual:
            return float(probability)
    return None


def fallback_label(row: dict) -> str | None:
    failure = row.get("fallback")
    if not failure:
        return None
    if "402" in failure:
        return "402 credit exhaustion"
    return "other fallback"


def classify(tp: dict, row: dict, opponent_probability: float | None) -> str:
    fallback = fallback_label(row)
    if fallback is not None:
        return f"excluded: {fallback}"
    if tp["cause"] != "direct" or tp["opp_action"] is None:
        return "missing state"
    if opponent_probability is None or opponent_probability < SURPRISE_THRESHOLD:
        return "opponent model"
    if row.get("values") and row.get("chosen") != row.get("prior_top"):
        return "leaf value"
    return "action prior"


def analyse(
    decisions_path: Path = DECISIONS, results_path: Path = RESULTS
) -> list[dict]:
    decisions = load_jsonl(decisions_path)
    results = load_jsonl(results_path)
    rows: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in decisions:
        rows[(row["battle"], row["turn"])].append(row)

    losses = [result for result in results if result.get("won") is False]
    output: list[dict] = []
    for result in losses:
        replay = ROOT / "work" / "poke-jev" / result["replay"]
        tp = first_faint(replay)
        row = row_for(rows, result["battle"], tp["turn"])
        probability = predicted_probability(row, tp["opp_action"])
        values = row.get("values") or {}
        output.append(
            {
                "battle": result["battle"],
                "turns": result["turns"],
                "turn": tp["turn"],
                "faint": tp["faint"],
                "cause": tp["cause"],
                "source": tp["source"] or "direct",
                "opp_action": tp["opp_action"] or "none",
                "opp_p": probability,
                "own_action": tp["own_action"] or "none",
                "chosen": row.get("chosen", "none"),
                "prior_top": row.get("prior_top", "none"),
                "chosen_value": values.get(row.get("chosen")),
                "classification": classify(tp, row, probability),
            }
        )
    return output


def fmt_probability(value: float | None) -> str:
    return "—" if value is None else f"{value:.3f}"


def fmt_value(value: float | None) -> str:
    return "—" if value is None else f"{value:.4f}"


def markdown(rows: list[dict]) -> str:
    classes = Counter(row["classification"] for row in rows)
    causes = Counter(row["cause"] for row in rows)
    active_rows = [
        row for row in rows if not row["classification"].startswith("excluded:")
    ]
    active_count = len(active_rows)
    lines = [
        "## Keyless autopsy output",
        "",
        f"- Losses analysed: **{len(rows)}**; all rows come from `results-abyssal.jsonl` with `won: false`.",
        "- First-event rule: first own-side faint in the committed replay; no loss in this set is a time loss.",
        f"- Fixed opponent-surprise threshold: predicted probability `< {SURPRISE_THRESHOLD:.2f}` or absent.",
        f"- Four-way hypothesis denominator: **{active_count}** rows with a Jev decision at the first faint.",
        "- Attribution is a mechanistic hypothesis, not a causal oracle; it is intended to rank the next tests.",
        "",
        "### Hypothesis counts",
        "",
        "| Hypothesis | Losses | Share of Jev-active losses |",
        "|---|---:|---:|",
    ]
    for label in ("missing state", "opponent model", "leaf value", "action prior"):
        count = classes[label]
        share = count / active_count if active_count else 0.0
        lines.append(f"| {label} | {count} | {share:.1%} |")
    lines += [
        "",
        "### Excluded first-faint rows",
        "",
        "| Exclusion | Losses |",
        "|---|---:|",
    ]
    for label, count in sorted(
        (label, count)
        for label, count in classes.items()
        if label.startswith("excluded:")
    ):
        lines.append(f"| {label.removeprefix('excluded: ')} | {count} |")
    lines += [
        "",
        "### Faint-cause counts",
        "",
        "| Replay cause | Losses |",
        "|---|---:|",
    ]
    for label, count in sorted(causes.items()):
        lines.append(f"| {label} | {count} |")
    lines += [
        "",
        "### Complete per-loss table",
        "",
        "| # | Battle | T | First faint | Cause | Opponent action | P(opp) | Own action | Chosen | Prior top | Chosen value | Hypothesis |",
        "|---:|---|---:|---|---|---|---:|---|---|---|---:|---|",
    ]
    for index, row in enumerate(rows, 1):
        lines.append(
            "| {index} | `{battle}` | {turn} | {faint} | {cause} | `{opp_action}` | {opp_p} | "
            "`{own_action}` | `{chosen}` | `{prior_top}` | {chosen_value} | {classification} |".format(
                index=index,
                battle=row["battle"],
                turn=row["turn"],
                faint=row["faint"],
                cause=row["cause"],
                opp_action=row["opp_action"],
                opp_p=fmt_probability(row["opp_p"]),
                own_action=row["own_action"],
                chosen=row["chosen"],
                prior_top=row["prior_top"],
                chosen_value=fmt_value(row["chosen_value"]),
                classification=row["classification"],
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", default="abyssal", help="Stage B result arm name")
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable rows"
    )
    args = parser.parse_args()
    rows = analyse(
        STAGE / f"decisions-{args.arm}.jsonl",
        STAGE / f"results-{args.arm}.jsonl",
    )
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print(markdown(rows), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
