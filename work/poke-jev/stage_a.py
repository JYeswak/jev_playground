#!/usr/bin/env python3
"""PokéJev Stage A: replay action prediction, Jev vs PokéChamp's published table (bead jev-jy7t.1.3).

Bar and protocol: docs/demos/upstream-repro/pokejev-stage-a-20260925.md, committed before the first call.

  sample  offline: pick 500 turns per Elo band from milkkarten/pokechamp (test split, gen9ou,
          pinned revision) plus 250 disjoint calibration turns per band; build each state with
          PokéChamp's own translator (pc.build_state); write stage-a/sample.jsonl, states.jsonl.gz,
          calib.jsonl
  run     live: one Jev request per row, two Choice questions (player action, opponent action),
          official Python SDK, model pinned jev-1.13.0; appends stage-a/jev.jsonl, resumable
  score   keyless: floors (uniform, usage-frequency, repeat-last) and Jev against the bar; writes
          stage-a/receipt.json

Run (from the repo root):
  work/poke-jev/.venv/bin/python work/poke-jev/stage_a.py sample
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \\
    work/poke-jev/.venv/bin/python work/poke-jev/stage_a.py run
  work/poke-jev/.venv/bin/python work/poke-jev/stage_a.py score
Never prints a key.
"""

from __future__ import annotations

import contextlib
import gzip
import hashlib
import io
import json
import math
import os
import random
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import replay  # noqa: E402

OUT = os.path.join(HERE, "stage-a")
SAMPLE = os.path.join(OUT, "sample.jsonl")
STATES = os.path.join(OUT, "states.jsonl.gz")
CALIB = os.path.join(OUT, "calib.jsonl")
JEV = os.path.join(OUT, "jev.jsonl")
RECEIPT = os.path.join(OUT, "receipt.json")

HF_REPO = "milkkarten/pokechamp"
HF_REV = "b5820ff5d0c8d5e5cec692d55f756b6e5a66a203"
BANDS = ["1200-1399", "1400-1599", "1600-1799", "1800+"]
PER_BAND = 500
CALIB_PER_BAND = 250
SEED = 20260925
JEV_MODEL = "jev-1.13.0"
CONCURRENCY = 8
PLAYER_Q = "player_action"
OPP_Q = "opponent_action"
PLAYER_INSTR = (
    "Which action the player (called 'You' and 'Your' in the state) chooses for the current turn of "
    "this Pokémon Showdown Gen 9 OU battle."
)
OPP_INSTR = "Which action the opponent chooses for the current turn of this Pokémon Showdown Gen 9 OU battle."

# The bar, fixed in bead jev-jy7t.1.3 and the prereg; never edited after data.
BAR_TOP1_PLAYER = 0.30
BAR_TOP1_OPP = 0.16
LOGLOSS_EPS = 1e-6


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def append(path, row):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_states():
    out = {}
    if os.path.exists(STATES):
        with gzip.open(STATES, "rt", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    out[r["id"]] = r["text"]
    return out


# ------------------------------------------------------------------------------------ sample


def battles_by_band():
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download

    by = {b: [] for b in BANDS}
    for i in range(5):
        path = hf_hub_download(
            HF_REPO,
            f"data/test-0000{i}-of-00005.parquet",
            repo_type="dataset",
            revision=HF_REV,
        )
        tb = pq.read_table(path)
        for r in tb.to_pylist():
            if r["gamemode"] == "gen9ou" and r["elo"] in by:
                by[r["elo"]].append(r)
    for b in BANDS:
        by[b].sort(key=lambda r: r["battle_id"])
    return by


def display_map(opts, names, move_name):
    out = {}
    for o in opts:
        if o.startswith("switch "):
            key = o[len("switch ") :]
            d = "Switch to " + names.get(key, key).title()
        else:
            mid = o[len("move ") :].removesuffix(replay.TERA_SUFFIX)
            d = move_name(mid) + (
                " and Terastallize" if o.endswith(replay.TERA_SUFFIX) else ""
            )
        if d in out.values():
            d = f"{d} ({o})"
        out[o] = d
    return out


def prev_move(blocks, turn, side, snap_now, snaps):
    prev = snaps.get(turn - 1)
    if (
        prev is None
        or turn - 1 not in blocks
        or prev["active"][side] != snap_now["active"][side]
    ):
        return None
    lab = replay.label(blocks[turn - 1], side)
    return f"move {lab['key']}" if lab and lab["kind"] == "move" else None


def cmd_sample():
    import pc

    os.makedirs(OUT, exist_ok=True)
    for p in (SAMPLE, STATES, CALIB):
        if os.path.exists(p):
            print(
                f"refusing: {p} exists (the sample is fixed once drawn)",
                file=sys.stderr,
            )
            return 2
    by = battles_by_band()
    stats = Counter()
    with gzip.open(STATES, "wt", encoding="utf-8") as states_fh:
        for bi, band in enumerate(BANDS):
            rng = random.Random(f"{SEED}-{band}")
            order = list(by[band])
            rng.shuffle(order)
            n_eval = n_cal = 0
            for battle in order:
                if n_eval >= PER_BAND and n_cal >= CALIB_PER_BAND:
                    break
                lines = replay.clean_lines(battle["text"])
                why = replay.is_excluded(lines)
                if why:
                    stats[f"excluded:{why}"] += 1
                    continue
                player = replay.winner_side(lines)
                opp = replay.other(player)
                el = replay.eligible_turns(lines, player)
                if not el:
                    stats["no-eligible-turn"] += 1
                    continue
                pick = rng.choice(el)
                snap, t = pick["snap"], pick["turn"]
                preview = replay.team_preview(lines)
                p_label = replay.option_key(pick["player_label"])
                o_label = replay.option_key(pick["opponent_label"])
                if n_eval < PER_BAND:
                    hind = replay.hindsight_moves(lines)
                    try:
                        st = pc.build_state(
                            lines,
                            player,
                            t,
                            battle["battle_id"],
                            snap["active"][player],
                        )
                    except Exception as exc:  # noqa: BLE001 - recorded, the battle is skipped
                        stats[f"state-failed:{type(exc).__name__}"] += 1
                        continue
                    p_opts = replay.options(
                        hind[player].get(snap["active"][player], []),
                        replay.switch_keys(snap, player, preview),
                        not snap["tera_used"][player],
                    )
                    opp_moves = []
                    for m in (
                        snap["seen_moves"][opp].get(snap["active"][opp], [])
                        + st["opp_seen"]
                        + st["opp_potential"]
                    ):
                        if m and m not in opp_moves:
                            opp_moves.append(m)
                    o_opts = replay.options(
                        opp_moves,
                        replay.switch_keys(snap, opp, preview),
                        not snap["tera_used"][opp],
                    )
                    if p_label not in p_opts:
                        stats["player-label-not-in-options"] += 1
                        continue
                    blocks = replay.turn_blocks(lines)
                    snaps = dict(replay.track(lines))
                    rid = f"{band}-{n_eval:03d}"
                    text = st["text"]
                    row = {
                        "id": rid,
                        "band": band,
                        "battle_id": battle["battle_id"],
                        "month": battle["month_year"],
                        "turn": t,
                        "player": player,
                        "player_species": snap["active"][player],
                        "opp_species": snap["active"][opp],
                        # sets_1000.json keys are full species ids (landorustherian), not team keys
                        "player_species_id": replay.to_id(
                            snap["names"][player][snap["active"][player]]
                        ),
                        "opp_species_id": replay.to_id(
                            snap["names"][opp][snap["active"][opp]]
                        ),
                        "player_options": p_opts,
                        "opp_options": o_opts,
                        "player_label": p_label,
                        "opp_label": o_label,
                        "opp_label_in_options": o_label in o_opts,
                        "player_prev": prev_move(blocks, t, player, snap, snaps),
                        "opp_prev": prev_move(blocks, t, opp, snap, snaps),
                        "player_tera_available": not snap["tera_used"][player],
                        "opp_tera_available": not snap["tera_used"][opp],
                        "player_display": display_map(
                            p_opts, snap["names"][player], pc.move_name
                        ),
                        "opp_display": display_map(
                            o_opts, snap["names"][opp], pc.move_name
                        ),
                        "state_sha256": hashlib.sha256(
                            text.encode("utf-8")
                        ).hexdigest(),
                        "state_chars": len(text),
                    }
                    append(SAMPLE, row)
                    states_fh.write(
                        json.dumps({"id": rid, "text": text}, ensure_ascii=False) + "\n"
                    )
                    n_eval += 1
                else:
                    for side, lab in (
                        (player, pick["player_label"]),
                        (opp, pick["opponent_label"]),
                    ):
                        append(
                            CALIB,
                            {
                                "band": band,
                                "battle_id": battle["battle_id"],
                                "turn": t,
                                "role": "player" if side == player else "opponent",
                                "kind": lab["kind"],
                                "tera": bool(lab.get("tera")),
                                "switch_available": bool(
                                    replay.switch_keys(snap, side, preview)
                                ),
                                "tera_available": not snap["tera_used"][side],
                            },
                        )
                    n_cal += 1
            stats[f"eval:{band}"] = n_eval
            stats[f"calib:{band}"] = n_cal
            print(f"{band}: eval {n_eval} calib {n_cal}", file=sys.stderr)
    with open(os.path.join(OUT, "sample-stats.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "hf_repo": HF_REPO,
                "hf_rev": HF_REV,
                "seed": SEED,
                "pokechamp": pc.PC_SHA,
                "stats": dict(stats),
            },
            fh,
            indent=1,
            sort_keys=True,
        )
        fh.write("\n")
    print(json.dumps(dict(stats), sort_keys=True), file=sys.stderr)
    return 0


# --------------------------------------------------------------------------------------- run


def questions(row):
    from typesafe_sdk import Choice

    return {
        PLAYER_Q: Choice(
            instructions=PLAYER_INSTR,
            criteria={row["player_display"][o]: None for o in row["player_options"]},
        ),
        OPP_Q: Choice(
            instructions=OPP_INSTR,
            criteria={row["opp_display"][o]: None for o in row["opp_options"]},
        ),
    }


def back_to_keys(ans, display):
    inv = {v: k for k, v in display.items()}
    return {
        "choice": inv.get(ans.choice, ans.choice),
        "confidence": float(ans.confidence),
        "probabilities": {
            inv.get(k, k): float(v) for k, v in ans.probabilities.items()
        },
    }


def cmd_run(limit=None):
    if not os.environ.get("TYPESAFE_API_KEY"):
        print(
            "unconfigured: TYPESAFE_API_KEY unset, no call made (NOT_RUN)",
            file=sys.stderr,
        )
        return 2
    from typesafe_sdk import TypeSafeClient

    rows = load_jsonl(SAMPLE)
    states = load_states()
    done = {r["id"] for r in load_jsonl(JEV) if "player" in r}
    todo = [r for r in rows if r["id"] not in done][:limit]
    print(f"jev: {len(todo)} to run, {len(done)} resumed", file=sys.stderr)
    client = TypeSafeClient(timeout=30.0)

    def one(row):
        text = states[row["id"]]
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != row["state_sha256"]:
            raise ValueError("state sha256 mismatch; no call made")
        t0 = time.perf_counter()
        resp = client.system_one(text, questions(row), model=JEV_MODEL)
        ms = int((time.perf_counter() - t0) * 1000)
        return {
            "id": row["id"],
            "model": resp.model,
            "latencyMs": ms,
            "usage": {
                "input_tokens": int(resp.usage.input_tokens),
                "output_tokens": int(resp.usage.output_tokens),
            },
            "player": back_to_keys(resp.answers[PLAYER_Q], row["player_display"]),
            "opponent": back_to_keys(resp.answers[OPP_Q], row["opp_display"]),
        }

    ok = failed = 0
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futs = {pool.submit(one, r): r for r in todo}
        for fut in as_completed(futs):
            try:
                out = fut.result()
                ok += 1
            except Exception as exc:  # noqa: BLE001 - recorded, scored as wrong
                out = {
                    "id": futs[fut]["id"],
                    "error": f"{type(exc).__name__}: {str(exc)[:500]}",
                }
                failed += 1
            append(JEV, out)
    print(f"jev done ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed else 0


# ------------------------------------------------------------------------------------- score


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 4), round(c + h, 4))


def calib_params(calib):
    sw = [c for c in calib if c["switch_available"]]
    mv = [c for c in calib if c["kind"] == "move" and c["tera_available"]]
    p_switch = sum(c["kind"] == "switch" for c in sw) / len(sw)
    p_tera = sum(c["tera"] for c in mv) / len(mv)
    return p_switch, p_tera, len(sw), len(mv)


def argmax(p):
    return max(p.items(), key=lambda kv: (kv[1], kv[0]))[0] if p else None


def score_side(rows, preds, label_key, opts_key):
    """preds: id -> probability dict over option keys (or None for an error row)."""
    n = len(rows)
    top1 = 0
    ll = []
    for r in rows:
        p = preds.get(r["id"])
        lab = r[label_key]
        if p and argmax(p) == lab:
            top1 += 1
        if lab in r[opts_key]:
            ll.append(-math.log(max((p or {}).get(lab, 0.0), LOGLOSS_EPS)))
    return {
        "n": n,
        "top1": round(top1 / n, 4) if n else 0.0,
        "top1_k": top1,
        "top1_wilson95": wilson(top1, n),
        "logloss": round(sum(ll) / len(ll), 4) if ll else None,
        "logloss_n": len(ll),
    }


def cmd_score():
    import pc  # sets data for the usage floor

    rows = load_jsonl(SAMPLE)
    calib = load_jsonl(CALIB)
    jev_rows = {r["id"]: r for r in load_jsonl(JEV)}
    sets = pc.sets_data()
    p_switch, p_tera, n_sw, n_mv = calib_params(calib)
    arms = {"jev": ({}, {}), "usage": ({}, {}), "uniform": ({}, {}), "repeat": ({}, {})}
    for r in rows:
        j = jev_rows.get(r["id"])
        arms["jev"][0][r["id"]] = (
            j["player"]["probabilities"] if j and "player" in j else None
        )
        arms["jev"][1][r["id"]] = (
            j["opponent"]["probabilities"] if j and "opponent" in j else None
        )
        sides = (
            (r["player_options"], r["player_species_id"], r["player_prev"]),
            (r["opp_options"], r["opp_species_id"], r["opp_prev"]),
        )
        for idx, (opts, species_id, prev) in enumerate(sides):
            usage = replay.usage_floor(opts, species_id, sets, p_switch, p_tera)
            arms["usage"][idx][r["id"]] = usage
            arms["uniform"][idx][r["id"]] = replay.uniform_floor(opts)
            if prev and prev in opts:
                arms["repeat"][idx][r["id"]] = {prev: 1.0}
            else:
                arms["repeat"][idx][r["id"]] = {argmax(usage): 1.0}
    result = {
        "rows": len(rows),
        "jev_rows": sum(1 for r in rows if jev_rows.get(r["id"], {}).get("player")),
        "calibration": {
            "p_switch": round(p_switch, 4),
            "p_switch_n": n_sw,
            "p_tera": round(p_tera, 4),
            "p_tera_n": n_mv,
        },
        "arms": {},
        "by_band": {},
    }
    for arm, (pp, po) in arms.items():
        result["arms"][arm] = {
            "player": score_side(rows, pp, "player_label", "player_options"),
            "opponent": score_side(rows, po, "opp_label", "opp_options"),
        }
        if arm == "repeat":
            for side in ("player", "opponent"):
                result["arms"][arm][side]["logloss"] = (
                    None  # a point prediction has no log-loss
                )
    for band in BANDS:
        br = [r for r in rows if r["band"] == band]
        result["by_band"][band] = {
            arm: {
                "player": score_side(br, pp, "player_label", "player_options")["top1"],
                "opponent": score_side(br, po, "opp_label", "opp_options")["top1"],
            }
            for arm, (pp, po) in arms.items()
        }
    jp, jo = result["arms"]["jev"]["player"], result["arms"]["jev"]["opponent"]
    up, uo = result["arms"]["usage"]["player"], result["arms"]["usage"]["opponent"]
    checks = {
        "top1_player>=0.30": jp["top1"] >= BAR_TOP1_PLAYER,
        "top1_opponent>=0.16": jo["top1"] >= BAR_TOP1_OPP,
        "logloss_player<usage": jp["logloss"] is not None
        and jp["logloss"] < up["logloss"],
        "logloss_opponent<usage": jo["logloss"] is not None
        and jo["logloss"] < uo["logloss"],
    }
    result["bar"] = {
        "checks": checks,
        "verdict": "PASS" if all(checks.values()) else "FAIL",
    }
    lat = sorted(j["latencyMs"] for j in jev_rows.values() if "latencyMs" in j)
    toks = sum(j["usage"]["input_tokens"] for j in jev_rows.values() if "usage" in j)
    result["jev_calls"] = {
        "ok": len(lat),
        "errors": sum(1 for j in jev_rows.values() if "error" in j),
        "models": dict(
            Counter(j.get("model") for j in jev_rows.values() if "model" in j)
        ),
        "latency_ms_p50": lat[len(lat) // 2] if lat else None,
        "latency_ms_p95": lat[int(len(lat) * 0.95)] if lat else None,
        "input_tokens": toks,
        "spend_usd_at_0.042_per_M_input": round(toks * 0.042 / 1e6, 4),
    }
    result["opp_label_coverage"] = (
        round(sum(r["opp_label_in_options"] for r in rows) / len(rows), 4)
        if rows
        else None
    )
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(
        json.dumps(
            {
                "bar": result["bar"],
                "jev": result["arms"]["jev"],
                "usage": result["arms"]["usage"],
                "jev_calls": result["jev_calls"],
            },
            indent=1,
        )
    )
    return 0


def cmd_verify_copy(n: int = 40) -> int:
    """pc.fast_copy is a faithful deepcopy: on n committed Stage A states, under the same RNG seed, the
    state text from the original battle, from LocalSim's own deepcopy and from pc.new_sim's fast copy
    must be identical, one simulated step must leave identical after-states on both copies, and the
    original battle must stay untouched. Offline, no key.

    PokéChamp's state text is not deterministic (its stat guesses sample), so a seeded rebuild need not
    equal the committed, unseeded sha256; that count is reported, not tested."""
    import random as pyrandom

    import numpy as np
    import pc
    import player as pj
    from poke_env.environment.move import Move
    from poke_env.player.local_simulation import LocalSim
    from poke_env.player.player import Player

    rows = load_jsonl(SAMPLE)[:n]
    want = {r["battle_id"] for r in rows}
    texts = {
        b["battle_id"]: b["text"]
        for band in battles_by_band().values()
        for b in band
        if b["battle_id"] in want
    }

    def text_of(sim):
        np.random.seed(0)
        pyrandom.seed(0)
        with contextlib.redirect_stdout(io.StringIO()):
            sp, st, sa = pc.state_translate2(sim, sim.battle)
        return hashlib.sha256((sp + "\n" + st + "\n" + sa).encode("utf-8")).hexdigest()

    bad, t_plain, t_fast, same_as_committed, stepped = [], 0.0, 0.0, 0, 0
    for r in rows:
        lines = replay.clean_lines(texts[r["battle_id"]])
        base = pc.replay_sim(
            lines, r["player"], r["turn"], r["battle_id"], r["player_species"]
        )
        before = pj.leaf_summary(base.battle)
        t0 = time.perf_counter()
        plain = LocalSim(
            base.battle,
            *pc.sim_args(),
            format=pc.SIM_FORMAT,
            prompt_translate=pc.state_translate2,
        )
        t_plain += time.perf_counter() - t0
        t0 = time.perf_counter()
        fast = pc.new_sim(base.battle)
        t_fast += time.perf_counter() - t0
        shas = {text_of(base), text_of(plain), text_of(fast)}
        same_as_committed += r["state_sha256"] in shas
        mv = base.battle.available_moves[0] if base.battle.available_moves else None
        opp_moves = r["opp_options"]
        memo_fast = pc.new_sim(
            base.battle
        )  # for the memo arm, stepped below with the memo on

        def step_summary(sim):
            np.random.seed(1)
            pyrandom.seed(1)
            with contextlib.redirect_stdout(io.StringIO()):
                sim.step(
                    Player.create_order(mv),
                    Player.create_order(Move(opp_moves[0][5:], gen=9)),
                )
            return json.dumps(pj.leaf_summary(sim.battle), sort_keys=True)

        leaf = set()
        can_step = mv is not None and opp_moves[0].startswith("move ")
        if can_step:
            stepped += 1
            leaf |= {step_summary(plain), step_summary(fast)}
        pc.memoize_predictor()
        memo_text = text_of(pc.new_sim(base.battle))
        memo_leaf = {step_summary(memo_fast)} if can_step else set()
        pc.unmemoize_predictor()
        untouched = json.dumps(
            pj.leaf_summary(base.battle), sort_keys=True
        ) == json.dumps(before, sort_keys=True)
        ok = (
            len(shas) == 1
            and len(leaf) <= 1
            and untouched
            and memo_text in shas
            and memo_leaf <= leaf
        )
        if not ok:
            bad.append(
                {
                    "id": r["id"],
                    "text_variants": len(shas),
                    "leaf_variants": len(leaf),
                    "untouched": untouched,
                    "memo_text_same": memo_text in shas,
                    "memo_leaf_same": memo_leaf <= leaf,
                }
            )
    print(
        json.dumps(
            {
                "rows": len(rows),
                "stepped": stepped,
                "mismatches": bad,
                "seeded_text_equals_committed": same_as_committed,
                "deepcopy_s_total": round(t_plain, 2),
                "fast_copy_s_total": round(t_fast, 2),
            },
            indent=1,
        )
    )
    print("VERIFY-COPY PASS" if not bad else f"VERIFY-COPY FAIL {len(bad)}/{len(rows)}")
    return 1 if bad else 0


def main(argv):
    if not argv or argv[0] not in ("sample", "run", "score", "verify-copy"):
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "sample":
        return cmd_sample()
    if argv[0] == "run":
        lim = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else None
        return cmd_run(lim)
    if argv[0] == "verify-copy":
        return cmd_verify_copy(int(argv[1]) if len(argv) > 1 else 40)
    return cmd_score()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
