"""Pokémon Showdown replay parsing for Stage A: labels, option sets, eligibility, floors.

Pure Python, no PokéChamp import, so the labelling and floor policy is testable offline.
The state text Jev reads is built separately by state.py through PokéChamp's own translator.

Log conventions (milkkarten/pokechamp, lowercased Showdown protocol):
  |switch|p1a: NICK|species, l50, m|100/100      |drag|... (forced)
  |move|p1a: NICK|move name|p2a: TARGET|[from]...  |cant|p1a: NICK|reason
  |-terastallize|p1a: NICK|type   |faint|p1a: NICK   |turn|N   |win|NAME

Label rule, per side X and turn t (the lines after |turn|t up to the next |turn|):
  the first event of X decides. |switch| before any |move| line and before any |faint| line is a
  chosen switch; a |move| line with no [from] tag is a chosen move (tera if X terastallized earlier in
  the same block); anything else (|cant|, |drag|, a [from] move, fainting first, no event) makes the
  turn unobservable for X and the row is not eligible.
"""

from __future__ import annotations

import re

SKIP_PREFIXES = (
    "|c|",
    "|raw|",
    "|j|",
    "|l|",
    "|n|",
    "|inactive",
    "|t:|",
    "|html|",
    "|uhtml",
    "|chat|",
)
TERA_SUFFIX = " + terastallize"


def to_id(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def species_key(species: str) -> str:
    """Team identity of a species: the id of the name before the first hyphen.

    Species clause (one per national dex number) makes this unique per team, and it merges the team
    preview name with the in-battle forme (ogerpon / ogerpon-wellspring, urshifu-* / urshifu-rapid-strike).
    """
    return to_id(species.split(",")[0].split("-")[0])


def clean_lines(text: str) -> list[str]:
    return [
        ln
        for ln in text.split("\n")
        if ln.startswith("|") and not ln.startswith(SKIP_PREFIXES)
    ]


def fields(line: str) -> list[str]:
    return line.split("|")


def side_of(ident: str) -> str:
    """'p1a: iron treads' -> 'p1'."""
    return ident[:2]


def nick_of(ident: str) -> str:
    return ident.split(":", 1)[1].strip() if ":" in ident else ident


def players(lines: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for ln in lines:
        f = fields(ln)
        if len(f) > 3 and f[1] == "player" and f[3] and f[2] not in out:
            out[f[2]] = f[3]
    return out


def winner_side(lines: list[str]) -> str | None:
    names = players(lines)
    wins = [fields(ln)[2] for ln in lines if ln.startswith("|win|")]
    if len(wins) != 1:
        return None
    for side, name in names.items():
        if name == wins[0]:
            return side
    return None


def is_excluded(lines: list[str]) -> str | None:
    """Reason a battle is not used, or None."""
    joined = "\n".join(lines)
    if "zoroark" in joined:
        return "illusion"
    if "|-transform|" in joined:
        return "transform"
    if "|gametype|singles" not in joined:
        return "not-singles"
    turns = [int(fields(ln)[2]) for ln in lines if ln.startswith("|turn|")]
    if not turns or max(turns) < 3 or max(turns) > 80:
        return "length"
    if winner_side(lines) is None:
        return "no-winner"
    return None


def team_preview(lines: list[str]) -> dict[str, list[str]]:
    team: dict[str, list[str]] = {"p1": [], "p2": []}
    for ln in lines:
        f = fields(ln)
        if len(f) > 3 and f[1] == "poke" and f[2] in team:
            team[f[2]].append(f[3].split(",")[0].strip())
    return team


def turn_blocks(lines: list[str]) -> dict[int, list[str]]:
    """Turn number -> the lines after |turn|N up to (not including) the next |turn| line."""
    blocks: dict[int, list[str]] = {}
    cur: int | None = None
    for ln in lines:
        if ln.startswith("|turn|"):
            cur = int(fields(ln)[2])
            blocks[cur] = []
        elif cur is not None:
            blocks[cur].append(ln)
    return blocks


def _move_is_chosen(f: list[str]) -> bool:
    return not any(x.startswith("[from]") for x in f[4:]) and to_id(f[3]) != "struggle"


def _move_in_moveset(f: list[str]) -> bool:
    """A move line that reveals a moveset slot: chosen, or repeated by a lock (outrage)."""
    tags = [x for x in f[4:] if x.startswith("[from]")]
    return to_id(f[3]) != "struggle" and all(
        t.replace(" ", "") in ("[from]lockedmove",) for t in tags
    )


def label(block: list[str], side: str) -> dict | None:
    """The chosen action of `side` in this turn block, or None if unobservable."""
    any_move = False
    any_faint = False
    tera = False
    for ln in block:
        f = fields(ln)
        if len(f) < 3:
            continue
        kind, who = f[1], f[2]
        mine = who.startswith(side + "a")
        if kind == "-terastallize" and mine:
            tera = True
            continue
        if kind == "switch" and mine:
            if any_move or any_faint:
                return None
            return {
                "kind": "switch",
                "key": species_key(f[3]),
                "species": f[3].split(",")[0].strip(),
            }
        if kind == "move":
            if mine:
                if not _move_is_chosen(f):
                    return None
                return {"kind": "move", "key": to_id(f[3]), "tera": tera}
            any_move = True
            continue
        if kind in ("cant", "drag", "faint", "replace") and mine:
            return None
        if kind == "faint":
            any_faint = True
    return None


def track(lines: list[str]):
    """Walk the log once; yield (turn, snapshot) at each |turn| line with the state before that turn.

    snapshot per side: active species key/name, fainted keys, terastallized flag, moves revealed so
    far per species key (chosen or locked move lines only), and the nick -> species map.
    """
    preview = team_preview(lines)
    nick_species: dict[tuple[str, str], str] = {}
    active: dict[str, str | None] = {"p1": None, "p2": None}
    fainted: dict[str, set[str]] = {"p1": set(), "p2": set()}
    tera_used = {"p1": False, "p2": False}
    seen_moves: dict[str, dict[str, list[str]]] = {"p1": {}, "p2": {}}
    names: dict[str, dict[str, str]] = {"p1": {}, "p2": {}}
    for side in ("p1", "p2"):
        for sp in preview[side]:
            names[side][species_key(sp)] = sp
    for ln in lines:
        f = fields(ln)
        if len(f) < 2:
            continue
        kind = f[1]
        if kind == "turn":
            yield (
                int(f[2]),
                {
                    "active": dict(active),
                    "fainted": {s: set(v) for s, v in fainted.items()},
                    "tera_used": dict(tera_used),
                    "seen_moves": {
                        s: {k: list(v) for k, v in d.items()}
                        for s, d in seen_moves.items()
                    },
                    "names": {s: dict(d) for s, d in names.items()},
                    "nick_species": dict(nick_species),
                },
            )
            continue
        if len(f) < 3:
            continue
        side = side_of(f[2])
        if side not in ("p1", "p2"):
            continue
        if kind in ("switch", "drag", "replace") and len(f) > 3:
            sp = f[3].split(",")[0].strip()
            nick_species[(side, nick_of(f[2]))] = sp
            key = species_key(sp)
            names[side][key] = sp
            active[side] = key
        elif kind == "faint":
            sp = nick_species.get((side, nick_of(f[2])))
            if sp:
                fainted[side].add(species_key(sp))
        elif kind == "-terastallize":
            tera_used[side] = True
        elif kind == "move" and len(f) > 3 and _move_in_moveset(f):
            sp = nick_species.get((side, nick_of(f[2])))
            if sp:
                mv = to_id(f[3])
                lst = seen_moves[side].setdefault(species_key(sp), [])
                if mv not in lst:
                    lst.append(mv)


def hindsight_moves(lines: list[str]) -> dict[str, dict[str, list[str]]]:
    """Every move each species used anywhere in the battle (the player's own-team knowledge)."""
    final: dict[str, dict[str, list[str]]] = {"p1": {}, "p2": {}}
    nick_species: dict[tuple[str, str], str] = {}
    for ln in lines:
        f = fields(ln)
        if len(f) < 4:
            continue
        side = side_of(f[2])
        if side not in final:
            continue
        if f[1] in ("switch", "drag", "replace"):
            nick_species[(side, nick_of(f[2]))] = f[3].split(",")[0].strip()
        elif f[1] == "move" and _move_in_moveset(f):
            sp = nick_species.get((side, nick_of(f[2])))
            if sp:
                lst = final[side].setdefault(species_key(sp), [])
                mv = to_id(f[3])
                if mv not in lst:
                    lst.append(mv)
    return final


def other(side: str) -> str:
    return "p2" if side == "p1" else "p1"


def eligible_turns(lines: list[str], player: str) -> list[dict]:
    """Turns where both sides' chosen actions are observable, with the pre-turn snapshot."""
    blocks = turn_blocks(lines)
    out = []
    for t, snap in track(lines):
        block = blocks.get(t)
        if (
            block is None
            or snap["active"]["p1"] is None
            or snap["active"]["p2"] is None
        ):
            continue
        lp = label(block, player)
        lo = label(block, other(player))
        if lp is None or lo is None:
            continue
        out.append({"turn": t, "snap": snap, "player_label": lp, "opponent_label": lo})
    return out


def option_key(action: dict) -> str:
    if action["kind"] == "switch":
        return "switch " + action["key"]
    return "move " + action["key"] + (TERA_SUFFIX if action.get("tera") else "")


def options(
    move_ids: list[str], switch_keys: list[str], tera_available: bool
) -> list[str]:
    """Option keys in a fixed order: moves, their tera variants, then switches."""
    out = [f"move {m}" for m in move_ids]
    if tera_available:
        out += [f"move {m}{TERA_SUFFIX}" for m in move_ids]
    out += [f"switch {k}" for k in switch_keys]
    return out


def switch_keys(snap: dict, side: str, preview: dict[str, list[str]]) -> list[str]:
    act = snap["active"][side]
    dead = snap["fainted"][side]
    keys = [species_key(sp) for sp in preview[side]]
    return [k for k in keys if k != act and k not in dead]


# ---------------------------------------------------------------- floors (offline, no model)


def usage_floor(
    opts: list[str], species_id: str, sets: dict, p_switch: float, p_tera: float
) -> dict[str, float]:
    """Usage-frequency floor: move mass split by the species' usage percentages (+1 smoothing),
    switch mass uniform, tera share fixed; every number comes from data we did not write."""
    moves = [o for o in opts if o.startswith("move ") and not o.endswith(TERA_SUFFIX)]
    teras = [o for o in opts if o.endswith(TERA_SUFFIX)]
    sws = [o for o in opts if o.startswith("switch ")]
    usage = {
        to_id(m["name"]): float(m["percentage"])
        for m in sets.get(species_id, {}).get("moves", [])
    }
    ps = p_switch if (sws and moves) else (1.0 if sws else 0.0)
    pt = p_tera if teras else 0.0
    w = {o: usage.get(o[5:], 0.0) + 1.0 for o in moves}
    total = sum(w.values()) or 1.0
    out: dict[str, float] = {}
    for o in moves:
        out[o] = (1 - ps) * (1 - pt) * w[o] / total
        if teras:
            out[o + TERA_SUFFIX] = (1 - ps) * pt * w[o] / total
    for o in sws:
        out[o] = ps / len(sws)
    return out


def uniform_floor(opts: list[str]) -> dict[str, float]:
    return {o: 1.0 / len(opts) for o in opts}
