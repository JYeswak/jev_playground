#!/usr/bin/env python3
"""Calibration audit v1: are Jev's probabilities calibrated?

Reads foundation/fixtures/calibration-v1.jsonl, asks one atomic question per
row over HTTPS, and writes foundation/runs/<utc>.json per report-v1.

Foundation contract (these bounds ARE the cancel-correctness story):
  TIMEOUT_S=30 per request, MAX_RETRIES=2, backoff capped at 8 s, one question
  per request, sequential. Ctrl-C writes a partial receipt (interrupted=true).
  Failures become rows with error_kind (timeout/http_error/malformed/refused),
  excluded from calibration denominators with counts disclosed. Nothing retries
  forever, nothing accumulates without bound, no global state.

Metrics: 10-bin ECE, Brier score, Wilson 95% CI per bin, threshold sweep
(accuracy/coverage at t in {0.25,0.5,0.75,0.8,0.9}), choice top-1 accuracy.

Usage: TYPESAFE_API_KEY=... python3 run_calibration.py [--fixture PATH] [--model jev-latest]
"""

import hashlib
import json
import math
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
API_URL = "https://api.typesafe.ai/v1/systemone"
TIMEOUT_S = 30
MAX_RETRIES = 2
BACKOFF_S = 2
THRESHOLDS = [0.25, 0.5, 0.75, 0.8, 0.9]
N_BINS = 10


class ApiError(Exception):
    def __init__(self, kind, detail=""):
        super().__init__(detail)
        self.kind = kind


def ask(api_key, model, state, question):
    body = json.dumps({"model": model, "state": state, "questions": {"q": question}}).encode()
    last_kind, last_detail, attempts, latency = "http_error", "", 0, 0.0
    for attempt in range(MAX_RETRIES + 1):
        attempts = attempt + 1
        req = urllib.request.Request(API_URL, data=body, headers={
            "Content-Type": "application/json", "Authorization": "Bearer " + api_key})
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                latency += (time.monotonic() - t0) * 1000
                payload = json.loads(resp.read().decode())
        except TimeoutError:
            last_kind, last_detail = "timeout", f"attempt {attempts}"
        except Exception as e:  # noqa: BLE001 - transport failure taxonomy ends here
            last_kind, last_detail = "http_error", f"{type(e).__name__}: {e}"[:200]
        else:
            try:
                return payload["answers"]["q"], latency, attempts
            except (KeyError, TypeError):
                last_kind, last_detail = "malformed", json.dumps(payload)[:200]
        if attempt < MAX_RETRIES:
            time.sleep(min(BACKOFF_S * 2 ** attempt, 8))
    raise ApiError(last_kind, last_detail)


def as_noul(answer):
    v = answer.get("noul")
    if not isinstance(v, (int, float)) or not (0.0 <= v <= 1.0):
        raise ApiError("malformed", f"noul out of range: {v!r}"[:200])
    return float(v)


def wilson(acc, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    d = 1 + z * z / n
    c = acc + z * z / (2 * n)
    m = z * math.sqrt(acc * (1 - acc) / n + z * z / (4 * n * n))
    return (max(0.0, (c - m) / d), min(1.0, (c + m) / d))


def main():
    fixture_path = os.path.join(HERE, "fixtures", "calibration-v1.jsonl")
    model = "jev-latest"
    args = sys.argv[1:]
    while args:
        if args[0] == "--fixture":
            fixture_path = args[1]; args = args[2:]
        elif args[0] == "--model":
            model = args[1]; args = args[2:]
        else:
            sys.exit(f"unknown arg {args[0]}")
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        sys.exit("TYPESAFE_API_KEY is not set")
    rows = [json.loads(l) for l in open(fixture_path) if l.strip()]
    started = datetime.now(timezone.utc)
    items, interrupted = [], False
    try:
        for i, row in enumerate(rows):
            q = {"type": "noul", "instructions": row["instructions"]} if row["kind"] == "noul" else {
                "type": "choice", "instructions": row["instructions"],
                "criteria": row["expected"]["options"]}
            try:
                ans, latency, attempts = ask(api_key, model, {"text": row["state"]}, q)
                if row["kind"] == "noul":
                    pred, conf = as_noul(ans), None
                else:
                    pred = ans.get("choice")
                    if not isinstance(pred, str):
                        raise ApiError("malformed", f"choice missing: {ans!r}"[:200])
                    conf = ans.get("confidence")
                items.append({"id": row["id"], "kind": row["kind"], "expected": row["expected"],
                              "predicted": pred, "confidence": conf, "error_kind": None,
                              "latency_ms": round(latency, 1), "attempts": attempts})
            except ApiError as e:
                items.append({"id": row["id"], "kind": row["kind"], "expected": row["expected"],
                              "predicted": None, "confidence": None, "error_kind": e.kind,
                              "latency_ms": 0.0, "attempts": MAX_RETRIES + 1})
            print(f"[{i+1}/{len(rows)}] {row['id']} "
                  f"{items[-1]['predicted']!r} err={items[-1]['error_kind']}", flush=True)
    except KeyboardInterrupt:
        interrupted = True
        print("\ninterrupted: writing partial receipt", flush=True)

    ok = [it for it in items if it["error_kind"] is None and it["kind"] == "noul"]
    errs = {}
    for it in items:
        if it["error_kind"]:
            errs[it["error_kind"]] = errs.get(it["error_kind"], 0) + 1
    bins = []
    for b in range(N_BINS):
        lo, hi = b / N_BINS, (b + 1) / N_BINS
        pts = [(it["predicted"], it["expected"]["p"]) for it in ok
               if (it["predicted"] == 1.0 and hi == 1.0 and lo <= 1.0) or (lo <= it["predicted"] < hi)]
        n = len(pts)
        acc = sum(y for _, y in pts) / n if n else 0.0
        mean_p = sum(p for p, _ in pts) / n if n else (lo + hi) / 2
        lo_ci, hi_ci = wilson(acc, n)
        bins.append({"bin": [lo, hi], "n": n, "mean_p": round(mean_p, 3),
                     "accuracy": round(acc, 3), "ci95": [round(lo_ci, 3), round(hi_ci, 3)]})
    ece = round(sum(abs(b["accuracy"] - b["mean_p"]) * b["n"] for b in bins) / len(ok), 4) if ok else None
    brier = round(sum((it["predicted"] - it["expected"]["p"]) ** 2 for it in ok) / len(ok), 4) if ok else None
    sweeps = []
    for t in THRESHOLDS:
        dec = [it for it in ok if max(it["predicted"], 1 - it["predicted"]) >= t]
        acc = sum(1 for it in dec if (it["predicted"] >= 0.5) == bool(it["expected"]["p"])) / len(dec) if dec else None
        sweeps.append({"threshold": t, "decided": len(dec), "coverage": round(len(dec) / len(ok), 3) if ok else 0,
                       "accuracy": round(acc, 3) if acc is not None else None})
    chc = [it for it in items if it["error_kind"] is None and it["kind"] == "choice"]
    ch_acc = sum(1 for it in chc if it["predicted"] == it["expected"]["choice"]) / len(chc) if chc else None
    report = {"schema": "jev-foundation.calibration-report.v1",
              "started_at": started.isoformat(), "interrupted": interrupted, "model": model,
              "fixture": {"name": os.path.basename(fixture_path), "rows": len(rows),
                          "sha256": hashlib.sha256(open(fixture_path, "rb").read()).hexdigest()},
              "config": {"timeout_s": TIMEOUT_S, "max_retries": MAX_RETRIES, "thresholds": THRESHOLDS},
              "items": items,
              "metrics": {"n": len(ok), "errors": errs, "ece": ece, "brier": brier, "bins": bins,
                          "thresholds": sweeps,
                          "choice_accuracy": round(ch_acc, 3) if ch_acc is not None else None}}
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    out = os.path.join(HERE, "runs", f"{stamp}.json")
    os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
    json.dump(report, open(out, "w"), indent=1)
    print(f"\nECE={ece} Brier={brier} choice_acc={report['metrics']['choice_accuracy']} "
          f"errors={errs} interrupted={interrupted}\nreceipt: {out}")
    for s in sweeps:
        print(f"  t={s['threshold']:<5} decided={s['decided']:>3}/{len(ok):<3} acc={s['accuracy']}")


if __name__ == "__main__":
    main()
