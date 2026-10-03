#!/usr/bin/env python3
"""Gate every live Jev call: class split, validity, noise ceiling, headroom, fit, rank.

Input: JSON candidate file (see --example). Output: JSON + one line.
Gates: G0b class gate (hard, first; savings = harmful-outcome base rate,
insurance = planted recall + cost ceiling) -> G0 shortcut floor (cheap
baseline on held) -> G1 validity (hard) -> G2 noise ceiling (agreement
inversion) -> G3 headroom -> G4 fit (Part A) -> rank + pilot rule.
Keyless; no network; no key.
"""

from __future__ import annotations
import json
import math
import os
import re
import subprocess
import sys

MIN_HEADROOM_DEFAULT = 0.05
MIN_HELD_N = 30
MIN_HARM_PER_WEEK_DEFAULT = 1.0
MIN_OUTCOME_N = 50
MIN_RECALL_DEFAULT = 0.9


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
    # G0b two classes, declared up front (default: savings).
    # SAVINGS (cost must occur in real traffic): blind-labelled OUTCOME
    # sample (>= MIN_OUTCOME_N) counting outcomes where the system must act;
    # harmful/week below the stated floor -> STOP.
    # INSURANCE (rare costly events): judged by recall on a preregistered
    # planted catastrophic set + daily cost below a stated ceiling, never
    # by real-harm frequency (rare by design). Recall below min_recall or
    # cost above the ceiling -> STOP.
    cls = candidate.get("class", "savings")
    if cls == "insurance":
        pl = candidate.get("planted")
        try:
            p_n = int(pl.get("n", -1))
            p_hit = int(pl.get("caught", -1))
            p_cost = float(candidate.get("est_daily_cost", -1))
            p_max = float(candidate.get("max_daily_cost", -1))
        except (TypeError, ValueError, AttributeError):
            p_n, p_hit, p_cost, p_max = -1, -1, -1, -1
        min_rec = candidate.get("min_recall", MIN_RECALL_DEFAULT)
        try:
            min_rec = float(min_rec)
        except (TypeError, ValueError):
            min_rec = MIN_RECALL_DEFAULT
        if (
            not isinstance(pl, dict)
            or p_n < 1
            or p_hit < 0
            or p_hit > p_n
            or p_cost < 0
            or p_max <= 0
        ):
            note(
                "G0b-insurance",
                False,
                "planted {n, caught} + est/max_daily_cost unstated or malformed: no insurance without a priced planted set",
            )
            status = "STOP"
        else:
            rec = p_hit / p_n
            ok0b = rec >= min_rec and p_cost <= p_max
            note(
                "G0b-insurance",
                ok0b,
                "planted recall %d/%d=%.3f (bar %.2f), cost $%.4f/day (ceiling $%.4f)"
                % (p_hit, p_n, rec, min_rec, p_cost, p_max),
            )
            if not ok0b:
                status = "STOP"
    else:
        if cls != "savings":
            note("G0b-class", False, "unknown class %r (savings|insurance)" % (cls,))
            status = "STOP"
        t = candidate.get("traffic")
        try:
            t_days = float(t.get("days", 0))
            t_opp = int(t.get("opportunities", -1))
            t_lab = int(t.get("outcomes_labelled", -1))
            t_harm = int(t.get("harmful", -1))
        except (TypeError, ValueError, AttributeError):
            t_days, t_opp, t_lab, t_harm = 0, -1, -1, -1
        floor = candidate.get("min_harmful_per_week", MIN_HARM_PER_WEEK_DEFAULT)
        try:
            floor = float(floor)
        except (TypeError, ValueError):
            floor = MIN_HARM_PER_WEEK_DEFAULT
        if (
            not isinstance(t, dict)
            or t_days <= 0
            or t_opp < 0
            or t_lab < MIN_OUTCOME_N
            or t_harm < 0
            or t_harm > t_lab
        ):
            note(
                "G0b-base-rate",
                False,
                "traffic {days, opportunities, outcomes_labelled>=%d, harmful} unstated/underpowered/malformed: no build without a blind-labelled outcome sample"
                % MIN_OUTCOME_N,
            )
            status = "STOP"
        else:
            hpw = t_harm / t_days * 7
            ok0b = hpw >= floor
            note(
                "G0b-base-rate",
                ok0b,
                "real traffic %d harmful / %d labelled outcomes over %.1fd = %.2f harmful/week (floor %.1f)"
                % (t_harm, t_lab, t_days, hpw, floor),
            )
            if not ok0b:
                status = "STOP"
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
    # G1-prior-overlap (jev-wjig): a replication must name the committed hash sets of every
    # earlier sample and share no row with them. 2026-10-02 a "fresh" longres replication
    # reused 67/67 files of the sample it claimed to replicate.
    priors = candidate.get("prior_samples") or []
    if candidate.get("replication") and not priors:
        ok = False
        note("G1-prior-overlap", False, "replication names no prior_samples hash files")
    elif priors:
        seen, missing = set(), []
        for path in priors:
            committed = (
                subprocess.run(
                    ["git", "ls-files", "--error-unmatch", path],
                    capture_output=True,
                    env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"),
                ).returncode
                == 0
            )
            try:
                text = open(path, encoding="utf-8").read()
            except OSError:
                committed = False
            if not committed:
                missing.append(path)
                continue
            for found in re.findall(r'"hash"\s*:\s*"([^"]+)"', text):
                seen.add(found)
        shared = sorted(set(hashes) & seen)
        if missing or shared:
            ok = False
            note(
                "G1-prior-overlap",
                False,
                "uncommitted prior %s; %d rows shared with prior samples %s"
                % (missing, len(shared), shared[:3]),
            )
        else:
            note(
                "G1-prior-overlap",
                True,
                "0 of %d rows in %d prior samples" % (len(hashes), len(priors)),
            )
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
                "traffic": {
                    "days": 7,
                    "opportunities": 500,
                    "outcomes_labelled": 60,
                    "harmful": 30,
                },
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
                "traffic": {
                    "days": 7,
                    "opportunities": 300,
                    "outcomes_labelled": 60,
                    "harmful": 20,
                },
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
                "traffic": {
                    "days": 7,
                    "opportunities": 100,
                    "outcomes_labelled": 60,
                    "harmful": 15,
                },
            },
            "STOP",
        )
    )
    # retry flip: REAL msax held-out (81 pairs, observed retry exits, session groups).
    # agreement illustrative {40,34} (no double-label sample taken) -> fit caps at PILOT.
    fixture = os.path.join(
        os.path.dirname(__file__), "fixtures", "msax-split-scrubbed.json"
    )
    with open(fixture, encoding="utf-8") as _fh:
        _msd_all = json.load(_fh)

    def expand_groups(groups):
        return [
            {"label": label, "session": group["group"]}
            for group in groups
            for label, count in ((1, group["pos"]), (0, group["neg"]))
            for _ in range(count)
        ]

    _ms = expand_groups(_msd_all["held"])
    _msd = expand_groups(_msd_all["dev"])
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
                "traffic": {
                    "days": 7,
                    "opportunities": 400,
                    "outcomes_labelled": 120,
                    "harmful": 40,
                },
            },
            "PILOT",
        )
    )
    # webscreen: REAL rows.jsonl (attack=pos, groups=source_sha, baseline=flagged_local).
    # agreement illustrative {60,57} (no rater study on these rows).
    import collections as _co

    ws_path = os.path.join(
        os.path.dirname(__file__), "..", "work", "hermes-webscreen-repro", "rows.jsonl"
    )
    with open(ws_path, encoding="utf-8") as _wfh:
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
                "traffic": {
                    "days": 7,
                    "opportunities": 423,
                    "outcomes_labelled": 100,
                    "harmful": 60,
                },
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
                "traffic": {
                    "days": 7,
                    "opportunities": 16464,
                    "outcomes_labelled": 100,
                    "harmful": 80,
                },
            },
            "GO",
        )
    )
    # G0b worked examples: real blind-labelled OUTCOME samples. The rows
    # below are scaffolding that passes every other gate, so only G0b
    # decides; the traffic blocks carry the real counts.
    # failtriage (1ba40655): 100 labelled outcomes (68 addressed, 32
    # harmless), 0 harmful in 7d -> STOP.
    fr = rows(40, 0.5, "fr")
    cases.append(
        (
            "failtriage-outcome",
            {
                "name": "failtriage",
                "class": "savings",
                "rows": fr,
                "label_source": "blind-human",
                "censoring_rate": 0.0,
                "recomputable": True,
                "baseline": {
                    "name": "always-neg",
                    "predictions": {
                        r["hash"]: "neg" for r in fr if r["split"] == "held"
                    },
                },
                "agreement": {"n": 40, "agree": 36},
                "features": {
                    "direction": "predict",
                    "future": False,
                    "answer_visible": True,
                    "primitive": "Score",
                },
                "daily_volume": 590,
                "action_value": 0.002,
                "traffic": {
                    "days": 7,
                    "opportunities": 4118,
                    "outcomes_labelled": 100,
                    "harmful": 0,
                },
            },
            "STOP",
        )
    )
    # vendor-paste (61ae2c43): 39 hunks blind-labelled, 0 vendored
    # executions. Sample underpowered (39 < 50) AND zero harm -> STOP.
    vp2 = rows(40, 0.5, "vp2")
    cases.append(
        (
            "vendor-paste-outcome",
            {
                "name": "vendor-paste",
                "class": "savings",
                "rows": vp2,
                "label_source": "blind-human",
                "censoring_rate": 0.0,
                "recomputable": True,
                "baseline": {
                    "name": "always-neg",
                    "predictions": {
                        r["hash"]: "neg" for r in vp2 if r["split"] == "held"
                    },
                },
                "agreement": {"n": 40, "agree": 36},
                "features": {
                    "direction": "predict",
                    "future": False,
                    "answer_visible": True,
                    "primitive": "Score",
                },
                "daily_volume": 50,
                "action_value": 0.01,
                "traffic": {
                    "days": 1,
                    "opportunities": 39,
                    "outcomes_labelled": 39,
                    "harmful": 0,
                },
            },
            "STOP",
        )
    )
    # gate cascade, INSURANCE class (conductor split): real harm ~0/50, so
    # savings would STOP; insurance judges planted recall + cost instead.
    # Planted set work/cascade-harm/planted.jsonl (30 rows: 19 in-scope
    # catastrophic, 7 quiet, 4 out-of-scope non-executable shapes): pre-rule
    # routes 19/19 catastrophic, 7/7 quiet clean. Cost: ~96 paid/day at
    # ~700 input tok (~$0.003/day) vs $0.05 ceiling -> GO.
    gc0 = rows(40, 0.5, "gc0")
    cases.append(
        (
            "cascade-insurance",
            {
                "name": "gate-cascade",
                "class": "insurance",
                "rows": gc0,
                "label_source": "blind-human",
                "censoring_rate": 0.0,
                "recomputable": True,
                "baseline": {
                    "name": "always-neg",
                    "predictions": {
                        r["hash"]: "neg" for r in gc0 if r["split"] == "held"
                    },
                },
                "agreement": {"n": 40, "agree": 36},
                "features": {
                    "direction": "predict",
                    "future": False,
                    "answer_visible": True,
                    "primitive": "Score",
                },
                "daily_volume": 800,
                "action_value": 0.002,
                "traffic": {
                    "days": 7,
                    "opportunities": 50,
                    "outcomes_labelled": 50,
                    "harmful": 0,
                },
                "planted": {"n": 19, "caught": 19},
                "est_daily_cost": 0.003,
                "max_daily_cost": 0.05,
            },
            "GO",
        )
    )
    # Insurance bar bites: recall 12/20 below 0.9 -> STOP even with harm present.
    im = rows(40, 0.5, "im")
    cases.append(
        (
            "insurance-miss",
            {
                "name": "leaky-screen",
                "class": "insurance",
                "rows": im,
                "label_source": "blind-human",
                "censoring_rate": 0.0,
                "recomputable": True,
                "baseline": {
                    "name": "always-neg",
                    "predictions": {
                        r["hash"]: "neg" for r in im if r["split"] == "held"
                    },
                },
                "agreement": {"n": 40, "agree": 36},
                "features": {
                    "direction": "predict",
                    "future": False,
                    "answer_visible": True,
                    "primitive": "Score",
                },
                "daily_volume": 800,
                "action_value": 0.002,
                "planted": {"n": 20, "caught": 12},
                "est_daily_cost": 0.003,
                "max_daily_cost": 0.05,
            },
            "STOP",
        )
    )
    # Mechanism proof (SYNTHETIC labels, clearly marked): 45 harmful in 60
    # labelled outcomes clears the default floor -> GO. Proves the gate
    # opens when harm exists; no real candidate currently does.
    syn = rows(40, 0.5, "syn")
    cases.append(
        (
            "mechanism-opens-on-harm",
            {
                "name": "synthetic-opener",
                "class": "savings",
                "rows": syn,
                "label_source": "blind-human",
                "censoring_rate": 0.0,
                "recomputable": True,
                "baseline": {
                    "name": "always-neg",
                    "predictions": {
                        r["hash"]: "neg" for r in syn if r["split"] == "held"
                    },
                },
                "agreement": {"n": 40, "agree": 36},
                "features": {
                    "direction": "predict",
                    "future": False,
                    "answer_visible": True,
                    "primitive": "Score",
                },
                "daily_volume": 800,
                "action_value": 0.002,
                "traffic": {
                    "days": 7,
                    "opportunities": 200,
                    "outcomes_labelled": 60,
                    "harmful": 45,
                },
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
    # G0b worked examples must be decided BY the base-rate finding.
    for name, gate, want_base in (
        ("failtriage-outcome", "G0b-base-rate", False),
        ("vendor-paste-outcome", "G0b-base-rate", False),
        ("cascade-insurance", "G0b-insurance", True),
        ("insurance-miss", "G0b-insurance", False),
        ("mechanism-opens-on-harm", "G0b-base-rate", True),
    ):
        cand = next(c for n, c, w in cases if n == name)
        g0b = [f for f in check(cand)["findings"] if f["gate"] == gate]
        okb = len(g0b) == 1 and g0b[0]["pass"] == want_base
        print(
            "%s %s=%s want %s %s"
            % (
                name,
                gate,
                g0b[0]["pass"] if g0b else "missing",
                want_base,
                "ok" if okb else "MISMATCH",
            )
        )
        if not okb:
            fails.append(name + ":G0b")
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
