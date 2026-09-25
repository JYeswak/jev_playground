#!/usr/bin/env python3
"""Keyless re-score of the Jev MiniWoB arm against the committed floors and published rows.

  python3 work/miniwob-jev/score.py            markdown tables + verdict
  python3 work/miniwob-jev/score.py --json     the same numbers as JSON

Stdlib only; reads committed rows and nothing else. Bar: bead jev-jy7t.1.5 and
docs/demos/upstream-repro/miniwob-jev-prereg-20260925.md, fixed before any call.
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
JEV_GLOB = os.path.join(HERE, "rows", "miniwob-jev.s*.jsonl")
FLOOR_GLOB = os.path.join(ROOT, "work", "game-floors", "rows", "miniwob.s*.jsonl")
EPISODES = 625
FLOOR_BAR_PCT = (
    22.4  # scripted floor, jev-jy7t.1.1 (closed); the bar's number, not recomputed
)
ALPHA = 0.05
Z = 1.959963984540054
USD_PER_INPUT_TOKEN = 0.042 / 1e6  # docs-mirror/typesafe/models.md:13,18

# BrowserGym leaderboard results/*/miniwob.json and README.md @294ebe1 (game-floors-20260924.md).
# n for the Wilson interval: 625 where the row ran this split; Orby's episode list is not public
# and its SE implies ~1,306. GenericAgent rows: AgentLab flags use_ax_tree=True, use_html=False,
# use_screenshot=False, action_set="bid" (free-text fill, select_option, press, scroll, drag...),
# chain-of-thought on, Playwright harness.
_GA = (
    "text-only like ours (AXTree, no screenshot), but a different observation (AXTree, not the "
    "Farama DOM list), a wider action set (BrowserGym bid set incl. free-text fill), "
    "chain-of-thought, BrowserGym Playwright harness"
)
PUBLISHED = [
    (
        "OrbyAgent-Claude-3.5-Sonnet",
        74.9,
        1.2,
        None,
        "screenshot + HTML, ~1,300 episodes from an unpublished list, BrowserGym harness",
    ),
    ("GenericAgent-GPT-5", 71.5, 1.8, EPISODES, _GA),
    ("GenericAgent-Claude-3.5-Sonnet", 69.8, 1.8, EPISODES, _GA),
    ("GenericAgent-GPT-4o", 63.8, 1.9, EPISODES, _GA),
    ("GenericAgent-GPT-4o-mini", 56.6, 2.0, EPISODES, _GA),
]
OUR_PROTOCOL = (
    "Farama miniwob 1.1.0 + Selenium, same HTML/seeds/10 steps/0.5 s wait; floor's DOM element "
    "list; click(ref) and type(ref, utterance span) only"
)


def load(pattern):
    rows = []
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as fh:
            rows.extend(json.loads(line) for line in fh if line.strip())
    return rows


def wilson(k, n, z=Z):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def binom_tail_ge(k, n):
    """P(X >= k), X ~ Binomial(n, 1/2), exact."""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2**n if n else 1.0


def mcnemar(b, c):
    """Exact McNemar: b = jev-only successes, c = floor-only successes."""
    n = b + c
    two = min(1.0, 2 * binom_tail_ge(max(b, c), n)) if n else 1.0
    return {
        "b_jev_only": b,
        "c_floor_only": c,
        "p_two_sided": two,
        "p_one_sided_jev": binom_tail_ge(b, n),
    }


def arm_stats(rows):
    n = len(rows)
    k = sum(1 for r in rows if r["success"] > 0 and not r.get("error"))
    lo, hi = wilson(k, n)
    mean = lambda key: sum(float(r.get(key) or 0.0) for r in rows) / n if n else 0.0  # noqa: E731
    return {
        "episodes": n,
        "successes": k,
        "success_pct": 100 * k / n if n else 0.0,
        "wilson95_pct": [100 * lo, 100 * hi],
        "se_pct": 100 * math.sqrt((k / n) * (1 - k / n) / n) if n else 0.0,
        "success_strict_pct": 100 * mean("success_strict"),
        "raw_reward_mean": mean("raw_reward"),
        "reward_miniwob_10s_mean": mean("reward_miniwob_10s"),
        "errors": sum(1 for r in rows if r.get("error")),
        "env_s_per_step": (
            sum(r["mean_step_s"] for r in rows if r.get("mean_step_s") is not None)
            / max(1, sum(1 for r in rows if r.get("mean_step_s") is not None))
        ),
    }


def score():
    jev = load(JEV_GLOB)
    floor = load(FLOOR_GLOB)
    key = lambda r: (r["task"], r["seed"], r["rep"])  # noqa: E731
    by_pol = {}
    for r in floor:
        by_pol.setdefault(r["policy"], {})[key(r)] = r
    scripted, random_ = by_pol["scripted"], by_pol["random"]
    problems = []
    jk = {}
    for r in jev:
        if r.get("policy") != "jev":
            problems.append(f"non-jev row {key(r)}")
        if key(r) in jk:
            problems.append(f"duplicate row {key(r)}")
        jk[key(r)] = r
    if set(jk) != set(scripted) or len(scripted) != EPISODES:
        problems.append(
            f"episode sets differ: jev {len(jk)}, scripted {len(scripted)}, "
            f"missing {len(set(scripted) - set(jk))}, extra {len(set(jk) - set(scripted))}"
        )
    rows = list(jk.values())
    arms = {
        "jev": arm_stats(rows),
        "scripted": arm_stats(list(scripted.values())),
        "random": arm_stats(list(random_.values())),
    }
    s = lambda r: r["success"] > 0 and not r.get("error")  # noqa: E731
    paired = [(s(jk[k2]), s(scripted[k2])) for k2 in scripted if k2 in jk]
    mc = mcnemar(
        sum(a and not b for a, b in paired), sum(b and not a for a, b in paired)
    )
    paired_r = [(s(jk[k2]), s(random_[k2])) for k2 in random_ if k2 in jk]
    mc_r = mcnemar(
        sum(a and not b for a, b in paired_r), sum(b and not a for a, b in paired_r)
    )
    j = arms["jev"]
    floor_pass = (
        not problems
        and j["wilson95_pct"][0] > FLOOR_BAR_PCT
        and mc["p_two_sided"] < ALPHA
        and mc["b_jev_only"] > mc["c_floor_only"]
    )
    published = []
    for name, pct, se, n, proto in PUBLISHED:
        p = pct / 100
        n_used = n or round(p * (1 - p) / (se / 100) ** 2)
        lo, hi = wilson(round(p * n_used), n_used)
        lo, hi = 100 * lo, 100 * hi
        if j["wilson95_pct"][0] > hi:
            label = "BEAT"
        elif j["wilson95_pct"][1] < lo:
            label = "LOSE"
        else:
            label = "TIE"
        published.append(
            {
                "row": name,
                "success_pct": pct,
                "se_pct": se,
                "n_for_wilson": n_used,
                "wilson95_pct": [lo, hi],
                "label": label,
                "protocol_matches": False,
                "protocol": proto,
            }
        )
    calls = sum(r.get("jev_calls", 0) for r in rows)
    tokens = sum(r.get("input_tokens", 0) for r in rows)
    steps = sum(r.get("steps", 0) for r in rows)
    e2e = [
        r["s_per_step_end_to_end"]
        for r in rows
        if r.get("s_per_step_end_to_end") is not None
    ]
    decisions = [d for r in rows for d in r.get("decisions", [])]
    lat = sorted(
        d["latency_ms"] for d in decisions if "latency_ms" in d and not d.get("failed")
    )
    per_task = {}
    for k2, r in jk.items():
        t = per_task.setdefault(k2[0], {"jev": 0, "scripted": 0, "random": 0, "n": 0})
        t["n"] += 1
        t["jev"] += s(r)
        t["scripted"] += s(scripted[k2]) if k2 in scripted else 0
        t["random"] += s(random_[k2]) if k2 in random_ else 0
    return {
        "problems": problems,
        "arms": arms,
        "mcnemar_vs_scripted": mc,
        "mcnemar_vs_random": mc_r,
        "floor_bar": {
            "rule": "PASS iff Jev Wilson95 lower > 22.4 AND exact McNemar vs scripted p_two_sided < 0.05 with b > c",
            "pass": floor_pass,
            "verdict": "PASS" if floor_pass else "KILL",
        },
        "published": published,
        "our_protocol": OUR_PROTOCOL,
        "cost": {
            "jev_calls": calls,
            "calls_per_episode": calls / len(rows) if rows else 0.0,
            "input_tokens": tokens,
            "input_tokens_per_episode": tokens / len(rows) if rows else 0.0,
            "input_tokens_per_call": tokens / calls if calls else 0.0,
            "usd": tokens * USD_PER_INPUT_TOKEN,
            "failed_calls": sum(len(r.get("failures", [])) for r in rows),
            "episodes_with_failed_call": sum(1 for r in rows if r.get("failures")),
            "models": sorted({m for r in rows for m in r.get("model", [])}),
        },
        "timing": {
            "steps": steps,
            "env_s_per_step_mean": j["env_s_per_step"],
            "end_to_end_s_per_step_mean": sum(e2e) / len(e2e) if e2e else None,
            "jev_latency_ms_p50": lat[len(lat) // 2] if lat else None,
            "jev_latency_ms_p90": lat[int(len(lat) * 0.9)] if lat else None,
            "wall_s_total_episodes": sum(r.get("wall_s") or 0 for r in rows),
        },
        "per_task": per_task,
    }


def fmt(x, d=1):
    return f"{x:.{d}f}"


def markdown(out):
    a = out["arms"]
    lines = []
    if out["problems"]:
        lines.append("PROBLEMS: " + "; ".join(out["problems"]))
    lines.append(
        "| Arm | N | Success % | Wilson 95% | SE | strict % | raw mean | 10 s reward | errors |"
    )
    lines.append("|---|---:|---:|---|---:|---:|---:|---:|---:|")
    for name in ("jev", "scripted", "random"):
        s = a[name]
        lines.append(
            f"| {name} | {s['episodes']} | {fmt(s['success_pct'])} | {fmt(s['wilson95_pct'][0])}–{fmt(s['wilson95_pct'][1])} "
            f"| {fmt(s['se_pct'])} | {fmt(s['success_strict_pct'])} | {fmt(s['raw_reward_mean'], 3)} "
            f"| {fmt(s['reward_miniwob_10s_mean'], 3)} | {s['errors']} |"
        )
    mc, mr = out["mcnemar_vs_scripted"], out["mcnemar_vs_random"]
    lines.append("")
    lines.append(
        f"McNemar vs scripted (paired 625): Jev-only {mc['b_jev_only']}, scripted-only {mc['c_floor_only']}, "
        f"exact p two-sided {mc['p_two_sided']:.3g}, one-sided (Jev better) {mc['p_one_sided_jev']:.3g}"
    )
    lines.append(
        f"McNemar vs random: Jev-only {mr['b_jev_only']}, random-only {mr['c_floor_only']}, "
        f"exact p two-sided {mr['p_two_sided']:.3g}"
    )
    lines.append(
        f"Floor bar: {out['floor_bar']['verdict']} ({out['floor_bar']['rule']})"
    )
    lines.append("")
    lines.append(
        "| Published row | Success % | Wilson 95% (n) | Jev vs row | Protocol matches? |"
    )
    lines.append("|---|---:|---|---|---|")
    for p in out["published"]:
        lines.append(
            f"| {p['row']} | {fmt(p['success_pct'])} ± {fmt(p['se_pct'])} | {fmt(p['wilson95_pct'][0])}–{fmt(p['wilson95_pct'][1])} ({p['n_for_wilson']}) "
            f"| {p['label']} | no: {p['protocol']} |"
        )
    c, t = out["cost"], out["timing"]
    lines.append("")
    lines.append(
        f"Calls {c['jev_calls']} ({fmt(c['calls_per_episode'], 2)}/episode), input tokens {c['input_tokens']:,} "
        f"({fmt(c['input_tokens_per_episode'], 0)}/episode, {fmt(c['input_tokens_per_call'], 0)}/call), "
        f"spend ${c['usd']:.4f}, failed calls {c['failed_calls']} in {c['episodes_with_failed_call']} episodes, "
        f"models {c['models']}"
    )
    lines.append(
        f"Steps {t['steps']}; env s/step {fmt(t['env_s_per_step_mean'], 3)}; end-to-end s/step "
        f"{fmt(t['end_to_end_s_per_step_mean'] or 0, 3)}; Jev latency p50 {t['jev_latency_ms_p50']} ms, "
        f"p90 {t['jev_latency_ms_p90']} ms"
    )
    diff = [
        (k, v) for k, v in sorted(out["per_task"].items()) if v["jev"] != v["scripted"]
    ]
    lines.append("")
    lines.append(
        "Tasks where Jev and scripted differ (jev/scripted of n): "
        + ", ".join(f"{k} {v['jev']}/{v['scripted']}" for k, v in diff)
    )
    solved = sum(1 for v in out["per_task"].values() if v["jev"] > 0)
    lines.append(f"Tasks with >= 1 Jev success: {solved} of {len(out['per_task'])}")
    return "\n".join(lines)


def main(argv):
    out = score()
    if "--json" in argv:
        print(json.dumps(out, indent=1, sort_keys=True))
    else:
        print(markdown(out))
    return 1 if out["problems"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
