#!/usr/bin/env python3
"""Keyless loss-depth autopsy of the MiniWoB AX-pruning run (jev-9gtw.7, NEGATIVE_EVIDENCE R107).

No TypeSafe call. It reads the eight committed row files and re-creates each step-0 page in local
headless Chrome with the pinned dd04baf floor (via run_frozen.load_pinned_ax). A page is accepted
only if its serialized full state matches the row's `full_state_bytes` byte for byte. The code and
random arms are re-run on those pages and must reproduce their rows' `seen_state_bytes`, too. On
the verified pages it measures:

1. Where the cut went. The rows carry no per-node Noul answers (ax_prune.LiveNoulPruner discards
   them), so per-Noul keep counts are NOT recoverable. What the pages do show: page size, closure
   structure, the questions spent on text runs, and the smallest observation that still contains
   the full arm's chosen target.
2. Token economics. The pruner's cost per node comes from a least-squares fit on the 100 measured
   requests. The planner's cost per observation is estimated by scaling the full arm's measured
   tokens by request bytes. That estimator is validated against the measured code and random arms.
3. Break-even planner cost ratios for the measured design and for the three hypotheses.

Usage: autopsy.py [--out PATH]   (prints the JSON summary; --out also writes it)
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_frozen  # noqa: E402

ROWS = HERE / "rows"
ARMS = ("full", "code", "jev", "random")
SPLITS = ("dev", "heldout")
PRUNER_QUESTIONS_PER_NODE = 3
BAR_CUT = 0.40


def load_rows() -> dict[tuple[str, str], dict[str, dict]]:
    out = {}
    for split in SPLITS:
        for arm in ARMS:
            rows = [json.loads(line) for line in open(ROWS / f"{split}-{arm}.jsonl")]
            out[(split, arm)] = {r["task"]: r for r in rows}
    return out


def compact(obj) -> int:
    return len(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode())


def planner_request_bytes(ax, utterance, els, opts) -> int:
    """Bytes of state + questions exactly as the step-0 v1 planner would build them."""
    fl, jv = ax.floor, ax.jev_v1
    state = fl.serialize_state(utterance, els, 0, ax.MAX_STEPS, [], opts)
    actions, text_spans, _ = jv.build_candidates(
        utterance, els, opts, include_none=True
    )
    questions = jv.build_questions(utterance, els, actions, text_spans)
    return compact({"state": state, "questions": questions})


def reconstruct(ax, rows) -> list[dict]:
    """One record per (split, task): the verified step-0 page plus derived measurements."""
    fl = ax.floor
    records = []
    for split in SPLITS:
        full_rows = rows[(split, "full")]
        for task, frow in full_rows.items():
            env = fl.make_env(task, fl.BENCHMARK_WAIT_MS)
            try:
                obs, _ = env.reset(seed=frow["js_seed"])
                driver = env.unwrapped.instance.driver
                driver.execute_script(fl._PATCH_JS, fl.BENCHMARK_EPISODE_MAX_MS)
                utterance = obs["utterance"]
                els = fl.elements_from_obs(obs)
                opts = fl.select_options(driver)
            finally:
                env.close()
            full_state = fl.serialize_state(utterance, els, 0, ax.MAX_STEPS, [], opts)
            ok = utterance == frow["utterance"] and all(
                compact(full_state) == rows[(split, arm)][task]["full_state_bytes"][0]
                for arm in ARMS
            )
            rec = {"split": split, "task": task, "verified": ok, "utterance": utterance}
            if not ok:
                records.append(rec)
                continue

            def seen_bytes(seen):
                return compact(
                    fl.serialize_state(utterance, seen, 0, ax.MAX_STEPS, [], opts)
                )

            code_seen = ax.code_selector(utterance, els)
            rng = random.Random(f"random|{task}|{frow['seed']}|0")
            random_seen = ax.random_selector(els, rng)
            positive = [e for e in els if int(e["ref"]) > 0]
            text_runs = [e for e in els if int(e["ref"]) < 0]
            parents = {int(e.get("parent", 0)) for e in els}
            target = int(frow["actions"][0]["ref"]) if frow["actions"] else 0
            minimal = ax.close_subgraph(els, {target}) if target > 0 else None
            jrow = rows[(split, "jev")][task]
            rec.update(
                {
                    "n_elements": len(els),
                    "n_positive": len(positive),
                    "n_text_runs": len(text_runs),
                    "n_containers": sum(int(e["ref"]) in parents for e in positive),
                    "code_bytes_match": seen_bytes(code_seen)
                    == rows[(split, "code")][task]["seen_state_bytes"][0],
                    "random_bytes_match": seen_bytes(random_seen)
                    == rows[(split, "random")][task]["seen_state_bytes"][0],
                    "req_bytes": {
                        "full": planner_request_bytes(ax, utterance, els, opts),
                        "code": planner_request_bytes(ax, utterance, code_seen, opts),
                        "random": planner_request_bytes(
                            ax, utterance, random_seen, opts
                        ),
                    },
                    "full_action": frow["actions"][0] if frow["actions"] else None,
                    "full_success": frow["success"] > 0,
                    "jev_kept_all": jrow["seen_nodes_total"]
                    == jrow["full_nodes_total"],
                    "jev_seen_nodes": jrow["seen_nodes_total"],
                    "minimal_nodes": len(minimal) if minimal is not None else None,
                    "minimal_state_bytes": seen_bytes(minimal) if minimal else None,
                    "text_questions": any(
                        e["kind"] in ax.jev_v1.floor.TEXT_INPUT_TAGS for e in els
                    ),
                }
            )
            if minimal:
                rec["req_bytes"]["minimal"] = planner_request_bytes(
                    ax, utterance, minimal, opts
                )
            records.append(rec)
    return records


def fit(x: np.ndarray, y: np.ndarray) -> tuple[list[float], float]:
    design = np.c_[np.ones_like(x), x]
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    pred = design @ coef
    r2 = 1 - float(((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())
    return [float(c) for c in coef], r2


def analyse(rows, records) -> dict:
    verified = [r for r in records if r["verified"]]
    by_key = {(r["split"], r["task"]): r for r in verified}
    out: dict = {
        "pages_total": len(records),
        "pages_verified": len(verified),
        "code_arm_reproduced": sum(r["code_bytes_match"] for r in verified),
        "random_arm_reproduced": sum(r["random_bytes_match"] for r in verified),
    }

    # --- Estimator: planner tokens ~ full tokens * request-bytes ratio, checked on code/random.
    errs = {"code": [], "random": []}
    for (split, task), r in by_key.items():
        full_tok = rows[(split, "full")][task]["planner_input_tokens"]
        for arm in errs:
            meas = rows[(split, arm)][task]["planner_input_tokens"]
            pred = full_tok * r["req_bytes"][arm] / r["req_bytes"]["full"]
            errs[arm].append((pred - meas) / meas)
    out["planner_token_estimator"] = {
        arm: {
            "median_abs_pct_err": round(100 * statistics.median(abs(e) for e in v), 2),
            "aggregate_pct_err": None,
            "n": len(v),
        }
        for arm, v in errs.items()
    }
    for arm in errs:
        pred_tot = meas_tot = 0.0
        for (split, task), r in by_key.items():
            full_tok = rows[(split, "full")][task]["planner_input_tokens"]
            pred_tot += full_tok * r["req_bytes"][arm] / r["req_bytes"]["full"]
            meas_tot += rows[(split, arm)][task]["planner_input_tokens"]
        out["planner_token_estimator"][arm]["aggregate_pct_err"] = round(
            100 * (pred_tot - meas_tot) / meas_tot, 2
        )

    # --- Pruner cost model from the 100 measured jev requests.
    jev = [rows[(s, "jev")][t] for s in SPLITS for t in rows[(s, "jev")]]
    n = np.array([r["full_nodes_total"] for r in jev], float)
    tok = np.array([r["pruner_input_tokens"] for r in jev], float)
    coef, r2 = fit(n, tok)
    out["pruner_tokens_per_element_fit"] = {
        "intercept": round(coef[0], 2),
        "per_element": round(coef[1], 2),
        "per_question": round(coef[1] / PRUNER_QUESTIONS_PER_NODE, 2),
        "r2": round(r2, 4),
        "n": len(jev),
    }
    # Two-term fit: per-element question text plus the state, sent once per request.
    b = np.array([r["full_state_bytes_total"] for r in jev], float)
    design = np.c_[np.ones_like(n), n, b]
    coef2, *_ = np.linalg.lstsq(design, tok, rcond=None)
    pred2 = design @ coef2
    r2b = 1 - float(((tok - pred2) ** 2).sum() / ((tok - tok.mean()) ** 2).sum())
    state_per_byte = float(coef2[2])
    out["pruner_tokens_two_term_fit"] = {
        "intercept": round(float(coef2[0]), 2),
        "per_element": round(float(coef2[1]), 2),
        "per_state_byte": round(state_per_byte, 4),
        "r2": round(r2b, 4),
    }

    per_split = {}
    for split in SPLITS:
        recs = [r for r in verified if r["split"] == split]
        full = rows[(split, "full")]
        jrows = rows[(split, "jev")]
        full_tok = sum(full[t]["planner_input_tokens"] for t in full)
        jev_tok = sum(jrows[t]["planner_input_tokens"] for t in jrows)
        pruner_tok = sum(jrows[t]["pruner_input_tokens"] for t in jrows)
        n_el = sum(r["n_elements"] for r in recs)
        n_text = sum(r["n_text_runs"] for r in recs)
        kept_all = [r for r in recs if r["jev_kept_all"]]
        # Minimal-closure bound: the full arm's target plus ancestors and text; "none" steps
        # keep the full page (nothing to aim at), which is conservative for the bound.
        min_tok = 0.0
        for r in recs:
            ft = full[r["task"]]["planner_input_tokens"]
            if "minimal" in r["req_bytes"]:
                min_tok += ft * r["req_bytes"]["minimal"] / r["req_bytes"]["full"]
            else:
                min_tok += ft
        saved_measured = full_tok - jev_tok
        saved_bound = full_tok - min_tok
        # Pruner token split by the two-term fit: the state part is paid once per request, the
        # question part scales with 3 Nouls per element (text runs included, answers unused).
        state_part = state_per_byte * sum(
            jrows[t]["full_state_bytes_total"] for t in jrows
        )
        question_part = pruner_tok - state_part
        no_text = (n_el - n_text) / n_el
        hyp_cost = {
            "H1_one_noul": state_part + question_part / PRUNER_QUESTIONS_PER_NODE,
            "H1_one_noul_no_text_runs": state_part
            + question_part / PRUNER_QUESTIONS_PER_NODE * no_text,
            "H2_fitted_cut": pruner_tok,
            "H3_node_text_state": question_part,
            "H1_H3_no_text_runs_combined": question_part
            / PRUNER_QUESTIONS_PER_NODE
            * no_text,
        }
        kept_min = kept_full = 0.0
        for r in kept_all:
            ft = full[r["task"]]["planner_input_tokens"]
            kept_full += ft
            kept_min += (
                ft
                * r["req_bytes"].get("minimal", r["req_bytes"]["full"])
                / r["req_bytes"]["full"]
            )
        per_split[split] = {
            "episodes": len(recs),
            "jev_kept_whole_page": len(kept_all),
            "kept_whole_page_elements_median": statistics.median(
                r["n_elements"] for r in kept_all
            )
            if kept_all
            else None,
            "pruned_page_elements_median": statistics.median(
                r["n_elements"] for r in recs if not r["jev_kept_all"]
            ),
            "kept_whole_page_tasks": sorted(r["task"] for r in kept_all),
            "kept_whole_page_with_text_input": sum(
                r["text_questions"] for r in kept_all
            ),
            "elements_total": n_el,
            "text_run_elements": n_text,
            "pruner_questions_total": PRUNER_QUESTIONS_PER_NODE * n_el,
            "pruner_questions_on_text_runs": PRUNER_QUESTIONS_PER_NODE * n_text,
            "containers_share_of_positive": round(
                sum(r["n_containers"] for r in recs)
                / sum(r["n_positive"] for r in recs),
                4,
            ),
            "full_planner_tokens": full_tok,
            "jev_planner_tokens": jev_tok,
            "pruner_tokens": pruner_tok,
            "measured_planner_cut": round(saved_measured / full_tok, 4),
            "minimal_closure_planner_cut_est": round(saved_bound / full_tok, 4),
            "minimal_closure_episodes_below_bar": sum(
                1
                for r in recs
                if "minimal" in r["req_bytes"]
                and 1 - r["req_bytes"]["minimal"] / r["req_bytes"]["full"] < BAR_CUT
            ),
            "none_action_episodes": sum("minimal" not in r["req_bytes"] for r in recs),
            "kept_whole_page_minimal_closure_cut_est": round(
                1 - kept_min / kept_full, 4
            )
            if kept_full
            else None,
            "pruner_state_part_tokens_est": round(state_part),
            "pruner_question_part_tokens_est": round(question_part),
            "pruner_tokens_est_by_hypothesis": {
                k: round(v) for k, v in hyp_cost.items()
            },
            # Break-even: pruning pays when c * planner_tokens_saved >= pruner_tokens,
            # c = planner price per input token / Jev price per input token. With a Jev
            # planner c = 1; equivalently, c is the number of planner calls one prune must serve.
            "break_even_ratio": {
                "measured_design_measured_cut": round(pruner_tok / saved_measured, 2),
                "measured_design_at_40pct_cut": round(
                    pruner_tok / (BAR_CUT * full_tok), 2
                ),
                "measured_design_minimal_closure_cut": round(
                    pruner_tok / saved_bound, 2
                ),
                **{
                    f"{k}_at_minimal_closure_cut": round(v / saved_bound, 2)
                    for k, v in hyp_cost.items()
                },
            },
        }
    out["per_split"] = per_split
    out["verified_task_failures"] = [
        f"{r['split']}/{r['task']}" for r in records if not r["verified"]
    ]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    ax, shas = run_frozen.load_pinned_ax()
    ax.floor.logging.getLogger().setLevel(ax.floor.logging.WARNING)
    rows = load_rows()
    records = reconstruct(ax, rows)
    summary = analyse(rows, records)
    summary["pinned_sources_sha256_16"] = {k: v[:16] for k, v in shas.items()}
    summary["live_requests"] = 0
    text = json.dumps(summary, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
