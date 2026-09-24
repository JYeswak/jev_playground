#!/usr/bin/env python3
"""Sampler for bead jev-2wc: every QuixBugs Python program pair, correct and buggy.

Source: jkoppel/QuixBugs at 4257f44b0ff1181dedaedee6a447e133219fcebf (the SHA jev-curate-w70 pinned),
GitHub's tarball for that commit, refused unless its sha256 matches. Pairs: every `*.py` present in
both `python_programs/` (buggy) and `correct_python_programs/` (correct), minus `*_test.py`, minus
byte-identical pairs (only `node.py`, a helper). 40 pairs, 80 programs.

Three texts per program, all frozen with the bar:
  canon : the program with every docstring and bare string statement removed and comments dropped,
          re-emitted by `ast.unparse`. The buggy files carry the task's spec as a trailing docstring
          and some correct files carry alternative solutions in string blocks, so the raw files differ
          by far more than the bug; after this step every pair differs in one or two lines, the fix.
  flat  : canon passed through jev-curate's own `pre_filter_sanity` (src/filter.rs:34-67 at d1a3a05):
          trim, trim every line, drop blank lines, cap at 32,000 chars. It strips Python indentation.
  asis  : the file as shipped, trimmed.

Run: python3 work/score-quixbugs/sample.py
Writes work/score-quixbugs/sample.jsonl: i, name, variant (correct | buggy), truth (bool, true =
correct), canon, flat, asis. Byte-identical on rerun.
"""

import ast
import hashlib
import io
import json
import os
import sys
import tarfile
import urllib.request

SHA = "4257f44b0ff1181dedaedee6a447e133219fcebf"
URL = f"https://codeload.github.com/jkoppel/QuixBugs/tar.gz/{SHA}"
TAR_SHA256 = "b9f87db002c152e579f9fab860417b122ad9d7e6240f311dbf49082965151b1f"
UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample.jsonl")
MAX_CHARS = 32_000


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read()
    got = hashlib.sha256(body).hexdigest()
    if got != TAR_SHA256:
        raise SystemExit(f"sha256 mismatch: got {got}, want {TAR_SHA256}")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as tar:
        for m in tar.getmembers():
            parts = m.name.split("/")
            if (
                m.isfile()
                and len(parts) == 3
                and parts[1] in ("python_programs", "correct_python_programs")
            ):
                files[(parts[1], parts[2])] = tar.extractfile(m).read().decode("utf-8")
    return files


def canon(src):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list):
            kept = [
                s
                for s in body
                if not (
                    isinstance(s, ast.Expr)
                    and isinstance(s.value, ast.Constant)
                    and isinstance(s.value.value, str)
                )
            ]
            node.body = kept or [ast.Pass()]
    return ast.unparse(tree)


def flat(text):
    """jev-curate pre_filter_sanity (src/filter.rs:34-67): the transform its filter applies to a row."""
    lines = [line.strip() for line in text.strip().splitlines()]
    return "\n".join(line for line in lines if line)[:MAX_CHARS]


def main():
    files = fetch()
    buggy = {n for d, n in files if d == "python_programs"}
    correct = {n for d, n in files if d == "correct_python_programs"}
    names = sorted(
        n
        for n in buggy & correct
        if n.endswith(".py")
        and not n.endswith("_test.py")
        and files[("python_programs", n)] != files[("correct_python_programs", n)]
    )
    rows = []
    for n in names:
        for variant, d in (
            ("correct", "correct_python_programs"),
            ("buggy", "python_programs"),
        ):
            src = files[(d, n)]
            c = canon(src)
            rows.append(
                {
                    "name": n[:-3],
                    "variant": variant,
                    "truth": variant == "correct",
                    "canon": c,
                    "flat": flat(c),
                    "asis": src.strip(),
                }
            )
    for n in names:
        a, b = (r["canon"] for r in rows if r["name"] == n[:-3])
        if a == b:
            raise SystemExit(f"canonical texts identical for {n}")
    with open(OUT, "w") as f:
        f.writelines(
            json.dumps({"i": i, **r}, ensure_ascii=False) + "\n"
            for i, r in enumerate(rows)
        )
    print(f"wrote {len(rows)} programs ({len(names)} pairs) to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
