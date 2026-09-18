# Q76 Rule: Label Declaration Transfers Authority, Not Construct Validity

**Decision:** the declared-vs-inferred remedy transfers to COD-H2 only on **authority/provenance**. It does not transfer as a mechanism that dissolves the label blocker.

## Same family, different load-bearing defect

The lane's filename defect was:

```text
receipt purpose inferred from filename
    -> regex label treated as authoritative
    -> gate decision
```

The COD-H2 defect is:

```text
policy pattern defines the label target
    -> same pattern grades the measurement
    -> apparent performance is tautological
```

Both reject hidden inference and require an explicit declaration. They are related authority defects, but the COD-H2 blocker is additionally a **construct-validity and independence** defect. A declared label can say who assigned a value; it cannot make a pattern-derived label independent of the pattern being tested.

## What declaration would buy

A label manifest should carry, per case:

- `label` and stable case ID;
- `label_author` and reviewer/auditor identity;
- `rubric_version` and clause path;
- raw/evidence span or evidence-manifest reference;
- whether the label was assigned before the model/measurement result was seen;
- source snapshot and case identity.

This would make label authority explicit, prevent filename/rubric inference from silently becoming truth, and permit a third party to reproduce who decided what. It would address the authority half of blocker 3.

## What declaration would not buy

It would not make the rung-4 target stable if:

- the label is computed from the same command-pattern rule used as the measured baseline;
- the policy author is the sole label source;
- the labeler sees the result before assigning the label;
- evidence is truncated or cannot establish the target property;
- a declaration merely repeats the existing regex output under a new field name.

Those conditions preserve the perfect-by-construction failure. A declared `label=pass` with `label_source=pattern-rule` is an explicit record of tautology, not ground truth.

## Ruling on the blocker

**No rung-4 blocker dissolves today.** The remedy transfers as a prerequisite for an honest label contract, not as a completed mechanism.

The label blocker can be reclassified only after a real manifest and independent labeling run demonstrate:

1. labels are assigned from the policy/rubric and evidence, not from the measurement pattern;
2. the label author is independent of the policy author, with the author boundary recorded;
3. the labeler is blind to the model/measurement result where the question permits blinding;
4. the corpus crosses the same command-characteristic strata into different outcomes;
5. a non-author audit clears the pre-registered agreement bar, with per-case disagreements retained;
6. the evidence spans support the label and are not merely truncated previews.

The Q40/Q45/Q51 work demonstrates why the sequence matters: declarations improve provenance; independent re-labeling tests the target; agreement and evidence spans test whether the target is stable and auditable.

## Remaining blockers

Even if an independent declared-label run eventually dissolves the construct-validity blocker, the five other blockers named in the current ruling remain:

- power: `.1135` upper bound versus the `<=5%` bar;
- guards: `6/6` absent;
- widening: exhausted source and struck credential stratum;
- ground truth: `5/20 = 25%` fresh agreement;
- evidence sufficiency: `40/68` previews insufficient, with four additionally unrelocatable.

Therefore no rung-4 reopening, promotion, or candidate-advancing claim follows from this rule.

## Re-examination condition

Re-examine this transfer when a committed label manifest exists with per-case author, rubric path, source evidence, blind-state, and result-independent assignment fields, and a non-author stratified audit has run. Re-open only if the audit clears its declared agreement floor and the label-free half demonstrates non-tautological cross-stratum outcomes.

If the manifest's labels are still produced by a pattern rule, classify the blocker as unresolved regardless of how explicit the metadata looks.

## Scope

This ruling establishes the authority contract and the no-tautology boundary. It does not create labels, implement the manifest, dissolve any blocker, or reopen COD-H2's rung 4.
