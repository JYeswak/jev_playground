#!/usr/bin/env python3
"""Aggregate the preregistered floor runs of bead jev-jy7t.1.1 into the receipt's tables.

Receipt and preregistration: docs/demos/upstream-repro/game-floors-20260924.md (prereg @922fda3).
Stdlib only, keyless, no model call. Reads the wave-2 JSONL rows the prereg's commands wrote,
committed in work/game-floors/rows/:

  python3 work/game-floors/aggregate.py work/game-floors/rows

Aggregations are the preregistered ones:
- ViZDoom: per reading and policy, mean +- SE (sample SD / sqrt n) of cumulative_reward over the
  runs, plus kills and deaths. Reading A = the frame-skip-2 runs; C and D = their 200- and
  300-decision checkpoints; B = the frame-skip-0 runs. Errored or incomplete runs are counted and
  excluded from the mean.
- MiniWoB: per policy, 100 x mean(success) over all rows with errors counted as 0,
  +- 100 x sqrt(p(1-p)/n); plus success_strict, raw_reward and reward_miniwob_10s means.
- RTRG: per game x level x policy, the mean of S over all runs; SE over the per-seed means
  (averaging within a seed first). S unclipped is primary; clipped S and raw R beside it.
"""

import glob
import json
import math
import os
import sys


def rows(pattern):
    out = []
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as fh:
            out.extend(json.loads(line) for line in fh if line.strip())
    return out


def mean_se(xs):
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = sum(xs) / n
    if n < 2:
        return m, float("nan")
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return m, sd / math.sqrt(n)


def fmt(m, se, digits=2):
    return f"{m:.{digits}f} ± {se:.{digits}f}"


def vizdoom(w):
    print("## ViZDoom defend_the_center (per run; mean ± SE over runs)")
    print(
        "| Reading | Policy | n ok | bad | cumulative_reward | kills | deaths | s/decision |"
    )
    print("|---|---|---:|---:|---|---|---|---:|")
    for reading, pattern, ck, fs in (
        ("A (600 dec, fs 2)", "vizdoom-A-*.jsonl", None, 2),
        ("C (200 dec, fs 2)", "vizdoom-A-*.jsonl", "200", 2),
        ("D (300 dec, fs 2)", "vizdoom-A-*.jsonl", "300", 2),
        ("B (600 dec, fs 0)", "vizdoom-B-*.jsonl", None, 0),
    ):
        rs = rows(os.path.join(w, pattern))
        for policy in ("random", "scripted"):
            prs = [r for r in rs if r["policy"] == policy]
            # A row counts only in the preregistered setting: 600 decisions at this frame skip.
            ok = [
                r
                for r in prs
                if r.get("complete")
                and not r.get("error")
                and r.get("decisions") == 600
                and r.get("frame_skip") == fs
            ]
            if ck:
                ok = [r for r in ok if ck in (r.get("checkpoints") or {})]
            bad = len(prs) - len(ok)
            src = [r["checkpoints"][ck] for r in ok] if ck else ok
            cr = mean_se([s["cumulative_reward"] for s in src])
            ki = mean_se([s["kills"] for s in src])
            de = mean_se([s["deaths"] for s in src])
            step = mean_se([r["mean_step_seconds"] for r in ok])[0]
            print(
                f"| {reading} | {policy} | {len(ok)} | {bad} | {fmt(*cr)} | {fmt(*ki)} | {fmt(*de)} | {step:.3f} |"
            )
    print()


def miniwob(w):
    rs = rows(os.path.join(w, "miniwob.s*.jsonl"))
    print("## MiniWoB++ (BrowserGym split; % over all episodes, errors = 0)")
    print(
        "| Policy | n | errors | success % ± SE | strict % | raw reward | reward at 10 s | s/step (incl. 0.5 s wait) |"
    )
    print("|---|---:|---:|---|---:|---:|---:|---:|")
    for policy in ("random", "scripted"):
        prs = [r for r in rs if r["policy"] == policy]
        n = len(prs)
        if n == 0:
            print(f"| {policy} | 0 | - | - | - | - | - | - |")
            continue
        err = sum(1 for r in prs if r.get("error"))
        p = sum((0 if r.get("error") else r["success"]) for r in prs) / n
        strict = sum((0 if r.get("error") else r["success_strict"]) for r in prs) / n
        raw = sum((r.get("raw_reward") or 0) for r in prs) / n
        r10 = sum((r.get("reward_miniwob_10s") or 0) for r in prs) / n
        steps = [r["mean_step_s"] for r in prs if r.get("mean_step_s") is not None]
        s = sum(steps) / len(steps) if steps else float("nan")
        se = 100 * math.sqrt(p * (1 - p) / n)
        print(
            f"| {policy} | {n} | {err} | {100 * p:.1f} ± {se:.1f} | {100 * strict:.1f} | {raw:.3f} | {r10:.3f} | {s:.3f} |"
        )
    tasks = {r["task"] for r in rs}
    print(
        f"\ntasks seen: {len(tasks)}; unavailable rows: {sum(1 for r in rs if r.get('reason') == 'unavailable')}"
    )
    print()


def rtrg(w):
    rs = rows(os.path.join(w, "rtrg.jsonl"))
    print(
        "## Real-Time Reasoning Gym (normalized S; mean over runs, SE over the 8 per-seed means)"
    )
    print(
        "| Game | Level | Policy | n | errors | S (unclipped) | S clipped | raw R | s/step |"
    )
    print("|---|---|---|---:|---:|---|---:|---:|---:|")
    for game in ("freeway", "snake", "overcooked"):
        for level in ("E", "M", "H"):
            for policy in ("default", "random", "scripted"):
                prs = [
                    r
                    for r in rs
                    if r["game"] == game
                    and r["difficulty"] == level
                    and r["policy"] == policy
                ]
                ok = [r for r in prs if not r.get("errors")]
                err = len(prs) - len(ok)
                if not ok:
                    print(
                        f"| {game} | {level} | {policy} | 0 | {err} | - | - | - | - |"
                    )
                    continue
                per_seed = {}
                for r in ok:
                    per_seed.setdefault(r["seed"], []).append(r["score"])
                seed_means = [sum(v) / len(v) for v in per_seed.values()]
                m = sum(r["score"] for r in ok) / len(ok)
                se = mean_se(seed_means)[1]
                mc = sum(r["score_clipped"] for r in ok) / len(ok)
                rr = sum(r["R"] for r in ok) / len(ok)
                st = sum(r["mean_step_s"] for r in ok) / len(ok)
                print(
                    f"| {game} | {level} | {policy} | {len(ok)} | {err} | {m:.3f} ± {se:.3f} | {mc:.3f} | {rr:.2f} | {st:.4f} |"
                )
    ms = os.path.join(w, "rtrg-freeway-minsteps.jsonl")
    if os.path.exists(ms):
        # pygame prints a banner to stdout before the rows; only JSON lines are rows.
        with open(ms, encoding="utf-8") as fh:
            lines = [json.loads(l) for l in fh if l.lstrip().startswith("{")]
        ranges = {"E": (0, 12), "M": (13, 16), "H": (17, 21)}  # paper Table 5
        print(
            f"\nFreeway minimum-steps check (Table 5 ranges E<=12, M 13-16, H 17-21): {len(lines)} rows"
        )
        for level, (lo, hi) in ranges.items():
            got = [
                (r["seed"], r["min_steps"]) for r in lines if r["difficulty"] == level
            ]
            out = [g for g in got if not lo <= g[1] <= hi]
            print(f"  {level}: min_steps {[g[1] for g in got]}; outside range: {out}")
    print()


def main(argv):
    if len(argv) != 2 or not os.path.isdir(argv[1]):
        raise SystemExit("usage: aggregate.py <wave2 dir>")
    vizdoom(argv[1])
    miniwob(argv[1])
    rtrg(argv[1])


if __name__ == "__main__":
    main(sys.argv)
