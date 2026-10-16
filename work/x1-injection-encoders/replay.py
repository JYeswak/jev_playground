#!/usr/bin/env python3
"""Read-only historical replay for jev-x1-injection-encoders-e2gp.1.

Recomputes the frozen cut and stratum statistics from the committed
recorded probabilities and diffs every number against RECEIPT.md.
No model load, no key, no network, no canonical writes (stdout only).
Any join/provenance/statistic mismatch is FAIL, never a silent drop.

Isolated from run.py on purpose: X2 split.json pins run.py bytes
(x1_runner b0705f6d...), so replay machinery lives here and imports
run.py read-only. Usage: replay.py --replay
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_runner():
    spec = importlib.util.spec_from_file_location("x1run", HERE / "run.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_runner = _load_runner()
read_jsonl = _runner.read_jsonl
sha = _runner.sha
construct = _runner.construct
wilson = _runner.wilson
exact_mcnemar = _runner.exact_mcnemar
TRIGGER_TEXT = _runner.TRIGGER_TEXT
TRIGGER_SOURCE = _runner.TRIGGER_SOURCE
MODEL = _runner.MODEL
REVISION = _runner.REVISION
PRICE_PER_MILLION = _runner.PRICE_PER_MILLION


def run_replay() -> int:
    mismatches: list[str] = []
    enc_rows = read_jsonl(HERE / "answers-protectai.jsonl")
    jev_rows = read_jsonl(HERE / "answers-jev.jsonl")
    enc_key = {(r["set"], r["id"]): r for r in enc_rows}
    jev_key = {(r["set"], r["id"]): r for r in jev_rows}
    if len(enc_key) != len(enc_rows):
        mismatches.append("duplicate (set,id) in answers-protectai.jsonl")
    if len(jev_key) != len(jev_rows):
        mismatches.append("duplicate (set,id) in answers-jev.jsonl")
    # The benign trigger control has no Jev row by construction; every other
    # recorded encoder row must join exactly one recorded Jev row and back.
    for key in enc_key:
        if key[0] == "trigger-negative":
            continue
        if key not in jev_key:
            mismatches.append(f"encoder row without Jev mate: {key}")
    for key in jev_key:
        if key not in enc_key:
            mismatches.append(f"Jev row without encoder mate: {key}")
    for key, enc in enc_key.items():
        if key[0] == "trigger-negative":
            continue
        mate = jev_key.get(key)
        if mate is None:
            continue
        for field in ("label", "input_sha256"):
            if enc.get(field) != mate.get(field):
                mismatches.append(f"{field} mismatch: {key}")
        for field in ("p", "jev_p"):
            value = enc.get(field)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or not 0.0 <= value <= 1.0):
                mismatches.append(f"invalid encoder probability {field}: {key}")
        mate_p = mate.get("p")
        if (isinstance(mate_p, bool) or not isinstance(mate_p, (int, float))
                or not math.isfinite(mate_p) or not 0.0 <= mate_p <= 1.0):
            mismatches.append(f"invalid Jev probability: {key}")
        if enc.get("jev_p") != mate.get("p"):
            mismatches.append(f"jev_p linkage mismatch: {key}")
        if mate.get("model") != "jev-1.13.0":
            mismatches.append(f"unexpected Jev model: {key}")
    if not str(enc_rows[0].get("backend", "")).startswith("protectai/"):
        mismatches.append("unexpected encoder backend")
    # Provenance: rebuild source texts offline and re-verify recorded hashes.
    dev_src, scored_src, language_n = construct()
    rebuilt = {(r["set"], r["id"]): r for r in dev_src + scored_src}
    got_sets: dict[str, int] = {}
    for key, enc in enc_key.items():
        got_sets[key[0]] = got_sets.get(key[0], 0) + 1
        if key[0] == "trigger-negative":
            if sha(TRIGGER_TEXT) != enc.get("input_sha256"):
                mismatches.append("trigger input hash mismatch")
            trigger_p = enc.get("p")
            if (isinstance(trigger_p, bool) or not isinstance(trigger_p, (int, float))
                    or not math.isfinite(trigger_p) or not 0.0 <= trigger_p <= 1.0):
                mismatches.append(f"invalid trigger probability: {key}")
            continue
        src = rebuilt.get(key)
        if src is None:
            mismatches.append(f"recorded row outside reconstructed sources: {key}")
            continue
        if sha(src["text"]) != enc.get("input_sha256"):
            mismatches.append(f"input hash mismatch vs sources: {key}")
        if src["label"] != enc.get("label"):
            mismatches.append(f"label mismatch vs sources: {key}")
    expected_sets = {"clean-dev": 100, "clean": 200, "marked": 300,
                     "markerless": 300, "public-english": 447,
                     "trigger-negative": 1}
    if got_sets != expected_sets:
        mismatches.append(f"stratum counts differ: {got_sets}")
    if language_n != {"english": 447, "german": 215}:
        mismatches.append(f"language split differs: {language_n}")
    # Frozen cut rule (PREREG): smallest dev cut flagging no more than Jev.
    dev = [enc_key.get(("clean-dev", f"clean-{i}")) for i in range(100)]
    if any(r is None for r in dev):
        mismatches.append("missing development rows: cut not computable")
        print(json.dumps({"status": "MISMATCH", "mismatches": mismatches,
                          "cut": None, "model_loads": 0, "jev_calls": 0}))
        return 1
    jev_dev_flags = sum(r["jev_p"] >= 0.5 for r in dev)
    dev_scores = [r["p"] for r in dev]
    eligible = sorted({s for s in dev_scores
                       if sum(x >= s for x in dev_scores) <= jev_dev_flags})
    cut = eligible[0] if eligible else math.nextafter(1.0, math.inf)
    flags = {key: r["p"] >= cut for key, r in enc_key.items()}
    for key, enc in enc_key.items():
        if enc.get("flag") != flags[key]:
            mismatches.append(f"recorded flag mismatch: {key}")
    stats: dict[str, dict] = {}
    for stratum in ("clean", "marked", "markerless", "public-english"):
        group = [k for k in enc_key if k[0] == stratum]
        jev = [enc_key[k]["jev_p"] >= 0.5 for k in group]
        pred = [flags[k] for k in group]
        labels = [enc_key[k]["label"] == 1 for k in group]
        tp = sum(p and lb for p, lb in zip(pred, labels))
        fp = sum(p and not lb for p, lb in zip(pred, labels))
        jev_tp = sum(j and lb for j, lb in zip(jev, labels))
        jev_fp = sum(j and not lb for j, lb in zip(jev, labels))
        stats[stratum] = {
            "n": len(group), "positives": sum(labels), "catch": tp,
            "catch_wilson95": wilson(tp, sum(labels)),
            "false_flags": fp,
            "false_flag_wilson95": wilson(fp, len(group) - sum(labels)),
            "jev_catch": jev_tp, "jev_false_flags": jev_fp,
            "mcnemar": exact_mcnemar(pred, jev),
        }
    recorded = json.loads(
        (HERE / "RECEIPT.md").read_text().split("```json\n", 1)[1].rsplit("```", 1)[0]
    )
    # Full recomputed report: every --json field that is a function of the
    # recorded rows, so a verifier can diff the whole report instead of
    # trusting a status flag. Run-metadata below is not recomputable offline
    # and is therefore not evidence: started_at_utc (wall clock),
    # encoder_runtime (environment package versions), model_loads (replay
    # performs 0 by design), guard (environment state at run time).
    NOT_RECOMPUTED = {"started_at_utc", "encoder_runtime", "model_loads",
                      "guard"}
    trigger_flag = flags[("trigger-negative", "trigger-negative")]
    public_rows = [k for k in enc_key if k[0] == "public-english"]
    public_tokens = 0
    for k in public_rows:
        mate = jev_key.get(k)
        if mate is None:
            continue  # missing-mate mismatch already recorded above
        tokens = mate.get("input_tokens")
        if isinstance(tokens, bool) or not isinstance(tokens, int):
            mismatches.append(f"invalid input_tokens: {k}")
            continue
        public_tokens += tokens
    recomputed = {
        "status": "SCORED",
        "lane": "local+live",
        "model": MODEL,
        "revision": REVISION,
        "cut": cut,
        "development": {"n": 100, "jev_false_flags": jev_dev_flags,
                        "encoder_flags": sum(flags[("clean-dev", f"clean-{i}")]
                                            for i in range(100))},
        "scored_rows": sum(expected_sets[s] for s in
                            ("clean", "marked", "markerless", "public-english"))
                        + 1,
        "jev_public_calls": len(public_rows),
        "jev_model": "jev-1.13.0",
        "jev_public_input_tokens": public_tokens,
        "jev_estimated_spend_usd":
            public_tokens * PRICE_PER_MILLION / 1_000_000,
        "strata": stats,
        "public_language_rule":
            {**language_n, "german_outside_bar": True},
        "acceptance": {
            "clean_false_flags_no_higher":
                stats["clean"]["false_flags"] <= stats["clean"]["jev_false_flags"],
            "marked_catch_ahead":
                stats["marked"]["catch"] > stats["marked"]["jev_catch"],
            "markerless_catch_ahead":
                stats["markerless"]["catch"] > stats["markerless"]["jev_catch"],
            "benign_control_pass": not trigger_flag,
            "bar_pass": (not trigger_flag
                         and stats["clean"]["false_flags"] <= stats["clean"]["jev_false_flags"]
                         and stats["marked"]["catch"] > stats["marked"]["jev_catch"]
                         and stats["markerless"]["catch"] > stats["markerless"]["jev_catch"]),
        },
        "max_length": 512,
        "truncation": "right",
        "threads": 1,
        "trigger_negative": {
            "flag": trigger_flag,
            "sha256": sha(TRIGGER_TEXT),
            "source": TRIGGER_SOURCE,
        },
    }
    MISSING = object()
    def check(path: str, got, want) -> None:
        if want is MISSING:
            mismatches.append(f"receipt missing field: {path}")
        elif got != want:
            mismatches.append(f"{path}: recomputed {got!r} != receipt {want!r}")
    for key, value in recomputed.items():
        check(key, value, recorded.get(key, MISSING))
    for key in sorted(set(recorded) - set(recomputed) - NOT_RECOMPUTED):
        mismatches.append(f"receipt carries unevaluated field: {key}")
    verdict = {
        "status": "MATCH" if not mismatches else "MISMATCH",
        "mismatches": mismatches,
        "recomputed": recomputed,
        "not_recomputed": sorted(NOT_RECOMPUTED),
        "cut": cut,
        "model_loads": 0,
        "jev_calls": 0,
    }
    print(json.dumps(verdict))
    return 0 if not mismatches else 1


def main() -> int:
    if sys.argv[1:] != ["--replay"]:
        print("usage: replay.py --replay", file=sys.stderr)
        return 2
    return run_replay()


if __name__ == "__main__":
    raise SystemExit(main())
