#!/usr/bin/env python3
"""Scorer for bead jev-3e2i: OpenRouter comparators against every committed Jev run on five sets.

Bar: docs/demos/upstream-repro/openrouter-incumbents-20260924.md. Stdlib only, no key, no network.
Run: python3 work/openrouter-incumbents/score.py [--selfcheck]
--selfcheck scores each unit's committed Haiku rows through this file's code as if Haiku were a
comparator, and exits 1 unless the committed headline pairing (Jev run 1 x Haiku) reproduces.

No verdict rule is restated where a unit's scorer can be imported:
  SST-5, Banking77   work/jev-variance/score.py (sst_eval, sst_run_verdict, b77_eval, b77_verdict)
  CLINC150           work/choice-clinc150/score.py (preds, correct, gate, handled, verdict)
  SciFact, FEVER     work/noul-variance/score.py (load_arm, pair, bar1) over noul-scifact/score.py
"""

import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
DIR = os.path.basename(HERE)


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, os.path.join(WORK, relpath))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


JV = _load("jev_variance", "jev-variance/score.py")
C = _load("clinc_score", "choice-clinc150/score.py")
NV = _load("noul_variance", "noul-variance/score.py")


def _free_structured():
    """jev-14qk's FREE_STRUCTURED tuple, read from its source without importing the adapter."""
    import ast

    with open(os.path.join(WORK, "openrouter", "provider.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and getattr(node.targets[0], "id", "") == "FREE_STRUCTURED"
        ):
            return tuple(ast.literal_eval(node.value))
    raise SystemExit("FREE_STRUCTURED not found in work/openrouter/provider.py")


FREE_STRUCTURED = _free_structured()

PAID = ("openai/gpt-5-nano", "deepseek/deepseek-v4-flash")
# USD per token, OpenRouter /api/v1/models, 2026-09-24 (listing sha256 in the receipt)
PRICE = {
    "openai/gpt-5-nano": (0.00000005, 0.0000004),
    "deepseek/deepseek-v4-flash": (0.000000088606, 0.000000177212),
}
FREE_MIN_ANSWERED = 49  # of jev-14qk's 50 SST-5 rows (pane 1, 2026-09-24)
FAIL_CEILING = 0.01
PROBE = 16
NONTRANSIENT = (
    "BadRequest",
    "UnprocessableEntity",
    " 400 ",
    " 422 ",
    "Error code: 400",
)
QUOTA = (
    "free-models-per-day",
    "per-day",
    "per day",
    "usage limit",
    "Payment Required",
    " 402 ",
)

SETS = {
    "sst5": (
        "score-sst5",
        "sample.jsonl",
        ("rows-jev.jsonl", "rows-jev-run2.jsonl", "rows-jev-run3.jsonl"),
    ),
    "banking77": (
        "choice-banking77",
        "subset.jsonl",
        ("rows-jev.jsonl", "rows-jev-run2.jsonl", "rows-jev-run3.jsonl"),
    ),
    "clinc150": (
        "choice-clinc150",
        "subset.jsonl",
        ("rows-jev.jsonl", "rows-jev-run2.jsonl", "rows-jev-run3.jsonl"),
    ),
    "scifact": ("noul-scifact", "sample.jsonl", tuple(f for _, f in NV.JEV_RUNS)),
    "fever": ("noul-fever", "sample.jsonl", tuple(f for _, f in NV.JEV_RUNS)),
}
WIN_UNDER_TEST = {
    "sst5": "MAE sign test WIN",
    "banking77": "accuracy WIN (McNemar)",
    "clinc150": "handled at peak >= 0.60 WIN",
    "scifact": "Brier WIN",
    "fever": "ECE WIN",
}


def load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def slug(model):
    return model.replace("/", "__").replace(":", "_")


def comparators():
    """Free models jev-14qk found answering >= 49/50 SST-5 rows, in its order, then the paid ones."""
    out = []
    for model in FREE_STRUCTURED:
        rows = load(os.path.join(WORK, "openrouter", f"rows-sst5-{slug(model)}.jsonl"))
        if rows is None:
            continue
        got = {r["i"] for r in rows if "score" in r}
        if len(got) >= FREE_MIN_ANSWERED:
            out.append(model)
    return out + list(PAID)


def is_answer(r):
    return "noul" in r or "choice" in r or "score" in r


def cell_file(dataset, model):
    """The structured file, or the prompted file when the 16-row structured probe was refused."""
    base = os.path.join(HERE, f"rows-{dataset}-{slug(model)}")
    rows = load(base + ".jsonl")
    refused = rows and len(rows) >= PROBE and not any(is_answer(r) for r in rows)
    if refused and all(
        any(t in r.get("error", "") for t in NONTRANSIENT) for r in rows
    ):
        return base + "-prompted.jsonl", "prompted (structured probe refused)"
    return base + ".jsonl", "structured"


def status(rows):
    """(answered ids, failed ids, quota ids): last row per id decides."""
    last = {}
    for r in rows:
        if is_answer(r) or r["i"] not in last or not is_answer(last[r["i"]]):
            last[r["i"]] = r
    ans = {i for i, r in last.items() if is_answer(r)}
    quota = {
        i
        for i, r in last.items()
        if not is_answer(r) and any(t in r["error"] for t in QUOTA)
    }
    failed = {i for i, r in last.items() if not is_answer(r)} - quota
    return ans, failed, quota


def zero_mass(r):
    """The adapter's all-zero map (jev-mly), per unit's recorded field."""
    if "rawSum" in r and r.get("choice") is not None:
        return r["rawSum"] == 0
    orig = r.get("originalProbabilities")
    return isinstance(orig, dict) and sum(orig.values()) == 0


# ---------------------------------------------------------------- per-set verdicts, one Jev run


def v_sst5(sample, jrows, crows, keep):
    je, ce = JV.sst_eval(sample, jrows), JV.sst_eval(sample, crows)
    s = [sample[k] for k in keep]
    je, ce = [je[k] for k in keep], [ce[k] for k in keep]
    out, passed = JV.sst_run_verdict(s, je, ce)
    (va, _pa), (vm, pm), counts = out[
        "Haiku"
    ]  # "Haiku" is the unit scorer's name for the other arm
    return {
        "win": vm == "WIN",
        "lose": "LOSE" in (va, vm),
        "pass": passed,
        "detail": f"acc {counts[0]}/{counts[1]} {va}; MAE {counts[2]}/{counts[3]} p={pm:.3g} {vm}",
    }


def v_banking77(sample, jrows, crows, keep):
    je, ce = JV.b77_eval(sample, jrows), JV.b77_eval(sample, crows)
    je, ce = [je[k] for k in keep], [ce[k] for k in keep]
    lab, b, c, p, jk = JV.b77_verdict(je, ce)
    return {
        "win": lab == "WIN",
        "lose": lab in ("LOSE", "NOT-SCORED"),
        "pass": lab in ("WIN", "NON-INFERIOR"),
        "detail": f"{jk} vs {sum(1 for x in ce if x[1])}, {b}/{c} p={p:.3g} {lab}",
    }


def v_clinc150(sample, jrows, crows, keep, zero_as_none=False):
    s = [sample[k] for k in keep]
    jp = [C.preds(sample, jrows)[k] for k in keep]
    cp = [C.preds(sample, crows, zero_as_none=zero_as_none)[k] for k in keep]
    n_oos = sum(1 for it in s if it["intent"] == C.OOS)
    ins = [k for k, it in enumerate(s) if it["intent"] != C.OOS]
    jc, cc = C.correct(s, jp), C.correct(s, cp)
    feasible = all(sum(x[k] for k in ins) / len(ins) >= C.FEASIBLE for x in (jc, cc))
    labs = {}
    for name, a, b in (
        ("overall", jc, cc),
        (
            "handled",
            C.handled(s, C.gate(s, jp, C.PRIMARY_GATE, "peak")),
            C.handled(s, C.gate(s, cp, C.PRIMARY_GATE, "peak")),
        ),
    ):
        lab, jk, ck, bb, c2, p, _ = C.verdict(a, b, n_oos)
        labs[name] = (
            lab if feasible else "NOT-SCORED",
            f"{name} {jk} vs {ck}, {bb}/{c2} p={p:.3g}",
        )
    return {
        "win": labs["handled"][0] == "WIN",
        "lose": any(v[0] in ("LOSE", "NOT-SCORED") for v in labs.values()),
        "pass": all(v[0] in ("WIN", "NON-INFERIOR") for v in labs.values()),
        "detail": "; ".join(f"{v[1]} {v[0]}" for v in labs.values()),
    }


def v_noul(metric):
    def f(sample, jarm, carm, y, keep):
        v = NV.pair(jarm, carm, y, keep)
        loses = "LOSE" in (v["acc"][3],) + tuple(v[m][2] for m in NV.METRICS)
        return {
            "win": v[metric][2] == "WIN",
            "lose": loses,
            "pass": NV.bar1(jarm, y)[0] and not loses,
            "detail": f"acc {v['acc'][0]}/{v['acc'][1]} {v['acc'][3]}; "
            + ", ".join(f"{m} {v[m][2]}" for m in NV.METRICS),
        }

    return f


# ---------------------------------------------------------------- one cell


def score_cell(dataset, crows_path):
    d, sname, jev_files = SETS[dataset]
    sample = load(os.path.join(WORK, d, sname))
    n = len(sample)
    crows = load(crows_path)
    if crows is None:
        return {"state": "NOT_RUN"}
    ans, failed, quota = status(crows)
    missing = n - len(ans) - len(failed) - len(quota)
    info = {
        "answered": len(ans),
        "failed": len(failed),
        "quota": len(quota),
        "missing": missing,
    }
    if quota or missing:
        return {"state": "BLOCKED" if quota else "INCOMPLETE", **info}
    if len(failed) > FAIL_CEILING * n:
        return {"state": "NOT-SCORED (failed rows over 1%)", **info}
    last = {}
    for r in crows:
        if is_answer(r):
            last[r["i"]] = r
    zm = {i for i, r in last.items() if zero_mass(r)}
    info["zero_mass"] = len(zm)
    readings = {"all": list(range(n))}
    if zm:
        readings["zero-mass dropped"] = [
            k for k, s in enumerate(sample) if s["i"] not in zm
        ]
    per_run = []
    for jf in jev_files:
        jrows = load(os.path.join(WORK, d, jf))
        res = {}
        for rname, keep in readings.items():
            if dataset in ("scifact", "fever"):
                y = [1 if s["truth"] else 0 for s in sample]
                jarm = NV.load_arm(d, jf, sample, y)
                carm = NV.load_arm(
                    os.path.relpath(os.path.dirname(crows_path), WORK),
                    os.path.basename(crows_path),
                    sample,
                    y,
                )
                res[rname] = v_noul("brier" if dataset == "scifact" else "ece")(
                    sample, jarm, carm, y, keep
                )
            elif dataset == "clinc150":
                shipped = v_clinc150(sample, jrows, crows, keep)
                if rname == "all" and zm:
                    none_r = v_clinc150(sample, jrows, crows, keep, zero_as_none=True)
                    res["zero-mass = none"] = none_r
                res[rname] = shipped
            else:
                res[rname] = {"sst5": v_sst5, "banking77": v_banking77}[dataset](
                    sample, jrows, crows, keep
                )
        per_run.append((jf, res))
    k = len(per_run)
    wins = sum(1 for _, res in per_run if all(v["win"] for v in res.values()))
    passes = sum(1 for _, res in per_run if all(v["pass"] for v in res.values()))
    loses = sum(1 for _, res in per_run if any(v["lose"] for v in res.values()))
    return {
        "state": "SCORED",
        **info,
        "runs": per_run,
        "k": k,
        "wins": wins,
        "passes": passes,
        "loses": loses,
        "win": "HOLDS" if wins == k else f"DOES NOT HOLD ({wins}/{k} Jev runs)",
        "pass": "HOLDS" if passes == k else f"FAILS ({passes}/{k} Jev runs pass)",
    }


def spend(model, paths):
    tin = tout = 0
    for p in paths:
        for r in load(p) or []:
            u = r.get("usage") or {}
            tin += u.get("input_tokens") or 0
            tout += u.get("output_tokens") or 0
    usd = None
    if model in PRICE:
        usd = tin * PRICE[model][0] + tout * PRICE[model][1]
    return tin, tout, usd


def selfcheck():
    """Committed Haiku rows through this file's code: the committed headline pairing must reproduce."""
    expect = {
        "sst5": True,
        "banking77": True,
        "clinc150": True,
        "scifact": True,
        "fever": True,
    }
    good = True
    for dataset in SETS:
        d = SETS[dataset][0]
        cell = score_cell(dataset, os.path.join(WORK, d, "rows-haiku.jsonl"))
        first = cell["runs"][0][1]["all"] if cell.get("state") == "SCORED" else None
        ok = first is not None and first["win"] == expect[dataset] and first["pass"]
        good = good and ok
        print(
            f"  {'ok ' if ok else 'BAD'} {dataset}: Jev run 1 x committed Haiku: {first['detail'] if first else cell}"
        )
    return good


def main(argv):
    print(
        "Self-check: each unit's committed headline (Jev run 1 x Haiku) through this scorer"
    )
    if not selfcheck():
        print("self-check failed; nothing else is scored")
        return 1
    if "--selfcheck" in argv:
        return 0
    models = comparators()
    print(f"\nComparators: {', '.join(models)}")
    print(
        f"(free models kept when jev-14qk's rows show >= {FREE_MIN_ANSWERED}/50 answered)\n"
    )
    print(
        "| Model | Set | Mode | State | Answered / failed / quota / zero-mass | Win under test vs every Jev run | Pass rule vs every Jev run |"
    )
    print("|---|---|---|---|---|---|---|")
    need_ne = []
    details = []
    for model in models:
        paths = []
        for dataset in SETS:
            path, mode = cell_file(dataset, model)
            paths += (
                [os.path.join(HERE, f"rows-{dataset}-{slug(model)}.jsonl"), path]
                if mode != "structured"
                else [path]
            )
            cell = score_cell(dataset, path)
            counts = f"{cell.get('answered', '')} / {cell.get('failed', '')} / {cell.get('quota', '')} / {cell.get('zero_mass', '')}"
            if cell["state"] != "SCORED":
                print(
                    f"| {model} | {dataset} | {mode} | {cell['state']} | {counts} | | |"
                )
                continue
            print(
                f"| {model} | {dataset} | {mode} | SCORED | {counts} | {WIN_UNDER_TEST[dataset]}: {cell['win']} | {cell['pass']} |"
            )
            if cell["wins"] < cell["k"] or cell["loses"]:
                need_ne.append(
                    f"{model} x {dataset}: win {cell['win']}; pass {cell['pass']}; runs with a LOSE {cell['loses']}"
                )
            for jf, res in cell["runs"]:
                for rname, v in res.items():
                    details.append(
                        f"| {model} | {dataset} | {jf} | {rname} | {v['detail']} |"
                    )
        tin, tout, usd = spend(model, sorted(set(paths)))
        print(
            f"|   spend {model} | | | | tokens {tin:,} in / {tout:,} out | {f'${usd:.4f} at list' if usd is not None else '$0 (free)'} | |"
        )
    print("\nPer Jev run and reading")
    print("| Model | Set | Jev run | Reading | Tests |")
    print("|---|---|---|---|---|")
    for line in details:
        print(line)
    print("\nNEGATIVE_EVIDENCE due (a win that does not hold, or any LOSE):")
    for line in need_ne or ["none"]:
        print(f"- {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
