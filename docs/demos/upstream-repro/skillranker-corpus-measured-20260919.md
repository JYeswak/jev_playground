# skillranker's own corpus, finally pointed at a judge — 8/10, just under their gate

**Date:** 2026-09-19 · **Level:** `[live]` · Oracle: `work/skillranker-eval/oracle.mjs`
Read-only extraction of `origin/main` at `~/Developer/skillranker-eval-probe`.

## The gap, still open at HEAD after 193 commits

`Dicklesworthstone/skillranker` ships an unusually good evaluation *contract*: 12 labelled cases
with `acceptable_additional_invocations_y`, a frozen 0/1/2 loss table, an always-abstain negative
control, and a **≥ 0.90 top-1 precision** promotion gate. Our clone was **193 commits behind**;
re-checked at `origin/main` today, and **`src/` still never reads
`tests/eval/synthetic_cases.v1.jsonl`.** The newer `expected_values.v1.json` is labelled
`"status": "deterministic_contract_examples_not_measured_results"` — more contract, still no
measurement. The repo says so itself: `frozen_contract_not_evidence`.

So this runs their measurement. **Scope, stated up front:** this measures **Jev's skill selection
on their corpus under their loss table**. It is *not* a measurement of skillranker the product —
that needs their binary and their prompt construction (their Rust build is still compiling here).
It answers the question their contract was built to ask.

## Result — live, their loss table, their gate

| metric | value | their reference |
|---|---|---|
| mean loss | **0.167** | always-abstain control **0.833** · coin-flip **1.011** · oracle 0.000 |
| top-1 precision on positives | **0.800** | promotion gate **0.90** |
| prevalence | 10 positives / 12 cases (83.3%) | — |

**8 of 10 positive cases correct; both no-match cases correctly abstained.** Mean loss is **5×
better than always-abstain** and well clear of the coin-flip baseline computed earlier (1.011,
itself *worse* than doing nothing). It misses the promotion gate by one case.

| case kind | picked | wanted | outcome |
|---|---|---|---|
| positive_advisory | rust-test-triage | rust-test-triage | ✅ |
| no_match_advisory | ABSTAIN | (none) | ✅ |
| near_miss_advisory | security-audit-for-saas | security-audit-for-saas | ✅ (the near-miss trap held) |
| multiple_valid_advisory | docs-de-slopify | readme-writing, docs-de-slopify | ✅ |
| explicit_request | testing-fuzzing | testing-fuzzing | ✅ |
| planning_or_explanation | beads-workflow | beads-workflow | ✅ |
| loaded_reference_empty_y | ABSTAIN | (none) | ✅ |
| repeatable_workflow_nonempty_y | multi-pass-bug-hunting | multi-pass-bug-hunting | ✅ |
| **overflow_retrieval** | **ABSTAIN** | testing-fuzzing | ❌ false abstention |
| compacted_or_terse_context | path-rationalization | path-rationalization | ✅ |
| roster_change | replacement-skill | replacement-skill | ✅ |
| **operational_failure_semantics** | **ABSTAIN** | beads-workflow | ❌ false abstention |

**Both failures are false abstentions, never wrong picks.** Under their loss table that is the
*cheap* error (1, not 2) — the model declines rather than misleads. The two it declined are the
paraphrase-under-overflow case and the operational-failure case: exactly where the task text
stops naming the skill's domain directly.

## A harness defect of mine, caught before publication

My first version also required a `helpful` noul ≥ 0.5 alongside the choice. It reported **mean
loss 0.750, top-1 precision 0.100, 11 of 12 abstentions** — i.e. "Jev abstains on everything."

That was **my question wording, not Jev.** The diagnostic: `topP` was **0.74–1.00** on every case
(the choice was confident) while the `helpful` noul read **0.07–0.48** on all twelve and never
cleared the gate. The phrasing — *"...versus answering directly"* — biases downward, and my extra
gate overrode a confident, mostly-correct pick twelve times out of twelve.

Scored the way the product actually works (a bounded Choice with `__none__` as the abstain
option, no second gate), the same run gives 0.167 / 0.800. **A 0.750→0.167 swing caused entirely
by an invented gate** — the fourth instrument defect this lane has caught in one day, and the
reason the rule is to inspect the distribution before believing an extreme result.

## NO-CLAIM

n=12, and the repo explicitly forbids treating `split: diagnostic_synthetic` as holdout evidence —
so this is **not** a promotion, for them or for us. It measures Jev on their corpus, not
skillranker: their ranker adds roster validation, retrieval and prompt construction that could
move the number either way. Single run, one model version. The 0.90 gate is *their* number and I
applied it unchanged; it is not obvious that 0.90 is the right bar for an advisory surface where
the dominant error is a cheap abstention rather than a costly wrong pick.
