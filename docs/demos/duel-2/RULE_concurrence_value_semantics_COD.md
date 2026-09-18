# Q80 Rule: `kill_concurrence` Value Semantics

**Decision:** do **not** split `none` into more STATUS values. Keep the value, but document that `none` is non-affirmative and context-dependent; bind its reason outside the gate column.

## Current vocabulary

The existing column remains:

```text
empty
none
author-self
nonauthor-kill:<receipt>@<sha>
concur:<pane>:<receipt>@<sha>
```

Semantics:

- **empty** — schema failure: no concurrence value was recorded;
- **author-self** — an author-self disposition is asserted; no concurrence is required under §3c rule 3;
- **nonauthor-kill** — the non-author kill receipt itself is identified;
- **concur** — a distinct concurrence receipt and actor are identified;
- **none** — no separate concurrence act is asserted. It is not “examined and fine,” not “concurrence unnecessary,” and not proof that the kill boundary was resolved.

For the live rows, demo-1's `none` is **unresolved/no-decision** because no discrete kill exists and conductor/author identity is not artifact-established. A future `none` may represent a grandfathered no-decision or another documented absence, but the value alone must not distinguish those cases.

## Why not split `none`

Splitting into values such as `none-grandfathered`, `none-no-decision`, and `none-identity-unresolved` would create three non-empty strings that the current gate treats identically. That expands vocabulary without adding discrimination. It would repeat the enum-growth failure Q75 avoided: describe every absence while the gate still answers the same binary question.

The gate currently checks only non-emptiness. Therefore its check is a **presence-of-record marker**, not semantic clearance. `none` passes the syntax check but carries no positive concurrence claim. A reader must not interpret the current `4/4 concurrence-recorded` count as “4/4 kills semantically validated” when one value is `none`.

## Required contextual metadata

Keep the STATUS value stable and attach a reason in an audit sidecar or concurrence receipt, keyed by candidate, STATUS revision, and row digest:

```text
none_reason = grandfathered | no-decision | identity-unresolved | not-applicable
```

The reason must point to opened evidence. For demo-1 the value is `identity-unresolved` plus `no-decision`; it must not be upgraded to `author-self` or `nonauthor-kill` without a new artifact establishing the identity and a discrete act.

This is documentation/provenance, not a new gate branch. New `RULED_OUT` rows should use an affirmative semantic value where applicable; `none` is retained for legacy/no-disposition cases and must carry a reason in the audit record.

## Interaction with the gate

- Empty `kill_concurrence` remains a fail-closed schema error for a `RULED_OUT` row.
- Non-empty `none` satisfies only the current column-presence syntax, not a semantic concurrence requirement.
- The gate must not be changed to treat `none` as `concur` or as author-self.
- If the project later requires semantic clearance rather than presence, add a separate validated field or gate after a pre-registered migration; do not overload `none`.

The wrong `pane2` author value demonstrated why this distinction matters: it hid the self-kill question and manufactured a cross-boundary appearance. Author-field correctness must be established before concurrence semantics can be adjudicated.

## Re-examination condition

Re-examine this rule when:

- a new `RULED_OUT` row uses `none` without a reason;
- a gate or report treats non-empty `none` as semantic approval;
- the sidecar cannot bind `none_reason` to the candidate/row revision;
- author identity becomes artifact-established for demo-1 or a discrete kill decision appears;
- a future gate needs to distinguish grandfathered, no-decision, and identity-unresolved behavior operationally.

Only then consider a split, with separate positive/negative arms proving that the new values change behavior rather than merely naming absence.

## Scope

This ruling preserves the existing value and prevents semantic overclaiming. It does not implement the reason sidecar, change the gate, or claim demo-1's self-kill/cross-boundary question is resolved.
