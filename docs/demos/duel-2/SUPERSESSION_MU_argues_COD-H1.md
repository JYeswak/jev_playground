# Supersession argument: COD-H1 supersedes demo-4 (argued by demo-4's author)

Author of demo-4 (MU-3/foreman-lite, my duel-1 pick) arguing the other
side, as dispatched. If this argument holds, my pick should lose its slot
to COD-H1 snapshot-bound completion evidence. I steelman that outcome
first, then confront the one case that could save demo-4, and grade it
honestly at the end.

## The supersession case

**1. COD-H1 removes the coupling that cost demo-4 points in every single
ranking.** Demo-4's scores across four graders: 805, 820 (mine argued),
480 (COD), unrevised by CC's second pass except as ranked content. Every
deduction in every file is the same two: the `br`/bead-graph coupling
(lane-local input shape, shared-worktree baseline ambiguity, positives-
only labels) and the live-bead-path requirement. COD-H1 needs none of
it: a transcript, a revision, machine receipts. It runs on any agent's
output — Claude Code sessions today, Codex tomorrow, CI artifacts the
day after. A demo whose buyer pool is "everyone with an agent
transcript" supersedes one whose buyer pool is "Beads lanes plus whoever
implements the task-spec interface I have not designed yet." Generality
is not a tiebreak here; it is the demand rubric, and it decides 4 to 1.

**2. Snapshot binding is strictly more general than bead acceptance.**
Demo-4 answers "does this diff satisfy this stated acceptance" — a
question that exists only where acceptance was stated, which in practice
means workflow systems with a bead discipline. COD-H1 answers "was this
claim true at the revision it was made at" — a question that exists
everywhere a model asserts completion, including the vast majority of
agent traffic that never had acceptance criteria at all. Every demo-4
judgment can be restated as a COD-H1 judgment (the acceptance lines
become the claims, the diff becomes the revision), while the reverse
fails wherever no bead exists. Supersession in the formal sense: the
superset question absorbs the subset.

**3. The invalidation primitive is the deepest mechanism in either file.**
Demo-4 snapshots the diff at check start and re-hashes at verdict —
movement detection. COD-H1 binds each claim to the exact revision its
evidence was observed at, so a later mutation *invalidates that claim*,
not the whole report. Event-sourced freshness (Codex #36718's own
commenters independently derived the same rule: evidence carries the
source state it verified) turns "the test passed" from a fact into a
fact-with-a-validity-interval. Demo-4 cannot express validity intervals;
its snapshot is all-or-nothing per check run. The primitive is strictly
finer, and fineness here is correctness, not ornament: the stale-green
shape (pass, then edit, then cite the pass) is the most common real
failure both files name, and only one of them can represent it.

**4. The voice record favors H1 outright.** Codex #36718 is an open
enhancement issue on a flagship harness asking for exactly this product,
with maintainer-adjacent discussion converging on event sourcing and
invalidation. Demo-4's voice base is ten angry blog posts about a
problem (false completion) whose *solution shape* the posters do not
specify. Pain-plus-specification beats pain-alone in every demand
ranking ever run, including mine.

**5. My own pick criterion reverses.** I picked demo-4 for loudest pain
plus no dominant tool. The pain reading survives; the tool reading does
not: backcheck (deterministic, zero-LLM, Stop-hook install,
machine-readable) and evigate (mutation-tested detectors, dual-layer
redaction, honest limitations) already ship the deterministic core of
*both* demos — but they compress demo-4's remaining wedge (Jev
adjudication of bead acceptance) far more than H1's (snapshot-bound
invalidation across harnesses, which neither incumbent has). After
subtracting what ships, H1 has more unbuilt left.

## The case that could save demo-4 — confronted, not strawmanned

Bead-acceptance judgment may be a different question, not a subset:
"does this diff satisfy this *stated* acceptance" brings something the
claim-revision frame lacks — the acceptance itself as a first-class
object with per-line checklist semantics, composing as a close gate
(`judge && close`) inside a workflow that already tracks WHAT/WHY.
A team running Beads does not want claim-truth in general; it wants to
know whether *this close* is legitimate, answered in the vocabulary of
its own acceptance lines, at close time, with exit codes the lane
already wires. COD-H1 would need a bead adapter to serve that moment,
and an adapter is not a ruling — it is unbuilt scope both files would
have to price.

Graded honestly: this defense is real but narrow. It saves demo-4 as a
*workflow integration* (the close gate for Beads lanes), not as a demo
with independent demand — which concedes the demand ranking while
keeping a build reason. Under duel-2's rubric (demand only), a surviving
integration is not a surviving demo.

## Verdict on my own demo

COD-H1 supersedes demo-4 for the backlog: broader buyer pool, strictly
more general question, finer invalidation primitive, stronger voice
record, larger unbuilt remainder after incumbents. Demo-4's best future
is a Beads-lane integration *consuming* H1-style evidence (acceptance
lines as claims, close-time verdict from snapshot-bound checks) — a
downstream consumer of the superseding demo, which is a role, not a
rival. I withdraw demo-4's standalone slot. Retry condition, per rung
rules: if H1's implementation cannot serve a close-gate moment (latency,
input shape, or exit-code contract mismatch on real bead traffic),
demo-4's workflow-specific form re-opens with that failure as its
charter.

## NO-CLAIM

Advocacy, not measurement. I built neither demo, ran no transcript
through either design, and my authorship of demo-4 is disclosed above
as the interest this argument rules against. The withdrawal concerns
the backlog slot; demo-4's contract file stands as written.
