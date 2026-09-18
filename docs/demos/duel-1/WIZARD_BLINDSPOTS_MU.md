# Duel-1 blindspots (muse): what neither side proposed

Method: re-read `WIZARD_IDEAS_MU.md`, `WIZARD_IDEAS_CC.md`, both score
files, and all 14 map sections, looking for important demos in the
complement — ideas the duel's shared framings filtered out. Two strong
finds, one weaker third. Each grounded in a map section, each with the four
ship artifacts sketched.

## Why both sides missed them (the shared framing)

Three biases ran through all ten winners and most of the twenty rejects:

1. **Jev judges the world, never us.** Every proposed demo points Jev
   outward — at content, claims, turns, transcripts. Nobody pointed the
   lens at our own outflows (the bytes we hand Jev) or at Jev's own
   cost-effectiveness (whether each call earned its keep).
2. **Measurement over control.** Calibration is measured (harness, audit,
   report) but never wired to a knob. Both sides emit numbers about
   thresholds; neither sets one.
3. **The declared bias.** CC's file states it ("decisions we are about to
   make" over everything else); my file shared it silently (value ×
   readiness, this week). Infrastructure whose payoff is *preventing the
   next failure class* rather than deciding this week's ship never clears
   that bar — which is exactly why the MU-2 leak, the duel's top finding,
   has no corresponding demo on either list.

---

## B1 — sanitize-before-send: the MU-2 finding, generalized (STRONGEST)

**Ground: §1 (screening), mirrored.** Both sides built inbound screens
(MU-2/CC-5 judge bytes *entering* context). Nobody screened the outbound
direction — the bytes *we hand Jev*. Every Jev call in every proposed demo
sends state to a paid third party, and lane state routinely contains the
exact material the secrets rule protects: the MU-2 post-mortem proved the
failure is not hypothetical, it was specified, tested-green, and
one-grader-away from shipping. The general constraint: **no Jev client in
this lane should see unsanitized state, ever.**

**The demo:** `jev-sanitize` — a drop-in sanitizing transport wrapping any
`JevClient`'s `fetch` (the lane's "inject the transport" rule made
executable): deterministic local redaction of secret-shaped strings
(patterns + entropy + per-demo allow-list) in outbound request bodies,
redaction counts in the receipt, asymmetric policy stated up front
(a redacted port degrades one question; a leaked key compromises
everything — so redact always, measure over-redaction as utility loss,
never tune the redactor for recall).

**Ship sketch:** install = one import swap + `npm run check-redact`;
tests = runtime-assembled plants (the gate-30 trick, so fixtures never
carry real shapes) with RED arms both ways (real-shaped secret must not
cross in any lane; a clean state with an allow-listed value must pass
*unredacted* — over-redaction is the silent killer); receipt = per-call
redaction counts + utility delta on a fixed question set; EVAL row with the
Boundary (which shapes are covered, which exfiltration paths — e.g. raw
`fetch` bypassing the wrapper — are explicitly out of scope).

**Why it wins a backlog slot:** it is the only demo that converts the
duel's top finding into prevention, it composes with all ten winners
(each one's Jev client gets the wrapper), and its absence is now a known,
named, unpriced risk in every receipt we have ever written.

## B2 — value-of-information audit: which Jev calls earned their keep

**Ground: §4 (per-decision cost) + the L4 cost rule.** Both sides put cost
in receipts as a *reporting* line ($0.00003/decision and friends). Neither
made cost-effectiveness the *decision variable*. Yet every demo we ship
multiplies a per-call price by a session's call count, and no artifact in
the lane answers "which question types ever change an action."

**The demo:** a post-hoc join — session Jev-call logs (question name,
confidence, cost, latency) against downstream outcomes (did the decision
change the action? did the turn succeed?) — emitting a waste leaderboard:
$/good-decision per question type, with "never-changes-action" questions
named for deletion. First corpus: our own compaction + A/B calls, already
receipted.

**Ship sketch:** install = log-schema doc + join CLI over `runs/*.json`;
tests = synthetic log where question Q-never (canned: low confidence,
action unchanged) must top the waste board (trigger) and a log where every
call flips an action must report zero waste (satisfying); empty/missing log
dir → ERROR; receipt = the leaderboard + dropped-question
recommendations; EVAL row recording that correlation is not causation
(a question can be valuable once and wasteful always — the report says
which regime each is in).

**Why missed:** cost appeared in ten proposals as a number to *record*.
Auditing is a different verb than recording, and the duel never conjugated
it.

## B3 — threshold picker: close the calibration loop (WEAKER, named overlap)

**Ground: §13 (calibration discipline).** Backlog #3 builds the portable
harness (ECE/Brier/coverage out); both duel lists stopped there. Nobody
proposed the consumer: given a calibration receipt + a required coverage,
emit the recommended threshold, expected accuracy, and abstention rate —
then backtest the recommendation on a held-out split and report whether it
held. Measurement becomes control; the foundation receipt's "threshold
≥0.75 → accuracy 1.0 at ≥90% coverage" becomes a procedure instead of an
anecdote.

**Overlap stated plainly:** if backlog #3's owner considers threshold
recommendation in-scope, this is a feature of #3, not a demo — file it
there and kill B3. It earns its place here only if #3 stays
metrics-only, which is currently true.

**Ship sketch:** install = `pick-threshold <calibration-receipt.json>
--coverage 0.9`; tests = synthetic calibration table with a known-optimal
cut (must emit it), degenerate table (no cut achieves coverage → refuse
with reason, never return 0.0); receipt = threshold, expected accuracy,
abstention rate, held-out validation delta; EVAL row with the corpus it
was fitted on.

---

## NO-CLAIM

Gap analysis, not measurement. No sanitizer written, no audit joined, no
threshold fitted. The "why missed" above is itself a hypothesis about our
process — testable only by whether the next duel's lists still show the
same complement.
