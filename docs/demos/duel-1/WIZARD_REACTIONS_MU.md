# Duel 1 — reaction, duelist B (muse) to the codex cross-scores

Scored by pane 2 (codex lineage), `WIZARD_SCORES_COD_ON_MU.md` @ `c221bac`:
**MU-1 875 · MU-3 805 · MU-4 735 · MU-5 640 · MU-2 470.**
Strongest MU-1, weakest MU-2. No merges. My order had been
MU-1 → MU-2 → MU-3 → MU-4 → MU-5; they kept my #1, sank my #2 to last,
and held my #3–#5 in order. The MU-2 call is the duel's most important
finding and it is correct. Details below.

---

## Where they are right, and I am changing the proposals accordingly

### 1. MU-2 credential branch leaks. Conceded fully — the finding of the duel.

Their deciding sentence: *"the literal implementation sends incoming
credential material to Jev in order to decide whether credential material
may enter context"* (`WIZARD_SCORES_COD_ON_MU.md:25-26`). True, no
qualification. My MU-2 specifies a Jev Noul — "carries credential material?"
(`WIZARD_IDEAS_MU.md:65-70`) — over the full incoming tool result. A Jev
question must receive the bytes before the hook can classify them, so a real
secret crosses the paid external boundary pre-decision, landing in a third
party's logs: the exact exposure class the lane secrets rule exists to
prevent. One clarifying boundary, not a defense: my *tests* were clean
(runtime-assembled fake plants, never real key material); the *shipped hook
as specified* was not. Tests clean, design leaking — the worse combination,
because green tests would have certified it.

Adopted redesign (theirs, verbatim in structure): a local deterministic
credential prefilter runs first; the Jev branch sees only a proven redacted
surrogate or the credential question is cut entirely; fail closed on
detector failure. The injection half is unaffected — the 0.99 witness, the
blind corpus, the shadow discipline all stand — so MU-2 survives at reduced
scope: injection screen now, credential gate only behind the prefilter with
its own receipt. Until then their verdict stands: *"should not advance in
its current credential-screening form."*

### 2. MU-4 "extracts verifiable working points" is the same sin I dinged.

Their hit: extraction + citation-span semantics underspecified
(`WIZARD_SCORES_COD_ON_MU.md:182-186`). They are right, and the parallel is
embarrassing in the precise way good grading should be: I scored CC-1 down
740 for "Noul judges, does not extract" and then wrote "extracts verifiable
working points" in MU-4 without a parser. Adopted, both halves: v1 requires
explicit claim blocks with structured citation paths (no arbitrary-prose
extraction claims), and the test plan gains their citation-span-mismatch arm
(a claim must not pass merely because some *other* evidence file contains
the same words). The `uvx`/`npx` fork they flagged goes too: one canonical
runtime per implementation language, per the lane toolchain rule.

### 3. MU-5 fit-refusal as specified is probabilistic theater.

Their hit: shuffled-labels refusal "needs a fixed seed, a pre-registered
statistical threshold, and a small-sample refusal test"
(`WIZARD_SCORES_COD_ON_MU.md:244-246`). Correct. "Refuse on shuffled
labels" without a seed is a coin flip with a lab coat; without a
pre-registered threshold the template grades its own homework. Adopted all
three, plus their receipt line (fit seed, coefficients, split policy).

### 4. MU-3 needs the concurrency baseline; MU-1 needs humbler readiness.

Snapshot diff + bead body at check start, fail closed on mid-check moves,
pin the `br` version, record the start revision
(`WIZARD_SCORES_COD_ON_MU.md:153-169`) — adopted whole; the shared-worktree
amend incident recorded in AGENTS.md's git section is my own lane's proof
that moving-HEAD hazards are not hypothetical. And "greenfield demo with a
good reuse seam, not a ready feature" (their MU-1 §, lines 55–56) replaces
my "ready now": the transcripts and adapter are an input seam, not a demo.
The 875 does not move — the number priced the seam correctly.

---

## Where I push back: exactly one — MU-5 at 640 underprices shippability-now

Their frame prices MU-5 as "greenfield research infrastructure, not a ready
demo" with low immediate lane value. Agreed on lane value (my own file gates
the local application at N≥50). The pushback is on the readiness axis their
own rubric names: MU-5's synthetic-offline-closed-loop — committed fixture →
fit → report → refusal arms, zero key, zero labels, zero lane dependencies —
makes it the *fastest of my five to all four artifacts*. MU-4, scored 95
points higher, needs a writer-side claim-block contract and evidence-corpus
conventions that do not exist yet; MU-3 needs the live bead path; MU-2 needs
the prefilter redesign above. Nothing in MU-5 is waiting on anyone.

Argued: MU-5 640 → 700, still last, gap to MU-4 narrows 95 → 35. I do not
claim the authority to move their number — weighting payoff against
shippability is the conductor's synthesis call, and that ordering is the
named settler: if readiness rules the next pick, MU-5 rises; if immediate
lane payoff rules, 640 stands as written.

---

## What changes in my own scores

Numerically: nothing. My MU_ON_CC numbers stand — with one addition the
duel forced: CC-5 (880, admission screen) gains a ship criterion from the
codex prescription, because the credential-transit constraint is general.
Any admission hook that Jev-screens *bytes* must specify the
credential-bearing-input path (local prefilter first, Jev sees surrogate or
nothing, Boundary excludes real-secret testing) before its L3 receipt
counts. CC-5 made no secret-safety claim so the 880 holds; without that
line its L3 would certify the MU-2 failure in another file.

My MU file stays frozen as the scored artifact — all adoptions above live
in this reaction, to be applied if/when each idea dispatches, not edited
retroactively into the thing that was graded.

## NO-CLAIM

Reaction to one grader; pane 1's scores on nothing (they grade nothing this
duel) and the conductor's synthesis are still open, so there is no consensus
set yet. I ran no harness, built no prefilter, fitted no model: the
redesigns adopted above are specified, not verified.
