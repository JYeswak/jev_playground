# WIZARD_SCORES_CC_ON_OTHERS: Claude scores Luna (COD) and Gemini (GMI)

Rubric: how good the idea is, its real use for humans and agents, whether it can be built
correctly, and whether the benefit justifies the complexity. Evidence cited is from this repo,
2026-09-25.

Process note: GMI's file quotes my `WIZARD_IDEAS_CC.md`, so it read my file before writing. Its
ideas are not fully independent of mine.

| origin | # | idea | score | one line |
|---|---|---|---:|---|
| COD | 1 | Shadow decision plane with outcome feedback | 870 | The only idea with a consumer today, and it adds the missing outcome join |
| COD | 2 | `jev-kit` thin package | 820 | Real packaging of proven code; TS first is the right cut |
| GMI | 1 | `jev-kit` + `jev` CLI with `doctor` | 810 | Same core as COD 2, plus the agent-first CLI the mentor audit found absent |
| COD | 3 | Unified experiment kernel | 760 | Needed (0 of 121 harnesses have a size check), but it is not what users touch |
| COD | 4 | Native omp `judge_batch` / `jevify` | 640 | Good reuse of omp primitives; the Jev judge role and key path are unproven |
| GMI | 4 | `jev-mcp` universal MCP server | 590 | Wide reach, but it publishes tools that have no consumer yet |
| GMI | 2 | `omp-safe-guard`, active blocking | 540 | Right seat, wrong mode: it blocks before real-traffic labels exist |
| COD | 5 | `jev_select` powered best-of-N | 470 | OSWorld is exhausted, and a new universe with headroom costs more than it teaches now |
| GMI | 5 | `jev-ci-gate` GitHub Action | 430 | Commit-diff alignment has no measurement behind it |
| GMI | 3 | `omp-compact-live` | 380 | Its savings are asserted, while measured compaction rules failed (R99/R100) |

## Detail

**COD 1 (870).** It extends the hook already on disk (`.omp/hooks/post/jev-gate-observe.ts`)
instead of building a new one. It joins each logged decision to what happened next (a revert or
a human label), which is exactly the ground truth `jev-ja32` lacked. It never blocks until a
preregistered held-out bar passes. It states its own blind spot: eval-prelude browser and
computer calls. I scored my own similar idea lower because I left out the outcome join.

**COD 2 (820) and GMI 1 (810).** Both extract `work/jev-client`, which has 102 importers and
uses the official SDK but has no `package.json`. What GMI adds is `jev doctor` and a CLI, which
the doctrine audit lists as ABSENT. What COD adds is the discipline: "if the kit cannot reduce a
new consumer to fewer files and fewer failure modes ... it is not a kit." GMI's five verbs
(`guard`, `route`, `score`, `rerank`, `verify`) risk promising capabilities that are not measured
per seat. Calibration is per workload (COD 9), and phishing and toxicity were poor.

**COD 3 (760).** I proposed this, so discount my score. The evidence for it is strong:
- 121 harnesses, none of which size-check, check reachability or launch detached;
- 19 Wilson and 20 McNemar copies.

GMI's objection lands, though. A kernel is infrastructure for measuring, not something a user
touches. It belongs behind the consumer, and COD orders it that way (third).

**COD 4 (640).** Using omp's native `judge` / `judge_batch` instead of our own fan-out is correct
reuse. It is unproven that a project profile can point the judge role at pinned Jev with a
host-owned key, and bulk data raises the secret-leak risk. Worth a keyless spike first.

**GMI 4 (590).** MCP reach is real. But `jev-mcp` is someone else's vendored clone (never patch
it), and packaging our tools as a server spreads tools no one uses yet. It should come after
kit + shadow consumer prove a seat.

**GMI 2 (540).**
- **Unsafe to block.** It blocks at p ≥ 0.80 on day one. The 78/100 at 1/300 figure comes from a
  sampled replay, not live traffic, and COD itself notes that real traffic shows a shadow signal
  is not yet a blocking policy.
- **Blind by design.** The regex whitelist skips Jev on "90%" of commands, which also blinds the
  gate to the commands we would learn from.

Shadow first (COD 1) dominates this.

**COD 5 (470).** It is honest about `jev-jjwt` being underpowered. But a new, non-overlapping
task universe with measured discordance is a new benchmark, which is the thing to freeze now.

**GMI 5 (430).** Advisory PR checks are plausible, but "commit message matches diff" has no
labelled data in this repo. It would be a new unmeasured surface published to strangers.

**GMI 3 (380).**
- **Unmeasured claims.** It claims 40–60% token savings and names `fast-jev-compaction` as
  "verified". Neither is measured here.
- **Contrary evidence.** Our compaction keep rules got 0/32 kept verbatim (R99), and no rule met
  the bar (R100).
- **Needs outcome labels first.** COD 12 has the right version: shadow, with real keep/drop
  outcomes, before any action.
