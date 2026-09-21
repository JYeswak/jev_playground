# Reality check — jev lane, 2026-09-21

**Method:** `skill://reality-check-for-project`, Phase 1. Docs are the measuring stick, code is
the ground truth. Every number below was executed today, not recalled.

---

## The one-sentence answer

**The mission is blocked at stage 2 by its own stage-1 result, and nothing in the bead queue
unblocks it.** Stage 1 says *validate Jev*; we did, and the answer is **zero certified seats**
(R69). Stage 2 says *build tools from what survives*. **Nothing survived.** Everything this lane
has shipped came from a different activity — mining our own defects — which is valuable and is
not the mission as written.

---

## Vision checklist — the five mission stages, measured

| # | Stage | Status | Evidence |
|---|---|---|---|
| 1 | **Validate Jev** | **WORKING — verdict ZERO** | R69: required n = ∞ at p̂ 0.50; exact conditional binomial b=3 c=0 → p=0.25; arrival rate 0/week. Independently reproduced. |
| 2 | **Build tools from what survives** | **NOT_STARTED — no input exists** | 117 `work/` directories; **0** Jev-derived capabilities shipped to any surface. `advisory-veto.mjs` logs and never blocks. |
| 3 | **Liven omp surfaces** | **PARTIAL** | 1 hook (`jev-compact.ts`), 1 MCP (morph), **0 tools, 0 extensions**, 6 project rules. Of 10 TTSR rules shipped, **8 disabled today**. |
| 4 | **Dogfood** | **PARTIAL / REGRESSED** | First real dogfood ran today and the instrument **failed its own audit** (R68: 19/19 false ZERO CONSUMERS). |
| 5 | **Share publicly** | **PARTIAL** | 1 upstream issue + 2 unprompted corrections. ARC.md written, **deliberately unpublished**. |

## The two rules still standing are the two we never measured

`bash-glob-silenced` and `bash-pipe-exit` are **live system-wide**. Their justification was
**exposure frequency** — 820 and 807 occurrences — which measures how often the *pattern* appears,
not how often the *rule* is wrong. They have:

- no FP labelling of any kind, not even an underpowered n=20;
- no `label_rows`, so under the plan's `unpersisted-rate` they could not claim `passed`;
- no negative control.

Everything we labelled, we eventually retired. **The survivors survived by not being measured.**
That is the single most uncomfortable fact in this audit and it was invisible from every summary
we have written.

## What the ledger actually says about our own claims

| signal | count |
|---|---|
| refutations recorded (`R…`) | **77** |
| retry conditions attached | 53 |
| `EVAL.md` rungs claimed L4 | 3 |
| `EVAL.md` rungs claimed L3 | 2 |
| occurrences of `ZERO` in `EVAL.md` | **24** |
| occurrences of `offline-verified` / `live-verified` | **0 / 0** |

77 refutations against 2 surviving unmeasured rules. **This lane is extremely good at refusing
and has almost no record of certifying.** Both halves of that sentence are findings.

## Answering the skill's five questions directly

**1. What IS working?** The refusal machinery. `exposure-check` (verified independently), the
gate suite (13 stages), the negative-evidence ledger with retry conditions, the upstream filing
chain with a mechanical submit gate, and a planning process that found **18 defects** in one
document before any code was written.

**2. What is NOT working?** Stage 2 has no input. Stage 3 has one hook and two unmeasured rules.
Stage 4's first real attempt found its own instrument broken. Stage 5 has fired twice.

**3. What is blocking us?** Not capability — *premise*. The mission assumes stage 1 yields
survivors. It yielded none, and the queue contains no bead that changes that.

**4. Would implementing all open/in-progress beads close the gap?** **No.** 6 beads sit
`in_progress`, 5 of them untouched for 2–3 days, and none addresses the premise failure. The
evidence-matrix plan (v8) improves how we *claim*, not what we *ship*.

**5. What vision goals have ZERO bead coverage?** Three:
- **the premise itself** — no bead asks "if no Jev seat certifies, what is this lane for?";
- **the two unmeasured live rules** — no bead labels `bash-glob-silenced` or `bash-pipe-exit`;
- **publication** — no bead owns getting stage 5 past n=2.

## The honest reframe

The lane's actual product this week is **a measurement discipline that reliably kills its own
output**: eight rules retired on their own statistics, a Jev seat retired at required-n = ∞, a
3.6× labelling error surfaced, and an upstream claim corrected unprompted within minutes of
publishing it.

That is a real and unusual asset. It is **not** "validate Jev → build tools from what survives",
and continuing to describe it that way is the same overclaim we spend every day catching in
smaller places.

**Boundary.** `foundation/gates.sh` was not run to completion in this audit (two attempts
aborted); the 13 stages are counted, not executed. `br` reports 17 beads while `.beads/issues.jsonl`
holds 68 — the DB has desynced, so bead counts here come from the JSONL, which is the source of
truth per AGENTS.md. No claim is made about test pass rates.
