# Q99b — Ruling: RETIRE the broadcast discipline

**Rule under judgment (mine, Q96b):** before editing rank 1–3 shared-exec files, broadcast
hold-runs via hub send to all. No lock state, no owner.
**Compliance record (corrected count: 9, not 10):** 9 edits to rank-1 lane-status.sh this session,
≥3 after the ranking landed, **0 broadcasts**. The conductor's own count-correction inside the
packet that asks to be held to account reads as the fourth datum below, not as an aside.

## (1) Keep or retire? RETIRE.

A discipline at 0/9 by its sole obligated party — 0/3 since enactment — is worse than the
never-fired class Q55–Q57 retired: it is violated, not merely untriggered. But non-compliance
alone could mean weak will rather than a bad rule. The deciding evidence is structural:

## (2) What would make it fire? Nothing available — it is inherently prose.

Verified this unit: hub sends leave **no durable queryable trace** (ntm streams dir empty, no
state file touched in 3h). Consequences, each fatal independently:
- No post-hoc audit is possible: a tick cannot check "was there a broadcast within N minutes
  before this edit" because broadcast times are unrecorded. Git gives edit times; nothing gives
  broadcast times.
- No pre-commit prevention is possible without building the lock the recommendation explicitly
  refused (a hook cannot see hub state; a token file reintroduces lock state with an owner).
- A rule that can neither fire nor be audited is prose by construction, not by neglect.

## (3) What replaces it — no discipline at all, by the conductor's own evidence.

The correction packet hands me the principled ground: the conductor asserted "TEN times" from
memory inside a packet about his own defects, in a session whose central recurring defect is
asserting un-re-derived numbers — **prose self-correction did not fire at maximal salience for
exactly this defect class.** A memory-dependent broadcast rule cannot be expected to outperform
that base rate. Retiring it is what the evidence says, not what flatters the recommender.

Replacement, none of which needs anyone to remember anything:
1. **Structural line (stands, adopted):** runtime IS exposure — 30s budget, short stages, python
   for long runners. Needs no compliance because it removes the window instead of guarding it.
2. **Self-fingerprint proposal (new, mechanical):** lane-status.sh already fingerprints its
   evidentiary inputs but not its own code — the one input that can splice it. Record `$0` bytes +
   HEAD before/after the scan (`git diff --quiet -- "$0"` + rev-parse); on change, report
   UNSTABLE-SELF with no verdict, in the TRANSIENT family (exit 10adjacent, new code, not a new
   exit). Zero compliance, covers exactly the rank-1 file, fails loudly on the Q93 shape.
3. **Retry condition for this retirement (every retirement ships one):** if a SECOND splice
   incident occurs (first: Q93, loud syntax error), re-open — the realized harm rate is what
   retired this, and a second incident changes the rate. Note the base rate honestly: one loud
   incident across dozens of rank 1–3 edits all session; the quiet-splice window this guarded has
   never bitten.

**Kept from the recommendation:** the ranking itself (lane-status first stands), the no-lock
position, the git-checkout-is-the-same-hazard note. Retired: the broadcast. A rule its author
recommends and its only follower ignores was never a rule — writing that down is the method
working on its own output.
