---
description: "Kit A5/B4: every ledger REJECT needs a testable retry predicate"
condition:
  - '(?i)retry predicate:?\**:?\s*(later|tbd|n/?a|none|todo|\?|-)?\s*$'
  - '(?i)retry predicate:?\**:?\s*(later|tbd|n/?a|todo)\b'
scope: "tool:edit(**/NEGATIVE_EVIDENCE.md), tool:write(**/NEGATIVE_EVIDENCE.md)"
interruptMode: always
---
The retry predicate is empty or a weasel word. The pre-commit hook will reject this row anyway; fix it now.

A retry predicate is an observable condition under which the rejected idea is worth re-testing, e.g. "when the A/A null on worker X is < 2% for 3 runs" or "when upstream crate Y >= 0.9 ships Z". Never "later", "TBD", "n/a".
