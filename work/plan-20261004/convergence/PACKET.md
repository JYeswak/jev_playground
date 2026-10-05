# Convergence review: is the jev bead graph ready to build end to end?

Joshua's bar (2026-10-04): build starts only when ALL are easy yeses:
1. Two consecutive review rounds produce zero NEW findings.
2. The bead graph is complete: closing it finishes the mission (ROADMAP.md "Mission").
3. PageRank order guides the build end to end with no gaps or gotchas.
4. Every bead's approach is research-backed AND validated against our actual system.

## Joshua's protocol (2026-10-04, verbatim intent)

- No build until at least TWO consecutive rounds bring zero new findings.
- After each round the conductor fixes the plan, then the next round is a full send again.
- At least ONE of the two clean rounds is a fresh-eyes round: each of the 5 lens agents dispatches
  2-3 background subagents with as little project context as possible (the snapshot path, the
  mission line, ROADMAP.md, and "poke holes in this"), so they are not anchored on our framing.
- "New" means a finding not already recorded in an earlier round's `r*/` files with the same bead +
  class + substance. Re-reports of known, unfixed items are not new, but they ARE listed.

## Rules (every round)

- READ-ONLY. No `br`, no source edits, no live model calls. Read beads from this round's
  snapshot: `var/agent-tmp/converge/r<N>/issues.jsonl` (includes comments). Code/files from the repo
  at HEAD. The conductor (pane 1) is the only writer and applies fixes between rounds.
- The snapshot contains planted defects. A round from you counts only if you find the ones in your
  lens. Report them like any other finding; do not guess which bead they are in.
- Every finding cites evidence: `path:line`, a command and its output, or a bead id + field.
  "Looks fine" is not evidence. Silence is not clean: if you find nothing, write one row with
  `class: "none"` stating what you checked and how (bead count, commands run).
- Output: `var/agent-tmp/converge/r<N>/<lens>-<Agent>.jsonl`, one JSON object per line:
  `{"round":N,"lens":"L1".."L5","reviewer":"<Agent>","bead":"<id or NEW>","class":"<class>",
  "severity":"P0|P1|P2|P3","text":"...","evidence":"...","fix":"<exact proposed change>"}`
- classes: missing-bead, missing-edge, wrong-edge, unreachable-from-root, unrunnable-acceptance,
  placeholder, no-research, research-misapplied, contradicts-system, contradicts-agents-md,
  tautology, overlap-other-session, gotcha, scope-creep, none.
- Callback: `ntm send jev --pane=1 "CONVERGE-R<N> <lens> <Agent> <n findings> <n P0/P1>"`.
- nice -n 10 for anything heavy; one suite at a time; defer if `sysctl -n vm.loadavg` 1-min > 80.

## Lenses

- **L1 Mission completeness.** For each pillar in ROADMAP.md, each family in
  work/plan-20261004/PRODUCT.md section 3, each decision D1-D17, each cadence row and each
  "What is ON" surface in AGENTS.md: which open bead delivers it, and does that bead's acceptance
  actually prove it (live both ways, measured, non-author)? Anything with no bead, or a bead whose
  acceptance would pass without the outcome, is a finding. Also: every open bead reachable from root
  `jev-q3q8`.
- **L2 Research backing.** For every open bead's approach: the primary source (arXiv id fetched and
  read, upstream repo file:line, or our own EVAL.md/NEGATIVE_EVIDENCE.md row) and whether the source
  supports THIS use on OUR data (prevalence, label counts, latency budget). A cited id that does not
  resolve or does not say what is claimed is `research-misapplied`. An approach NEGATIVE_EVIDENCE.md
  already refuted is `contradicts-system`.
- **L3 System fit.** Run (or dry-check) every acceptance command against HEAD: does the path exist,
  or does the bead name who creates it and when? Does the tool/flag exist (`br`, `omp`, `ntm`, kit
  CLI flags)? Is the data present (logs under ~/.local/state/jev, rows files)? Does it respect omp's
  limits (30 s handler, extension load at session start), the key path, localbench's gateway for
  local models? Placeholders like `<ledger script>` are findings.
- **L4 Gotchas and honesty.** Adversarial: forbidden patterns (AGENTS.md twelve), paid
  comparators, tautological tests, bars set after data, self-verification, shared-infra hazards
  (br SYNC_CONFLICT, GPU, cross-repo blast radius), ownership overlaps with omp-kit / localbench /
  uds (ROADMAP.md Neighbours), cost or call caps missing on live work.
- **L5 Graph and PageRank.** Run the PageRank certificate (skill `pagerank-bead-triage`; damping
  0.85, blocking edges, compare with `bv --robot-triage`'s top) on the snapshot's open subgraph.
  Then SIMULATE the build: take beads in the order PageRank + readiness would hand them out; at each
  step, does the bead's acceptance need an artifact from a bead that is not its (transitive)
  prerequisite? Each such case is `missing-edge`. Also: edges that block without need
  (`wrong-edge`), critical path length, beads that can never become ready.
