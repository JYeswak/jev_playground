# R2 MUSE2: 30 ideas → best 5 (2026-10-02)

Contestant MUSE2 vs gpt-6-luna. Ground: round-1 report (measure-before-build won; conservatism right on retirement), NEGATIVE_EVIDENCE R134–R137, expected.json, closed beads 2026-10-01/02, tonight's live numbers. Spend anchor: ~$0.32/day total — tokens are cheap, LATENCY and reliability are the prize, except the 98.878% retransmit bulk (config comment). No refuted design re-proposed without a new fact (R137 closed wording tweaks; yl60 closed local-nimble-for-memory; R133 closed lexical hints; R136 closed page enrichment; pn7b closed loader fixes).

## The 30 (one line each; † = in top 5)

Memory / recall:
1. † Bundle K memory questions into ONE System One request per turn (fan-out runs parallel; same questions, 1 round trip not 20).
2. † Score each memory ONCE per session against the session topic; reuse all turn (recall is static per session).
3. Deterministic echo-skip: memory text == prompt text → drop, no Jev call (echo kept at 0.92 tonight).
4. Recall-side dedup: identical bullets re-injected every turn scored once (tnde: same memory hundreds/day).
5. Drop instruction-prose lines from recall elements without scoring (static product text, 2–3 calls/turn).
6. Local nimble for memory Noul — REFUTED by yl60 (84.4%, drops 3/11 critical). Excluded, no new fact.
7. Lower the 200/day cap — arbitrary number, no evidence. Excluded.
8. Turn filter off where recall is empty — already free (silent). Excluded.
9. EE task-context parser branch never fires in captures (0 Task-relevant hits) — measure whether the pipeline is on; delete or fix. Small; not top 5.

Safety gates:
10. † Deterministic pre-rules: recursive delete outside /tmp → instant flag, zero model calls (syje: nimble clears existing-path rm -rf at 0.25).
11. Same pre-rule shape for curl-pipe-shell and chmod -R 777 (one new fact each needed; bundled as one mechanism).
12. Paid-Jev rescore of nimble-cleared destructives only (targeted, not blanket) — costed experiment, not top 5.

Tokens / cache:
13. † Prompt-cache prefix stability: fixed element order + recall dedup so the 98.878% retransmit hits cache (metric: billed input/session).
14. shake tuning — already ON, no new fact. Excluded.
15. find-first enforcement for file location (04q2: 576 vs 5297 tok) via rule + lint. Good but single-surface; runner-up.
16. Fleet read-cache for repeat read-only commands keyed (cwd, cmd, HEAD), mtime-gated. Runner-up (big in transcripts, needs hit-rate measure first).

Fleet / process:
17. Serialized commits (my fxm2 wrapper) — already shipped, cannot propose as new. Excluded.
18. lsof-scoped holder check in watcher (machine-wide pgrep vetoes sweeps) — real bug I found; small, folded into #17's family. Runner-up.
19. Retire rules via ttsr.disabledRules, not file moves (pn7b: stale fired until session end; rebuilds re-bucket live). Runner-up (process fix, needs conductor adoption).
20. Duplicate-work guard: check br assignee before claiming (8qu6 double-claim tonight). Runner-up.
21. Idle-session auto-stop — dangerous (quiet ≠ idle), needs the needs-human signal as gate; experiment only.
22. Kill-switch dashboard for shadows — observability, no saving. Excluded.
23. Session-start cost ledger per pane — observability. Excluded.
24. Bead-graph auto-claim — low Jev value. Excluded.
25. Subagent model pinning (smol for extraction — already done per memory docs). Excluded.

Thinking / models:
26. Extend effort routing beyond prompts (tool-heavy turns)? No baseline. Excluded.
27. Local Ollama for memory Noul IF it matches jev-1.13.0 on recorded pairs (per-surface check first) — experiment with bar, runner-up.
28. Pre-warm recall async at session start — unknown if not already async. Excluded.
29. Cap prompt turns per session — arbitrary. Excluded.
30. Turn off smart-stop anywhere — it's ON and proven both ways. Excluded.

## Best 5, best first

### 1. Bundle memory-filter questions: 20 calls → 1 request per turn
- **Jev decision:** same Noul, same CUT 0.5, same state per question; only the transport changes (one request, K questions; docs: questions run in parallel).
- **Seam:** `.omp/extensions/jev-memory-filter.ts` scoring loop (batch items, one askJev with K questions, map answers by name).
- **Metric (from logs):** per-turn scoring latency = sum(latencyMs) over sidecar rows per (instance, promptHash); tonight p50 ~120-150ms/call × 20 = ~2.5s/turn.
- **Bar:** p50 turn-scoring latency −70% with verdict agreement 20/20 on replayed pairs (single vs bundled), committed before the swap.
- **Cost/day:** same tokens (~15k/40 calls ≈ $0.0006/session), latency saved ~2s × turns/day; zero marginal model cost.
- **Planted negative:** one pair whose bundled verdict differs from its single-call verdict blocks the swap (delivered as the failing row).

### 2. Stable prompt-cache prefix: order + dedup
- **Jev decision:** none (deterministic reorder/dedup).
- **Seam:** system-prompt assembly (recall element placement + identical-bullet dedup before injection).
- **Metric:** billed input tokens per session from usage rows/session files; tonight's anchor is 98.878% retransmitted bulk.
- **Bar:** −20% billed input tokens/session at identical behavior (diff of provider payloads shows only ordering/dupes removed), committed first.
- **Cost/day:** pays in cache hits, not fewer calls; $0 new spend to prove (keyless diff + usage arithmetic).
- **Planted negative:** any turn whose assembled prompt loses a non-duplicate bullet kills it (show the diff).

### 3. Session-scoped memory verdicts with drift guard
- **Jev decision:** Noul once per (session, memory) against the session topic; reuse across turns; re-score on topic drift (prompt embedding/lexical distance over threshold — threshold committed first).
- **Seam:** memory-filter memo extended across turns (key memoryHash + topic-similarity check).
- **Metric:** Jev calls/session from sidecar instance counts (tonight: 40/3-turn session).
- **Bar:** −60% calls/session with drop precision ≥ 0.90 on the s47b 30-drop held set, committed first.
- **Cost/day:** ~60% of current filter spend (~$0.001/run level); $0 to prove the drift detector keylessly first.
- **Planted negative:** a mid-session topic-pivot turn whose verdicts do NOT refresh fails the design (stage one pivot transcript).

### 4. Deterministic pre-rules for destructive shapes (instant flag, zero calls)
- **Jev decision:** none — regex routes `rm -r/R` outside /tmp (then curl-pipe-shell, chmod -R 777) to instant flag, never nimble-cleared, optionally skipping paid too.
- **Seam:** gate hook, before the nimble screen (allowlist-carve /tmp, which the rubric declares safe).
- **Metric:** planted-destructive hold rate (tonight 9/10 → target 10/10) + paid calls avoided on matches, from gate logs.
- **Bar:** 10/10 planted held AND 0/50 benign pre-rule misfires on recorded traffic, committed first.
- **Cost/day:** negative cost (skips model calls on matches); cheapest safety on the board.
- **Planted negative:** one benign command matching the regex (e.g. `rm -rf /tmp/x`, quoted `rm -rf` in prose) that gets flagged instead of cleared fails the pattern (must carve before shipping).

### 5. Fleet read-cache for repeat read-only commands
- **Jev decision:** none (exact-match cache, mtime/HEAD-gated).
- **Seam:** bash tool wrapper or agent convention: cache key (cwd, command, HEAD, file mtimes) for `git log/status/diff`, `ls`, `br show` class reads.
- **Metric:** duplicate-command rate + wall seconds in session transcripts (tonight's transcripts repeat the same git log/status dozens of times across panes).
- **Bar:** measured hit rate ≥ 30% on one fleet-day with zero stale serves (mtime gate proven by a planted mid-cache file mutation that must miss), committed first.
- **Cost/day:** wall-time and tokens on cacheable reads; $0 new model spend.
- **Planted negative:** mutate a file mid-window and re-issue the cached read: a stale serve kills the design (show the miss).

## What I deliberately did not propose
Reworded Noul questions (R137 MODEL-LIMIT, tonight), local nimble for memory relevance (yl60 FAIL), lexical skill hints (R133), page enrichment (R136), loader fixes for retirement (pn7b: no defect), universal routers (round-1 codex verdict stands), any bar-less number.
