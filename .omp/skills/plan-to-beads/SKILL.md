---
name: plan-to-beads
description: 'Convert reviewed plans to traceable Beads graphs. Use for plan-to-bead conversion,
  programmatic plan traceability, or implementation-ready graph requests.'
---

# Plan to Beads — source-linked, not title-matched

Input: one approved/frozen plan, repository instructions, existing issue graph, and the user's activation boundary. Output: a verified map from each **activated** plan execution contract to one bead, with self-contained WHAT/WHY/ACCEPTANCE, blocking edges, conditional work held out, and an explicit readiness verdict. This specializes `skill://beads-workflow` (general conversion) and `skill://beads-north-star` (issue anatomy); read both before writing.

## Trigger Phrases

- plan-to-bead conversion
- programmatic plan traceability
- implementation-ready graph

## Why this form

The Franken projects do not expose a universal parser that infers a plan's semantic prerequisites. Observed patterns: `franken_node/.beads/bulk_import.md` makes an intermediate issue manifest; `frankensqlite/docs/planning/PROPOSED_BEADS_2026-05-19.import.sh` executes `br create` and `br dep add` in two passes; `franken_ocr/docs/PROPOSED_ARCHITECTURE.md:920-930` maps named plan units and proof obligations into issue shapes; `frankensympy/tools/validate_planning.py` validates plan structure. See [conversion-example.md](references/conversion-example.md) for exact source anchors and anti-patterns. Adopt the **two-pass ID map and independent checks**, not a naive rule that every heading is one issue. An unowned option/failed experiment remains conditional, not a ready worker task.

## Procedure

1. **Freeze and classify.** Read the entire current plan plus review log, user halt, current graph and repo rules. Extract every stable plan ID and classify it `execution / conversion-only / conditional / already satisfied / excluded`. Maintain an explicit ledger `plan ID → title → class → why → immediate prerequisites → wake trigger`. If the plan has not survived its required reviews, stop; do not call a draft executable. Keep source plan IDs unchanged. A reviewed plan may still say `NOT_RUN` for gates; copying contracts into issues cannot upgrade that claim.
2. **Check for existing owner before create.** For every activated contract, search current issues by ID **and semantics**. An already-owned contract links to its existing bead, not a duplicate. Verify the existing bead still has the same scope and acceptance; do not mutate a sibling's work. Draft each bead so a fresh agent given only its body can implement: current pre-state and source path; named real consumer/action; exact deliverable and rationale; positive observation; planted negative/refusal; tests/commands/receipts; explicit non-claims; blocked/wake/STOP conditions. Keep phase-exit gates separate from runtime proof. Do not invent expected numbers or new live calls.
3. **Create in two passes via `br`, never by editing JSONL.** Reserve `.beads/issues.jsonl` and any other shared paths; use `--actor <agent>` on *every* write. Pass one full description and stable `--slug`, labels, priority, type. Record the **returned ID** against the plan ID after each successful create. Do not derive IDs by title or assume requested slugs are returned verbatim. In pass two, use `br dep add <dependent> <prerequisite> --actor <agent>` for *actual* blocking edges only. Alternatives get conditional wake rules, not false prerequisites. A blocked parent with a closed prerequisite is a defect to diagnose, not proof that the task is parked safely.
4. **Honor activation.** Approval to convert is not permission to execute. If execution remains halted, set new beads `deferred` with an explicit user-release wake note, then confirm `br ready --json` contains none of these new IDs; leave any pre-existing ready bead and assignment untouched. Conditional experiments stay in the plan until named demand and safety prerequisites exist; do not fabricate four ready slots or a conversion meta-bead just to satisfy a queue.
5. **Prove correspondence and graph.** `br show <id> --json` for each new ID; assert one ID per activated execution contract, no duplicate source IDs, correct fields and disposition. Inspect `br dep list <id>` and `br dep cycles --json`; compare actual edges with the plan's direct dependencies and exclusion clauses, verify no orphan/undefined predecessor. `bv --robot-insights` / `bv --robot-plan` can show priority and bottlenecks but are not runtime proof. Test the **most obscure bead standalone**: from only its description, can a stranger identify inputs, implementation boundary, negative, evidence and STOP without reopening the plan? If not, revise the bead. Audit plan-to-bead coverage including deferred and already-owned contracts; mark any conditional branch `NOT_ACTIVATED` instead of silently dropping it.
6. **Save only owned artifacts.** `br sync --flush-only`, stage explicit issue JSONL and skill/plan paths you changed, inspect `git diff --cached --stat`, then commit under repo rules if applicable. No blanket stage; no vendored-clone commit. State the plan snapshot, new IDs, exact edge set, excluded branches, cycle result and readiness; do not claim executable/validated from a clean graph alone.

## Minimal programmatic shape

Use the **CLI**, not a regex that rewrites the issue store. A shell loop or a small `subprocess.run(["br", ...], check=True)` controller MAY execute an explicit reviewed `{plan_id, body, deps}` mapping. Build `id_by_plan_id` from returned `br create --json` only; assert unique source IDs before writes; resolve every dependency from the map or a verified existing bead; fail on missing ID or nonzero edge creation; verify through `br show` afterwards. For long bodies, `br create --description-file -` receives exact stdin. Do not silently skip by matching a title; do not swallow creation/edge errors. The small worked mapping and source tradeoffs are in [conversion-example.md](references/conversion-example.md).

## Stop conditions

No reviewer convergence → return `PLAN_NOT_FROZEN`. No named owner/prerequisite → hold the branch with a wake trigger. Reservation conflict → coordinate, never overwrite. Script returning success without `br` readback → `UNVERIFIED`. A ready bead appearing under a user halt → defer it before delivery. Dependency cycles or missing active contracts → conversion is incomplete. Never infer that implementation, runtime safety, paid-eval evidence, or public claims are complete merely because the issue graph parses.
