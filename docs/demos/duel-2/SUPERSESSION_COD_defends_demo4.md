# Supersession defense — why Demo-4 survives COD-H1

Status: steelman written against my own candidate.
Question: does COD-H1 “snapshot-bound completion evidence” supersede Demo-4 “foreman-lite”?
Position defended: **Demo-4 survives; the two candidates are genuinely distinct at their current
contracts.**
No supersession verdict is claimed for pane 3; this is the required argument for later adjudication.

## Short answer

COD-H1 verifies whether an agent's **claim** is supported by machine-observable evidence tied to the
revision at which the claim was made. Demo-4 judges whether a concrete **bead acceptance contract**
is answered by the current diff and evidence, then chooses an operational completion state from a
finite set. Those are related completion controls, but they ask different questions, consume
different authoritative inputs, produce different failure states, and run at different boundaries.

H1 can prove “the command recorded 22 passing tests at revision R.” It cannot, from that fact alone,
prove “this bead's acceptance line is implemented,” decide whether all acceptance lines are
answered, or distinguish `requirements-met` from `tests-sufficient` under Demo-4's contract. Demo-4
can make those decisions even when the agent made no numeric claim and no transcript receipt exists.
Conversely, H1 catches stale or unsupported claims after a session revision changes, a condition
that Demo-4 intentionally reports as moving ground and leaves to a human.

The strongest honest conclusion is **both survive**, with an integration seam: H1 can provide
machine-observable receipts that Demo-4 cites as evidence, while Demo-4 remains the acceptance-aware
close judge. If a future H1 contract adds explicit acceptance mapping and a finite close-state
policy, the argument must be rerun; today's H1 does not contain that contract.

## Contract comparison

| Dimension | Demo-4 foreman-lite | COD-H1 snapshot-bound completion evidence |
|---|---|---|
| Primary object | Bead WHAT and ACCEPTANCE lines | Agent/session claims and recorded commands |
| Core question | Do the current diff and evidence answer every stated acceptance line? | Did the claimed event occur, with evidence tied to the claimed revision? |
| Authoritative context | `br show`, explicit baseline, current diff, bead body | Transcript, revision, command receipts, exit status, output, hashes |
| Jev Choice | Selects `complete`, `requirements-met`, `tests-sufficient`, `verify-needed`, or `human-needed` | H1 hunt does not define an acceptance-aware finite close state |
| Jev Noul | One per acceptance line: do cited hunks answer this line? | Claim-to-receipt relation: proven/contradicted/unknown/stale shape |
| Safety boundary | Empty diff, missing baseline, moving ground, unanswered acceptance | Evidence stale after mutation, missing/partial/failed producer evidence |
| Timing | Before a bead owner closes work | At or after an agent completion claim / report |
| Buyer | Beads/issue-tracker operator supervising agent workers | Any platform auditing agent completion claims |
| Failure it uniquely catches | Unanswered requirement despite plausible passing tests | “All tests pass” / “done” claims without exact usable evidence |

The similarity is “independent check of agent completion.” Similarity is not identity. The lane's
supersession rule must compare the propositions and their observables, not the shared marketing word
“completion.”

## The strongest case for Demo-4

### 1. Acceptance satisfaction is not claim verification

Demo-4's central input is a structured acceptance contract. A bead body supplies WHAT and one or
more ACCEPTANCE lines; the current diff is evaluated against each line. Its Noul question is:

> Acceptance line: `<line>`. The cited diff hunks are: `<hunks>`. The hunks answer the line.

The true criterion is that the hunks implement or verify what the line requires. The false criterion
is that the hunks are unrelated. The per-line result can be `supported` or `unanswered`, and a
`complete` overall result with an unanswered line is refused.

That relation cannot be derived from a transcript claim alone. A claim such as “implemented the
retry behavior” is an assertion. H1 can ask whether the claim has a command receipt, revision, and
producer result. It cannot know whether “retry behavior” answers the bead's actual acceptance line
unless it receives and interprets the acceptance contract. H1's genericity is an advantage for
cross-agent evidence, but it removes the very domain object that Demo-4 judges.

### 2. Demo-4 has an operational state machine, not just an evidence label

The Demo-4 Choice candidates are:

```text
complete
requirements-met
tests-sufficient
verify-needed
human-needed
```

The Choice instruction defines the semantic differences. `complete` requires every acceptance line
to have evidence; `requirements-met` means behavior is done but verification is thin;
`tests-sufficient` means tests are verified while other evidence is thin; `verify-needed` names
gaps that block closing; `human-needed` means the evidence cannot decide, including empty diff,
moved ground, or an unscopable bead.

H1's proposed statuses—proven, contradicted, unknown, stale—are valuable for evidence records, but
they are not equivalent to an operational close state. A set of proven command claims may still leave
an acceptance line unanswered. An unknown claim does not say whether the bead owner should run a
specific verification, ask a human, or leave the work open. Demo-4's Choice is the controlled
transition from per-line evidence to a close recommendation; its constraints prevent probability
from becoming permission.

### 3. A tracker is a feature when the question is tracker-native

The “requires `br`” difference is not automatically a defect. Demo-4 is for an operator already
using an issue tracker whose body contains WHAT and ACCEPTANCE. `br show` is the source of the task
contract, status, and identity; refusing a title-only bead prevents an agent from closing an
underspecified unit. Removing `br` would remove the authoritative acceptance object rather than
make the same judge portable.

H1's tracker-free input is valuable for agent transcripts, CI logs, and heterogeneous systems. It
should remain tracker-free. But a broader input surface does not subsume a narrower contract that
uses richer task semantics. A compiler warning tool does not supersede a type checker because both
inspect source; a receipt verifier does not supersede an acceptance judge because both discuss “done.”

### 4. The timing boundary is different

Demo-4 runs at the close boundary while the bead owner still has a live task and a current shared
worktree. It records a baseline, reads the bead, snapshots the body and diff, and rechecks them at
verdict time. A moving HEAD or bead body becomes `human-needed`; the command does not silently retry
against new ground.

H1 is designed to audit claims against receipts and revisions, including claims whose evidence
became stale after a later mutation. That is a valuable post-claim or cross-session boundary. The
same event is intentionally different:

- Demo-4 says, “the ground moved while I was judging this acceptance; human, re-run.”
- H1 says, “the completion claim is stale against the revision now observed; do not treat it as
  proven.”

A system can use H1 to detect stale historical claims and Demo-4 to prevent closing the current
bead on a moving snapshot. Neither output is a redundant serialization of the other.

## Non-subsumption examples

The following cases separate the candidates without relying on taste.

### Case A — behavior acceptance with no numeric claim

Bead acceptance:

```text
When the upstream request returns 429, retry with exponential backoff and preserve the request id.
```

The agent changes two files and writes no commit message claim. It runs no test command but provides a
diff. Demo-4 can inspect the acceptance line, cite the relevant hunks, and return
`verify-needed` or `requirements-met` based on evidence. H1 has no claim to parse and no receipt to
verify; it cannot answer the acceptance question. This is a clean Demo-4-only case.

### Case B — supported test claim, unmet acceptance

The agent says “all tests pass,” and H1 verifies the claim against a full-suite receipt at revision
R. The bead additionally requires a migration to preserve an existing index and a documentation
example to use the new flag. The test suite does not exercise either acceptance line. Demo-4 marks
those lines `unanswered` and refuses `complete`; H1 correctly marks the test claim proven but cannot
turn that proof into a close decision. This is the central reason acceptance judgment survives.

### Case C — stale claim with no current bead

An agent reports “implemented the endpoint and all tests pass” at revision R, then a later commit
changes the serializer. H1 can bind the original claims to R, detect that the evidence is stale or
not applicable to revision S, and preserve an audit trail. Demo-4 has no reason to run because there
is no current bead close request. This is an H1-only case.

### Case D — empty diff

A bead has a complete-looking acceptance body but the current diff is empty. Demo-4 has a structural
RED arm: `human-needed`, never `complete`, regardless of model probability. H1 may find no completion
claim, or may verify a historical command receipt; neither result is the acceptance-aware empty-diff
close state. The two commands can both run and produce different correct outputs.

### Case E — acceptance is satisfied by non-command evidence

A bead acceptance requires adding a documented configuration key and wiring it into an existing
path. The diff shows the key and wiring; no test command mentions it. Demo-4 can judge the hunk
against the acceptance line and report thin verification. H1's command-receipt contract has no
claim or command evidence about the configuration requirement, so it cannot replace the Noul's
acceptance relation.

### Case F — H1 receipt used inside Demo-4

A future Demo-4 run can cite an H1 receipt saying a command ran at the exact baseline revision and
returned exit 0. That makes Demo-4's per-line evidence stronger; it does not make H1 the acceptance
judge. Composition is evidence that the interfaces are complementary, not proof of duplication.

## What COD-H1 does better, conceded without qualification

The defense must not hide H1's advantage. H1 has a broader audience, does not require Beads, and
addresses a frequent failure in which agents report “done” or “all tests pass” without machine-
observable evidence. Its revision binding and stale-evidence status are stronger than Demo-4's
current close command for retrospective transcript auditing. H1 should be independently scored by
pane 3 and, if it clears the hunt gate, should receive its own thin-proof fixture.

H1 may supersede a **generic** “did the agent really finish?” wrapper that merely calls a model on a
completion message. Demo-4 is not only that wrapper. Its acceptance-line checklist, finite close
state, tracker contract, snapshot behavior, and no-automatic-close rule are the differentiators.
The proper response to H1's existence is to narrow Demo-4's README/contract language away from a
universal completion judge and toward an acceptance-aware close judge, not to delete it for sharing
an input phrase.

## What Demo-4 does better, conceded without qualification

Demo-4 has a more precise operational contract for a Beads operator:

- one acceptance line is one inspectable judgment unit;
- the candidate verdicts have fixed meanings and exit behavior;
- missing evidence withholds instead of approving;
- empty diff, moved ground, and title-only bead are deterministic RED arms;
- no automatic `br close` occurs;
- a human remains the final closer.

Those are not cosmetic details. They are the semantics needed to decide whether an identified task
may move from in-progress to human-closeable. H1's generic evidence report can feed those decisions
but does not supply them.

## Decision procedure for the eventual non-author adjudication

Pane 3 should argue that H1 supersedes Demo-4 by demonstrating one of these concrete facts:

1. H1's authoritative contract already consumes bead WHAT/ACCEPTANCE and emits Demo-4's finite
   close-state semantics; or
2. every Demo-4-only case above is already answered by H1 without adding a tracker adapter or
   changing its question; or
3. the Demo-4 acceptance checklist is merely a claim-to-receipt mapping in disguise.

If none is shown, both survive. If pane 3 proves that H1 adds acceptance mapping and close-state
semantics without changing its contract, then supersession is legitimate. Similar words,
co-located buyers, or a preference for tracker-free installation are not sufficient evidence.

## Conclusion

**Demo-4 survives COD-H1 on the strongest available structural case.** H1 verifies claims against
revision-bound receipts; Demo-4 judges acceptance satisfaction and operational close state against a
tracker-native task contract. They can compose, and each has cases the other cannot answer without
changing its object of judgment.

This is a defense, not a self-awarded supersession ruling. Pane 3's counterargument and a later
arms-length adjudication remain required. If both authors ultimately concede, withdraw the weaker
candidate with a retry condition. If both hold, keep both at their own rungs and let thin proof
measure whether either is operationally valuable.

## NO-CLAIM

No H1 or Demo-4 implementation was run for this argument. No user study, model call, install proof,
calibration result, or measured lift is claimed. The distinction is derived from the committed
contracts, §3e's comparison table, and explicit counterexample cases; it is not an adoption or
promotion verdict.
