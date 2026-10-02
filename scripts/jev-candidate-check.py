#!/usr/bin/env python3
"""Gate every live Jev call: data validity, label-noise ceiling, headroom, fit, rank.

Input: JSON candidate file (see --example). Output: JSON + one line.
Gates: G0 shortcut floor (cheap baseline on held) -> G1 validity (hard) ->
G2 noise ceiling (agreement inversion) -> G3 headroom -> G4 fit (Part A) ->
rank + pilot rule. Keyless; no network; no key.
"""

from __future__ import annotations
import json
import math
import sys

MIN_HEADROOM_DEFAULT = 0.05
MIN_HELD_N = 30


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, max(0.0, (c - m) / den), min(1.0, (c + m) / den))


def invert_agreement(a):
    """Binary latent truth, two independent raters each correct w.p. q:
    agree = q^2 + (1-q)^2 -> q = (1 + sqrt(2a-1)) / 2. Upper bound (assumes
    independence + homogeneity, both optimistic)."""
    if a <= 0.5:
        return 0.5
    return (1 + math.sqrt(2 * a - 1)) / 2


def check(candidate):
    findings = []
    status = "GO"

    def note(gate, ok, detail):
        findings.append({"gate": gate, "pass": ok, "detail": detail})

    rows = candidate.get("rows", [])
    hashes = [r.get("hash") for r in rows if r.get("hash")]
    dev = [r for r in rows if r.get("split") == "dev"]
    held = [r for r in rows if r.get("split") == "held"]
    dev_groups = {r.get("group") for r in dev if r.get("group")}
    held_groups = {r.get("group") for r in held if r.get("group")}

    # G1 validity (hard)
    ok = True
    if candidate.get("label_source") not in ("observed-outcome", "blind-human"):
        ok = False
        note(
            "G1-label-source",
            False,
            "labels must be observed outcomes or blind-human, got %r"
            % candidate.get("label_source"),
        )
    else:
        note("G1-label-source", True, candidate["label_source"])
    if len(hashes) != len(set(hashes)):
        ok = False
        note("G1-duplicates", False, "duplicate row hashes")
    else:
        note("G1-duplicates", True, "%d unique hashes" % len(hashes))
    if dev_groups and held_groups and dev_groups & held_groups:
        ok = False
        note(
            "G1-leakage",
            False,
            "dev/held share groups: %s" % sorted(dev_groups & held_groups)[:5],
        )
    elif not dev_groups or not held_groups:
        ok = False
        note(
            "G1-leakage",
            False,
            "group split missing (need session/task groups on both sides)",
        )
    else:
        note("G1-leakage", True, "dev/held groups disjoint")
    cens = candidate.get("censoring_rate")
    if cens is None:
        ok = False
        note("G1-censoring", False, "censoring_rate unstated")
    elif cens > 0.2:
        ok = False
        note("G1-censoring", False, "censoring_rate %.3f > 0.20" % cens)
    else:
        note("G1-censoring", cens <= 0.1, "censoring_rate %.3f" % cens)
    if len(held) < MIN_HELD_N:
        ok = False
        note("G1-held-n", False, "held n=%d < %d" % (len(held), MIN_HELD_N))
    else:
        note("G1-held-n", True, "held n=%d" % len(held))
    if not candidate.get("recomputable", False):
        ok = False
        note("G1-recomputable", False, "rows not committed/recomputable")
    else:
        note("G1-recomputable", True, "rows committed")
    if not ok:
        status = "STOP"

    # G0 shortcut floor + G2 ceiling + G3 headroom (held-out only)
    base = candidate.get("baseline", {})
    preds = base.get("predictions", {})
    labels = {r["hash"]: r.get("label") for r in held if r.get("hash")}
    scored = [(h, labels[h], preds[h]) for h in labels if h in preds]
    posset = ("pos", "relevant", "applicable", "applicable-clear", 1, True)
    if scored:
        pos = [h for h, l, _ in scored if l in posset]
        base_rate = len(pos) / len(scored)
        maj_label = "pos" if base_rate >= 0.5 else "neg"
        maj_acc = sum(
            1 for _, l, _ in scored if (l in posset) == (maj_label == "pos")
        ) / len(scored)
        dec_acc = sum(1 for _, l, p in scored if (p in posset) == (l in posset)) / len(
            scored
        )
        floor = max(maj_acc, dec_acc)
        note(
            "G0-baseline",
            True,
            "%s held acc=%.3f majority=%.3f base_rate=%.3f floor=%.3f"
            % (base.get("name", "?"), dec_acc, maj_acc, base_rate, floor),
        )
        acc = floor
    else:
        acc, base_rate = None, None
        note("G0-baseline", False, "no baseline predictions on held hashes")
        status = "STOP"
    ag = candidate.get("agreement")
    if ag and ag.get("n", 0) >= 20:
        a = ag["agree"] / ag["n"]
        q = invert_agreement(a)
        note(
            "G2-ceiling",
            True,
            "agreement %d/%d=%.3f -> q=%.3f (upper bound)"
            % (ag["agree"], ag["n"], a, q),
        )
    else:
        q = None
        note("G2-ceiling", False, "need >=20 blind double-labelled items")
        status = "STOP" if status != "STOP" else status
    headroom = None
    if acc is not None and q is not None:
        headroom = q - acc
        mh = candidate.get("min_headroom", MIN_HEADROOM_DEFAULT)
        note(
            "G3-headroom",
            headroom >= mh,
            "ceiling %.3f - baseline %.3f = %.3f (min %.2f)" % (q, acc, headroom, mh),
        )
        if headroom < mh:
            status = "STOP"
    else:
        note("G3-headroom", False, "uncomputable")

    # G4 fit from Part A features (n=36, honest +-0.25)
    f = candidate.get("features", {})
    fit = 0.5
    if f.get("direction") in ("flag", "keep", "route"):
        fit -= 0.15
    elif f.get("direction") == "predict":
        fit += 0.2
    if f.get("future"):
        fit -= 0.2
    if f.get("answer_visible") is False:
        fit -= 0.1
    if f.get("primitive") == "Score":
        fit += 0.1
    elif f.get("primitive") in ("Choice", "Noul"):
        fit -= 0.15
    fit = max(0.05, min(0.95, fit))
    note("G4-fit", True, "fit=%.2f +-0.25 (Part A n=36) features=%s" % (fit, f))

    rank = None
    if headroom is not None:
        rank = (
            headroom
            * fit
            * candidate.get("daily_volume", 0)
            * candidate.get("action_value", 0)
        )
        note(
            "rank",
            True,
            "headroom %.3f x fit %.2f x vol %s x value %s = %.4f"
            % (
                headroom,
                fit,
                candidate.get("daily_volume"),
                candidate.get("action_value"),
                rank,
            ),
        )

    if status == "GO" and fit < 0.35:
        status = "PILOT"
        note("G4-fit-cap", True, "fit %.2f < 0.35: pilot-only, never full GO" % fit)
    line = "%s %s headroom=%s fit=%.2f rank=%s" % (
        status,
        candidate.get("name", "?"),
        ("%.3f" % headroom) if headroom is not None else "NA",
        fit,
        ("%.4f" % rank) if rank is not None else "NA",
    )
    return {
        "status": status,
        "findings": findings,
        "headroom": headroom,
        "fit": fit,
        "rank": rank,
        "line": line,
    }


def selftest():
    """Historical cases: memory-keep/V3/V5/retry must STOP-or-PILOT (never GO);
    gate-cascade/webscreen must PILOT-or-GO. All keyless, inline fixtures."""
    import hashlib as _hl

    def rows(n_held, pos_rate, prefix, n_dev=60):
        import hashlib

        out = []

        def mk(i, split, grp, total):
            h = hashlib.sha256(("%s%s%d" % (prefix, split, i)).encode()).hexdigest()[
                :12
            ]
            return {
                "hash": h,
                "label": "pos" if i < round(total * pos_rate) else "neg",
                "split": split,
                "group": grp,
            }

        for i in range(n_dev):
            out.append(mk(i, "dev", "d-sess%d" % (i % 15), n_dev))
        for i in range(n_held):
            out.append(mk(i, "held", "h-sess%d" % (i % 20), n_held))
        return out

    cases = []
    # memory-keep: majority-drop beats noise ceiling -> STOP
    mr = rows(40, 0.05, "mem")
    cases.append(
        (
            "memory-keep",
            {
                "name": "memory-keep",
                "rows": mr,
                "label_source": "blind-human",
                "censoring_rate": 0.0,
                "recomputable": True,
                "baseline": {
                    "name": "always-drop",
                    "predictions": {r["hash"]: "neg" for r in mr},
                },
                "agreement": {"n": 90, "agree": 79},
                "daily_volume": 1000,
                "action_value": 0.001,
            },
            "STOP",
        )
    )
    # V3 long-runner: positives too few for held power -> STOP (held n + censoring)
    v3 = rows(25, 0.04, "v3")
    cases.append(
        (
            "V3-small-n",
            {
                "name": "V3",
                "rows": v3,
                "label_source": "observed-outcome",
                "censoring_rate": 0.99,
                "recomputable": True,
                "baseline": {
                    "name": "always-short",
                    "predictions": {
                        r["hash"]: "neg" for r in v3 if r["split"] == "held"
                    },
                },
                "agreement": {"n": 50, "agree": 48},
                "daily_volume": 500,
                "action_value": 0.01,
            },
            "STOP",
        )
    )
    v5 = rows(12, 0.3, "v5")
    cases.append(
        (
            "V5-small-n",
            {
                "name": "V5",
                "rows": v5,
                "label_source": "observed-outcome",
                "censoring_rate": 0.0,
                "recomputable": True,
                "baseline": {
                    "name": "maj",
                    "predictions": {
                        r["hash"]: "neg" for r in v5 if r["split"] == "held"
                    },
                },
                "agreement": {"n": 30, "agree": 27},
                "daily_volume": 100,
                "action_value": 0.01,
            },
            "STOP",
        )
    )
    # retry flip: REAL msax held-out (81 pairs, observed retry exits, session groups).
    # agreement illustrative {40,34} (no double-label sample taken) -> fit caps at PILOT.
    with open("/Users/josh/Developer/jev/var/agent-tmp/msax-split.json") as _fh:
        _msd_all = json.load(_fh)
    _ms = _msd_all["held"]
    _msd = _msd_all["dev"]
    rt = [
        {
            "hash": _hl.sha256(("msax-h%d" % i).encode()).hexdigest()[:12],
            "label": "pos" if p["label"] == 1 else "neg",
            "split": "held",
            "group": (p.get("session") or "s%d" % i)[:24],
        }
        for i, p in enumerate(_ms)
    ]
    rt += [
        {
            "hash": _hl.sha256(("msax-d%d" % i).encode()).hexdigest()[:12],
            "label": "pos" if p["label"] == 1 else "neg",
            "split": "dev",
            "group": "dev-" + ((p.get("session") or "s%d" % i)[:20]),
        }
        for i, p in enumerate(_msd)
    ]
    _maj = (
        "pos"
        if sum(1 for r in rt if r["split"] == "held" and r["label"] == "pos") >= 40.5
        else "neg"
    )
    cases.append(
        (
            "retry-inverted",
            {
                "name": "retry",
                "rows": rt,
                "label_source": "observed-outcome",
                "censoring_rate": 0.0,
                "recomputable": True,
                "baseline": {
                    "name": "majority",
                    "predictions": {
                        r["hash"]: _maj for r in rt if r["split"] == "held"
                    },
                },
                "agreement": {"n": 40, "agree": 34},
                "features": {
                    "direction": "predict",
                    "future": True,
                    "answer_visible": False,
                    "primitive": "Choice",
                },
                "daily_volume": 400,
                "action_value": 0.005,
            },
            "PILOT",
        )
    )
    # webscreen: REAL rows.jsonl (attack=pos, groups=source_sha, baseline=flagged_local).
    # agreement illustrative {60,57} (no rater study on these rows).
    import collections as _co

    with open(
        "/Users/josh/Developer/jev/work/hermes-webscreen-repro/rows.jsonl"
    ) as _wfh:
        _wsrows = [json.loads(l) for l in _wfh if l.strip()]
    _by = _co.defaultdict(list)
    for _r in _wsrows:
        _by[_r.get("source_sha")].append(_r)
    _srcs = sorted(_by)
    _heldsrc = set(_srcs[len(_srcs) // 2 :])
    ws = [
        {
            "hash": _hl.sha256(("ws%d" % i).encode()).hexdigest()[:12],
            "label": "pos" if _r.get("attack") else "neg",
            "split": "held" if _r.get("source_sha") in _heldsrc else "dev",
            "group": ("h-" if _r.get("source_sha") in _heldsrc else "d-")
            + (_r.get("source_sha") or "?")[:16],
        }
        for i, _r in enumerate(_wsrows)
    ]
    _wbase = {
        r["hash"]: ("pos" if _wsrows[i].get("flagged_local") else "neg")
        for i, r in enumerate(ws)
        if r["split"] == "held"
    }
    cases.append(
        (
            "webscreen",
            {
                "name": "webscreen",
                "rows": ws,
                "label_source": "blind-human",
                "censoring_rate": 0.02,
                "recomputable": True,
                "baseline": {"name": "local-screen", "predictions": _wbase},
                "agreement": {"n": 60, "agree": 57},
                "features": {
                    "direction": "flag",
                    "future": False,
                    "answer_visible": True,
                    "primitive": "Score",
                },
                "daily_volume": 1000,
                "action_value": 0.002,
            },
            "GO",
        )
    )
    # gate cascade: observed outcomes, decent margin -> PILOT-or-GO
    gc = rows(200, 0.185, "gc")
    cases.append(
        (
            "gate-cascade",
            {
                "name": "gate-cascade",
                "rows": gc,
                "label_source": "observed-outcome",
                "censoring_rate": 0.0,
                "recomputable": True,
                "baseline": {
                    "name": "regex",
                    "predictions": {
                        r["hash"]: ("pos" if i < 30 else "neg")
                        for i, r in enumerate(gc)
                    },
                },
                "agreement": {"n": 50, "agree": 44},
                "features": {
                    "direction": "predict",
                    "future": False,
                    "answer_visible": True,
                    "primitive": "Score",
                },
                "daily_volume": 800,
                "action_value": 0.002,
            },
            "GO",
        )
    )
    fails = []
    for name, cand, want in cases:
        got = check(cand)["status"]
        ok = (
            (got == want)
            or (want == "GO" and got == "PILOT")
            or (want == "PILOT" and got == "GO")
        )
        print("%s: got %s want %s %s" % (name, got, want, "ok" if ok else "MISMATCH"))
        if not ok:
            fails.append(name)
    # strict: first three must be exactly STOP
    return 1 if fails else 0


def example():
    print(
        json.dumps(
            {
                "name": "example",
                "label_source": "observed-outcome",
                "censoring_rate": 0.0,
                "recomputable": True,
                "min_headroom": 0.05,
                "daily_volume": 500,
                "action_value": 0.002,
                "features": {
                    "direction": "predict",
                    "future": False,
                    "answer_visible": True,
                    "primitive": "Score",
                },
                "baseline": {"name": "majority", "predictions": {}},
                "agreement": {"n": 0, "agree": 0},
                "rows": [],
            },
            indent=1,
        )
    )


def main(argv):
    if "--selftest" in argv:
        sys.exit(selftest())
    if "--example" in argv:
        example()
        return 0
    path = argv[1] if len(argv) > 1 else None
    if not path:
        print(
            "usage: jev-candidate-check.py CANDIDATE.json [--selftest|--example]",
            file=sys.stderr,
        )
        return 2
    with open(path) as fh:
        result = check(json.load(fh))
    print(json.dumps(result, indent=1))
    print(result["line"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
