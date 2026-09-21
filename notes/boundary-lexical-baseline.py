#!/usr/bin/env python3
"""Apply the B5 two-bit admissibility test to the `boundary` question's live 7/7.

Bit 1 asks: is the label a function of the literal input tokens? If yes, a regex is the correct
answer and Jev's 7/7 is evidence about the task, not about Jev.

This scores a security-keyword regex against the same 7 authored diffs `measure.mjs` scored live,
so the comparison is head-to-head on identical rows. Offline, zero API calls; Jev's scores are the
ones measured live at 2026-09-21 on jev-1.13.0 and are pasted, not re-fetched.

NOTE ON A PRIOR DEFECT IN THIS FILE'S FIRST DRAFT: the first version parsed only 6 of 7 cases,
extracted one diff body as the empty string, and printed a hardcoded /7 denominator over 6 rows.
v2 parses every case, asserts every body is non-empty, and derives the denominator.
"""

import re, pathlib, sys

src = pathlib.Path("work/omp-jev-review/measure.mjs").read_text()

consts = dict(re.findall(r"^const ([A-Z_0-9]+) = `(.*?)`;\s*$", src, re.S | re.M))

# BIG_REFACTOR is built by an IIFE (400 generated rename lines), not a template literal, so the
# regex above cannot see it. Reconstructed here EXACTLY as measure.mjs:102-118 builds it, so the
# lexical baseline scores the same bytes Jev scored. Verified against the source loop.
if "BIG_REFACTOR" not in consts or not consts.get("BIG_REFACTOR"):
    _body = []
    for _i in range(200):
        _body.append(f"-  const tmp{_i} = mkNode({_i});")
        _body.append(f"+  const node{_i} = makeNode({_i});")
    consts["BIG_REFACTOR"] = (
        "commit e5f6071\n    tidy up\n\n"
        "diff --git a/src/graph/build.ts b/src/graph/build.ts\n"
        "index 8888888..9999999 100644\n--- a/src/graph/build.ts\n+++ b/src/graph/build.ts\n"
        "@@ -20,400 +20,400 @@ export function buildGraph(): Graph {\n"
        + "\n".join(_body)
        + "\n"
    )

# case objects: name / diff-const / truth block, field order tolerant
cases = []
for blk in re.findall(r"\{\s*name:\s*'([^']+)',(.*?)\n\s*\}", src, re.S):
    name, body = blk
    cm = re.search(r"diff:\s*([A-Z_0-9]+)", body)
    tb = re.search(r"boundary:\s*(true|false)", body)
    if cm and tb:
        cases.append((name, cm.group(1), tb.group(1) == "true"))

# live Jev scores, measured 2026-09-21, jev-1.13.0, measure.mjs after the scores.push fix
JEV = {
    "comment-only": 0.02,
    "default-changed": 0.03,
    "auth-check-deleted": 0.97,
    "cors-widened": 0.94,
    "big-refactor-tidy": 0.03,
    "new-test-file": 0.03,
    "dep-bump-lockfile": 0.21,
}

# a generous security-keyword regex — deliberately broad, to give the lexical baseline its best shot
LEX = re.compile(
    r"\b(auth\w*|authz|authn|permission\w*|credential\w*|token|secret|"
    r"cors|origin\w*|allowlist|whitelist|rbac|acl|privilege|oauth|session"
    r"|forbidden|unauthorized|403|401)\b",
    re.I,
)

missing = [c for _, c, _ in cases if not consts.get(c)]
if missing:
    print(
        f"FATAL: diff body empty/absent for {missing} — refusing to score.",
        file=sys.stderr,
    )
    sys.exit(2)
if len(cases) != 7:
    print(
        f"FATAL: parsed {len(cases)} cases, expected 7 — refusing to score.",
        file=sys.stderr,
    )
    sys.exit(2)

print(
    f"{'case':<20}{'truth':<7}{'regex':<7}{'jev':<7}{'regex':<7}{'jev':<6}{'lexical tokens found'}"
)
rh = jh = 0
for name, cname, truth in cases:
    body = consts[cname]
    toks = sorted(set(m.group(0).lower() for m in LEX.finditer(body)))
    r = bool(toks)
    j = JEV[name] >= 0.5
    rh += r == truth
    jh += j == truth
    print(
        f"{name:<20}{str(truth):<7}{str(r):<7}{JEV[name]:<7}"
        f"{'HIT' if r == truth else 'MISS':<7}{'HIT' if j == truth else 'MISS':<6}"
        f"{','.join(toks) if toks else '(none)'}"
    )

n = len(cases)
print(f"\nlexical keyword regex : {rh}/{n}")
print(f"jev (live)            : {jh}/{n}")
pos = [(nm, cn) for nm, cn, t in cases if t]
print(f"\npositives only ({len(pos)}):")
for nm, cn in pos:
    toks = sorted(set(m.group(0).lower() for m in LEX.finditer(consts[cn])))
    print(
        f"  {nm:<20} regex={'CATCHES' if toks else 'MISSES ':<8} jev={JEV[nm]:.2f}  tokens={toks or '(none)'}"
    )
