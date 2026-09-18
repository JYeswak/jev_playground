# Q57 Rule Rulings: Delete, Demote, or Keep-and-Mark

**Status:** third-party ruling
**Decision date:** 2026-09-18
**Inputs:** Q56 non-author audit `audit-gauntlet-spec-20260918T081500Z.json` at `226adfb`, `GAUNTLET_SPEC_MU.md` at `c9a2fd9`, and the lane's §3h dead-gate precedent.

## Decision table

| Candidate | Ruling | Classification | Re-examination condition |
|---|---|---|---|
| Conductor-kill concurrence (§3c rule 3) | **DEMOTE-TO-GUIDANCE** | Trigger did not arise; no conductor kill of another pane's candidate was licensed or blocked by this rule. It remains a useful safety boundary, but it is not validated as a firing gate. | Restore as an enforceable gate when a conductor proposes to kill another pane's candidate. The kill receipt must identify the non-author concurrence before the ruling lands. |
| “Resolving a hold is not raising a score” | **DEMOTE-TO-GUIDANCE** | Trigger never arose. No record shows anyone treating hold resolution as score improvement. The rule is a one-line semantic reminder, not outcome-changing evidence. | Re-promote only when a receipt or dispatch conflates a resolved prerequisite with a changed score; attach the exact conflicting fields and require a separate score receipt. |
| Rung-5 gate as specified | **KEEP-AND-MARK** | Dormant-by-design, not dead. No promotion was attempted, so its condition was never exercised. It is not an unsatisfiable gate like the former two-non-author-grader gate. | At the first promotion attempt, run all four rung-5 conditions with a non-conductor owner and a project-level kill criterion. After that attempt, audit whether the gate is satisfiable and outcome-changing. |

## Rule for deletion decisions

A rule is deleted only when its trigger arose, the system passed without it, and the rule therefore added no protection. That condition is not established for any of these three candidates.

- **No trigger:** demote or mark dormant; do not delete.
- **Trigger arose and passed without it:** delete, following the §3h precedent.
- **Trigger arose and changed an outcome:** keep as a gate, with its re-examination condition.
- **Trigger is impossible by construction:** delete or replace with a satisfiable gate; do not call it rigorous.

## Candidate-specific reasoning

### 1. Conductor-kill concurrence — DEMOTE-TO-GUIDANCE

The rule is not disproven by non-use. The lane's kills were executed or concurred by non-authors through other mechanisms, and no conductor killed another pane's candidate while relying on this clause. That is trigger-never-arose, not trigger-arose-and-passed.

Demotion is safer than deletion because the rule protects an explicit authorship boundary at a high-risk action. Its reactivation trigger is concrete: a conductor proposes a kill of a candidate authored by another pane. The requirement remains simple and testable: named non-author concurrence before the kill is recorded.

### 2. Hold-versus-score reminder — DEMOTE-TO-GUIDANCE

The rule was mistake-proofing against an error nobody committed. It should not be counted as evidence of discipline or retained as a separate gate. Demotion preserves the semantic distinction inside the HELD definition without imposing an untriggered workflow step.

The distinction remains real: resolving a prerequisite changes state from HELD to actionable; it does not raise a numeric score. If a future receipt places a score delta on a hold-resolution event, the rule's trigger has fired and the guidance must become a blocking check for that event.

### 3. Rung-5 gate — KEEP-AND-MARK

This is a dormant project-promotion boundary, not a failed gate. Promotion was never attempted, so no evidence supports deleting or validating it. The honest state is four tested rungs plus one grey, untested rung.

The §3h precedent applies only to the former two-non-author-grader requirement because that gate was structurally unsatisfiable with the available pane topology. Rung 5 is conditional and potentially satisfiable; its trigger is a promotion attempt. Keep it, mark it untested, and require a named owner and project kill criterion when the trigger arrives.

## Result

None of the three candidates is deleted now:

- two are demoted because their triggers never arose;
- one is kept and marked dormant-by-design because its trigger never arose and it is not known to be impossible.

This is not a claim that all three are validated. It is a classification of the evidence state and a concrete condition under which each ruling must be revisited.
