"""Draw real diffs with future-derived labels (OFFLINE, read-only).

WORSE: a non-mine commit sharing >=1 NON-LEDGER file with a LATER
fix/correct/revert/bogus/wrong/supersede/mistake commit (the transcript
corrected it there). Ledger files touched by everything are excluded from
overlap, or every commit is 'worse'.
BETTER: non-mine commit, rank>40 from HEAD (time to be corrected), zero
later-fix overlap on its non-ledger files.
MY_SHAS: every commit this pane authored this session plus prior pane-3
attributions found in receipts (85d75a0, 71183c0) -- excluded win or lose.
Usage: python draw.py  (writes review_draw.jsonl; prints pools)
"""

import json
import re
import subprocess

FIX = re.compile(r"fix|correct|revert|bogus|wrong|supersede|mistake", re.IGNORECASE)
MINE = {
    "b4375e7",
    "1fd02d2",
    "dfba8c1",
    "c83e761",
    "66fa05d",
    "74edeff",
    "6b4db43",
    "d185fdf",
    "f0fcf32",
    "fa845ed",
    "170958c",
    "f43d590",
    "155b76b",
    "6cf749a",
    "8559948",
    "85d75a0",
    "71183c0",
}
LEDGER = {
    "EVAL.md",
    "NEGATIVE_EVIDENCE.md",
    "STATUS.tsv",
    "docs/demos/STATUS.tsv",
    "docs/demos/ORACLE-MANIFEST.tsv",
    ".beads/issues.jsonl",
    "TESTS.md",
    "GATES.md",
    "RECIPES.md",
    "docs/demos/STATUS.tsv",
}


def log(*args):
    return subprocess.run(
        ["git", "log", "--no-merges", *args], capture_output=True, text=True, check=True
    ).stdout


def main():
    shas = log("--format=%H").split()
    subj = {}
    for h in shas:
        subj[h] = log("-1", "--format=%s", h).strip()
    files = {}
    for block in log("--name-only", "--format=END_OF_COMMIT_%H").split(
        "END_OF_COMMIT_"
    ):
        lines = block.strip().split("\n")
        if not lines or len(lines[0]) != 40:
            continue
        h, fs = lines[0], [x for x in lines[1:] if x.strip()]
        files[h] = fs
    rank = {h: i for i, h in enumerate(shas)}
    is_fix = {h for h in shas if FIX.search(subj[h] or "")}
    mine = {h for h in shas if h[:7] in MINE}
    bare = {h: [f for f in files.get(h, []) if f not in LEDGER] for h in shas}
    worse, better = [], []
    for h in shas:
        if h in mine or not bare[h]:
            continue
        hits = [
            g
            for g in shas
            if rank[g] < rank[h]
            and g in is_fix
            and g not in mine
            and set(bare[h]) & set(bare[g])
        ]
        if hits:
            worse.append((h, hits[0]))
        elif rank[h] > 40:
            better.append((h, None))
    print(
        f"worse_pool={len(worse)} better_pool={len(better)} mine_excluded={len(mine)}"
    )
    for h, g in worse[:14]:
        print(f"W {h[:7]} <- {g[:7]} :: {(subj[h] or '')[:75]}")
    pick_w = [h for h, _ in worse[:8]]
    step = max(1, len(better) // 14)
    pick_b = [h for h, _ in better[::step][:14]]
    print(f"pick: worse={len(pick_w)} better={len(pick_b)}")
    with open("review_draw.jsonl", "w") as fh:
        for h in pick_w + pick_b:
            d = subprocess.run(
                ["git", "show", "--format=", "--stat", h],
                capture_output=True,
                text=True,
            ).stdout[:400]
            fh.write(
                json.dumps(
                    {
                        "sha": h,
                        "short": h[:7],
                        "subject": subj[h],
                        "label": "worse" if h in pick_w else "better",
                        "corrected_by": next(
                            (g[:7] for hh, g in worse if hh == h), None
                        ),
                        "stat": d,
                    }
                )
                + "\n"
            )


if __name__ == "__main__":
    main()
