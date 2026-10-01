# jev-7vn9 design: memory-relevance filter hook point

Evidence base: jev-wb7j loss depth PASS (held-out precision 0.978, reduction
0.807, commit 9ff9f951): one Noul per memory (`is this memory relevant to the
current request?`), DROP iff noul < 0.5, invalid answer → KEEP.

## Named seam: `context` extension event
`pi.on("context", handler)` — event `{messages}` is a deep copy of the
messages about to be sent to the LLM; returning `{messages}` replaces only
the LLM-bound copy ("Original session messages are NOT modified", omp
`shared-events.ts:176-185`). The filter parses `<memories>` and
`ee-task-context` blocks out of that copy, scores each item, and drops
low-scoring items before return. Session history stays intact: fully
reversible, shadow-measurable (log would-drop, return copy unchanged).

Why not the alternatives: `before_agent_start` sees the prompt but not the
assembled context blocks; `before_provider_request` fires later with the
same power but less documented result contract (`BeforeProviderRequestEventResult
= unknown`); MCP-librarian filtering would only cover retrieval-time EE
memories, not session_init injections. `context` covers both block types in
one place, project scope (`.omp/extensions/jev-memory-filter.ts`), no profile
edits.

## Bounded design (per AGENTS.md live-call shape)
- One Noul per memory item, base wording, `jev-1.13.0`, tau 0.5,
  invalid/timeout → KEEP (fail safe, measured direction).
- Caps: max 20 items scored per turn (rest kept unlogged-flagged), daily call
  cap in code, stop on 401/402/403, per-call timeout → KEEP all.
- Logs (hashes only, never raw text): session/prompt/memory sha256, units,
  dropped count, top score, latency, tokens, status, model — same columns as
  the validated webscreen shadow log.
- Rollout: Phase 0 count-only shadow (parse + count, $0) to measure live
  per-turn volume first; Phase 1 Noul shadow (log would-drop, change nothing);
  Phase 2 enforce. Gate each phase on its own bead.

## Cost estimate at fleet injection volume
- Noul cost measured: ~800 input tokens/item ≈ $0.000034/item (79,047 tok /
  100 pairs held-out run).
- Disk-measured volume (7d census, -Developer-jev profiles): 347 items ≈
  50 items/day → filter cost ≈ **$0.0017/day**; savings ≈ 80% of injected
  memory tokens (~11k tok/7d on disk — small in absolute terms).
- Live per-turn Mnemopi volume is NOT persisted to session files (wb7j
  boundary) and is visibly larger (injections seen live every turn in
  memory-backend sessions). True savings unknown until Phase 0 measures it.
- Breakeven is strongly positive wherever volume exists: filtering $0.000034
  removes ~80% of memory tokens billed at the session model's input price
  (opus-class ≈ $15/M: 800 memory tokens ≈ $0.012 saved per item filtered).

NO-CLAIM: design only. No benefit claim until Phase 1 shadow measures live
drop precision and Phase 2 measures turn-cost delta.
