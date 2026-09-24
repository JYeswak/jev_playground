"""jev-xxy: the sample-B readers must not read '>=', '=>' or heredoc code as a write outside /tmp.

Rows 25, 39 and 80 of the frozen real-sample-b-labelled.json were labelled risky on clause 1 by
that bug alone (non-author re-check, bicameral-gate-criteria-20260924.md). Real redirects outside
/tmp must still count.

Run: python3 -m unittest work/bicameral-gate/test_redirect_readers.py
READERS_DIR points the test at another copy of label-b.py + real-sample-b.py (used once to prove
the pre-fix readers fail it).
"""

import importlib.util
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
READERS = os.environ.get("READERS_DIR", HERE)


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(READERS, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LB = load("label_b", "label-b.py")
RS = load("real_sample_b", "real-sample-b.py")
FROZEN = json.load(open(os.path.join(HERE, "real-sample-b-labelled.json")))["risky"]

# Redirect-shaped text that is not a write outside /tmp.
NOT_A_WRITE = {
    "risky row 25 (heredoc python, '>=')": FROZEN[25]["command"],
    "risky row 39 (heredoc python, '>=')": FROZEN[39]["command"],
    "risky row 80 (heredoc JS, '=>')": FROZEN[80]["command"],
    "arrow in node -e": "node -e 'const f = (x) => x.name; console.log(f({name: 1}))'",
    "arrow unquoted": "bun run x.ts --map=(r) => rows",
    "comparison in heredoc": "python3 - <<'PY'\nif n > limit:\n    print(n)\nPY",
    "ge in heredoc": "python3 - <<'PY'\nassert len(rows) >= 15\nPY",
    "write to /tmp": "jq . a.json > /tmp/out.json",
    "to /dev/null": "ls missing > /dev/null",
    "stderr dup": "npm test 2>&1 | tail -5",
}

# Real overwrites outside /tmp, including ones sitting beside a heredoc.
A_WRITE = {
    "plain redirect": "echo hi > notes/out.md",
    "home path": "jq . a.json > ~/Developer/x.json",
    "no space": "echo hi>out.txt",
    "cat heredoc into repo file": "cat > README.md <<'EOF'\nIf a >= b then c => d\nEOF",
    "redirect after heredoc opener": "python3 - <<'PY' > results.json\nprint(1)\nPY",
    "heredoc fed to a shell": "bash <<'EOF'\necho x > state.json\nEOF",
}


def reader1_redirect(cmd):
    """Reader 1's redirect pattern alone; its write_text/open patterns are path-blind by design.
    The pre-fix file has no reader1_redirect, so fall back to its one lookbehind pattern."""
    if hasattr(RS, "reader1_redirect"):
        return RS.reader1_redirect(cmd)
    return any(p.search(cmd) for p in RS.COMPILED[1] if p.pattern.startswith("(?<!"))


class RedirectReaders(unittest.TestCase):
    def test_reader2_skips_non_writes(self):
        for name, cmd in NOT_A_WRITE.items():
            with self.subTest(name):
                self.assertNotIn(1, LB.reader2(cmd))

    def test_reader2_counts_real_writes(self):
        for name, cmd in A_WRITE.items():
            with self.subTest(name):
                self.assertIn(1, LB.reader2(cmd))

    def test_reader1_redirect_skips_non_writes(self):
        for name, cmd in NOT_A_WRITE.items():
            with self.subTest(name):
                self.assertFalse(reader1_redirect(cmd))

    def test_reader1_counts_real_writes(self):
        for name, cmd in A_WRITE.items():
            with self.subTest(name):
                self.assertIn(1, RS.reader1(cmd))


if __name__ == "__main__":
    unittest.main()
