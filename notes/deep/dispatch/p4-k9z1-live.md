# Pane 4 (MistyTurtle) - unblock `jev-k9z.1` live: rerank advisory

From pane 1 AmberWillow, 2026-09-24. You own `jev-k9z` and built this tool.

## 1. Mission

Validate Jev -> build tools from what survives -> liven omp surfaces with them -> dogfood them in
our own systems -> share the process publicly (AGENTS.md "THE MISSION"). This unit is stage 3:
a tool you already built gets its live proof in an omp surface. Joshua, 2026-09-23: "this repo needs
to PROVE jev work - and we can only do that by using the API."

## 2. Why it is unblocked

Your 2026-09-21 BLOCKED comment named three unmet items, all blocked on spend: live N>=20 with a
latency tail, cost per 30-item call, and the keyed L3 direction. The spend restriction was lifted
2026-09-21 (AGENTS.md "Live Call Budget Gate - LIFTED"). Nothing else blocked it. The bead's
acceptance stays exactly as written; do not rewrite it to fit the evidence.

## 3. Steps, in order

1. `br update jev-k9z.1 --status in_progress --assignee MistyTurtle`.
2. Bar first, committed `[pending]` before any call, in a new receipt
   `docs/demos/upstream-repro/nev-rerank-live-20260924.md`: the corpus (the ground-truth rows
   `work/nev-rerank/pairs.jsonl` was built from, or the rerank-bench rows, whichever has labels you
   did not author), N>=20 queries of ~30 candidates each, the metric (the one your
   `rank.test.mjs` and the 219-call run already used), the incumbent arm (the zero-API TF-IDF/BM25
   ranker on identical rows), and the pass rule. Pin `jev-1.13.0`.
3. Constant first: `node work/jev-prevalence-first/prevalence-check.mjs` or its ranking
   equivalent (random order, lexical order) on the same rows, printed before any call.
4. Live arm: N>=20, key via `infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --`.
   Record every call's latency (p50/p95/max), tokens, and cost per 30-item call.
5. L3 both directions in a real omp session with the key present: the `jev_rerank` tool returns
   `ordered=true` with a changed order on a real query, AND a planted bad input (empty passage list
   or malformed candidate) is refused without throwing. Paste the toolResult frames into the
   receipt. The keyless direction you already have counts; cite its commit.
6. Close only if every acceptance clause is met, and only after a non-author pane re-scores the rows
   from the committed files. Otherwise leave it open with the unmet clause named.

## 4. Rules

Depth directive binds (`notes/deep/dispatch/DEPTH-DIRECTIVE.md`). Reserve files, stage explicit
paths, read back `git diff --cached --stat`, no amend, push after each commit. Do not edit
`8q7.12` (pane 2) or `8q7.11` (pane 3). If `.git/index.lock` exists, check `pgrep -x git` before
touching it and tell pane 1.

## 5. Callback

`CALLBACK-P4-K9Z1-DONE` via `ntm send jev --pane=1`: bar commit, live N, metric for both arms and
the constant, latency tail, cost per 30-item call, L3 frames (both directions), non-author, and a
NO-CLAIM. Advisory order only; not a blocking filter.
